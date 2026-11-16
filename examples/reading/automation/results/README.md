# 주간 독서 자동화 실행 결과

2026-11-16, Windows·Python3.15.2에서 **공개 가상 샘플7건**으로 아래 명령을 실제 실행했다. 개인 원본이나 비밀 설정은 사용하지 않았다. 상대 경로는 저장소 루트 기준이다.

```powershell
python examples/reading/automation/weekly_digest.py --input examples/reading/automation/samples/reading-log.csv --week 2026-11-09 --output examples/reading/automation/work/output
python examples/reading/automation/weekly_digest.py --input examples/reading/automation/samples/reading-log.csv --week 2026-11-09 --output examples/reading/automation/work/output --apply
python examples/reading/automation/weekly_digest.py --input examples/reading/automation/samples/reading-log.csv --week 2026-11-09 --output examples/reading/automation/work/output --apply
```

| 결과 파일 | 실제 확인 |
| --- | --- |
| [dry-run.json](dry-run.json) | mode=dry-run, action=create. 출력 폴더도 만들지 않음 |
| [apply.json](apply.json) | action=created. 지정한 실행 키 폴더에 결과3개 생성 |
| [retry.json](retry.json) | action=already-complete. 첫 실행 파일의 내용과 수정 시간이 모두 유지됨 |
| [digest.md](digest.md) | 11/09~11/15의 완독3건·540쪽·평점 분모2·평균4점 |
| [summary.json](summary.json) | 같은 지표·원본 해시·처리 버전·실행 키 |
| [manifest.json](manifest.json) | 완성된 요약과 Markdown의 SHA-256 |

샘플의 직전 일요일11/08, 다음 월요일11/16, 읽는 중의 평점은 이 주의 계산에서 제외됐다. 원본 해시가 실행 전후 같았다. 샘플 CSV는 Git에서도 LF 줄바꿈을 유지하도록 설정해 입력 바이트와 실행 키가 바뀌지 않게 했다.

추가로 앱 자동 검사 **16개 통과**: 미리보기 무변경, 같은 작업 재실행, 입력 변경 시 새 키, 빈 주·연도 경계, UTF-8 BOM·CP949, 잘못된 입력, 기존 결과 변조·누락, 출력 경로 오류, 중간 쓰기 실패 후 정리와 재시도, 링크 경로 거절을 확인했다. 중간 쓰기 실패는 테스트에서 파일 쓰기를 실패시키는 방식으로 재현했고, 실제 CLI의 생성·재실행과 구분한다.

별도 clone에서 automation 프로필을 적용해 스킬10종·문서MCP2개·격리Playwright 클릭 검사까지 통과했다. 그 clone의 `python scripts/vibe.py verify`는 등록된 검사4개를 모두 통과했다(starter65개 중62개 통과·Windows symlink권한3개skip, 앱14개 통과). 이 기록만으로 다른OS·분산 동시 실행·실제 예약·외부 메시지 발송이 검증됐다고 해석하지 않는다. 원격 CI 결과는 저장소의 해당 실행을 확인한다.

이후 독립 리뷰에서 `Path.is_junction`이 없는 Python3.11에서 junction 검사가 빠질 수 있음을 발견했다. starter와 같은 `lstat`의 reparse 속성 검사로 출력 부모·완료 폴더·파일을 일관되게 거절하도록 수정했다. 실제 Windows junction을 만들고 새 pathlib API를 사용하지 않는 조건에서 원본과 대상 파일 보존을 확인하는 회귀2개를 추가해 최종16개를 통과했다. 제한된 실행 환경에서는 junction 생성이 Access denied로 실패했고, 허용된 실행 환경에서 누락 없이16개를 완료했다. 이는 로컬Python3.15에서 구API조건을 재현한 검사이며 실제Python3.11 실행은 해당 원격 CI를 근거로 구분한다.
