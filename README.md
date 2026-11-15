# Vibe Coding Starter

[![Validate starter](https://github.com/CHOI-SEUNGPYO/vibe-coding-starter/actions/workflows/validate.yml/badge.svg)](https://github.com/CHOI-SEUNGPYO/vibe-coding-starter/actions/workflows/validate.yml)

**공식 도구와 커뮤니티 전문 스킬을 조합한 Codex 개발 환경.** 작업 규칙, 역할별 에이전트, 스킬 14종, MCP 연결과 검증 도구가 들어 있습니다. 기본 `web` 환경에는 스킬 10종과 MCP 3개가 이미 적용되어 있습니다.

프레임워크나 모델 이름을 강제하지 않습니다. 현재 계정의 모델과 프로젝트의 기술 스택을 유지하고, 해야 할 일에 맞춰 환경을 고릅니다. 새 컴퓨터에서 필요한 작업은 의존성 복원과 본인 계정 인증입니다.

## 바로 시작하기

아래는 **Windows에서 독서 기록 웹앱을 처음 만드는 순서**입니다. 환경을 준비한 뒤 첫 작업 지시를 복사해 Codex에 보내면 됩니다. 직접 원하는 앱으로 시작하려면 [첫 작업 지시 양식](templates/first-task.md)의 빈칸을 채우세요.

### 1. 필요한 프로그램 준비하기

[Git](https://git-scm.com/downloads), [Python **3.11 이상**](https://www.python.org/downloads/), [Node.js **22 이상**](https://nodejs.org/en/download), Codex와 GitHub 계정이 필요합니다. 설치 후 PowerShell을 새로 열고 확인합니다.

```powershell
git --version
python --version
node --version
npm.cmd --version
```

명령을 찾지 못하면 해당 프로그램 설치와 PATH 설정을 확인하세요. Windows에서 `python`이 Microsoft Store를 열거나 동작하지 않으면 `py -3 --version`으로 확인하고, 아래의 `python`을 모두 `py -3`로 바꿔 실행합니다. Windows 예시는 PowerShell의 스크립트 실행 정책에 막히지 않도록 `npm.cmd`를 사용합니다. 실행 정책을 변경할 필요는 없습니다. macOS/Linux에서는 `npm`을 사용하세요. Node.js 22는 이 환경의 최소 조건이며, 새 앱은 선택한 프레임워크가 요구하는 세부 버전도 확인해야 합니다.

### 2. 프로젝트용 저장소 만들고 내려받기

[이 저장소](https://github.com/CHOI-SEUNGPYO/vibe-coding-starter)에서 **Use this template → Create a new repository**를 누르고 이름을 `reading-log`로 정합니다. Owner는 본인 계정, 공개 범위는 새 프로젝트에 맞게 선택합니다. 여러 독립 프로젝트를 만들 때는 Template이 편합니다. 원본과 연결해 변경을 추적하거나 기여하려면 **Fork**를 사용해도 되며, 이후 순서는 같습니다.

만든 **내 저장소**에서 **Code → HTTPS** 주소를 복사합니다. 아래 `YOUR-ACCOUNT`를 본인 GitHub 계정으로 바꾸고, 저장소 이름도 다르게 정했다면 함께 바꿉니다. 같은 위치에 `reading-log` 폴더가 이미 있다면 새 폴더 이름을 사용하세요.

```powershell
cd "$env:USERPROFILE\Documents"
git clone https://github.com/YOUR-ACCOUNT/reading-log.git
cd .\reading-log
```

이제 현재 폴더에 `README.md`, `AGENTS.md`, `scripts`가 보여야 합니다. **이후 명령은 따로 안내하지 않는 한 이 저장소 루트에서 실행합니다.** macOS/Linux도 같은 저장소를 clone한 뒤 루트에서 진행하며, Python 실행 파일 이름이 `python3`이면 아래 명령의 `python`을 바꿉니다.

### 3. 웹 개발 환경 적용하기

```powershell
python scripts/setup.py --profile web
```

이 명령은 다음 작업을 순서대로 실행합니다. 의존성과 브라우저 다운로드, 문서 서버 조회에 인터넷 연결이 필요합니다.

1. 웹 개발용 스킬 10종과 MCP 3개 설정 적용
2. 잠금 파일에 맞춰 MCP 실행 도구 설치
3. 격리된 브라우저 검사에 사용할 Chromium 준비
4. 설정과 스킬 파일 검사
5. OpenAI Docs·Context7의 실제 문서 검색과 Playwright 브라우저 조작 확인

모두 성공하면 아래 문구가 나옵니다.

```text
web 환경 준비 완료. Codex에서 이 폴더를 신뢰하고 새 채팅을 시작하세요.
```

실패하면 마지막 오류를 해결한 뒤 같은 명령을 다시 실행합니다. 예를 들어 Windows의 Python 실행 문제라면 `py -3 scripts/setup.py --profile web`을 사용합니다. Linux에서 브라우저 시스템 라이브러리가 부족하면 안내에 따라 `node node_modules/playwright/cli.js install --with-deps chromium`으로 준비합니다. 연결 오류는 [MCP 문제 해결 안내](docs/mcp.md)를 확인하세요. 이 단계는 개발 환경 준비이며 웹앱은 다음 단계에서 만듭니다.

### 4. Codex에서 폴더 열기

Codex에서 방금 내려받은 **`reading-log` 루트 폴더**를 엽니다. 프로젝트 신뢰 요청이 나오면 저장소 설정을 확인한 뒤 허용하고 **새 채팅**을 시작합니다. 모델은 현재 계정에서 사용할 수 있는 모델을 선택합니다.

루트의 `AGENTS.md`는 작업 규칙, `.agents/skills`는 현재 프로필의 스킬, `.codex`는 도구와 에이전트 설정입니다. 필요한 스킬을 작업에 맞게 선택하도록 구성되어 있으므로 각각 따로 설치할 필요는 없습니다. GitHub·DB·배포 서비스의 인증은 복사되지 않으며, 필요한 서비스는 본인 계정으로 연결합니다.

루트의 `package.json`과 `package-lock.json`은 MCP 실행 환경용입니다. 아래 예시는 **앱을 `apps/web`에 만들도록** 요청해 기존 설정을 함께 유지합니다. `apps/web`은 이 예시의 권장 위치이며 아직 생성된 앱이 아닙니다. 폴더 생성과 앱 의존성 설치는 Codex가 진행합니다.

### 5. 첫 작업 지시 보내기

아래 내용을 그대로 **Codex 채팅에** 붙여넣습니다. 터미널에 실행하는 명령이 아닙니다. 기능·기술 스택·디자인을 바꾸려면 [첫 작업 지시 양식](templates/first-task.md)을 사용하세요.

```text
$task-delivery로 독서 기록 웹앱의 첫 버전을 만들어줘.

먼저 AGENTS.md와 docs/environments.md, docs/skill-routing.md를 읽고
현재 web 프로필의 스킬과 MCP를 사용할 수 있는지 확인해줘.
연결이 실패한 도구는 성공했다고 처리하지 말고 원인을 알려줘.

앱은 React + TypeScript + Vite로 apps/web에 만들어줘.
설치된 Node.js와 프레임워크 버전의 호환성을 먼저 확인하고,
루트의 MCP용 package.json과 package-lock.json, 설정은 보존해줘.

이번에 만들 기능:
- 책 제목, 저자, 읽는 상태, 메모를 입력해서 저장
- 저장한 책 목록 조회와 수정·삭제
- 제목·저자 검색과 읽는 상태 필터
- 브라우저 localStorage에 저장하고 새로고침해도 유지
- 한국어 화면과 모바일 대응

첫 버전은 이 브라우저에서 사용하는 개인용 앱으로 만들어줘.
로그인, 서버 DB, 기기 간 동기화는 이번 범위에서 제외해줘.

디자인은 docs/design-references.md를 참고해줘.
https://www.saasframe.io/ 와 https://mobbin.com/ 에서 접근 가능한
목록·필터·빈 상태 사례 2~3개를 확인하고 ui-ux-pro-max로 후보를 비교해줘.
로그인이나 결제가 필요한 사례는 공개 사례로 대체하고,
선택한 링크와 적용할 요소를 간단히 설명한 뒤 구현을 이어가줘.

구현에는 프로젝트의 Ponytail과 React 지침을 적용하고,
라이브러리 사용법은 설치 버전에 맞는 문서로 확인해줘.
독립적으로 나눌 수 있는 작업에만 보조 에이전트를 써줘.

.vibe/project.json을 이 앱의 목표와 완료 조건에 맞게 갱신하고,
실제 앱의 타입 검사·테스트·빌드 명령을 등록해줘.
앱 폴더를 실행 위치로 지정하고 기존 환경 검사도 필요한 범위에서 유지해줘.
GitHub Actions에서도 변경된 검사 명령을 실행할 수 있도록
Node 준비와 앱 의존성 설치 등 필요한 단계를 함께 맞춰줘.
앱의 dev 명령을 준비하고, 계속 켜 둘 개발 서버는 검사 목록과 별도로 실행해줘.

완료 전에 다음을 확인해줘.
- 책 등록 → 검색 → 수정 → 새로고침 → 삭제
- 빈 목록, 검색 결과 없음, 잘못된 입력, 저장 실패
- 모바일 화면에서 가로 넘침과 주요 버튼 사용
- 키보드로 입력·저장·대화상자 닫기(대화상자가 있다면)
- python scripts/vibe.py verify 실행
- Playwright로 실제 사용자 흐름 확인
- Ponytail Review로 변경 검토

README에 이 앱의 실행·검사 방법을 적어줘.
마지막에는 실행 방법과 실제 접속 주소, 확인한 항목, 남은 제한을 알려줘.
이번에는 로컬 구현과 검증까지 진행하고 GitHub push와 서비스 배포는 별도 요청할게.
```

`localStorage` 예제의 데이터는 해당 브라우저에만 저장됩니다. 다른 기기와 공유되지 않고, 브라우저 데이터를 지우면 사라질 수 있습니다. 여러 사람이 함께 사용하는 앱은 이후 서버 저장과 인증을 별도 작업으로 추가하세요.

### 6. 결과 확인하고 다음 작업 이어가기

Codex가 구현한 뒤 안내한 로컬 주소를 브라우저에서 엽니다. 개발 서버를 다시 켜려면 **위 작업에서 앱과 `dev` 명령이 만들어진 뒤**, 저장소 루트에서 실행합니다.

```powershell
npm.cmd --prefix apps/web run dev
```

터미널에 출력된 주소로 접속합니다. 서버를 켠 터미널은 유지하고 검사는 다른 터미널에서 실행합니다. 서버를 종료할 때는 해당 터미널에서 `Ctrl+C`를 누릅니다. 등록된 검사를 다시 실행하려면 저장소 루트에서 다음 명령을 사용합니다.

```powershell
python scripts/vibe.py verify
```

**처음 들어 있는 검사는 starter 자체를 검사합니다.** 첫 작업에서 `.vibe/project.json`에 실제 앱 검사 명령을 등록해야 앱도 검사됩니다. Playwright로 확인한 사용자 흐름과 아직 확인하지 못한 항목도 결과에서 확인하세요. 기존 GitHub Actions도 이 검사 목록을 실행하므로, 앱 검사를 추가할 때 **CI의 Node 준비·앱 의존성 설치 단계도 함께 맞춰야 합니다.** 위 첫 작업 지시에 이 내용이 포함되어 있습니다.

이후에는 “책 목록에 표지 이미지를 추가해줘”처럼 원하는 변경을 말하면 됩니다. 같은 프로젝트에서 매번 환경을 다시 설치할 필요는 없습니다. 새 컴퓨터에서 복원할 때는 `python scripts/setup.py`를 실행하면 현재 프로필을 유지합니다. 만든 앱의 의존성은 별도로 복원합니다. 이 예시처럼 npm 잠금 파일을 사용하는 앱이라면 Windows에서 `npm.cmd --prefix apps/web ci`, macOS/Linux에서 `npm --prefix apps/web ci`를 실행합니다.

## 내 프로젝트의 첫 작업 지시 작성하기

[첫 작업 지시 양식](templates/first-task.md)을 열고 프로젝트명·목적·사용자·핵심 기능·데이터 저장·디자인·완료 조건을 채운 뒤 Codex에 보냅니다. 잘 모르는 기술 선택은 “추천해줘”로 남겨도 됩니다. 원하는 결과와 이번에 하지 않을 범위를 적으면 첫 작업의 크기를 정하기 쉽습니다.

웹앱은 위 예시를 그대로 시작점으로 사용할 수 있습니다. 다른 목적은 [환경 사용 가이드](docs/environments.md)의 프로필을 먼저 적용하고, 양식의 앱 경로와 검증 항목을 해당 프로젝트에 맞게 바꿉니다.

## 목적별로 어떻게 쓰나요?

환경을 바꿀 때도 `python scripts/setup.py --profile api`처럼 프로필 이름만 바꿉니다. 자세한 순서와 목적별 요청 예시는 [환경 사용 가이드](docs/environments.md)에 있습니다. 레퍼런스는 복제할 완성품이 아니라 정보 배치·사용 흐름·컴포넌트 동작을 비교할 근거로 사용합니다.

구현은 Ponytail, 원인이 불명확한 실패는 디버깅 스킬, 검토는 Ponytail Review로 연결합니다. 화면·React·API·Postgres·Python 전문 지침은 해당 작업일 때 사용합니다. [목적별 스킬 사용 순서와 요청 예시](docs/skill-routing.md)

| 만들려는 것 | 환경 | 처음 볼 레퍼런스 | 진행 순서 |
| --- | --- | --- | --- |
| 랜딩 페이지·브랜드 사이트 | `web` | [Lapa Ninja](https://www.lapa.ninja/), [Landbook](https://land-book.com/), [Recent](https://recent.design/) | 사례 2~3개에서 레이아웃·타이포 선택 → 구현 → 모바일·CTA 흐름 확인 |
| SaaS·관리자·대시보드 | `web` | [Mobbin](https://mobbin.com/), [SaaSFrame](https://www.saasframe.io/), [shadcn/ui](https://ui.shadcn.com/) | 목록·검색·필터·빈 상태 비교 → 데이터 연결 → 실제 사용자 흐름 검사 |
| 백엔드·API | `api` | [OpenAPI](https://spec.openapis.org/oas/latest.html), [Swagger 예제](https://petstore.swagger.io/) | 입력·응답 계약 확인 → 구현 → 권한·실패·통합 테스트; 관리 화면이 필요하면 웹 레퍼런스도 사용 |
| 데이터 분석·시각화 | `data` | [Observable Plot](https://observablehq.com/plot/), [Vega-Lite 예제](https://vega.github.io/vega-lite/examples/) | 질문에 맞는 차트 선택 → 스키마·누락 확인 → 분석 → 지표·축·재현성 검증 |
| 업무·브라우저 자동화 | `automation` | [n8n 워크플로 사례](https://n8n.io/workflows/), [Mobbin](https://mobbin.com/) | 입력·분기·결과 흐름 조사 → dry-run → 재실행·실패 복구 확인 |
| 작은 수정·CLI·기존 코드 조사 | `minimal` | 해당 도구 공식 문서; UI 수정이면 [Radix Primitives](https://www.radix-ui.com/primitives) | 실패 재현 → 최소 수정 → 변경된 동작 확인 |

디자인 사이트별 특징, 공개 범위와 선택 기준은 [디자인 레퍼런스 가이드](docs/design-references.md)를 참고하세요. 유료·로그인 전용 화면의 접근 권한은 이 저장소에 포함되지 않습니다.

## 이미 들어 있는 구성

| 구성 | 실제 파일 | 하는 일 |
| --- | --- | --- |
| 작업 하네스 | [AGENTS.md](AGENTS.md), [.vibe/project.json](.vibe/project.json) | 요청 범위, 완료 조건, 검증 명령과 결과 기준 |
| Codex 설정 | [.codex/config.toml](.codex/config.toml) | 프로젝트 범위 권한, 필요 시 승인, MCP 연결 |
| 오케스트레이션 | [.codex/agents](.codex/agents), [운영 방식](docs/orchestration.md) | 주 에이전트 + 조사·검토·테스트 보조 최대 3개; 파일 담당 분리 |
| 활성 스킬 | [.agents/skills](.agents/skills) | 현재 web 프로필의 실제 발견 경로 |
| 전체 스킬 원본 | [skills](skills), [skills.lock.json](skills.lock.json) | 프로필별 설치 원본, 출처·고정 커밋·파일 해시 |
| MCP 설정 | [mcp](mcp), [연결 가이드](docs/mcp.md) | OpenAI·라이브러리 문서 검색, 격리된 브라우저 자동화, 선택적 GitHub 연결 |
| 검증과 CI | [scripts](scripts), [GitHub Actions](.github/workflows/validate.yml) | 파일 보존·환경 전환·오류 처리·스킬 무결성·실제 브라우저 검사 |

에이전트 역할은 작업 분담 지침입니다. 별도 OS 권한 격리를 만들지 않으며, 실제 권한은 부모 세션과 조직 정책을 따릅니다. 작은 작업은 주 에이전트가 직접 처리합니다.

## 어떤 스킬을 가져왔나요?

| 스킬 | 출처 | 쓰는 상황 | 포함 프로필 |
| --- | --- | --- | --- |
| `task-delivery` | 이 저장소에서 작성 · MIT | 요청을 완료 조건·구현·검증으로 연결 | 전체 |
| `parallel-work` | 이 저장소에서 작성 · MIT | 독립 작업 분담, 파일 충돌 방지, 결과 통합 | 전체 |
| `release-check` | 이 저장소에서 작성 · MIT | 게시 범위·검사·원격 결과 확인 | 전체 |
| `playwright` | [OpenAI 공식 스킬](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/playwright) · Apache-2.0 | 브라우저 조작·UI 확인의 작업 절차 | web, automation |
| `gh-fix-ci` | [OpenAI 공식 스킬](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/gh-fix-ci) · Apache-2.0 | 실패한 GitHub Actions 원인 조사·수정 | web, api |
| `gh-address-comments` | [OpenAI 공식 스킬](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/gh-address-comments) · Apache-2.0 | PR 리뷰 의견 확인·반영 | automation |
| `ponytail` | [DietrichGebert/Ponytail](https://github.com/DietrichGebert/ponytail) · MIT | 기존 코드·표준 기능을 활용한 구현 | 전체 |
| `ponytail-review` | [DietrichGebert/Ponytail](https://github.com/DietrichGebert/ponytail) · MIT | 정확성·보안·회귀·성능·불필요한 코드 검토 | 전체 |
| `debugging-and-error-recovery` | [Addy Osmani](https://github.com/addyosmani/agent-skills) · MIT | 재현·원인 조사·수정·회귀 확인 | 전체, 관련 오류에 사용 |
| `ui-ux-pro-max` | [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) · MIT | 로컬 검색으로 디자인 시스템·타이포·레이아웃 후보 선택 | web |
| `vercel-react-best-practices` | [Vercel](https://github.com/vercel-labs/agent-skills) · MIT 선언 보존 | React·Next.js 성능 지침 | web, React일 때 |
| `api-and-interface-design` | [Addy Osmani](https://github.com/addyosmani/agent-skills) · MIT | API 계약·멱등성·재시도·오류 설계 | api, automation |
| `supabase-postgres-best-practices` | [Supabase](https://github.com/supabase/agent-skills) · MIT | Postgres 인덱스·연결·권한·트랜잭션 | api, data, Postgres일 때 |
| `python-patterns` | [ECC](https://github.com/affaan-m/ECC) · MIT | Python 타입·예외·자원 관리·구조 | data, automation |

외부 스킬은 각각 **고정된 공개 커밋**에서 가져왔고 라이선스·출처·파일 해시를 기록했습니다. OpenAI 스킬의 고정 커밋은 `49f948faa9258a0c61caceaf225e179651397431`, Ponytail은 v5.3.3입니다. UI UX Pro Max의 Codex 경로 수정은 원본 해시와 수정 이유를 따로 남겼습니다. Vercel의 MIT 선언은 원본 README로 보존합니다. 전역 플러그인의 개인 설정·자동 hook을 복사하지 않았습니다. [출처·호환성 설명](docs/skills.md), [외부 라이선스](THIRD_PARTY_NOTICES.md)

Ponytail은 프로젝트의 `.agents/skills/ponytail`을 기준으로 사용합니다. 전역 Engineering Suite가 설치되어 있어도 그 플러그인을 수정하지 않습니다. 현재 요청과 한국어 설명을 우선하며, 스킬의 일률적인 승인·출력 규칙 때문에 이미 요청된 작업을 중단하지 않도록 조합했습니다.

원본 Playwright 스킬의 Bash CLI와 이 저장소의 Playwright MCP는 별개입니다. Windows에서는 구성된 MCP를 우선합니다. `gh-*`의 CLI 절차에는 GitHub CLI 설치·로그인이 필요하며, 연결된 GitHub 앱이 있으면 그 도구를 먼저 사용합니다. 이 저장소에 계정 인증 정보는 없습니다.

## MCP는 어디까지 준비되어 있나요?

- **OpenAI Docs:** 키 없이 사용하는 공식 검색 서버. web/api/data/automation에서 활성화합니다.
- **Context7:** 공개 라이브러리 문서를 검색합니다. web/api/data/automation에서 활성화하며 키 없이 실제 조회를 확인했습니다. 요청 한도나 인증 정책은 서비스에 따라 바뀔 수 있고, 설치 버전과 결과 출처를 함께 확인합니다.
- **Playwright:** `@playwright/mcp@0.0.85`와 의존성을 고정했습니다. web/automation에서 격리 Chromium을 실행합니다.
- **GitHub:** 현재 Codex에 연결한 GitHub 앱을 우선합니다. 별도 CLI용 원격 MCP 설정도 포함되어 있으며 읽기 전용입니다. 본인 토큰이 필요한 선택 연결이므로 기본으로 켜지 않습니다.

GitHub·배포 서비스·DB의 계정 권한은 fork로 전달되지 않습니다. 사용자의 현재 연결이나 본인 인증을 사용합니다. 추가 MCP는 작업에 필요한 것만 연결합니다. [설정·인증·문제 해결](docs/mcp.md)

## 검사·전환·기존 프로젝트에 적용

```bash
# 현재 환경의 실제 검사 실행
python scripts/vibe.py verify

# OpenAI Docs + Context7 실제 문서 검색 + 브라우저 조작 시험
node scripts/check_mcp.mjs

# 변경될 파일을 먼저 확인하고 프로필 전환
python scripts/vibe.py init --profile data --dry-run
python scripts/setup.py --profile data

# 기존 프로젝트에 적용하기: 기존 파일과 충돌하면 변경 전에 중단
python scripts/vibe.py init --profile api --target ../my-existing-project --dry-run
python scripts/vibe.py init --profile api --target ../my-existing-project
```

`init`은 파일을 적용하며 네트워크 설치는 하지 않습니다. `setup.py`는 이 starter 안에서 의존성 복원과 실제 연결 검증까지 실행합니다. 기존 프로젝트에 `--target`으로 적용할 때는 해당 프로젝트의 런타임과 검증 명령을 유지하고, 웹 프로필은 대상에서 Node·Chromium도 준비해야 합니다. 상세 내용은 [환경 사용 가이드](docs/environments.md)를 따릅니다.

`--update`는 관리 중인 파일이 이전 설치 해시와 같을 때만 바꿉니다. 직접 수정한 설정과 기존 `AGENTS.md`는 자동 덮어쓰기하지 않습니다. `.vibe/project.json`도 보존합니다. 검사 명령이 비어 있으면 `verify`는 실패합니다.

원본 스킬을 추가·수정하면 해당 프로필과 lock도 함께 갱신해야 합니다. 무결성 검사는 목록에 없는 스킬이나 바뀐 파일도 감지합니다. 이 검사는 저장소 내부 일관성을 확인하며 외부 작성자의 신원을 암호학적으로 인증하는 서명은 아닙니다.

## 검증 범위와 유지보수

설정은 **2026-11-15 / Codex CLI 0.169.0-alpha.11.1**에서 확인했습니다. 확인하지 않은 모델 ID는 고정하지 않았습니다. 새 버전에서 설정 형식이 바뀌면 공식 문서와 실제 설정 로딩 결과를 먼저 확인합니다.

CI는 Windows·macOS·Linux에서 Python 하네스 검사를 실행하고 Linux에서 실제 Chromium MCP 흐름을 실행합니다. 외부 Docs 서버 검사는 수동 온라인 검사에 포함해 네트워크 장애가 코드 회귀와 섞이지 않게 했습니다. [검증 기록](docs/verification.md)

설정과 스킬을 먼저 읽고 사용할 프로젝트를 신뢰하세요. 검사 명령은 실제 프로그램을 실행합니다. 비밀키·토큰·회사 원본·개인 데이터는 커밋하지 않습니다. 자체 파일은 [MIT](LICENSE), 가져온 스킬은 각 원본 라이선스를 따릅니다.
