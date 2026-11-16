# api 예제 결과

2026-11-16, Windows·Python3.15.2에서 `examples/reading/api`에 새 가상환경을 만들고 잠금 파일로 의존성을 복원했다. 복사본의 **테스트21개와 pip check가 통과**했다.

- [requests-and-responses.json](requests-and-responses.json): 새 임시 SQLite DB에서 수행한 가상 요청9개와 실제 응답. 상태 확인, 인증 거절, 등록·목록·수정·상세·입력 오류·삭제·삭제 후 조회를 포함한다.
- [openapi.json](openapi.json): 같은 앱이 실제 제공한 OpenAPI 명세. 인증 스키마와 입력·응답 계약을 확인할 수 있다.

DB와 Bearer 토큰은 실행 중 임시로 만들었고 토큰 값·인증 헤더·개인 파일 경로는 결과에 기록하지 않았다. 실제 사용자의 `.env`나 DB를 읽지 않았다. 가상 도서와 메모만 사용했다.

같은 결과를 새 폴더에 재현하려면 저장소 루트에서 실행한다.

```powershell
examples/reading/api/.venv/Scripts/python.exe examples/reading/api/capture_example.py --output examples/reading/api/output/capture-1
```

macOS/Linux는 `.venv/bin/python`을 사용한다. 출력 폴더가 있으면 다른 이름을 지정한다. 이 생성 명령은 TestClient로 실제 앱 요청 처리를 검증하며 외부 네트워크 서버에 연결하는 검사를 대신하지 않는다.

최초 API 실습에서는 별도 Uvicorn 서버의 실제 HTTP43개 항목과 프로세스 종료·재시작 후 보존도 확인했다. 이번 공개본에서는 새 가상환경의21개 테스트와 위9개 요청을 다시 실행했다. 단일 개인 토큰 API이며 다중 사용자 권한·운영 부하·TLS·외부 배포는 이 결과에 포함하지 않는다.
