# 책갈피 — web 프로필 예제

React + TypeScript + Vite로 만든 개인 독서 기록 앱이다. 책 제목·저자·읽는 상태·메모를 저장하고 수정·삭제하며 제목·저자 검색과 상태 필터를 제공한다. 처음 열면 빈 서재가 나타나며 시험 기록을 사용자 데이터로 넣지 않는다.

## 환경과 실행

**저장소 루트**에서 실행한다. starter의 `web` 환경과 이 앱의 의존성은 별도로 준비한다. Node24.x 중24.15 이상을 권장하며 실제 확인은 Node24.22.1이다. 전체 잠금 의존성의 지원 범위는 `^22.22.2 || ^24.15.0 || >=26.0.0`이다.

```powershell
python scripts/setup.py --profile web
npm.cmd --prefix examples/reading/web ci
npm.cmd --prefix examples/reading/web run dev
```

기본 주소는 http://127.0.0.1:5173/ 이며 서버 터미널은 계속 켜 둔다. 이미 쓰는 포트라면 다음처럼 다른 포트를 지정한다. 종료는 해당 서버 터미널의 `Ctrl+C`다.

```powershell
npm.cmd --prefix examples/reading/web run dev -- --port 5174
```

macOS/Linux는 `npm.cmd` 대신 `npm`을 사용한다. 브라우저에서 책 등록 → 검색·필터 → 수정 → 새로고침 → 삭제를 확인한다. 코드와 상태 모델은 이 폴더 안에 있고 루트의 MCP용 package.json은 바꾸지 않는다.

## 검사

```powershell
npm.cmd --prefix examples/reading/web run typecheck
npm.cmd --prefix examples/reading/web test
npm.cmd --prefix examples/reading/web run build
```

루트의 `python scripts/vibe.py verify`는 기본적으로 starter만 검사한다. 이 예제도 포함하려면 `checks.example.json`의 항목을 루트 `.vibe/project.json`의 `checks`에 추가한다. CI에서는 Node와 이 예제의 잠금 의존성을 먼저 설치해야 한다.

테스트는 등록·검색·수정·재조회·삭제, 잘못된 입력, 저장·삭제 실패 시 데이터 보존, 손상 데이터, 다른 탭과의 변경 충돌을 확인한다. DOM 테스트와 실제 브라우저의 포커스·작은 화면 확인은 구분한다. 공개본의 실제 검사와 화면 결과는 [results/README.md](results/README.md)에 기록한다.

## 저장과 제한

- `localStorage`의 `reading-log:books:v1` 키에 저장하며 계정·서버·기기 간 동기화는 없다.
- 브라우저 프로필·호스트·포트가 달라지면 저장 공간도 다르다. `localhost`와 `127.0.0.1`도 구분되므로 같은 주소를 사용한다.
- 이전 기록이 있는 주소에서 실행하면 그 기록이 나타날 수 있다. 새 시험은 격리된 브라우저나 다른 포트에서 시작한다. 앱 실행이나 샘플 확인을 위해 기존 저장 데이터를 자동으로 지우지 않는다.
- 저장 성공 후에만 목록을 바꾸며 저장 공간 오류 때 입력·기존 기록을 보존한다. 손상된 JSON을 새 데이터로 덮어쓰는 자동 복구는 하지 않는다.
- 다른 탭의 변경을 감지하면 오래된 화면의 저장을 차단한다. 입력을 따로 보관한 뒤 새로고침한다.
- 제목200자, 저자120자, 메모5,000자까지 입력할 수 있으며 삭제는 확인을 거친다.

디자인 선택·레퍼런스와 사용한 패키지 근거는 [DESIGN.md](DESIGN.md)에 있다. `node_modules`, `dist`, 로컬 결과는 Git에서 제외한다. 실제 사용자 브라우저의 저장 데이터는 이 공개 예제에 포함되지 않는다.
