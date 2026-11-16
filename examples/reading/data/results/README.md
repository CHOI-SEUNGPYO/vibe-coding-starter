# data 예제 결과

모든 결과는 [공개 가상 샘플](../samples/reading-log.csv)12건에서 생성했다. 실제 개인 CSV를 포함하지 않는다.

- [report.md](report.md): 한국어 해석과 지표의 한계
- [reading-summary.png](reading-summary.png): 월별 완독과 상태별 기록 차트
- [summary.json](summary.json): 지표·분모·원본 해시
- [monthly.csv](monthly.csv), [status.csv](status.csv): 검산 가능한 집계표

정답은 **전체12건 / 완독7건 / 완독한 책2,000쪽 / 평점을 남긴 완독6건 / 평균4.333점**이다. 2026년1~6월 완독 수는2·0·2·0·2·1이다. 재독은 별도 기록으로 세며 읽는 중인 책의 평점은 완독 평균에서 제외한다.

2026-11-16, Windows·Python3.15.2에서 공개본에 새 `.venv`를 만들고 잠금 의존성을 설치했다. **테스트18개와 pip check를 통과**했고, 아래 명령을 실제 실행해 결과를 다시 만들었다.

```powershell
examples/reading/data/.venv/Scripts/python.exe examples/reading/data/analyze.py --input examples/reading/data/samples/reading-log.csv --output examples/reading/data/output/publish-lf
```

게시 준비 중 Windows의 기본 줄바꿈과 Git의 LF 정규화가 달라질 수 있음을 확인해 JSON·CSV·보고서는 LF로 저장하도록 고정했다. 위 명령으로 다시 생성한5개 파일을 이 폴더에 반영하고 바이트 일치를 확인했으며18개 테스트도 다시 통과했다. 같은 실행 환경에서 일치하며 서로 다른 OS·렌더러 버전의 PNG 바이트 일치까지 보장하지 않는다. 한글·축·빈 달과 수치는 원본 결과와 같다.

최초 data 실습의 독립 CLI34개 항목과 이미지 확인은 별도 폴더에서 수행한 이력이다. 이번 공개본에서 다시 실행한 검사는 위18개와 실제 분석·결과 비교다. 대용량 처리·예측 모델·인과 분석은 포함하지 않는다.
