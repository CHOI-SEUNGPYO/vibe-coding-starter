# 목적에 맞게 환경 고르기

이 저장소는 Codex가 프로젝트 규칙, 스킬, 도구를 함께 읽는 **작업 환경**이다. 프레임워크나 제품 코드를 강제로 만들지는 않는다. 기본 활성 환경은 `web`이며, 다른 목적이라면 아래 프로필로 바꾼다.

| 프로필 | 이런 작업에 사용 | 포함 스킬 | 활성 MCP | 제품에서 확인할 것 |
| --- | --- | --- | --- | --- |
| `minimal` | 작은 버그 수정, CLI, 기존 프로젝트 탐색 | 공통 6종 | 없음 | 변경 전 재현, 변경 후 결과 |
| `web` | 웹앱, 대시보드, 화면 구현 | 공통 + UI UX Pro Max, React 지침, Playwright, CI 처리 | OpenAI Docs, Context7, Playwright | 핵심 흐름, 작은 화면, 오류·빈 상태, 접근성 |
| `api` | 서버, REST API, 외부 API 연결 | 공통 + API 설계, Postgres 지침, CI 처리 | OpenAI Docs, Context7 | 입력 검증, 권한, 멱등성, 오류 응답, 저장소 통합 |
| `data` | CSV 처리, 분석, 예측 실험 | 공통 + Python 패턴, Postgres 지침 | OpenAI Docs, Context7 | 스키마, 누락, 데이터 누수, 재현 가능한 지표 |
| `automation` | 반복 작업, 브라우저 자동화, PR 대응 | 공통 + API 설계, Python 패턴, PR 의견, Playwright | OpenAI Docs, Context7, Playwright | 미리보기, 재실행, 중간 실패, 결과 확인 |

공통 6종은 `task-delivery`, `parallel-work`, `release-check`, `ponytail`, `ponytail-review`, `debugging-and-error-recovery`다. 전부 매번 실행하는 것이 아니라 구현·원인 조사·검토 등 해당 단계에서 사용한다. OpenAI Docs는 OpenAI API·Codex 설정에, Context7은 다른 라이브러리 문서를 찾는 데 사용한다. 기술 스택 지침은 React·Postgres·Python이 실제로 해당될 때만 적용한다. [스킬별 사용 순서와 요청 예시](skill-routing.md)

## 프로필 적용

저장소 루트에서 실행한다. Windows에서 `python`이 Microsoft Store로 연결된다면 `python3` 또는 `py -3`를 사용한다.

```bash
python scripts/vibe.py init --profile api --dry-run
python scripts/vibe.py init --profile api --update
python scripts/vibe.py doctor
```

`--update`는 이전에 설치한 뒤 직접 수정하지 않은 관리 파일만 갱신한다. 수정한 파일이 충돌하면 자동으로 덮어쓰지 않는다. 기존 내용을 살릴지 새 설정을 받을지 diff를 보고 합친다. 목적을 바꿔도 애플리케이션 소스나 전역 설정을 바꾸지 않는다.

각 프로필의 `mcp` 목록은 활성 연결이다. GitHub는 이미 연결된 앱을 우선 사용하고, 독립 CLI에서 필요하면 `--mcp github`로 추가한다. 토큰은 별도로 준비해야 한다. 자세한 연결 조건은 [MCP 안내](mcp.md)를 따른다.

## 프로젝트마다 채울 내용

`.vibe/project.json`의 목표와 검증 명령을 실제 제품에 맞게 채운다. `checks`가 비어 있으면 제품 검증을 통과한 것으로 취급하지 않는다. 패키지 관리자는 기존 lockfile을 유지하고, 새 프로젝트에서만 팀이 사용할 도구를 정한다.

`checks`의 명령은 문자열 배열로 적고 `timeout_seconds`로 제한 시간을 정한다. `{python}`은 기본적으로 현재 검증 도구를 실행한 Python이며, 아래 `venv`를 지정하면 앱의 가상환경 Python으로 바뀐다. 제한 시간이 지나면 실행 중인 검사와 그 하위 프로세스를 종료한다. Windows에서는 검사가 정상 종료되어도 같은 작업에 남아 있는 하위 프로세스를 정리하므로, 계속 켜 둘 개발 서버는 검사 목록과 별도로 실행한다. 이 실행기는 신뢰하는 프로젝트 검사를 실행하는 도구이며 임의 코드를 격리하는 보안 경계가 아니다.

Windows의 `npm` 같은 `.cmd`·`.bat` 실행 파일은 운영체제가 명령 해석기를 거친다. 예기치 않은 명령 연결·변수 치환을 막기 위해 이 형식의 실행 경로·인수에 `& | < > ^ % ! ( ) "` 또는 줄바꿈이 있으면 거부한다. 해당 문자가 필요한 검사는 `node`나 Python으로 실제 스크립트를 직접 실행한다. 일반 `npm test`처럼 특수문자가 없는 명령은 실행 파일을 찾아 처리한다.

| 목적 | 준비할 실행 환경 | 권장 검증 조합 |
| --- | --- | --- |
| 웹 | 프로젝트가 정한 Node 버전과 lockfile, 개발 서버 주소 | 타입 검사 + 핵심 단위 테스트 + 실제 브라우저 흐름 |
| API | 프로젝트 언어 런타임, 로컬 또는 테스트용 DB | 계약 테스트 + 인증·권한 테스트 + 통합 테스트 |
| 데이터 | 별도 Python 가상환경, 버전이 고정된 의존성, 공개 가능한 샘플 | 스키마 검사 + 작은 입력 회귀 테스트 + 고정 seed 재실행 |
| 자동화 | 대상 시스템의 테스트 계정과 최소 권한 연결 | dry-run + 두 번 실행 + 실패 후 재시도 |
| 최소 환경 | 대상 언어 런타임만 | 실패 재현과 변경된 동작 검사 |

데이터 프로필에서 회사 원본·개인정보·비공개 자료를 저장소에 넣지 않는다. 분석은 원본을 읽고 별도 결과를 만들도록 구성하며, 학습·평가 데이터를 나눈 근거를 남긴다. 자동화는 읽기 작업을 먼저 확인한 뒤, 사용자가 요청한 쓰기 작업만 수행한다.

### Python 앱의 가상환경 연결

Python API·데이터 앱의 패키지는 별도 가상환경에 설치한다. starter를 실행하는 Python과 앱의 Python은 다를 수 있다. `.vibe/project.json`의 `checks` 배열에 다음처럼 **실제 앱 검사**를 추가한다. 테스트 경로와 명령은 만든 앱에 맞춘다.

```json
{
  "name": "API 계약·저장·인증",
  "cwd": "apps/api",
  "venv": ".venv",
  "command": ["{python}", "-m", "unittest", "discover", "-s", "tests", "-v"],
  "timeout_seconds": 60
}
```

- `cwd`는 저장소 루트 기준, `venv`는 **그 `cwd` 기준 상대 경로**다. 위 설정은 `apps/api/.venv`를 가리킨다. 다른 이름도 지정할 수 있다.
- `venv`를 지정한 명령의 첫 항목은 정확히 `{python}`이어야 한다. Windows에서는 `Scripts/python.exe`, macOS/Linux에서는 `bin/python`을 찾아 실행하므로 OS 경로를 검사 명령에 고정하지 않는다.
- `python -m venv apps/api/.venv`로 먼저 만들고, 그 가상환경의 Python으로 앱 의존성을 설치한다. 가상환경 활성화나 `Activate.ps1` 실행 정책 변경은 필요 없다. [Python 공식 venv 안내](https://docs.python.org/3/library/venv.html)
- 가상환경의 `pyvenv.cfg`·실행 파일이 없거나 경로가 잘못되면 **어떤 검사도 실행하기 전에 실패**한다. 기본 Python으로 조용히 바꾸지 않는다. `.venv` 자체를 링크로 연결하지 않으며, POSIX 가상환경의 표준 `bin/python` 링크는 지원한다.
- `venv`를 생략한 기존 `{python}` 명령은 그대로 동작한다. Python이 아닌 검사는 기존 `node`·`npm` 등의 실행 명령을 유지한다.

이후에는 저장소 루트에서 `python scripts/vibe.py verify` 하나로 검사한다. CI도 **현재 프로필 check → 런타임·가상환경 준비 → 앱 잠금 의존성 설치 → verify** 순으로 맞춘다. starter의 CI는 현재 프로필을 바꾸지 않지만 새 앱의 패키지 설치까지 자동으로 추론하지는 않는다. 새 앱을 추가한 작업에서 CI도 수정해야 한다. 서버를 계속 켜는 명령은 검사 목록에 넣지 않는다.

## 목적별 레퍼런스와 작업 방법

아래 링크는 2026-11-15에 해당 공식 페이지를 확인했다. 레퍼런스에서 무엇을 배울지 정하고 프로젝트의 완료 조건으로 연결한다. 디자인 사이트별 접근 범위와 전체 비교는 [디자인 레퍼런스 안내](design-references.md)에 있다.

### `minimal` — 작은 수정

바로 실행할 코드는 [독서 JSON 검색 예제](../examples/reading/minimal/README.md), 새 요청용 양식은 [작은 도구 양식](../templates/first-minimal-task.md)에 있다. `setup.py --profile minimal`은 스킬6종을 적용하며 MCP·Node·브라우저 준비를 요구하지 않는다. 예제는 읽기 전용 검색·필터와 잘못된 입력·원본 보존을 검사한다. 각 예제의 `checks.example.json`은 기존 프로젝트 검사 목록에 병합해서 사용한다.

문제를 재현하고 기존 구현 방식으로 고친 다음 해당 동작을 확인한다. UI가 바뀐다면 [Radix UI](https://www.radix-ui.com/)에서 필요한 컴포넌트의 키보드·포커스 패턴만 확인한다. CLI나 순수 로직 수정에는 디자인 사이트나 브라우저 MCP를 추가할 필요가 없다.

```text
설정 대화상자를 Escape로 닫았을 때 포커스가 열기 버튼으로 돌아오게 고쳐줘.
https://www.radix-ui.com/ 의 대화상자 동작을 참고하되 현재 라이브러리를 유지해줘.
변경 전 문제를 재현하고 키보드로 열기 → 닫기 → 다시 열기를 확인해줘.
```

### `web` — 화면과 사용자 흐름

랜딩·브랜드 사이트는 [Lapa Ninja](https://www.lapa.ninja/), [Landbook](https://land-book.com/design/website/single-page), [Recent](https://recent.design/)에서 정보 순서와 시각적 방향을 정한다. SaaS·대시보드는 [Mobbin](https://mobbin.com/)과 [SaaSFrame](https://www.saasframe.io/)에서 탐색·설정·빈 상태를 살펴본다. [shadcn/ui](https://ui.shadcn.com/)는 필요한 컴포넌트 구현을 검토할 때 쓴다. 대표 화면 하나를 만든 뒤 작은 화면과 실제 데이터로 확장한다.

```text
팀의 요청 관리 대시보드를 만들어줘. https://www.saasframe.io/ 의 대시보드와
빈 상태 예시 2개를 골라 정보 배치와 필터 구조를 설명하고 우리 작업에 적용해줘.
요청 검색 → 상세 보기 → 담당자 변경 흐름을 먼저 연결해줘.
Playwright로 좁은 화면, 키보드 탐색, 검색 결과 없음, 저장 실패를 확인해줘.
```

### `api` — 계약과 오류 처리

[OpenAPI 공식 문서](https://spec.openapis.org/)를 기준으로 요청·응답·인증 계약을 먼저 적고, [Swagger UI](https://swagger.io/open-source/swagger-ui/)와 [Petstore 예제](https://petstore.swagger.io/)에서 API 문서를 보여 주는 방식을 참고한다. 실제 프로젝트가 지원하는 명세 버전을 따른다. FastAPI를 선택하면 [시작 안내](https://fastapi.tiangolo.com/tutorial/first-steps/)와 [TestClient 검사 안내](https://fastapi.tiangolo.com/tutorial/testing/)를 설치 버전에 맞춰 확인한다.

처음 시작하는 전체 명령과 완성된 독서 기록 API 지시는 [README API 시작 순서](../README.md#api-개발로-시작하기), 다른 요구사항을 채울 양식은 [API 첫 작업 지시](../templates/first-api-task.md)에 있다. `python scripts/setup.py --profile api`는 스킬 9종과 문서 MCP 2개를 준비한다. Node22 이상은 MCP 검사에 쓰이며 앱의 런타임·DB·의존성은 별도로 준비한다. SQLite 예제에 Postgres 전문 지침을 억지로 적용하지 않는다.

서버만 만드는 작업은 실제 HTTP·계약·저장소 통합 검사로 검증한다. 화면 디자인과 Playwright는 필요하지 않다. 관리자 화면도 필요하면 웹 레퍼런스를 함께 쓰고 [MCP 안내](mcp.md)에 따라 브라우저 연결과 의존성을 추가한다. 단일 개인 토큰에는 사용자별 권한을 보장한다고 쓰지 않고, 다중 사용자라면 타 사용자 데이터 접근도 검사한다. DB 쓰기 실패와 **실제 프로세스 재시작 후 저장 보존**을 확인하고, POST·PATCH·DELETE의 재시도 정책을 각각 정한다.

```text
요청 생성·조회 API를 구현해줘. https://spec.openapis.org/ 의 명세 구조를
참고해 현재 프레임워크가 지원하는 버전으로 요청·응답·오류를 문서화해줘.
잘못된 입력, 인증 없음, 권한 없는 조회, 정상 생성 후 조회를 테스트해줘.
관리자 화면은 이번 범위에 포함하지 않아.
```

### `data` — 재현 가능한 분석과 시각화

작은 샘플에서 스키마·단위·결측값을 먼저 확인한다. 시각화는 [Observable Plot 갤러리](https://observablehq.com/@observablehq/plot-gallery)와 [Vega-Lite 갤러리](https://vega.github.io/vega-lite/examples/)에서 비교·추세·분포에 맞는 표현을 고른다. 이 링크를 참고했다고 JavaScript로 옮길 필요는 없다. 기존 Python 등 프로젝트 도구로 같은 표현을 구현해도 된다. 결과를 해석할 때 표본 크기와 집계 기준을 함께 표시한다.

[README 데이터 시작 순서](../README.md#데이터-분석으로-시작하기)에는 실제 독서 CSV 실습과 첫 지시·실행 명령·내 파일 적용 방법이 있다. 다른 분석은 [데이터 첫 작업 양식](../templates/first-data-task.md)을 채운다. `python scripts/setup.py --profile data`는 스킬 8종과 문서 MCP 2개를 준비하며 분석 패키지·차트·앱 검사를 대신 만들지는 않는다.

- **입력과 공개 범위:** 공개 가능한 가상 샘플은 `apps/data/samples/`, 개인 원본은 `apps/data/data/private/`, 결과는 `apps/data/output/`에 둔다. starter의 `**/data/private/`와 `output/` 제외 규칙은 이미 추적된 파일에는 적용되지 않는다. `*.csv` 전체를 숨겨 공개 검산 자료까지 빠뜨리지 않는다. 다른 프로젝트에 설정만 설치했다면 그 프로젝트의 Git 제외 규칙도 확인한다.
- **스키마와 오류:** UTF-8 BOM 여부와 인코딩을 명시한다. 누락·중복·잘못된 날짜·숫자·행 길이를 조용히 버리지 않는다. 빈 데이터와 읽기 실패를 구분하며 집계 분모·기간·중복 정책을 설명한다. 독서 실습은 잘못된 행이 하나라도 있으면 전체 분석을 실패시킨다.
- **실행 환경:** 전용 `.venv`와 잠금 파일을 사용하고 전이 의존성까지 확인한다. 실습의 Matplotlib3.11.2는 Python3.11 이상이지만 잠금 NumPy2.5.5·contourpy1.4.0은 3.12 이상을 요구해, 앱 안내와 CI를 3.12 이상으로 맞췄다. starter 자체의 Python3.11 지원과 구분한다.
- **그림:** [Matplotlib 갤러리](https://matplotlib.org/stable/gallery/index.html)를 참고하고 GUI 없이 파일을 만드는 backend와 한글 폰트·라이선스를 준비한다. 파일이 생긴 것만 확인하지 말고 실제 PNG에서 글자·축·잘림·빈 상태를 확인한다. 정적인 차트 프로젝트에 Playwright나 웹 서버를 필수로 넣지 않는다.
- **검사와 재실행:** 고정 정답을 별도로 계산해 검산하고 원본 해시·반복 집계 일치·출력 실패 후 보존을 확인한다. 실습은 기존 결과 폴더를 덮어쓰지 않으므로 새 출력 이름을 지정한다. `.vibe/project.json`에는 `cwd: apps/data`, `venv: .venv`로 앱 검사를 등록하고 CI에서 그 패키지를 먼저 설치한다. `verify`의 “등록된 검사”가 starter 검사뿐인지 앱 계산까지 포함하는지 구분한다.

```text
월별 처리시간 CSV를 분석해줘. https://vega.github.io/vega-lite/examples/ 에서
분포 비교와 추세를 보여 주는 예시를 골라 선택 이유를 설명해줘.
원본은 보존하고 단위·결측값·집계 기준을 확인한 뒤 표와 그래프를 만들어줘.
작은 고정 샘플의 계산 결과와 다시 실행했을 때의 일치 여부를 검사해줘.
```

### `automation` — 반복 실행과 실패 복구

[주간 독서 요약 예제](../examples/reading/automation/README.md)는 기본 dry-run, 명시적 apply, 같은 입력의 중복 실행 방지, 결과 변조·누락 확인을 실제로 구현했다. [자동화 첫 작업 양식](../templates/first-automation-task.md)에는 트리거·입력·쓰기 범위·재시도·실패 복구를 채운다. 프로필은 스킬10종과 문서·브라우저 MCP3개를 준비하지만, 로컬 파일 자동화에서 사용자 브라우저나 외부 전송을 억지로 사용하지 않는다. 실행 CLI와 정기 일정 등록은 별개다.

[n8n 워크플로 템플릿](https://n8n.io/workflows/)에서 비슷한 작업의 트리거·변환·분기·결과 저장 순서를 참고한다. 템플릿의 외부 연결이나 유료 기능을 자동으로 설치·구독하지 않는다. 현재 선택한 도구로 구현하고, 테스트 데이터로 미리보기·중복 실행·실패 후 재시도를 확인한다. 사람이 검토하는 화면이 필요하면 [Mobbin](https://mobbin.com/)의 확인·오류 처리 흐름도 참고한다.

```text
CSV의 새 요청을 정리해 결과 파일을 만드는 자동화를 만들어줘.
https://n8n.io/workflows/ 에서 파일 처리 흐름의 단계 구성을 참고하되
이 프로젝트의 Python으로 구현해줘. 실제 외부 메시지는 보내지 않아.
dry-run 결과, 두 번 실행했을 때 중복 여부, 중간 실패 후 복구를 검사해줘.
```

## 모델과 병렬 작업

모델 ID와 추론 수준은 고정하지 않았다. 현재 계정에서 선택한 모델을 이어받으므로 사용할 수 없는 모델 이름 때문에 실행이 막히지 않는다. 복잡한 설계·원인 분석은 충분한 추론 수준을, 단순 수정은 가벼운 설정을 선택하면 된다. 이 선택은 제품의 테스트를 대신하지 않는다.

`config/codex.base.toml`은 부모 1개와 보조 에이전트 최대 3개를 허용한다. `explorer`는 조사, `reviewer`는 변경 검토, `tester`는 검증을 맡는다. 파일 작성 권한이 겹치는 일은 주 에이전트가 순서를 정한다. 짧은 수정에는 보조 에이전트를 만들 필요가 없다.

현재 Codex의 사용자 정의 에이전트는 `.codex/agents/*.toml`에서 읽는다. 조사·검토 역할의 “파일을 수정하지 않는다”는 작업 지침이며 별도 읽기 전용 격리를 만들지는 않는다. 실제 권한은 부모 세션과 관리 정책을 따른다. [공식 하위 에이전트 문서](https://learn.chatgpt.com/docs/agent-configuration/subagents)

## 호환 범위

Python 명령의 안내와 오류는 콘솔 언어에 관계없이 UTF-8로 출력한다. `--target`은 심볼릭 링크나 junction을 포함하지 않는 실제 경로를 사용한다. macOS의 `/var`처럼 운영체제가 제공하는 링크를 거치는 임시 경로를 자동 생성한다면, 대상 폴더를 정한 뒤 `Path(...).resolve()`로 실제 경로를 확인해 전달한다. 의도적으로 지정한 링크를 설치 도구가 자동으로 따라가지는 않는다.

기본 TOML은 2026-11-15에 Codex CLI `0.169.0-alpha.11.1`의 strict 설정 로딩으로 확인했다. 오래된 Codex에서 키를 거부하면 클라이언트를 업데이트하고 [현재 설정 문서](https://learn.chatgpt.com/docs/config-file/config-reference)를 확인한다. 프로젝트를 신뢰한 뒤 새 세션을 열어 설정과 스킬을 다시 읽게 한다. 이 저장소가 계정 권한·조직 정책·클라우드 실행 환경을 변경하지는 않는다.
