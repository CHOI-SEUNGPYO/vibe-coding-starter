# 실제 실행 결과

2026-11-16, Windows·Python3.15.2에서 공개 가상 샘플 `../samples/books.json`을 사용했다. 이 폴더의 JSON은 아래 명령의 실제 stdout을 저장한 것이다. 개인 기록이나 기존 웹앱·API 저장소를 읽지 않았다.

저장소 루트에서 재현한다.

```powershell
python examples/reading/minimal/search.py --input examples/reading/minimal/samples/books.json --query "숲" --status reading
python examples/reading/minimal/search.py --input examples/reading/minimal/samples/books.json --query STRASSE
python examples/reading/minimal/search.py --input examples/reading/minimal/samples/books.json --query "없는 제목"
```

| 결과 파일 | 확인한 동작 |
| --- | --- |
| [search.json](search.json) | 제목에 숲이 있고 reading인 ID2 한 권 |
| [unicode.json](unicode.json) | STRASSE가 Straße에 대응해 ID4 한 권 |
| [empty.json](empty.json) | 찾는 책이 없어도 성공하고 빈 배열 반환 |
| [verification.json](verification.json) | 실제 명령·환경·입력 해시·검사 개수·원본 보존 기록 |

앱 검사11개와 별도 clone의 통합4개 검사를 통과했다. 통합에는 starter65개 검사가 포함되며62개 통과·Windows symlink 권한 관련3개 건너뜀이다. 공개 예제 위치에서도 앱11개를 다시 실행했다. 검색·빈 결과·잘못된 JSON·중복ID·BOM·Unicode·실제 CLI 종료 코드와 원본 보존을 확인했다.

이 기록은 로컬 실행 결과이며 원격 CI 결과를 대신하지 않는다. 대용량 성능, 다른 언어권의 모든 검색 규칙, 자동 변환·편집은 검증 범위가 아니다. 저장소를 새 OS에서 복원하면 앱 검사를 다시 실행한다.
