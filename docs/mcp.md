# MCP 연결과 실제 사용

MCP는 외부 도구를 호출하는 연결이다. 스킬은 그 도구를 언제 어떻게 사용할지 알려 주는 작업 절차다. 연결이 등록되어 있다는 사실과 로그인·실행이 성공했다는 사실을 구분한다.

## 제공하는 연결

| ID | 용도 | 인증·런타임 | 기본 선택 |
| --- | --- | --- | --- |
| `openai-docs` | OpenAI API·Codex 공식 문서 검색 | 인증 없음, HTTPS 접근 | web/api/data/automation |
| `playwright` | 웹 화면 조작·스크린샷·브라우저 검증 | Node.js, 잠금 파일의 npm 패키지, Chromium | web/automation |
| `github` | 저장소·이슈·PR·Actions 조회 | `GITHUB_PERSONAL_ACCESS_TOKEN` | 직접 추가 |

OpenAI Docs는 문서만 제공하며 API 호출을 대행하지 않는다. [공식 Docs MCP 안내](https://developers.openai.com/learn/docs-mcp)

Playwright는 `@playwright/mcp` **0.0.85**를 지정한다. 저장소에서는 잠금 파일로 복원한 패키지를 사용하고, 기존 프로젝트에 설정만 설치한 경우 `npx`가 같은 버전을 캐시에 받는다. 처음에는 다운로드를 위한 네트워크 접근이 필요할 수 있다. Chromium은 화면 없이 별도 세션에서 실행하며 개인 브라우저의 로그인 쿠키를 자동으로 가져오지 않는다. [공식 릴리스](https://github.com/microsoft/playwright-mcp/releases/tag/v0.0.85), [실행 옵션](https://github.com/microsoft/playwright-mcp)

## 새 컴퓨터에서 준비

Python 3.11 이상과 Node.js 22 이상을 준비한다. 저장소를 가져온 후 패키지를 잠금 파일대로 복원한다.

```bash
npm ci
node node_modules/playwright/cli.js install chromium
python scripts/vibe.py doctor
codex mcp list
```

Linux에서 브라우저 운영체제 의존성이 없다는 오류가 나면 Playwright가 안내하는 설치 항목을 확인한다. 필요한 시스템 설치는 해당 컴퓨터의 관리 권한으로 진행한다.

Codex에서 프로젝트를 신뢰하고 새 세션을 연다. `/mcp`에서 연결을 확인한 뒤 아래처럼 실제 호출을 시켜 본다.

```text
OpenAI Docs로 Codex 프로젝트 설정 문서를 찾아 공식 링크를 알려줘.
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
| GitHub 401/403 | 프로세스 환경 변수 전달, 토큰 만료, 대상 저장소·조직 허용 범위 확인 |
| 목록에 연결이 안 보임 | 프로젝트 신뢰, 새 세션, `.codex/config.toml` 경로 확인 |
| 회사망에서 연결 실패 | 서버 도메인에 대한 조직 네트워크 정책 확인 |

STDIO·HTTP 설정과 환경 변수 인증 형식은 [Codex 공식 MCP 문서](https://learn.chatgpt.com/docs/extend/mcp)를 기준으로 작성했다. 확인 날짜는 **2026-11-15**다. 서버 업데이트는 릴리스 검토 → 버전·잠금 파일 수정 → 실제 연결 시험 순서로 진행한다.
