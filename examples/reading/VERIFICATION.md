# 독서 예제 검증 기록

2026-11-16에 5개 프로필의 독서 프로젝트를 실제로 구현·실행하고, 공개 예제 폴더에서 다시 확인했다. 아래 수치는 로컬에서 관찰한 결과이며 원격 CI의 성공 여부는 [GitHub Actions 실행 기록](https://github.com/CHOI-SEUNGPYO/vibe-coding-starter/actions/workflows/validate.yml)에서 확인한다.

## 환경 적용부터 첫 실행까지

각 실습은 starter를 별도 폴더에 복제한 뒤 해당 `setup.py --profile`부터 시작했다. 원래 실습 폴더와 상세 조사 보고서는 Git에 넣지 않았다. 공개본에는 앱 소스·잠금 파일·가상 샘플·재현할 수 있는 결과만 옮겼다.

| 프로필 | 실제 적용한 환경 | 공개본에서 다시 확인한 내용 |
| --- | --- | --- |
| web | 스킬10종, 문서 MCP2개·Playwright | 타입 검사, 테스트16개, 빌드, 실제 Chromium 등록·검색·수정·새로고침·삭제·모바일 |
| api | 스킬9종, 문서 MCP2개, 앱 설치 전 브라우저 다운로드 없음 | 새 가상환경, 테스트21개·pip check, 임시 DB의 요청9개와 OpenAPI 생성 |
| data | 스킬8종, 문서 MCP2개, 브라우저 의존성 없음 | 새 가상환경, 테스트18개·pip check, CSV 분석과 결과5개 재생성·검산 |
| minimal | 스킬6종, MCP0개, Node 없이 준비 | 테스트11개, 실제 CLI의 제목·저자·Unicode 검색·빈 결과·원본 해시 보존 |
| automation | 스킬10종, 문서 MCP2개·격리 Chromium 클릭 | 테스트16개, 실제 dry-run·저장·재실행·결과 무변경, 주 경계·평점 분모 검산 |

로컬 환경은 Windows·Python3.15.2·Node24.22.1·npm11.19.1이다. 앱마다 필요한 최소 버전과 의존성이 다르므로 해당 README를 따른다. setup의 MCP 확인과 앱의 기능 검사는 별개의 검사다. 예를 들어 automation 앱은 파일만 처리하며, 브라우저 검사는 프로필 준비 과정에서 수행했다.

## 공개 결과와 확인 방법

| 예제 | 가상 입력과 기대 결과 | 결과 파일 |
| --- | --- | --- |
| web | 빈 서재에서 화면으로3권 등록, 삭제 후2권, 재등록 후3권 | [PC·모바일 화면과 흐름](web/results/README.md) |
| api | 새 임시 DB에서 인증 거절·등록·조회·수정·입력 오류·삭제 | [요청·응답9개, OpenAPI](api/results/README.md) |
| data | 12건 중 완독7건·2,000쪽, 평점 분모6건·평균4.333점 | [보고서·표·차트](data/results/README.md) |
| minimal | 숲+reading 검색 ID2, STRASSE 검색 ID4, 없는 제목은 빈 배열 | [JSON 응답과 원본 해시](minimal/results/README.md) |
| automation | 2026-11-09~15 완독3건·540쪽, 평점 분모2건·평균4점 | [미리보기·생성·재실행·요약·manifest](automation/results/README.md) |

각 README에 설치·실행·검사 명령이 있다. 기본 `python scripts/vibe.py verify`는 starter에 등록된 검사를 실행한다. 예제도 함께 실행하려면 `checks.example.json`을 기존 `.vibe/project.json`에 병합하고 필요한 앱 의존성을 먼저 설치한다.

최초 API 실습의 실제 HTTP43개 항목·프로세스 재시작, 데이터 실습의 독립 CLI34개 항목은 [이전 검증 기록](../../docs/verification.md)에 구분했다. 공개 API 결과 생성기는 TestClient를 사용하므로 외부 서버에 보낸 네트워크 요청이라고 표현하지 않는다.

## 이번 실습에서 보완한 것

- 작은 도구와 자동화 전용 첫 작업 양식을 추가했다. 입력 계약·종료 코드·원본 보존과, 미리보기·중복 실행·부분 실패·검증된 결과 재사용을 각각 완료 조건으로 삼는다.
- 예제는 루트 MCP용 의존성과 분리했다. 최소 Python 버전, 실제 명령 위치, 앱 검사 등록 방법을 예제마다 제공한다.
- Windows와 Git의 줄바꿈 차이로 원본 해시·실행 키가 바뀌지 않도록 공개 샘플과 텍스트 결과를 LF로 고정했다. 데이터 분석 결과5개를 새로 생성해 공개 파일과 바이트를 대조했다.
- 자동화의 Windows junction 검사를 Python3.11에서도 동작하는 `lstat` 속성 검사로 바꿨다. 출력 부모·완료 폴더·결과 파일에 같은 규칙을 적용하고, 실제 junction을 사용하는 회귀 검사를 추가했다.
- 개인 입력·출력과 공개 결과를 구분했다. API 토큰·로컬 DB·사용자 브라우저 상태·의존성 폴더는 게시 대상에서 제외했다. 한국어 차트의 폰트는 출처·라이선스와 함께 포함했다.

## 자동 검사와 범위

[워크플로](../../.github/workflows/validate.yml)는 총11개 작업으로 구성했다.

- 6개: Windows·macOS·Linux × Python3.11·3.13에서 starter와 minimal·automation 검사.
- 1개: Node22에서 MCP 응답 검사와 실제 Chromium 클릭.
- 3개: Windows·macOS·Linux × Python3.13에서 별도 가상환경의 API·data 검사와 의존성 충돌 확인.
- 1개: Linux·Node24에서 web 의존성 복원·타입 검사·16개 테스트·빌드.

심볼릭 링크·junction 검사는 해당 OS와 실행 권한에 따라 실행 또는 건너뜀으로 기록한다. 구성에 적혀 있다는 이유만으로 성공했다고 판단하지 않는다. 게시 커밋과 같은 SHA의 원격 실행을 확인한다.

이 예제들은 서로 독립적이다. 통합 서비스, 다중 사용자 운영, 외부 배포, 대용량 성능을 검증한 결과가 아니다. 자동화는 로컬에서 순서대로 실행하는 파일 처리까지 구현했고 실제 예약·외부 메시지 발송은 등록하지 않았다. 차트의 수치 재현과 OS가 다른 PNG의 바이트 일치는 구분한다.
