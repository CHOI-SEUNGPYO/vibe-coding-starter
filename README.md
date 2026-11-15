# Vibe Coding Starter

[![Validate starter](https://github.com/CHOI-SEUNGPYO/vibe-coding-starter/actions/workflows/validate.yml/badge.svg)](https://github.com/CHOI-SEUNGPYO/vibe-coding-starter/actions/workflows/validate.yml)

**공식 도구와 커뮤니티 전문 스킬을 조합한 Codex 개발 환경.** 작업 규칙, 역할별 에이전트, 스킬 14종, MCP 연결과 검증 도구가 들어 있습니다. 기본 `web` 환경에는 스킬 10종과 MCP 3개가 이미 적용되어 있습니다.

프레임워크나 모델 이름을 강제하지 않습니다. 현재 계정의 모델과 프로젝트의 기술 스택을 유지하고, 해야 할 일에 맞춰 환경을 고릅니다. 새 컴퓨터에서 필요한 작업은 의존성 복원과 본인 계정 인증입니다.

## 바로 시작하기

아래는 **Windows에서 독서 기록 웹앱을 처음 만드는 순서**입니다. 서버만 만들려면 [API 개발로 시작하기](#api-개발로-시작하기)로 이동하세요. 원하는 앱으로 시작하려면 [웹앱 첫 작업 양식](templates/first-task.md) 또는 [API 첫 작업 양식](templates/first-api-task.md)의 빈칸을 채우세요.

### 1. 필요한 프로그램 준비하기

[Git](https://git-scm.com/downloads), [Python **3.11 이상**](https://www.python.org/downloads/), [Node.js **24.x(24.15 이상)**](https://nodejs.org/en/download), Codex와 GitHub 계정이 필요합니다. 설치 후 PowerShell을 새로 열고 확인합니다.

```powershell
git --version
python --version
node --version
npm.cmd --version
```

명령을 찾지 못하면 해당 프로그램 설치와 PATH 설정을 확인하세요. `python`이 Microsoft Store를 열거나 동작하지 않으면 `python3 --version`, `py -3 --version` 순서로 확인합니다. **실제로 3.11 이상 버전을 출력하는 명령 하나를 골라 이후에도 같은 명령을 사용하세요.** 예를 들어 `python3`가 동작하면 아래 `python`을 모두 `python3`로 바꿉니다. Python이 설치되어 있어도 `py -3`가 `No installed Python found!`라고 나올 수 있으며, 다른 명령이 정상 동작하면 다시 설치할 필요는 없습니다.

Windows 예시는 PowerShell의 스크립트 실행 정책에 막히지 않도록 `npm.cmd`를 사용합니다. 실행 정책을 변경할 필요는 없습니다. macOS/Linux에서는 `npm`을 사용하세요. **아래 독서 기록 앱 실습은 Node.js 24.22.1에서 확인했으며 24.x 중 24.15 이상을 권장합니다.** starter 자체는 22부터 실행되지만, 앱은 프레임워크와 테스트 도구의 조건을 모두 충족해야 합니다. 예를 들어 [Vite](https://vite.dev/guide/)의 22.12 조건만 보면 이번 앱의 jsdom 테스트 의존성 조건을 놓치게 됩니다. 에이전트가 선택한 실제 의존성의 요구 버전을 함께 확인하도록 요청하세요.

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

실패하면 마지막 오류를 해결한 뒤 같은 명령을 다시 실행합니다. Python 실행 문제라면 1단계에서 확인한 명령을 사용합니다. 예를 들어 `python3 scripts/setup.py --profile web`입니다. Linux에서 브라우저 시스템 라이브러리가 부족하면 안내에 따라 `node node_modules/playwright/cli.js install --with-deps chromium`으로 준비합니다. 연결 오류는 [MCP 문제 해결 안내](docs/mcp.md)를 확인하세요. 이 단계는 개발 환경 준비이며 웹앱은 다음 단계에서 만듭니다.

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
설치된 Node.js가 프레임워크와 테스트 도구의 요구 버전을 모두 충족하는지 확인하고,
루트의 MCP용 package.json과 package-lock.json, 설정은 보존해줘.
명령은 이 컴퓨터에서 실제 동작하는 Python과 패키지 관리자 실행 파일을 써줘.
앱 의존성의 잠금 파일을 만들고 빌드 산출물과 로컬 시험 자료는 Git에서 제외해줘.
package.json의 engines와 README의 실행 조건도 실제 의존성 요구 범위에 맞춰줘.

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
서버의 시작 메시지만 보지 말고 실제 주소의 응답과 Playwright 접속을 확인해줘.
접속이 실패하면 서버 종료·주소·포트·실행 환경의 접근 제한을 구분해 해결하고,
브라우저 확인을 못 한 상태를 검증 완료로 보고하지 마.

완료 전에 다음을 확인해줘.
- 책 등록 → 검색 → 수정 → 새로고침 → 삭제
- 빈 목록, 검색 결과 없음, 잘못된 입력, 저장 실패 시 기존 기록·입력 보존
- 모바일 화면에서 가로 넘침과 주요 버튼 사용
- 키보드로 입력·저장하고, 대화상자를 Escape·취소·닫기·저장으로 닫은 뒤
  원래 버튼으로 포커스가 돌아오는지 확인(대화상자가 있다면)
- 삭제 확인을 취소한 뒤 해당 삭제 버튼으로 포커스 복귀
- python scripts/vibe.py verify 실행
- Playwright로 실제 사용자 흐름 확인
- Ponytail Review로 변경 검토

README에 이 앱의 실행·검사 방법을 적어줘.
마지막에는 실행 방법과 실제 접속 주소, 확인한 항목, 남은 제한을 알려줘.
이번에는 로컬 구현과 검증까지 진행하고 GitHub push와 서비스 배포는 별도 요청할게.
```

`localStorage` 예제의 데이터는 해당 브라우저 프로필과 접속 주소에 저장됩니다. 다른 기기와 공유되지 않고, 브라우저 데이터를 지우면 사라질 수 있습니다. **`localhost`와 `127.0.0.1`, 또는 서로 다른 포트는 저장 공간도 다릅니다.** 기록할 때 사용한 주소를 북마크하고 같은 주소로 다시 접속하세요. [저장 범위 설명](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)

Playwright 검사는 격리된 시험 브라우저에서 실행합니다. 시험 중 넣은 책이 본인의 일반 브라우저에 나타나지 않는 것은 정상입니다. 여러 사람이 함께 사용하는 앱은 이후 서버 저장과 인증을 별도 작업으로 추가하세요.

### 6. 결과 확인하고 다음 작업 이어가기

Codex가 구현한 뒤 안내한 로컬 주소를 브라우저에서 엽니다. 개발 서버를 다시 켜려면 **위 작업에서 앱과 `dev` 명령이 만들어진 뒤**, 저장소 루트에서 실행합니다.

```powershell
npm.cmd --prefix apps/web run dev
```

터미널에 출력된 주소로 접속합니다. 서버를 켠 터미널은 유지하고 검사는 다른 터미널에서 실행합니다. 서버를 종료할 때는 해당 터미널에서 `Ctrl+C`를 누릅니다. 등록된 검사를 다시 실행하려면 저장소 루트에서 다음 명령을 사용합니다.

```powershell
python scripts/vibe.py verify
```

화면이 열리지 않으면 서버 터미널이 여전히 실행 중인지, 접속 주소와 포트가 출력과 같은지 먼저 확인하세요. Codex가 서버를 실행했다면 “서버가 계속 켜져 있고 이 주소에서 실제 페이지가 응답하는지 확인해줘”라고 요청하면 됩니다. 앱은 켜져 있는데 도구만 접속하지 못하는 경우에는 실행 환경의 로컬 접속 권한을 구분해 확인해야 합니다. 전체 방화벽이나 PowerShell 실행 정책을 끄는 방식으로 해결하지 않습니다.

**처음 들어 있는 검사는 starter 자체를 검사합니다.** 첫 작업에서 `.vibe/project.json`에 실제 앱 검사 명령을 등록해야 앱도 검사됩니다. Playwright로 확인한 사용자 흐름과 아직 확인하지 못한 항목도 결과에서 확인하세요. 기존 GitHub Actions도 이 검사 목록을 실행하므로, 앱 검사를 추가할 때 **CI의 Node 준비·앱 의존성 설치 단계도 함께 맞춰야 합니다.** 위 첫 작업 지시에 이 내용이 포함되어 있습니다.

이후에는 “책 목록에 표지 이미지를 추가해줘”처럼 원하는 변경을 말하면 됩니다. 같은 프로젝트에서 매번 환경을 다시 설치할 필요는 없습니다. 새 컴퓨터에서 복원할 때는 `python scripts/setup.py`를 실행하면 현재 프로필을 유지합니다. 만든 앱의 의존성은 별도로 복원합니다. 이 예시처럼 npm 잠금 파일을 사용하는 앱이라면 Windows에서 `npm.cmd --prefix apps/web ci`, macOS/Linux에서 `npm --prefix apps/web ci`를 실행합니다.

## API 개발로 시작하기

웹 화면 없이 **독서 기록을 저장하고 조회하는 API**를 만드는 순서입니다. 아래 단계는 별도 복제본에 `api` 프로필을 적용해 FastAPI + SQLite로 실제 구현·검증했습니다. 예제 앱은 starter에 들어 있지 않으며, 3단계의 지시로 새로 만듭니다.

### 1. 프로그램 준비와 프로젝트 복제

[Git](https://git-scm.com/downloads), [Python 3.11 이상](https://www.python.org/downloads/), [Node.js 22 이상](https://nodejs.org/en/download), Codex와 GitHub 계정을 준비합니다. **여기서 Node는 문서 MCP 연결 검사에 사용합니다.** Python API를 실행하는 런타임과는 별개이며, 웹 실습의 Vite·jsdom 버전 조건은 적용하지 않습니다. PowerShell에서 `git --version`, `python --version`, `node --version`으로 확인하세요. Python 명령이 안 되면 [웹 안내의 1단계](#1-필요한-프로그램-준비하기)처럼 실제 동작하는 실행 파일을 고릅니다.

이 저장소를 **Use this template** 또는 **Fork**로 본인 계정에 가져옵니다. 여러 프로젝트를 따로 만들 때는 Template을 권장합니다. 이름을 `reading-api`로 정했다면, `YOUR-ACCOUNT`를 본인 계정으로 바꾸고 실행합니다.

```powershell
cd "$env:USERPROFILE\Documents"
git clone https://github.com/YOUR-ACCOUNT/reading-api.git
cd .\reading-api
python scripts/setup.py --profile api
```

이후 명령은 저장소 루트에서 실행합니다. 준비가 끝나면 `api 환경 준비 완료`가 표시됩니다. API 설계·Ponytail·리뷰 등을 포함한 **스킬 9종**, **OpenAI Docs와 Context7**이 적용됩니다. API 프로필은 Playwright·Chromium을 설치하지 않습니다. Python 프레임워크·DB·가상환경은 다음 작업에서 만듭니다. MCP 조회 실패는 [문제 해결 안내](docs/mcp.md)를 확인한 뒤 같은 명령으로 다시 검사하세요.

### 2. Codex에서 프로젝트 열기

`reading-api` **루트 폴더**를 열고 프로젝트 설정을 확인한 뒤 신뢰하고 새 채팅을 시작합니다. 기존 웹 작업의 채팅을 계속 쓰는 대신 새 프로필을 읽게 합니다. `.agents/skills`와 `.codex`는 이미 준비되어 있습니다. SQLite 예제에는 Postgres 연결이나 별도 클라우드 계정이 필요하지 않습니다.

### 3. 첫 작업 지시 보내기

아래를 **Codex 채팅**에 붙여 넣습니다. 다른 API는 [API 전용 첫 작업 양식](templates/first-api-task.md)을 사용하세요. 레퍼런스는 [OpenAPI](https://spec.openapis.org/)의 계약 구조, [Swagger Petstore](https://petstore.swagger.io/)의 요청·응답 표현, [FastAPI 문서](https://fastapi.tiangolo.com/tutorial/first-steps/)의 실제 실행 방식을 비교하는 데 씁니다.

```text
$task-delivery로 개인용 독서 기록 API를 구현하고 검증해줘.

AGENTS.md, docs/environments.md, docs/skill-routing.md를 읽고
api 프로필과 OpenAI Docs·Context7 연결을 확인해줘.
API 설계와 Ponytail을 적용하고 마지막에는 Ponytail Review로 검토해줘.

Python + FastAPI + SQLite로 apps/api에 만들어줘.
제목·저자·상태(want/reading/done)·메모를 저장하고,
POST /api/books, GET 목록·상세, PATCH 부분 수정, DELETE를 제공해줘.
제목·저자 검색, 상태 필터, page와 pageSize 페이지 조회도 포함해줘.
입력 조건, 상태코드, 공통 오류 본문, 인증을 OpenAPI와 README에 명시해줘.
https://spec.openapis.org/ 와 https://petstore.swagger.io/ 를 참고하되
설치한 FastAPI가 지원하는 명세 버전을 사용해줘.

책 API는 개인용 Bearer 토큰으로 보호해줘. 사용자 역할 구분은 없어.
BOOKS_API_TOKEN은 무작위로 만들어 Git에서 제외한 apps/api/.env에 저장하고,
기존 파일을 덮어쓰거나 토큰을 답변·로그에 출력하지 마.
서버 토큰 미설정은503, 요청 토큰 누락·오류는401로 거절해줘.
DB는 apps/api/data/books.sqlite3에 저장하고 실행 위치·재시작과 무관하게 유지해줘.
PATCH는 생략 필드를 유지하고 null은 거절해줘. 반복 삭제는204로 해줘.
POST는 비멱등으로 명시하고 자동 재시도하지 않도록 안내해줘.
회원가입, 웹 화면, 외부 도서 검색, 외부 공개와 운영 배포는 제외해줘.

앱 전용 apps/api/.venv와 requirements.lock을 만들고 실제 의존성을 설치해줘.
전역 패키지·실행 정책을 바꾸지 말고 가상환경 Python을 직접 사용해줘.
루트 MCP용 package.json·잠금 파일·설정은 보존하고 .env·DB·.venv는 Git에서 제외해줘.
설치한 라이브러리와 테스트 도구의 런타임 조건을 공식 문서로 확인해줘.

.vibe/project.json을 이 앱의 목표와 완료 조건으로 갱신해줘.
실제 앱 검사는 cwd:"apps/api", venv:".venv", command:["{python}", ...]로 등록해줘.
CI도 현재 프로필 check → 가상환경 생성 → 잠금 의존성 설치 → verify로 맞춰줘.
CI에서 web 프로필을 다시 적용하지 마. 앱 검사는 임시 DB와 시험용 토큰을 사용해줘.

인증 후 등록 → 검색 → 부분 수정 → 서버 종료·재시작 → 다시 조회 → 삭제를 확인해줘.
한글·이모지, 잘못된 타입·길이·공백·NUL·null, 알 수 없는 필드, 없는 ID,
인증 누락·오류·설정 누락, 페이지 경계, 중복 요청 정책도 검사해줘.
실제 DB 쓰기 실패를 재현하고 기존 데이터가 보존되는지 확인해줘.
python scripts/vibe.py verify와 별도 실제 HTTP 검사를 모두 실행해줘.
검사가 멈추면 코드 오류와 DNS·로컬 소켓·포트 제한을 구분하고 실패를 숨기지 마.

서버는 검사 목록과 별도로 127.0.0.1:8001에서 실행해줘.
/health, /docs, /openapi.json과 실제 인증·CRUD 요청이 응답하는지 확인해줘.
화면이 없는 API에는 브라우저 검사를 필수로 추가하지 마.
README에 OS별 실행·검사·인증 명령과 HTTP 예시, DB 위치를 적어줘.
마지막에 실제 접속 주소·통과한 검사·남은 제한을 알려줘.
이번에는 로컬 구현·검증까지 진행하고 GitHub push와 배포는 별도 요청할게.
```

### 4. 서버 실행과 첫 요청

**3단계에서 코드·의존성·`.env`를 만든 뒤** 사용할 명령입니다. Codex가 서버를 켜 두었다면 같은 포트로 또 실행하지 말고 아래 주소부터 확인하세요. 다시 켤 때는 루트에서 실행하고 터미널을 유지합니다.

```powershell
apps/api/.venv/Scripts/python.exe -m uvicorn main:app --app-dir apps/api --env-file apps/api/.env --host 127.0.0.1 --port 8001
```

macOS/Linux는 실행 파일을 `apps/api/.venv/bin/python`으로 바꿉니다. [API 문서](http://127.0.0.1:8001/docs)에서 **Authorize**에 `.env`의 로컬 토큰 값을 넣으면 책 API를 호출할 수 있습니다. `BOOKS_API_TOKEN=`이나 `Bearer ` 접두사는 입력하지 않습니다. `.env`는 본인 컴퓨터의 편집기에서만 확인하고 채팅·GitHub에 복사하지 않습니다.

PowerShell에서 직접 호출하려면 **다른 터미널을 열어 같은 저장소 루트로 이동**한 뒤 아래를 실행합니다. 토큰은 파일에서 읽어 헤더에 넣고 출력하지 않습니다. 한국어 본문은 UTF-8 바이트로 보냅니다.

```powershell
Invoke-RestMethod http://127.0.0.1:8001/health
$apiToken = ((Get-Content apps/api/.env | Select-String '^BOOKS_API_TOKEN=').Line -replace '^BOOKS_API_TOKEN=', '').Trim()
$apiHeaders = @{ Authorization = "Bearer $apiToken" }
$apiBody = @{ title = '어린 왕자'; author = '생텍쥐페리'; status = 'reading'; note = '첫 기록' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8001/api/books -Headers $apiHeaders -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($apiBody))
Invoke-RestMethod -Uri http://127.0.0.1:8001/api/books -Headers $apiHeaders
```

인증 없이 책 주소를 열면 **401**이 정상입니다. **503**이면 서버 토큰이 설정됐는지와 `--env-file` 경로를 확인합니다. `/health`의 성공은 DB 연결 확인이며 토큰 설정과 쓰기 성공까지 보장하지 않습니다. POST를 반복하면 책이 중복 등록되므로 응답을 못 받은 경우 먼저 목록을 확인하세요.

### 5. 검증과 다음 실행

```powershell
python scripts/vibe.py verify
```

`.vibe/project.json`에 등록한 앱 검사는 `venv` 설정 덕분에 앱의 Python으로 실행됩니다. 가상환경을 활성화할 필요가 없습니다. 기본 Python의 `ModuleNotFoundError`를 해결하려고 전역에 패키지를 설치하지 말고 [가상환경 검사 설정](docs/environments.md#python-앱의-가상환경-연결)을 확인하세요.

서버 터미널에서 `Ctrl+C`로 종료하고 4단계 명령으로 다시 켠 뒤 목록을 조회하면 같은 DB의 기록이 남아 있어야 합니다. 가상환경과 DB는 별개입니다. **새 컴퓨터에 clone하면 Git에서 제외한 DB와 토큰은 따라오지 않습니다.** 서버 재시작 보존과 다른 컴퓨터로의 데이터 이전을 구분하세요.

새 컴퓨터에서는 `python scripts/setup.py`로 현재 프로필을 복원한 뒤, 앱 의존성을 별도로 준비합니다. 다음은 위 예시가 만들어진 프로젝트의 Windows 명령입니다.

```powershell
python -m venv apps/api/.venv
apps/api/.venv/Scripts/python.exe -m pip install -r apps/api/requirements.lock
```

macOS/Linux는 `python3 -m venv apps/api/.venv`, `apps/api/.venv/bin/python -m pip install -r apps/api/requirements.lock`을 사용합니다. 위 예시의 새 로컬 토큰 파일은 다음처럼 만듭니다. 토큰은 출력하지 않으며 기존 `.env`가 있으면 덮어쓰지 않고 실패합니다. 처음 구현하면서 이미 만들었다면 다시 실행하지 않습니다.

```powershell
python -c "from pathlib import Path; import secrets; Path('apps/api/.env').open('x', encoding='utf-8').write('BOOKS_API_TOKEN=' + secrets.token_urlsafe(32) + '\nBOOKS_DB_PATH=data/books.sqlite3\n')"
```

macOS/Linux는 `python`을 `python3`로 바꿉니다. 설정 이름을 변경한 앱은 그 앱의 README와 `.env.example`을 따르세요. DB를 옮길 경우 별도 백업·복원 절차를 따릅니다. 기존 DB나 `.env`를 초기화하지 마세요.

이 검증 예제는 한 사람의 로컬 API입니다. 다중 사용자 권한·외부 공개·TLS·운영 백업은 이후 별도 요구사항으로 추가합니다. 실제로 실행한 검사와 제한은 [검증 기록](docs/verification.md#api-프로필-실제-앱-검증-2026-11-16)에 있습니다.

## 내 프로젝트의 첫 작업 지시 작성하기

[웹앱 양식](templates/first-task.md) 또는 [API 양식](templates/first-api-task.md)을 열고 목적·사용자·기능·데이터·완료 조건을 채운 뒤 Codex에 보냅니다. 웹은 화면·사용 흐름, API는 인증·입출력·오류·재시도 계약을 적습니다. 잘 모르는 기술 선택은 “추천해줘”로 남겨도 됩니다.

웹앱과 API는 위의 완성된 첫 지시를 시작점으로 사용할 수 있습니다. 다른 목적은 [환경 사용 가이드](docs/environments.md)의 프로필을 먼저 적용하고, 양식의 앱 경로와 검증 항목을 해당 프로젝트에 맞게 바꿉니다.

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
