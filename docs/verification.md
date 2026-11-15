# 실제 검증 기록

확인 날짜: **2026-11-15**. 이 문서는 설정이 무엇을 보장하는지 구분하기 위한 기록이다. 새 컴퓨터에서는 `python scripts/setup.py --profile web`으로 다시 확인한다.

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

특정 앱의 기능·품질, 유료 모델의 성능, 사용자의 GitHub CLI 로그인, 선택적 GitHub 원격 MCP 토큰, 배포 계정, 디자인 사이트의 유료 접근은 검증 대상이 아니다. 하네스의 검사 통과를 새로 만든 제품의 검사 통과라고 설명하지 않는다.

확인 환경은 Windows, Python 3.15.2, Node.js 24.22.1이다. 의존성은 `package-lock.json`, 외부 스킬은 `skills.lock.json`으로 고정했다. 버전을 바꾸면 이 기록에 기대지 말고 관련 검사를 다시 실행한다.
