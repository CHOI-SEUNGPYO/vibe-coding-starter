# 읽기 전용 독서 기록 검색

`minimal` 환경에서 만든 작은 Python 도구다. JSON의 제목·저자와 읽는 상태를 검색하고 결과를 화면에 출력한다. 파일 수정, 네트워크 연결, 외부 패키지 설치는 하지 않는다. 샘플의 책·작가·메모는 모두 가상이다.

## 실행

Python 3.11 이상이 필요하다. 실제 검증 환경은 Windows·Python 3.15.2다. 별도 복제본에서 `python scripts/setup.py --profile minimal`을 실제 적용해 스킬6종과 MCP0개를 확인했다. 이 저장소에서도 같은 준비 명령으로 minimal 환경을 선택할 수 있다. Node나 가상환경은 이 도구에 필요하지 않다. setup은 작업 환경을 준비하는 명령이며 JSON 검색은 아래 앱 명령으로 실행한다.

저장소 루트에서 실행한다.

```powershell
python examples/reading/minimal/search.py --input examples/reading/minimal/samples/books.json
python examples/reading/minimal/search.py --input examples/reading/minimal/samples/books.json --query "윤서" --status want
python examples/reading/minimal/search.py --input examples/reading/minimal/samples/books.json --query STRASSE
```

macOS/Linux에서 Python 실행 이름이 `python3`라면 바꿔 실행한다. 두 번째 명령은 ID3의 가상 책 한 권, 세 번째는 `Straße`가 들어 있는 ID4 한 권을 반환한다. 검색어를 생략하거나 공백만 넣으면 모든 기록을 조회하고, 상태를 함께 지정하면 두 조건을 모두 만족하는 기록만 출력한다. 메모는 검색하지 않는다.

성공은 종료 코드0과 UTF-8 JSON 배열이다. 결과가 없을 때도 `[]`와 코드0이다. 오류는 stderr와 코드2이며 성공 JSON을 함께 출력하지 않는다. 결과 순서는 원본 순서를 유지한다. `--help`로 옵션을 확인한다.

## 입력과 원본 보존

```json
[
  {"id":1,"title":"가상의 책","author":"가상 작가","status":"want","note":""}
]
```

- UTF-8 JSON 배열을 받으며 UTF-8 BOM도 허용한다.
- 다섯 필드는 모두 필요하며 알 수 없는 필드는 거절한다.
- `id`는 양의 정수이고 중복할 수 없다. `true`, 문자열 숫자, 소수는 ID가 아니다.
- `title`·`author`는 공백만으로 이루어지지 않은 문자열이다. `note`는 빈 문자열을 허용한다.
- `status`는 `want`, `reading`, `done` 중 하나다.
- 중복 JSON 필드, NUL, 잘못된 Unicode surrogate 문자를 거절한다. 내용은 고쳐 저장하지 않는다.

검색할 때만 NFC 정규화와 `casefold`를 적용하므로 자모로 분해된 한글이나 `Straße`/`STRASSE`도 비교할 수 있다. JSON 결과의 원래 제목·메모·순서는 유지한다. 자동 번역·오타 교정·정렬은 하지 않는다.

개인 JSON은 `examples/reading/minimal/data/private/`에 복사하고 `--input`을 그 경로로 바꾼다. 저장소의 `**/data/private/` 규칙은 새 개인 파일을 Git에서 제외하지만 이미 추적 중인 파일에는 적용되지 않는다. 공개 `samples/`를 개인 기록으로 덮어쓰지 않는다. 출력은 요청한 책의 메모까지 포함하므로 공개할 때는 가상 샘플만 사용한다.

API나 웹앱의 실제 저장소와 자동으로 연결되지 않는다. JSON 계약이 다르면 원본을 보존한 별도 변환 파일을 만든다. 작은 개인 기록을 메모리에 읽는 도구이며 대용량 인덱스나 동시 편집은 다루지 않는다.

## 검사와 다음 수정

```powershell
python -m unittest discover -s examples/reading/minimal/tests -v
```

기본 `python scripts/vibe.py verify`는 starter 검사만 실행한다. 이 예제를 함께 검사하려면 `checks.example.json`의 검사 항목을 루트 `.vibe/project.json`의 `checks` 배열에 추가한다. 기존 항목을 통째로 덮어쓰지 않는다. 실제 별도 복제본에서는 앱 검사를 연결해 통합 검증했다. 고정 기대 결과, NFC·casefold, 조건 교집합, BOM, 원본 SHA-256 보존, 빈 배열, 잘못된 JSON·필드·중복·상태, 실제 CLI 종료 코드를 검사한다. 임시 파일만 사용하며 개인 입력을 읽지 않는다.

다음 수정 예시: “메모도 검색 대상에 추가하고, 기존 제목·저자 검색과 원본 보존이 유지되는지 검사해줘.” 먼저 현재 실패 조건을 재현하고 작은 함수와 관련 검사만 고치는 방식으로 이어갈 수 있다.

## 레퍼런스

- [argparse](https://docs.python.org/3/library/argparse.html): 표준 옵션·도움말·잘못된 인수 처리.
- [json](https://docs.python.org/3/library/json.html): JSON 읽기·쓰기와 중복 키 처리를 위한 `object_pairs_hook`.
- [unicodedata](https://docs.python.org/3/library/unicodedata.html): NFC 정규화.
- [str.casefold](https://docs.python.org/3/library/stdtypes.html#str.casefold): Unicode 대소문자 구분 없는 비교.
