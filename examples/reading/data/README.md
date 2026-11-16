# 독서 기록 CSV 분석

이 예제는 저장소 루트에서 `python scripts/setup.py --profile data`를 실행한 뒤 사용할 수 있다. 설정 적용과 앱 의존성 설치는 별개다. 아래 명령은 모두 **저장소 루트 기준**이다.

CSV를 읽어 집계표와 한국어 차트를 만드는 개인용 도구다. 원본은 수정하지 않고, 오류가 있는 행을 몰래 버리지 않는다. 샘플은 모두 가상의 책·작가·독서 기록이며 실제 개인 기록이 아니다.

## 설치

**모든 명령은 저장소 루트**에서 실행한다. 앱은 Python **3.12 이상**이 필요하다. starter 자체는 3.11부터 동작하지만, 이 앱의 잠금 파일에 포함된 NumPy 2.5.5와 contourpy 1.4.0은 3.12 이상을 요구한다. 실제 확인 환경은 Windows / Python 3.15.2다. Node22 이상은 starter의 문서 MCP 검사에만 사용하며 분석 실행에는 필요 없다.

Windows PowerShell:

```powershell
python --version
python -m venv examples/reading/data/.venv
examples/reading/data/.venv/Scripts/python.exe -m pip install -r examples/reading/data/requirements.lock
```

macOS / Linux:

```sh
python3 --version
python3 -m venv examples/reading/data/.venv
examples/reading/data/.venv/bin/python -m pip install -r examples/reading/data/requirements.lock
```

가상환경을 활성화하거나 전역 Python 패키지·PowerShell 실행 정책을 변경할 필요는 없다. 다른 Python 버전으로 만든 기존 가상환경은 패키지를 설치하기 전에 해당 환경의 버전을 확인한다.

## 첫 분석

```powershell
$dataOutput = 'examples/reading/data/output/demo'
examples/reading/data/.venv/Scripts/python.exe examples/reading/data/analyze.py --input examples/reading/data/samples/reading-log.csv --output $dataOutput
if ($LASTEXITCODE -eq 0) {
    Invoke-Item "$dataOutput/reading-summary.png"
    Get-Content -Encoding utf8 "$dataOutput/report.md"
} else {
    throw '분석에 실패했습니다. 위 오류를 확인하고 새 출력 이름으로 다시 실행하세요.'
}
```

위 코드는 PowerShell용이다. 분석 명령이 성공한 경우에만 PNG와 보고서를 연다. **실패했다면 기존 폴더의 보고서를 이번 실행 결과로 읽지 않는다.** 기존 결과가 있다면 첫 줄의 `$dataOutput`만 `examples/reading/data/output/demo-2` 같은 새 이름으로 바꾼다.

macOS/Linux의 분석 명령은 다음과 같다. `&&` 뒤의 보고서 읽기는 분석에 성공한 경우에만 실행된다. 성공 메시지 뒤에 `reading-summary.png`도 이미지 뷰어로 연다. 브라우저나 서버를 켤 필요는 없다.

```sh
data_output=examples/reading/data/output/demo
examples/reading/data/.venv/bin/python examples/reading/data/analyze.py --input examples/reading/data/samples/reading-log.csv --output "$data_output" && cat "$data_output/report.md"
```

| 파일 | 확인할 내용 |
| --- | --- |
| `summary.json` | 전체·완독 수, 완독 페이지, 평점 평균과 분모, 상태별 수, 원본 SHA-256 |
| `monthly.csv` | 완독일 기준 월별 기록 수·완독 페이지 합계. 중간에 기록 없는 달도 0 |
| `status.csv` | want·reading·done별 기록 수. 0인 상태도 포함 |
| `reading-summary.png` | 한국어 요약, 월별 완독, 상태별 기록. 축은 0에서 시작 |
| `report.md` | 지표 해석, 분모, 원본 해시와 분석 한계 |

가상 샘플의 기대값은 **전체12건, 완독7건, 완독 페이지2,000쪽, 평점을 남긴 완독6건, 완독 평균 평점4.333**이다. 상태는 want2·reading3·done7이다. 2026년1~6월의 완독 수는 2·0·2·0·2·1, 페이지는 420·0·580·0·640·360이다. 같은 책의 재독 두 건은 다른 record_id로 저장했다.

같은 명령을 다시 실행하면 기존 결과 폴더가 있다는 오류로 끝난다. 재실행은 `--output examples/reading/data/output/demo-2`처럼 **새 폴더**를 지정한다. 임의로 덮어쓰거나 이전 결과를 지우지 않는다. 같은 파일을 같은 실행 환경에서 분석하면 JSON·CSV·보고서와 PNG가 동일한지 자동 검사로 확인한다. 다른 OS·폰트 렌더러 버전 사이의 PNG 바이트 일치까지 보장하지는 않는다.

## 내 CSV 사용하기

1. 개인 원본은 `examples/reading/data/data/private/`에 복사한다. 이 경로는 Git에서 제외되어 있다. `samples/`는 공개해도 되는 가상 자료만 둔다.
2. 아래 스키마에 맞춰 **복사본**을 준비한다. 열 이름은 영문 그대로 사용하고 순서는 바꿔도 된다. 원본 자료가 다른 형식이면 원본을 보존하고 별도 변환 파일을 만든다.
3. `--input`을 새 파일로 바꾸고 새로운 `--output`을 지정한다. 공백이 있는 경로는 따옴표로 감싼다.

```powershell
New-Item -ItemType Directory -Force examples/reading/data/data/private
```

이 폴더에 CSV를 준비한 뒤:

```powershell
examples/reading/data/.venv/Scripts/python.exe examples/reading/data/analyze.py --input "examples/reading/data/data/private/내 독서.csv" --output examples/reading/data/output/my-reading
```

기본 인코딩은 UTF-8이며 BOM이 있어도 읽는다. 한국어 Windows의 오래된 CSV가 CP949라면 명시한다. 인코딩을 자동으로 추측하거나 깨진 문자를 바꾸어 읽지 않는다.

```powershell
examples/reading/data/.venv/Scripts/python.exe examples/reading/data/analyze.py --input "examples/reading/data/data/private/내 독서.csv" --encoding cp949 --output examples/reading/data/output/my-reading-cp949
```

Git에서 제외됐는지 확인하려면 `git check-ignore examples/reading/data/data/private/내독서.csv`처럼 해당 경로를 검사한다. 이미 Git에 추적된 파일은 `.gitignore`만으로 추적이 해제되지 않는다. 개인 데이터를 Git·문서 검색 MCP·공개 서비스에 보내지 않는다. 생성된 집계도 민감할 수 있으므로 출력 폴더 역시 Git에서 제외한다.

## 입력 계약

```csv
record_id,title,author,status,pages,rating,finished_date
R001,가상의 책,가상 저자,done,240,4,2026-01-12
R002,다음에 읽을 책,가상 저자,want,320,,
```

| 열 | 조건 |
| --- | --- |
| `record_id` | 필수 문자열. 앞뒤 공백 제거 후 중복 불가. 재독은 다른 ID |
| `title`, `author` | 앞뒤 공백을 제외한 필수 문자열 |
| `status` | `want`, `reading`, `done` 중 하나 |
| `pages` | ASCII 숫자 1~6자리, 값 1~100000의 정수. 책 전체 페이지 수 |
| `rating` | 빈 값 또는 정수1~5. 빈 값은 미평점이며 0점이 아님 |
| `finished_date` | done이면 실제 달력의 `YYYY-MM-DD` 필수. 다른 상태면 빈 값 |

열 누락·추가·중복, 행의 열 개수 불일치, 잘못된 따옴표, 필수값 누락, NUL·제어문자, 숫자 대신 `NaN`·`null`·무한대 등을 넣으면 종료 코드2와 행 번호·이유를 표시한다. 빈 행을 포함해 잘못된 행을 조용히 건너뛰지 않는다. 완전히 빈 파일은 오류지만 **헤더만 있는 파일은 0건 분석**으로 처리한다. 미래 날짜를 임의로 제거하지 않으며 입력자가 의도한 날짜인지 확인해야 한다.

원본 파일은 바이트 단위로 읽고 SHA-256을 계산한다. 결과에는 제목·저자·개별 행을 복사하지 않는다. 입력 오류면 결과 폴더를 만들지 않는다. 차트 쓰기 등 생성 중 실패해도 임시 결과는 정리하고 완료된 결과처럼 노출하지 않는다. 기존 결과 폴더는 보존한다.

## 지표를 읽을 때

- **완독 수**는 status=done인 독서 기록 수다. 재독도 한 건이므로 고유 도서 수와 다르다.
- **완독 페이지**는 완독 기록의 책 전체 페이지 합계다. 읽는 중인 책의 진도나 실제 하루 독서량은 계산하지 않는다.
- **완독 평균 평점**은 완독 중 평점이 있는 기록만 분모로 삼는다. 미완독 평점은 평균에서 제외한다. 분모가0이면 JSON은 null, 보고서는 계산하지 않았다고 표시한다.
- 월별 범위는 첫 완독 달부터 마지막 완독 달까지다. 이전·이후의 미기록 기간을 자동으로 추측하지 않는다. 완독이 없으면 빈 월별 표와 안내 차트를 만든다.
- 작은 개인 CSV를 메모리에서 분석한다. 데이터베이스·대용량 처리·예측 모델·인과 분석은 포함하지 않는다.

## 검사

아래 명령으로 공개 예제 자체를 검사한다. 루트 `verify`는 기본적으로 starter 검사만 실행한다. 예제도 포함하려면 `checks.example.json`을 루트 `.vibe/project.json`의 `checks`에 추가한다.

```powershell
examples/reading/data/.venv/Scripts/python.exe -m unittest discover -s examples/reading/data/tests -v
examples/reading/data/.venv/Scripts/python.exe -m pip check
```

검사는 임시 CSV·임시 출력 폴더를 쓰며 개인 CSV나 `output/demo`를 바꾸지 않는다. 고정 기대값, 원본 보존, UTF-8/BOM/CP949, 누락·중복·날짜·숫자·NUL, 빈 목록, 재실행 일치, 기존 결과 보존, 차트 쓰기 실패, 실제 CLI와 PNG를 확인한다. 공개 복사본에서 자동 검사18개를 통과했다. 루트 CI의 예제 검사는 Python3.13에서 예제 가상환경·잠금 의존성을 준비한 뒤 실제 앱 테스트를 실행한다. 원격 결과는 해당 GitHub Actions 실행에서 확인한다.

## 한글 폰트와 재현성

화면 없는 실행 환경에서도 Matplotlib의 Agg 백엔드로 PNG를 저장한다. 설치된 기본 한국어 폰트에 의존하지 않으며 `.cache/matplotlib/`를 앱 안의 로컬 캐시로 사용한다. 원본 폰트는 [Google Fonts Noto Sans KR 고정 커밋](https://github.com/google/fonts/tree/b38c5c93af322c45f633e17ac440ec1e6c94d489/ofl/notosanskr)이다. SIL OFL1.1 라이선스 전문, 출처·SHA-256은 `fonts/OFL.txt`, `fonts/source.json`에 있다.

처음 variable TTF를 그대로 사용했을 때 Matplotlib에서 normal/bold가 weight100으로 대체되는 경고와 가는 글자를 확인했다. fontTools4.68.0의 공식 instancer로 weight400·700을 고정한 Regular·Bold TTF를 만들고 사용한다. 원본 폰트의 고정 URL·해시와 파생 파일의 해시·변환 정보를 남겼다. 실행에 필요한 Regular·Bold 파일만 번들하고 원본 variable 파일은 중복 저장하지 않았다. 폰트가 빠지면 다른 글꼴로 조용히 대체하지 않고 실패한다.

실제 설치 버전은 Matplotlib3.11.2, NumPy2.5.5, contourpy1.4.0이며 전이 의존성을 포함한 11개를 `requirements.lock`으로 고정했다. 새 OS/Python에서 복원하면 그 환경에서 검사를 다시 실행한다.

- [Python CSV](https://docs.python.org/3/library/csv.html): newline·명시적 인코딩·CSV 형식 검사.
- [Matplotlib3.11.2 백엔드](https://github.com/matplotlib/matplotlib/blob/v3.11.2/galleries/users_explain/figure/backends.rst): Agg와 파일 저장. Context7에서 이 버전의 공식 문서를 확인했다.
- [fontTools4.68.0 instancer](https://github.com/fonttools/fonttools/blob/4.68.0/Doc/source/varLib/instancer.rst): 모든 축을 고정한 static font 생성과 이름 갱신.

대표 가상 샘플의 공개 결과는 [results/report.md](results/report.md), 이번 복사본의 검사 기록은 [results/README.md](results/README.md)에 있다. 개인 CSV나 기존 로컬 결과는 포함하지 않았다.
