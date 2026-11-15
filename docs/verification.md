# 실제 검증 기록

최초 확인: **2026-11-15**, API 실습 추가: **2026-11-16**. 이 문서는 설정과 실제 앱 검증이 무엇을 확인했는지 구분하기 위한 기록이다. 새 컴퓨터에서는 `python scripts/setup.py`로 현재 프로필을 복원하고 다시 확인한다.

## 로컬에서 확인한 내용

| 검사 | 확인 결과 |
| --- | --- |
| Codex 설정 | CLI `0.169.0-alpha.11.1`의 strict 설정 로딩 성공; 기본 설정과 MCP 조합 검사 |
| 설치 하네스·스킬 검사 | Python 62개 검사 실행, 실패 없음. 로컬 Windows에서 symlink 권한 관련 2개 건너뜀 |
| MCP 응답 처리 | Node 11개 검사 통과. 오류·빈 응답·잘못된 출처·인증 실패·사용 한도를 실패로 처리 |
| 프로필 | 5개 프로필 설치·재설치·전환, 기존 사용자 파일 충돌 시 변경 전 중단 |
| 깨끗한 복제본 | Git 게시 파일을 바이트 그대로 복제한 뒤 minimal → api → data → automation → web 전환, 무결성 검사와 사용자 프로젝트 설정 보존 확인 |
| Windows 실행 | npm 명령 해석, 끊어진 junction 차단, 시간 초과 시 자식 프로세스 종료 |
| 언어·경로 호환성 | ASCII·cp1252 출력 환경의 한글 메시지, macOS의 표준 임시 디렉터리 경로 처리 회귀 검사 |
| 스킬 원본 | 14개 스킬·227개 파일의 로컬 해시 확인. 새 외부 원본·라이선스 200개 파일은 고정 커밋과 대조 후 UIUX 수정 2개 파일을 별도 기록 |
| 활성 스킬 | 기본 web 프로필의 10개 스킬이 lock에 기록한 배포 파일과 일치 |
| 디자인 검색 | 영어 focus 질의에서 관련 접근성 지침 반환, 미일치 질의는 결과 없음, 검색 전후 스킬 파일 무변경 확인 |
| 공식 문서 MCP | 초기화, 도구 5개 발견, `search_openai_docs` 실제 검색 응답 |
| Context7 MCP | 키 없이 도구 2개 발견, FastAPI 라이브러리 식별 후 공식 출처가 있는 실제 예제 조회 |
| Playwright MCP | 초기화, 도구 25개 발견, Chromium에서 로컬 페이지 표시와 버튼 클릭 후 상태 변경 확인 |
| GitHub | 연결된 앱에서 계정·새 공개 저장소·Template 속성 확인 |

MCP 검사는 이름 등록만 확인하지 않는다. 공식 문서 서버에 실제 검색을 보내고, 브라우저는 별도 로컬 HTTP 테스트 페이지를 열어 버튼을 누른다. Playwright 0.0.85의 스냅샷 파일 응답과 `browser_click.target` 형식에 맞춰 검증했다.

## 자동 검사

[GitHub Actions](https://github.com/CHOI-SEUNGPYO/vibe-coding-starter/actions/workflows/validate.yml)는 다음을 실행한다. 아래 목록은 검사 구성이고, 각 실행의 성공 여부는 해당 실행 결과가 근거다.

- Windows·macOS·Linux × Python 3.11·3.13: 설치·무결성·실행 검증
- Linux × Node.js 22: MCP 응답 회귀 검사, 잠금 파일로 복원한 Playwright MCP와 실제 Chromium 클릭 흐름

CI에서 symlink·junction 관련 검사의 실행 또는 건너뜀 여부는 운영체제 권한에 따라 달라진다. 외부 문서 서버 온라인 검사는 수동 setup에 포함한다.

## 이 검사에 포함되지 않는 것

위 starter 자동 검사만으로 개별 앱의 기능·품질을 보장하지 않는다. 별도로 구현해 시험한 API의 결과는 아래에 기록했다. 유료 모델의 성능, 사용자의 GitHub CLI 로그인, 선택적 GitHub 원격 MCP 토큰, 배포 계정, 디자인 사이트의 유료 접근은 검증 대상이 아니다. 하네스의 검사 통과를 새로 만든 제품의 검사 통과라고 설명하지 않는다.

확인 환경은 Windows, Python 3.15.2, Node.js 24.22.1이다. 의존성은 `package-lock.json`, 외부 스킬은 `skills.lock.json`으로 고정했다. 버전을 바꾸면 이 기록에 기대지 말고 관련 검사를 다시 실행한다.

## API 프로필 실제 앱 검증 (2026-11-16)

공개 저장소의 `5ae792fb664836a35e5c9f8914e0a57083dd3119`를 별도 폴더에 clone하고 README 순서로 `api` 환경을 적용했다. FastAPI + SQLite 독서 기록 API를 구현한 뒤 아래를 확인했다. 앱·토큰·DB·상세 실험 보고서는 starter 게시 파일에 포함하지 않았다.

| 단계 | 실제 결과 |
| --- | --- |
| 환경 적용 | `setup.py --profile api` 성공. 스킬 9종, OpenAI Docs·Context7의 실제 요청 성공. 앱 설치 전 node_modules·Chromium 다운로드 없음 |
| 구현 | 책 CRUD, Unicode 검색, 상태 필터, 페이지 조회, 단일 Bearer 토큰, 공통 오류, OpenAPI, 파일 SQLite |
| 앱 자동 검사 | 임시 DB·시험용 토큰을 사용하는 테스트 21개 통과. 인증·설정 누락, 입력 경계, 동시 등록, 실제 DB 쓰기 실패, 재생성 후 보존 포함 |
| 실제 HTTP | 43개 검증 항목 통과. 인증·CRUD·검색·오류, DB를 실제 잠갔을 때 500과 기존 데이터 보존, Swagger 문서 응답 포함. README의 PowerShell 첫 요청도 별도 실행해 한글 저장·조회 확인 |
| 실제 재시작 | 서버 프로세스를 종료하고 새 프로세스로 같은 DB를 열어 저장한 제목·메모가 유지됨을 확인 |
| 통합 실행 | 수정한 하네스로 기본 `python scripts/vibe.py verify` 실행, 5/5 검사 통과. starter 65개 중 62개 통과·OS symlink 권한 관련 3개 건너뜀, 앱 21개 통과, `pip check` 통과 |
| 독립 검토 | NUL 제목·저자가 500을 내는 문제 재현 → 422 입력 검증으로 수정 → POST/PATCH 회귀 및 실제 HTTP 확인. 하네스 가상환경 경로·실패 전 차단·기존 명령 호환성 검토 |

재현한 막힘과 starter 반영 내용:

- 앱 `.venv`에만 의존성을 설치하면 기존 `{python}`은 starter의 Python을 사용했다. 선택적 `checks[].venv`를 추가하고 실제 가상환경 전용 모듈로 실행을 검증했다. 누락된 가상환경·잘못된 경로는 모든 검사 실행 전에 거절한다.
- CI의 `init --profile web`은 이미 적용된 `api` 프로필과 충돌했다. 현재 프로필을 검사하는 `check`로 바꿨다. 새 앱을 만들 때 CI에 앱의 의존성 설치도 추가하도록 첫 지시에 명시했다.
- 기존 첫 작업 양식은 웹 화면·Playwright 중심이었다. API 전용 양식과 README 시작 순서에 계약·인증·DB·재시도·HTTP 검사·재시작 확인을 추가했다.
- Windows 실행 환경의 제한 때문에 패키지 설치 DNS 실패와 TestClient 내부 로컬 소켓 대기를 관찰했다. 허용된 실행 환경에서 같은 설치·검사를 성공시켰다. 이를 앱 실패와 구분하되 미실행 검사를 통과로 처리하지 않도록 안내했다.

앱 실측 환경은 Windows·Python 3.15.2, FastAPI 0.163.1, Uvicorn 0.54.0, Pydantic 2.14.3, Starlette 1.10.0, HTTPX2 2.16.0이다. 설치 버전의 [Starlette TestClient 지침](https://www.starlette.io/testclient/)에 맞춰 HTTPX2를 사용했다. 앱 의존성은 별도 잠금 파일로 고정했다. 다른 OS/Python에서 이 **앱**을 실행하거나 운영 배포한 결과는 아니다. starter의 Windows·macOS·Linux CI와 앱의 로컬 검증을 구분한다.

이번 API는 개인용 로컬 실행 범위다. 다중 사용자 권한·운영 성능·외부 공개·TLS·운영 백업은 검증하지 않았다. API 프로필이 모든 제품 요구사항을 자동으로 해결한다는 의미도 아니다.
