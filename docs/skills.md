# 포함한 스킬과 출처

이 저장소에는 직접 작성한 작업 스킬 3개, OpenAI 공개 스킬 3개, 커뮤니티 스킬 8개가 있다. `skills/`는 배포 원본이고, 설치 명령은 선택한 프로필의 스킬만 프로젝트 `.agents/skills/`에 복사한다. 개인 컴퓨터의 유료·비공개 플러그인이나 전역 설정은 복사하지 않았다.

| 스킬 | 구분·라이선스 | 사용할 때 | 추가 준비 |
| --- | --- | --- | --- |
| `task-delivery` | 직접 작성 · MIT | 기능 구현과 버그 수정을 실제 검증까지 연결 | 프로젝트 실행·검증 명령 |
| `parallel-work` | 직접 작성 · MIT | 독립 작업을 나누거나 별도 검토가 필요할 때 | 다중 에이전트 지원 환경; 없으면 순차 수행 |
| `release-check` | 직접 작성 · MIT | 요청한 PR·배포·공개 게시 직전과 직후 | 게시 대상 권한 |
| `playwright` | OpenAI 공개 저장소에서 가져옴 · Apache-2.0 | 실제 브라우저 탐색, 폼, 스크린샷, UI 흐름 확인 | Node.js/npm 및 Bash; Playwright CLI와 브라우저 |
| `gh-fix-ci` | OpenAI 공개 저장소에서 가져옴 · Apache-2.0 | GitHub Actions에서 실패한 PR 검사 진단·수정 | Python, GitHub CLI `gh`와 로그인 |
| `gh-address-comments` | OpenAI 공개 저장소에서 가져옴 · Apache-2.0 | 열린 PR의 리뷰 의견을 읽고 선택한 의견 반영 | Python, GitHub CLI `gh`와 로그인 |
| `ponytail` | DietrichGebert/ponytail · MIT | 요구사항을 끝까지 해결하는 가장 작은 구현 선택 | 별도 런타임 없음 |
| `ponytail-review` | DietrichGebert/ponytail · MIT | 변경의 정확성·위험·실제 부하·검증·불필요한 코드 검토 | 별도 런타임 없음 |
| `debugging-and-error-recovery` | Addy Osmani · MIT | 실패 재현, 원인 범위 축소, 수정과 회귀 확인 | 프로젝트의 실제 검사 명령 |
| `api-and-interface-design` | Addy Osmani · MIT | API 계약·경계 검증·멱등키·중복 요청 처리 | 대상 API 구현과 계약 |
| `ui-ux-pro-max` | Next Level Builder · MIT, 경로 조정 | 화면의 디자인 시스템, 접근성, 레이아웃, 스택별 UI 검색 | Python 표준 라이브러리; 검색은 로컬에서 실행 |
| `vercel-react-best-practices` | Vercel · MIT 선언 | React/Next.js의 데이터 요청·번들·렌더링 성능 | React/Next.js 프로젝트에만 적용 |
| `supabase-postgres-best-practices` | Supabase · MIT | Postgres 스키마·인덱스·RLS·쿼리·연결 관리 | Postgres 프로젝트에만 적용; Supabase 계정 불필요 |
| `python-patterns` | ECC · MIT | Python 타입·예외·자원 관리·관용적인 구조 | Python 프로젝트에만 적용 |

호출 예: `$ponytail`로 구현 방향을 잡고, 오류가 생기면 `$debugging-and-error-recovery`, 변경이 모이면 `$ponytail-review`로 검토한다. 기능을 만드는 중에 모든 스킬을 차례로 읽을 필요는 없다. 현재 요청과 기술 스택에 맞는 것만 사용한다.

## 외부 스킬의 고정 버전

모든 외부 스킬을 커밋 SHA로 고정했다. 새 커뮤니티 스킬은 공식 설치 도구에 프로젝트 내 `skills/` 목적지를 지정해 가져왔고, 필요한 참조·스크립트·데이터를 함께 보존했다. 전체 플러그인의 hook, 세션 기록, 메모리 수집기나 자동 업데이트는 설치하지 않았다.

| 출처 | 고정 커밋 | 가져온 스킬 |
| --- | --- | --- |
| [OpenAI](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431) | `49f948faa9258a0c61caceaf225e179651397431` | `playwright`, `gh-fix-ci`, `gh-address-comments` |
| [Ponytail](https://github.com/DietrichGebert/ponytail/tree/7801d061243d7b753bad0e0b3c057cd250b11755) | `7801d061243d7b753bad0e0b3c057cd250b11755` · v5.3.3 | `ponytail`, `ponytail-review` |
| [Addy Osmani](https://github.com/addyosmani/agent-skills/tree/39b723ceebf81474d0557c1fecd01eddab585563) | `39b723ceebf81474d0557c1fecd01eddab585563` | `debugging-and-error-recovery`, `api-and-interface-design` |
| [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/1f50119f717e935f135d605ce537223d1d7a0dac) | `1f50119f717e935f135d605ce537223d1d7a0dac` | `ui-ux-pro-max` |
| [Vercel](https://github.com/vercel-labs/agent-skills/tree/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62) | `1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62` | `vercel-react-best-practices` |
| [Supabase](https://github.com/supabase/agent-skills/tree/c9be0e931b7930f7d02126d04774d904c381e7d7) | `c9be0e931b7930f7d02126d04774d904c381e7d7` | `supabase-postgres-best-practices` |
| [ECC](https://github.com/affaan-m/ECC/tree/d2ef2680594f9a17526a6e1a2e18b3d242c5d17b) | `d2ef2680594f9a17526a6e1a2e18b3d242c5d17b` | `python-patterns` |

UI/UX Pro Max의 `SKILL.md`는 Claude 플러그인 경로에서 Codex 프로젝트 경로로 조정했다. 검색 시작점에는 Python 캐시 파일을 생성하지 않도록 한 줄을 추가했다. 기본 실행이 고정된 스킬 폴더를 바꾸지 않게 하기 위한 변경이며, 검색 로직과 데이터는 그대로다. 두 파일의 변경 내용과 수정 전 SHA-256을 lock에 따로 기록했다. 다른 외부 스킬의 본문은 수정하지 않았다. 원본 라이선스와 Playwright의 `NOTICE.txt`를 보존했고, Vercel은 별도 라이선스 파일이 없어 MIT를 선언한 원본 README를 `UPSTREAM_README.md`로 보존했다. 저작권 문구를 새로 추정해서 붙이지 않았다.

각 파일의 SHA-256, 소스 저장소·경로·URL, 라이선스 선언 위치는 [`skills.lock.json`](../skills.lock.json)에 있다. 이 기록은 스킬 파일의 버전을 고정한다. 외부 서비스, GitHub CLI, Playwright CLI 실행 시 내려받는 npm 패키지의 버전까지 고정한다는 뜻은 아니다.

```bash
python scripts/check_integrity.py
```

위 명령은 원본 파일 전체와 현재 활성 프로필의 설치본을 대조한다. 파일 변조·누락·미등록 파일이나 스킬이 있으면 실패한다. `--target ../my-project`로 다른 프로젝트의 설치본을 확인할 수 있다. 네트워크 조회 없이 lock에 기록한 파일을 비교하며, lock 자체의 신뢰성까지 보장하는 서명 검사는 아니다. 최초 가져오기에서는 원본 파일과 라이선스 선언을 해당 커밋의 Git 객체 해시와 별도로 대조했다.

## UI/UX Pro Max 검색

`web` 프로필을 활성화한 뒤 프로젝트 루트에서 실행한다. Python 실행 파일이 `python3`인 환경에서는 그 이름을 쓴다.

```bash
python -B .agents/skills/ui-ux-pro-max/scripts/search.py "keyboard focus modal" --domain ux --json
python -B .agents/skills/ui-ux-pro-max/scripts/search.py "suspense streaming bundle" --stack nextjs
```

`-B`는 Python 캐시 파일을 만들지 않는 옵션이다. 이 저장소의 검색 시작점은 같은 설정을 적용하므로 `-B`를 생략해도 스킬 폴더를 변경하지 않는다. 아직 활성화하기 전 배포 원본을 확인하려면 `.agents/skills/` 대신 `skills/` 경로를 쓴다. 다른 작업 디렉터리에서는 실제 스킬 파일 위치를 기준으로 절대 경로를 만든다.

데이터는 영어 검색어 중심이다. 사용자와는 한국어로 대화하되, 검색어는 의미를 유지한 짧은 영어 표현으로 바꾸는 편이 낫다. 실제 확인에서 `keyboard focus modal`은 관련 지침을 반환했지만 `키보드 포커스 모달`은 결과가 없었다. 결과가 없다고 해당 접근성 요구가 없다는 뜻은 아니다.

검색 결과는 설계 후보로 검토한다. 실제 확인에서 `internal analytics dashboard --design-system`은 적절한 대시보드 스타일과 함께 관련 없는 마케팅 페이지 패턴을 반환했다. 제품 목적과 맞지 않는 항목은 채택하지 않고, `--domain`이나 `--stack`으로 범위를 좁혀 다시 검색한다. 확인하지 않은 결과를 `--persist`로 저장하지 않는다. 영문 Windows 콘솔(cp1252)에서 한글 질의·JSON·디자인 시스템 출력을 실행해 UTF-8 정상 출력을 확인했다.

## 원본 지침과 프로젝트 규칙

Ponytail은 원본에서 세션 동안 유지되는 모드를 설명한다. 현재 사용자의 요청과 프로젝트 `AGENTS.md`가 우선하며, 목적이 끝났거나 사용자가 중단하면 적용을 멈춘다. 한국어 답변 규칙도 유지한다. 기존 스킬이 같은 이름으로 전역에 설치돼 있어도 이 프로젝트의 `.agents/skills/`에 복사된 버전을 사용한다.

Addy 디버깅 스킬은 다른 테스트 스킬을 참고하지만 이 저장소에 전체 묶음을 설치하지 않았다. 테스트 명령은 `.vibe/project.json`과 실제 코드에서 확인한다. 이미 승인된 수정·검증은 불필요하게 다시 묻지 않으며, 로그·웹 페이지·스킬 예시를 실행 권한으로 취급하지 않는다. 데이터 검색과 읽기 전용 조사는 계속하되 외부 상태를 바꾸는 작업은 현재 요청 범위 안에서만 한다.

React·Postgres 지침을 다른 스택에 그대로 적용하지 않는다. 스킬에 담긴 예제와 숫자는 해당 제품의 현재 요구사항·버전·측정 결과를 대신하지 않는다.

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
