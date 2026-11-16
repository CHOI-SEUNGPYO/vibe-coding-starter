# 개인 독서 기록 API

이 예제는 저장소 루트에서 `python scripts/setup.py --profile api`를 실행한 뒤 사용할 수 있다. 설정 적용과 앱 의존성 설치는 별개다. 아래 명령은 모두 **저장소 루트 기준**이다.

FastAPI와 Python 표준 `sqlite3`로 만든 개인용 API다. 제목, 저자, 독서 상태, 메모를 기록한다. 하나의 Bearer 토큰을 공유하는 단일 사용자용이며 브라우저 앱·회원가입·외부 DB는 포함하지 않는다.

## 설치와 실행

아래 명령은 **저장소 루트**에서 실행한다. Python 3.11 이상이 필요하며, 이번 로컬 검증 환경은 Windows / Python 3.15.2다. 가상환경 활성화는 필요 없다.

Windows PowerShell:

```powershell
python -m venv examples/reading/api/.venv
examples/reading/api/.venv/Scripts/python.exe -m pip install -r examples/reading/api/requirements.lock
```

macOS / Linux:

```sh
python3 -m venv examples/reading/api/.venv
examples/reading/api/.venv/bin/python -m pip install -r examples/reading/api/requirements.lock
```

처음 한 번만 로컬 토큰 파일을 만든다. 이 명령은 토큰을 출력하지 않으며, 기존 `.env`가 있으면 덮어쓰지 않고 실패한다. 이 공개 예제에는 `.env`가 없으므로 처음 실행하기 전에 생성한다.

```powershell
python -c "from pathlib import Path; import secrets; Path('examples/reading/api/.env').open('x', encoding='utf-8').write('BOOKS_API_TOKEN=' + secrets.token_urlsafe(32) + '\nBOOKS_DB_PATH=data/books.sqlite3\n')"
```

macOS/Linux에서는 위 명령의 `python`을 `python3`로 바꾼다.

Windows:

```powershell
examples/reading/api/.venv/Scripts/python.exe -m uvicorn main:app --app-dir examples/reading/api --env-file examples/reading/api/.env --host 127.0.0.1 --port 8001
```

macOS / Linux:

```sh
examples/reading/api/.venv/bin/python -m uvicorn main:app --app-dir examples/reading/api --env-file examples/reading/api/.env --host 127.0.0.1 --port 8001
```

- API 문서: <http://127.0.0.1:8001/docs>
- OpenAPI 명세: <http://127.0.0.1:8001/openapi.json>
- DB 연결 상태: <http://127.0.0.1:8001/health>

기본 DB 파일은 `examples/reading/api/data/books.sqlite3`다. `BOOKS_DB_PATH`가 상대 경로이면 항상 `examples/reading/api`를 기준으로 해석하므로 서버를 다른 폴더에서 실행해도 저장 위치가 바뀌지 않는다. 다른 작업 폴더에서 서버를 시작할 때는 `--app-dir`과 `--env-file`에 절대 경로를 사용한다.

## 인증과 설정

`--env-file`이 `.env`를 환경변수로 읽는다. 이미 프로세스에 설정된 환경변수가 있으면 그 값이 우선한다.

| 설정 | 역할 |
| --- | --- |
| `BOOKS_API_TOKEN` | 책 API에 필요한 비밀 토큰. 기본 토큰은 없으며 공백만 있는 값도 거절한다. |
| `BOOKS_DB_PATH` | SQLite 파일 경로. 기본값 `data/books.sqlite3`. |

책 요청마다 `Authorization: Bearer <로컬 토큰>` 헤더를 보낸다. `/docs`의 **Authorize**에도 로컬 토큰을 넣어 호출할 수 있다. 토큰을 URL이나 소스·문서·로그에 넣지 않는다. `.env`, `.venv`, DB 파일은 Git에서 제외한다.

서버 토큰이 설정되지 않으면 모든 책 요청은 **503 `SERVER_NOT_CONFIGURED`**다. 서버 토큰이 설정된 상태에서 요청 토큰이 없거나 틀리면 **401 `UNAUTHORIZED`**와 `WWW-Authenticate: Bearer`를 반환한다. 별도 사용자 권한 등급이 없으므로 403 역할은 없다. `/health`, `/docs`, `/openapi.json`은 공개이며 `/health`의 200은 DB 연결 가능 여부를 나타낸다. 인증 설정 여부나 DB 쓰기 권한까지 보장하지는 않는다.

기본 서버 주소는 이 컴퓨터에서만 접속할 수 있는 `127.0.0.1`이다. 외부 공개·TLS·운영 배포는 이 실험에 포함하지 않는다.

## 요청과 응답 계약

| 메서드·경로 | 성공 응답 | 동작 |
| --- | --- | --- |
| `POST /api/books` | 201 + 기록, `Location` 헤더 | 새 독서 기록 등록 |
| `GET /api/books` | 200 + `data`, `pagination` | ID 내림차순 목록 |
| `GET /api/books/{id}` | 200 + 기록 | 없는 ID는 404 |
| `PATCH /api/books/{id}` | 200 + 기록 | 보낸 필드만 수정, 없는 ID는 404 |
| `DELETE /api/books/{id}` | 204, 빈 본문 | 없는 ID도 204 |

등록 예시:

```json
{"title":"소년이 온다","author":"한강","status":"reading","note":"두 번째 장까지 읽음"}
```

기록 응답은 위 필드에 서버가 만든 양의 정수 `id`를 더한 객체다.

- `title`, `author`: 필수 문자열, 앞뒤 공백 제거 후 1~200자. SQLite 길이 계산과 일치하도록 NUL 문자는 허용하지 않는다.
- `status`: `want`, `reading`, `done` 중 하나. 등록 시 생략하면 `want`.
- `note`: 최대 5,000자 문자열. 등록 시 생략하면 빈 문자열. 한글·이모지·줄바꿈을 보존한다.
- 알 수 없는 필드, 잘못된 타입, 명시적인 `null`, 범위를 넘는 길이는 422다.
- PATCH에서 생략한 필드는 유지한다. `{}`는 기존 기록을 그대로 반환한다. 메모를 지우려면 `{"note":""}`를 보낸다.
- 유효하지 않은 ID(0, 음수, 정수가 아닌 값, SQLite 정수 범위 초과)는 422다.

조회 예시:

```text
GET /api/books?q=한강&status=reading&page=1&pageSize=20
```

`q`는 최대 200자이며 제목·저자의 부분 문자열을 Unicode `casefold`로 비교한다. `%`와 `_`도 일반 글자로 검색한다. 비어 있거나 공백뿐이면 전체 조회다. `status`를 생략하면 모든 상태를 조회한다. `page`는 기본 1(최대 1,000,000,000), `pageSize`는 기본 20(1~100)이다. 총 페이지 수를 넘으면 빈 `data`와 전체 개수를 반환한다.

```json
{"data":[],"pagination":{"page":1,"pageSize":20,"totalItems":0,"totalPages":0}}
```

삭제는 반복해도 204이므로 재시도할 수 있다. 같은 PATCH를 반복하면 같은 필드 값이 유지된다. **POST는 비멱등이다.** 같은 요청을 두 번 보내면 기록도 두 개 생긴다. 응답을 못 받았다고 자동 재시도하지 말고 목록을 확인한다. `Idempotency-Key`는 지원하지 않으며 헤더를 보내면 400 `UNSUPPORTED_IDEMPOTENCY_KEY`로 거절한다.

오류 본문은 공통 구조를 사용한다. 422의 `details`에는 필드 위치·메시지·오류 종류만 담으며 입력값은 되돌려주지 않는다. 실제 DB 읽기·쓰기 실패는 500 `STORAGE_ERROR`로 처리하고 성공으로 보고하지 않는다. 내부 경로나 SQLite 오류 원문도 응답에 포함하지 않는다.

```json
{"error":{"code":"BOOK_NOT_FOUND","message":"독서 기록을 찾을 수 없습니다.","details":[]}}
```

## 검사

이 공개 예제의 검사는 다음처럼 직접 실행한다. 루트 `verify`는 기본적으로 starter 검사만 실행한다. 예제를 함께 검사하려면 `checks.example.json`의 항목을 루트 `.vibe/project.json`의 `checks`에 추가한다.

```powershell
examples/reading/api/.venv/Scripts/python.exe -m unittest discover -s examples/reading/api/tests -v
examples/reading/api/.venv/Scripts/python.exe -m pip check
```

macOS/Linux에서는 가상환경 실행 경로를 `examples/reading/api/.venv/bin/python`으로 바꾼다. 검사는 임시 폴더의 DB와 별도 테스트 토큰을 사용하므로 로컬 기록과 `.env`를 읽거나 바꾸지 않는다. 자동 검사는 CRUD, 한글·이모지, Unicode 검색, 상태 필터, 페이지 조회, 필수·길이·enum·extra·null 검증, 인증, 빈 수정·삭제 재시도, 실제 DB 쓰기 실패, 동시 등록, 앱 재생성 시 보존을 확인한다. 별도 실제 HTTP·프로세스 재시작 검증은 이 테스트와 구분한다.

Windows의 실행 권한이 로컬 소켓 생성을 제한하면 TestClient도 asyncio 내부 `socketpair`에서 멈출 수 있다. 이번 환경에서 이 현상을 최소 재현으로 확인했으며 허용된 실행 환경에서는 검사가 정상 종료됐다. 검사 타임아웃이나 의존성 설치 DNS 실패를 앱 검사 통과로 간주하지 않는다.

CI에서 이 예제를 검사할 때는 Python 준비 → 예제 가상환경 생성 → 잠금 파일 설치 → 위 테스트 명령 순으로 실행한다. 실제 실행 기록은 [results/README.md](results/README.md)에서 확인한다.

2026-11-16 로컬 최종 확인: `python scripts/vibe.py verify`의 등록 검사 **5개 모두 통과**. starter 회귀 검사 **65개 중 62개 통과·3개 건너뜀**(Windows symlink 생성 권한 제한), API 검사 **21개 통과**, `pip check` 통과다. 제목·저자에 NUL 문자를 넣으면 SQLite 저장 오류가 나던 경계값도 422로 거절하도록 수정하고 POST/PATCH 회귀 입력에 포함했다.

## 의존성과 확인한 근거

2026-11-16에 PyPI에서 실제 설치한 직접 의존성은 FastAPI **0.163.1**, Uvicorn **0.54.0**, HTTPX2 **2.16.0**, python-dotenv **1.2.4**다. Pydantic **2.14.3**과 Starlette **1.10.0**을 포함한 전이 의존성도 `requirements.lock`에 고정했다. Python 3.15용 Pydantic Core wheel 설치와 `pip check`를 확인했다. 잠금 파일은 이 조합의 재설치용이며 다른 Python/OS 조합의 실측 결과를 대신하지 않는다.

- [FastAPI 보안 도구](https://fastapi.tiangolo.com/reference/security/): Bearer 인증과 OpenAPI 연결.
- [FastAPI 부분 수정](https://fastapi.tiangolo.com/tutorial/body-updates/): `exclude_unset`으로 전달한 필드만 수정.
- [Pydantic 필드](https://docs.pydantic.dev/latest/concepts/fields/): 필수값, 타입과 길이 제약.
- [Python sqlite3](https://docs.python.org/3/library/sqlite3.html): 바인딩 매개변수와 트랜잭션, 연결 종료.
- [Starlette TestClient](https://www.starlette.io/testclient/): 설치 버전에서 HTTPX는 deprecated이므로 권장 클라이언트 HTTPX2 사용.
- [FastAPI PyPI](https://pypi.org/project/fastapi/), [Uvicorn PyPI](https://pypi.org/project/uvicorn/), [HTTPX2 PyPI](https://pypi.org/project/httpx2/): 배포 버전과 Python 요구사항.

SQLite는 작은 개인 기록에 맞춘 선택이다. 전체 부분 문자열 검색은 테이블을 훑고, 여러 쓰기 작업은 파일 잠금으로 직렬화한다. 다중 사용자, 큰 데이터나 외부 공개가 필요해지면 그 요구에 맞춰 별도 설계를 검토한다.

공개 가상 요청·응답과 OpenAPI를 [results/README.md](results/README.md)에서 볼 수 있다. 다시 생성할 때는 `capture_example.py --output <새 폴더>`를 사용하며 실제 로컬 토큰·DB를 읽지 않는다.
