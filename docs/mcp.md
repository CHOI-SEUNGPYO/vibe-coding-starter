# MCP 연결과 실제 사용

MCP는 외부 도구를 호출하는 연결이다. 스킬은 그 도구를 언제 어떻게 사용할지 알려 주는 작업 절차다. 연결이 등록되어 있다는 사실과 로그인·실행이 성공했다는 사실을 구분한다.

## 제공하는 연결

| ID | 용도 | 인증·런타임 | 기본 선택 |
| --- | --- | --- | --- |
| `openai-docs` | OpenAI API·Codex 공식 문서 검색 | 인증 없음, HTTPS 접근 | web/api/data/automation |
| `context7` | 라이브러리·프레임워크 문서와 사용 예제 검색 | 공개 HTTPS 서버, 이 설정에는 키 없음 | web/api/data/automation |
| `playwright` | 웹 화면 조작·스크린샷·브라우저 검증 | Node.js, 잠금 파일의 npm 패키지, Chromium | web/automation |
| `github` | 저장소·이슈·PR·Actions 조회 | `GITHUB_PERSONAL_ACCESS_TOKEN` | 직접 추가 |

OpenAI Docs는 문서만 제공하며 API 호출을 대행하지 않는다. [공식 Docs MCP 안내](https://developers.openai.com/learn/docs-mcp)

Context7은 OpenAI 이외의 라이브러리를 조사할 때 쓴다. 먼저 `resolve-library-id`로 프로젝트에 맞는 라이브러리를 고른 다음 `query-docs`로 질문한다. 반환한 원문 링크와 프로젝트에 설치된 버전을 함께 확인한다. 라이브러리에 따라 버전별 인덱스가 없거나 최신 변경이 아직 반영되지 않을 수 있으므로, 결과를 정확한 설치 버전의 보증으로 보지 않는다. OpenAI 설정은 OpenAI Docs를 우선하고, Context7에 없는 내용은 해당 라이브러리의 공식 문서에서 확인한다. [Context7 공식 저장소](https://github.com/upstash/context7)

이 프리셋은 `https://mcp.context7.com/mcp`에 키 없이 연결한다. 공식 안내는 더 높은 사용 한도를 위한 API 키를 권장한다. 공개 연결의 무제한 사용이나 가용성을 보장하지 않으며, 인증 정책·사용 한도는 서비스 측에서 바뀔 수 있다. 401·403·429 또는 통신 오류가 나면 연결 검사는 실패한다. 공식 문서로 필요한 작업을 이어 가되 MCP 검증이 성공했다고 보고하지 않는다. 키가 필요해진 경우에도 저장소에 넣지 말고, 계정 설정은 별도로 진행한다. [인증·연결 안내](https://github.com/upstash/context7#installation)

문서 서버에는 공개 라이브러리 이름·버전과 필요한 API 질문을 전달한다. 토큰, 개인 정보, 회사 코드 전체를 검색어로 보내지 않는다. 파일 읽기·검색·Git 작업은 기존 로컬 도구를 사용하므로 같은 기능의 MCP를 추가할 필요가 없다.

Playwright는 `@playwright/mcp` **0.0.85**를 지정한다. 저장소에서는 잠금 파일로 복원한 패키지를 사용하고, 기존 프로젝트에 설정만 설치한 경우 `npx`가 같은 버전을 캐시에 받는다. 처음에는 다운로드를 위한 네트워크 접근이 필요할 수 있다. Chromium은 화면 없이 별도 세션에서 실행하며 개인 브라우저의 로그인 쿠키를 자동으로 가져오지 않는다. [공식 릴리스](https://github.com/microsoft/playwright-mcp/releases/tag/v0.0.85), [실행 옵션](https://github.com/microsoft/playwright-mcp)

## 새 컴퓨터에서 준비

Python 3.11 이상과 Node.js 22 이상을 준비한 뒤 저장소 루트에서 실행한다. `minimal`은 Node.js나 MCP 연결이 필요 없다.

```bash
python scripts/setup.py
```

현재 프로필을 복원하며, 설치 기록이 없으면 `web`을 선택한다. 해당 프로필의 기본 MCP와 기존에 추가한 연결을 설치하고, Playwright가 포함되면 잠금 파일의 패키지와 Chromium을 준비한다. 환경을 바꾸려면 `python scripts/setup.py --profile api`처럼 지정한다. 명시적으로 프로필을 바꾸면 새 프로필의 기본 연결을 적용한다. 기존 관리 파일을 직접 수정했다면 덮어쓰지 않고 중단한다.

`setup.py`는 프로필 기본 구성을 복원하는 명령이다. 앞서 `--no-mcp`로 기본 연결을 제외했더라도 다시 복원한다. 연결을 직접 골라 관리하려면 `scripts/vibe.py init`과 아래 개별 검사 명령을 쓴다. 선택한 GitHub 연결은 보존할 수 있지만 이 명령에서 계정 인증을 검사하지 않는다.

등록 상태와 서버 동작을 따로 확인할 수도 있다.

```bash
python scripts/vibe.py doctor
codex mcp list
node scripts/check_mcp.mjs docs
node scripts/check_mcp.mjs context7
node scripts/check_mcp.mjs browser
```

`docs`는 OpenAI Docs 검색만, `context7`은 공개 FastAPI 라이브러리 검색과 공식 출처가 있는 예제 조회까지, `browser`는 로컬 시험 페이지의 Chromium 접속과 버튼 클릭을 확인한다. `all`은 세 검사를 모두 실행한다. `setup.py`는 선택된 서버만 각각 검사하며 첫 실패에서 멈춘다. 이 검사는 제품 자체의 기능 검증을 대신하지 않는다.

Linux에서 브라우저 운영체제 의존성이 없다는 오류가 나면 Playwright가 안내하는 설치 항목을 확인한다. 필요한 시스템 설치는 해당 컴퓨터의 관리 권한으로 진행한다.

Codex에서 프로젝트를 신뢰하고 새 세션을 연다. `/mcp`에서 연결을 확인한 뒤 아래처럼 실제 호출을 시켜 본다.

```text
OpenAI Docs로 Codex 프로젝트 설정 문서를 찾아 공식 링크를 알려줘.
프로젝트에 설치된 FastAPI 버전을 먼저 확인하고 Context7으로 관련 문서를 찾아줘.
Pydantic 요청 본문 선언 예제와 원문 링크를 알려줘. 인덱스에 버전이 없으면 구분해 줘.
Playwright로 로컬 개발 서버의 첫 화면을 열고 제목과 콘솔 오류를 확인해줘.
```

`codex mcp list`는 등록 확인이다. 인증 성공이나 브라우저 실행 성공까지 증명하지 않는다. 제품의 로컬 주소를 열어 실제 동작을 확인해야 한다.

## GitHub는 연결된 앱부터

Codex에 GitHub 앱이 이미 연결되어 있으면 그것을 사용한다. 같은 계정의 MCP를 중복 등록할 필요는 없다. 독립 CLI에서 GitHub 연결이 필요할 때만 다음 설정을 추가한다.

```bash
python scripts/vibe.py init --profile web --mcp github --update
```

GitHub의 토큰 관리 화면에서 대상 저장소와 필요한 읽기 권한만 고른다. 토큰은 운영체제의 비밀 저장소 또는 Codex를 시작하는 프로세스 환경의 `GITHUB_PERSONAL_ACCESS_TOKEN`으로 전달한다. `.env` 파일을 만들어도 Codex가 이 변수를 자동으로 읽는다고 가정하지 않는다. 토큰 값을 채팅이나 저장소 파일에 붙여 넣지 않는다.

제공한 GitHub 연결은 `X-MCP-Readonly: true`로 쓰기 도구를 제외한다. PR 작성·댓글·병합이 필요한 경우에는 이미 승인된 GitHub 앱이나 별도 권한이 있는 도구를 사용한다. 이 설정을 바꾸는 일과 실제 쓰기 작업의 사용자 승인은 별개다. [GitHub 공식 서버 설정](https://github.com/github/github-mcp-server/blob/main/docs/server-configuration.md)

## 문제가 있을 때

| 증상 | 확인할 내용 |
| --- | --- |
| `npx`를 찾지 못함 | Node 설치 후 Codex를 다시 실행하고 PATH 확인 |
| Playwright 패키지가 없음 | 저장소 루트에서 `npm ci` 실행 |
| 브라우저 실행 파일이 없음 | 동일 저장소에서 `node node_modules/playwright/cli.js install chromium` 실행 |
| Context7 401/403 | 서비스의 현재 인증 정책 확인. 키를 커밋하지 않고 공식 문서로 계속 조사 |
| Context7 429 | 사용 한도 확인 후 나중에 재시도. 필요하면 계정의 공식 키 설정 안내 확인 |
| Context7에 버전·라이브러리가 없음 | 실제 설치 버전을 확인하고 해당 버전의 공식 문서 사용 |
| GitHub 401/403 | 프로세스 환경 변수 전달, 토큰 만료, 대상 저장소·조직 허용 범위 확인 |
| 목록에 연결이 안 보임 | 프로젝트 신뢰, 새 세션, `.codex/config.toml` 경로 확인 |
| 회사망에서 연결 실패 | 서버 도메인에 대한 조직 네트워크 정책 확인 |

STDIO·HTTP 설정과 환경 변수 인증 형식은 [Codex 공식 MCP 문서](https://learn.chatgpt.com/docs/extend/mcp)를 기준으로 작성했다. 확인 날짜는 **2026-11-15**다. 서버 업데이트는 릴리스 검토 → 버전·잠금 파일 수정 → 실제 연결 시험 순서로 진행한다.
