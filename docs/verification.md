# 실제 검증 기록

확인 날짜: **2026-11-15**. 이 문서는 설정이 무엇을 보장하는지 구분하기 위한 기록이다. 새 컴퓨터에서는 `python scripts/setup.py --profile web`으로 다시 확인한다.

## 로컬에서 확인한 내용

| 검사 | 확인 결과 |
| --- | --- |
| Codex 설정 | CLI `0.169.0-alpha.11.1`의 strict 설정 로딩 성공; 기본 설정과 MCP 조합 검사 |
| 설치 하네스·스킬 검사 | 총 38개 테스트 중 36개 통과, Windows에서 symlink 생성 권한이 필요한 2개 건너뜀 |
| 프로필 | 5개 프로필 설치·재설치·전환, 기존 사용자 파일 충돌 시 변경 전 중단 |
| 깨끗한 복제본 | 실제 Git clone 후 minimal → web → api 전환과 무결성 검사 통과 |
| Windows 실행 | npm 명령 해석, 끊어진 junction 차단, 시간 초과 시 자식 프로세스 종료 |
| 스킬 원본 | 6개 스킬 파일 목록·SHA-256 일치; 외부 3개 스킬의 21개 파일은 고정 커밋의 Git blob과 일치 |
| 활성 스킬 | 기본 web 프로필의 5개 스킬이 원본과 일치 |
| 공식 문서 MCP | 초기화, 도구 5개 발견, `search_openai_docs` 실제 검색 응답 |
| Playwright MCP | 초기화, 도구 25개 발견, Chromium에서 로컬 페이지 표시와 버튼 클릭 후 상태 변경 확인 |
| GitHub | 연결된 앱에서 계정·새 공개 저장소·Template 속성 확인 |

MCP 검사는 이름 등록만 확인하지 않는다. 공식 문서 서버에 실제 검색을 보내고, 브라우저는 별도 로컬 HTTP 테스트 페이지를 열어 버튼을 누른다. Playwright 0.0.85의 스냅샷 파일 응답과 `browser_click.target` 형식에 맞춰 검증했다.

## 자동 검사

[GitHub Actions](https://github.com/CHOI-SEUNGPYO/vibe-coding-starter/actions/workflows/validate.yml)는 다음을 실행한다. 아래 목록은 검사 구성이고, 각 실행의 성공 여부는 해당 실행 결과가 근거다.

- Windows·macOS·Linux × Python 3.11·3.13: 설치·무결성·실행 검증
- Linux × Node.js 22: 잠금 파일로 복원한 Playwright MCP와 실제 Chromium 클릭 흐름

CI에서 symlink·junction 관련 검사의 실행 또는 건너뜀 여부는 운영체제 권한에 따라 달라진다. 외부 문서 서버 온라인 검사는 수동 setup에 포함한다.

## 이 검사에 포함되지 않는 것

특정 앱의 기능·품질, 유료 모델의 성능, 사용자의 GitHub CLI 로그인, 선택적 GitHub 원격 MCP 토큰, 배포 계정, 디자인 사이트의 유료 접근은 검증 대상이 아니다. 하네스의 검사 통과를 새로 만든 제품의 검사 통과라고 설명하지 않는다.

확인 환경은 Windows, Python 3.15.2, Node.js 24.22.1이다. 의존성은 `package-lock.json`, 외부 스킬은 `skills.lock.json`으로 고정했다. 버전을 바꾸면 이 기록에 기대지 말고 관련 검사를 다시 실행한다.
