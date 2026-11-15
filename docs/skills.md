# 포함한 스킬과 출처

이 저장소는 직접 작성한 작업 스킬 3개와 공개된 OpenAI 스킬 3개를 포함한다. 개인 컴퓨터에 설치된 유료·비공개 플러그인을 복사하지 않았다. `skills/`는 배포 원본이고, 설치 명령이 선택한 스킬만 프로젝트의 `.agents/skills/`에 복사한다.

| 스킬 | 구분·라이선스 | 사용할 때 | 추가 준비 |
| --- | --- | --- | --- |
| `task-delivery` | 직접 작성 · MIT | 기능 구현과 버그 수정을 실제 검증까지 연결 | 프로젝트 실행·검증 명령 |
| `parallel-work` | 직접 작성 · MIT | 독립 작업을 나누거나 별도 검토가 필요할 때 | 다중 에이전트 지원 환경; 없으면 순차 수행 |
| `release-check` | 직접 작성 · MIT | 요청한 PR·배포·공개 게시 직전과 직후 | 게시 대상 권한 |
| `playwright` | OpenAI 공개 저장소에서 가져옴 · Apache-2.0 | 실제 브라우저 탐색, 폼, 스크린샷, UI 흐름 확인 | Node.js/npm 및 Bash; Playwright CLI와 브라우저 |
| `gh-fix-ci` | OpenAI 공개 저장소에서 가져옴 · Apache-2.0 | GitHub Actions에서 실패한 PR 검사 진단·수정 | Python, GitHub CLI `gh`와 로그인 |
| `gh-address-comments` | OpenAI 공개 저장소에서 가져옴 · Apache-2.0 | 열린 PR의 리뷰 의견을 읽고 선택한 의견 반영 | Python, GitHub CLI `gh`와 로그인 |

## 외부 스킬의 고정 버전

세 스킬은 [openai/skills의 고정 커밋](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated) `49f948faa9258a0c61caceaf225e179651397431`에서 가져왔다. 원본 디렉터리의 스크립트·참조 문서·이미지·라이선스를 함께 유지했다. Playwright의 `NOTICE.txt`도 보존했다. 다운로드한 파일은 수정하지 않았다.

각 파일의 SHA-256, 소스 URL, 라이선스는 [`skills.lock.json`](../skills.lock.json)에 있다. 이 기록은 스킬 파일의 버전을 고정한다. 외부 서비스, GitHub CLI, Playwright CLI 실행 시 내려받는 npm 패키지의 버전까지 고정한다는 뜻은 아니다.

```bash
python scripts/check_integrity.py
```

위 명령은 원본 파일 전체와 현재 활성 프로필의 설치본을 대조한다. 파일 변조·누락·미등록 파일이나 스킬이 있으면 실패한다. `--target ../my-project`로 다른 프로젝트의 설치본을 확인할 수 있다. 네트워크 조회 없이 lock에 기록한 파일을 비교하며, lock 자체의 신뢰성까지 보장하는 서명 검사는 아니다. 최초 가져오기에서는 외부 21개 파일을 공식 커밋의 Git 객체 해시와 별도로 대조했다.

## 프로젝트 경로와 Windows

가져온 Playwright 스킬은 사용자 전체 설치 경로인 `~/.codex/skills/playwright`와 Bash 래퍼를 예시로 사용한다. 이 저장소에서 설치한 경로는 `<프로젝트>/.agents/skills/playwright`이므로 **실제로 설치된 경로를 사용**한다. 이 경로 차이는 프로젝트 `AGENTS.md`에도 안내한다.

Git Bash 또는 WSL에서 프로젝트 루트를 기준으로 실행할 수 있다.

```bash
bash .agents/skills/playwright/scripts/playwright_cli.sh --help
```

PowerShell만 사용하는 환경에서는 [Playwright MCP 설정](mcp.md)을 선택할 수 있다. CLI 스킬과 MCP는 서로 다른 인터페이스다. `playwright-cli`의 `e12` 같은 참조를 MCP 호출에 그대로 넘기지 않는다. 현재 사용하는 도구에서 얻은 화면 상태와 참조를 따른다.

원본 Bash 래퍼는 `npx --package @playwright/cli`로 CLI를 실행하며 패키지 버전이 고정되어 있지 않다. 반복 가능한 브라우저 실행 환경이 필요하면 검증한 CLI 버전을 프로젝트의 lockfile로 관리하거나, 이 저장소에서 제공하는 버전 고정 MCP 구성을 사용한다. 설치 도구는 이 스킬을 복사할 뿐 Node.js, npm 패키지나 브라우저를 자동 설치하지 않는다.

`gh` 기반 스킬은 Codex의 GitHub 플러그인 로그인과 별개로 GitHub CLI 인증을 사용한다. `gh auth status`로 확인하고, 필요할 때 직접 `gh auth login`을 진행한다. 토큰을 저장소 파일에 쓰지 않는다. 원본 스킬의 계획 확인·리뷰 의견 선택 단계는 실제 작업 범위를 정하는 데 사용하되, 사용자가 이미 지정한 범위와 승인은 반복해서 묻지 않는다.

## 추가·업데이트

1. 필요한 작업이 현재 스킬로 해결되는지 먼저 본다. 설명만 비슷한 스킬을 여러 개 설치하지 않는다.
2. 외부 스킬은 소스의 라이선스와 실행 스크립트를 먼저 읽고, 태그나 브랜치 대신 커밋 SHA를 기록한다.
3. 관련 파일 전체와 라이선스·NOTICE를 가져온다. 원본을 수정했다면 수정 사실과 변경 내용을 남긴다.
4. `skills.lock.json`의 파일 해시를 갱신하고, 해당 프로필의 설치·검증을 다시 실행한다.
5. README와 이 목록에서 실제 포함된 스킬, 선택 설치 스킬, 외부 도구 의존성을 구분한다.

직접 작성한 스킬을 수정할 때는 사용자의 작업 범위를 넓히지 않는지, 불필요한 승인이나 고정 순서를 만들지 않는지 함께 검토한다. 스킬의 설명은 언제 적용할지 판단할 수 있을 만큼 구체적으로 유지한다.
