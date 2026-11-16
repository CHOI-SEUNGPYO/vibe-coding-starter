# 주간 독서 요약 자동화

로컬 독서 CSV에서 한 주의 완독 기록을 요약한다. 기본 실행은 **미리보기만** 하며 `--apply`를 붙여야 Markdown·JSON을 저장한다. 외부 메시지 발송이나 실제 예약 작업을 등록하지 않는다.

Python3.11 이상 표준 라이브러리만 사용한다. 별도 패키지·DB·계정은 필요 없다. 이 설명의 명령은 저장소 루트에서 실행한다. 이 폴더의 코드·샘플은 공개 가능한 자료이며 결과 예시는 `results/`에서 확인한다.

```powershell
python scripts/setup.py --profile automation
python examples/reading/automation/weekly_digest.py --input examples/reading/automation/samples/reading-log.csv --week 2026-11-09 --output examples/reading/automation/work/output
```

`mode: dry-run`, `action: create`와 예상 요약을 확인한다. 이 명령만으로는 `work/output`도 생기지 않는다. 계획이 맞으면 **같은 명령에만 `--apply`를 추가**한다.

```powershell
python examples/reading/automation/weekly_digest.py --input examples/reading/automation/samples/reading-log.csv --week 2026-11-09 --output examples/reading/automation/work/output --apply
```

응답의 `destination` 폴더에 `summary.json`, `digest.md`, `manifest.json`이 생긴다. 같은 명령을 다시 실행하면 `action: already-complete`이며 파일을 다시 쓰지 않는다. 실행 결과를 읽을 때는 종료 코드0을 먼저 확인한다. 출력 폴더를 만들고도 실패한 실행은 완료로 처리하지 않는다.

## CSV와 기간

샘플은 모두 가상의 기록7건이다. 필수 열은 `record_id,title,author,status,pages,rating,finished_date`이며 헤더 순서는 바뀌어도 된다.

- `record_id`, `title`, `author`: 앞뒤 공백을 제외한 필수 문자열. record_id 중복은 오류이며 재독은 다른ID로 기록한다.
- `status`: want/reading/done.
- `pages`: ASCII숫자1~6자리, 값1~100000의 정수. 전체 책의 분량이다.
- `rating`: 빈 값 또는1~5의 정수. 빈 값을0점으로 계산하지 않는다.
- `finished_date`: done이면 실제 달력의 YYYY-MM-DD, 다른 상태면 빈 값.

기본 인코딩은 UTF-8이며 BOM을 허용한다. CP949 파일은 `--encoding cp949`를 명시한다. 누락·중복·열 개수·잘못된 날짜·숫자·NUL은 행 번호와 원인을 알리고 종료코드2로 거절한다. 일부 행을 조용히 버리지 않는다. 헤더만 있으면0건, 완전히 빈 파일은 오류다.

`--week`는 **월요일**이다. 해당 월요일부터 일요일까지 양끝을 포함하며 완독일이 이 범위에 속하는 done 기록만 집계한다. 날짜만 있으므로 시간대 변환은 없다. 가상 샘플의 2026-11-09주는 완독3건·540쪽·평점 분모2건·평균4점이다. 직전 일요일11/08과 다음 월요일11/16의 기록, 미완독 평점은 제외한다. 완독이 없는 주의 평균은 null이다.

## 재실행과 실패 복구

실행 키는 원본 바이트의 SHA-256, 주 시작일, 인코딩, 처리 버전으로 결정한다. 원본 내용이 달라지면 의미가 비슷해도 새로운 키다. 제목·저자·개별 행은 결과에 복사하지 않는다.

실제 저장은 같은 출력 폴더의 임시 폴더에서 모두 만든 뒤 완료 폴더로 옮긴다. 중간 쓰기 실패는 임시 결과를 정리하고 기존 결과와 원본을 보존한다. 다시 `--apply`하면 새로 시도할 수 있다. 원본 파일은 수정하지 않는다.

완료 폴더가 있으면 세 파일의 목록과 실제 바이트를 이번 입력으로 다시 계산한 결과와 대조한다. 파일을 지우거나 수정하면 `already-complete`로 속이지 않고 실패한다. 그런 결과를 덮어쓰지 말고 원인을 확인한 뒤 다른 `--output`을 지정한다. manifest는 보안 서명이 아니라 무결성 확인 자료다.

한 사람이 로컬에서 순서대로 실행하는 예제다. 분산 스케줄러나 동시 실행의 정확히 한 번 처리까지 보장하지 않는다. 강제 종료 때 임시 폴더가 남을 수 있으나 완료 폴더로 읽지는 않는다. 처리 규칙을 바꾸면 `VERSION`도 바꾸어 다른 실행으로 구분한다.

## 검사와 내 데이터

```powershell
python -m unittest discover -s examples/reading/automation/tests -v
```

위 명령은 예제를 직접 검사한다. 루트 `python scripts/vibe.py verify`에도 연결하려면 `checks.example.json`의 검사 항목을 루트 `.vibe/project.json`의 기존 `checks` 배열에 추가한다. 기존 환경 검사를 지우지 않는다. 원래 starter 검사만 실행한 것을 이 예제의 검증으로 해석하지 않는다.

개인 원본은 `examples/reading/automation/data/private/`에 두고 입력 경로만 바꾼다. 새 실행 결과를 저장하는 `work/`는 이 예제의 `.gitignore`에서 제외한다. 공개 `samples/`와 `results/`는 가상 자료만 사용한다. 이미 Git이 추적하는 파일은 ignore로 숨겨지지 않으므로 게시 전에 `git status`와 `git ls-files`도 확인한다.

automation 프로필의 스킬10종과 MCP3개는 일반 반복 작업을 위한 구성이다. 이번 파일 처리 도구는 브라우저를 호출하지 않는다. 프로필 준비 과정에서는 별도로 OpenAI Docs·Context7·격리Chromium 클릭을 실제 확인했다. 앱 테스트16개는 미리보기·주 경계·재시도·변조·입력 오류·중간 쓰기 실패와 링크 경로 거절을 확인한다. 실측 환경은 Windows·Python3.15.2이며 다른 운영체제의 앱 검증 여부는 해당 CI 결과를 따른다.

출력 부모·완료 폴더·결과 파일의 심볼릭 링크와 Windows reparse point를 거절한다. Python3.11에서도 junction을 판별하도록 `lstat` 파일 속성을 사용한다. Windows의 실제 junction 회귀 검사는 임시 폴더에서 링크를 만들 수 있는 실행 권한이 필요하며, 제한 때문에 실행하지 못한 검사는 통과로 처리하지 않는다.

레퍼런스: [n8n 워크플로](https://n8n.io/workflows/)에서 입력→변환→저장·재시도 흐름을 참고했고 n8n 설치는 요구하지 않는다. 구현은 [Python CSV](https://docs.python.org/3/library/csv.html), [tempfile](https://docs.python.org/3/library/tempfile.html), [pathlib](https://docs.python.org/3/library/pathlib.html)를 사용한다.
