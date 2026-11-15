# Vibe Coding Starter

[![Validate starter](https://github.com/CHOI-SEUNGPYO/vibe-coding-starter/actions/workflows/validate.yml/badge.svg)](https://github.com/CHOI-SEUNGPYO/vibe-coding-starter/actions/workflows/validate.yml)

**Codex에서 바로 쓰는 목적별 바이브코딩 환경.** 작업 규칙, 역할별 에이전트, 실제 스킬, MCP 연결 설정과 검증 도구가 들어 있습니다. 기본 `web` 환경의 `.codex`와 `.agents/skills`도 이미 적용된 상태로 제공합니다.

프레임워크나 모델 이름을 강제하지 않습니다. 현재 계정의 모델과 프로젝트의 기술 스택을 유지하고, 해야 할 일에 맞춰 환경을 고릅니다. 새 컴퓨터에서 필요한 작업은 의존성 복원과 본인 계정 인증입니다.

## 바로 시작하기

Git·Python **3.11+**·Node.js **22+**·Codex가 필요합니다. Windows에서 `python`이 Microsoft Store를 열면 `python3` 또는 `py -3`를 쓰세요.

1. 이 저장소의 **Use this template → Create a new repository**로 내 프로젝트를 만듭니다. 이 저장소의 변경을 추적하고 기여하려면 **Fork**를 사용합니다. 같은 계정에서 여러 프로젝트를 만들 때는 Template이 편합니다.
2. 만든 저장소를 clone하고 해당 폴더에서 아래 명령을 실행합니다.

```bash
python scripts/setup.py --profile web
```

이 명령이 프로필 적용 → 잠금 파일대로 MCP 설치 → Chromium 준비 → 설정·스킬 검사 → 공식 문서 검색·브라우저 조작 시험까지 실행합니다. 실패하면 성공이라고 표시하지 않습니다. Linux에서 브라우저 시스템 라이브러리가 부족하면 안내에 따라 `node node_modules/playwright/cli.js install --with-deps chromium`으로 준비합니다.

3. Codex에서 폴더를 열고 프로젝트를 신뢰한 뒤 새 채팅을 시작합니다. 모델은 계정에서 선택한 것을 사용합니다.
4. 원하는 기능을 말합니다. 에이전트가 `.vibe/project.json`의 목표·완료 조건·검사 명령을 **실제 앱에 맞게** 바꾸도록 함께 요청하세요. 처음 들어 있는 검사는 이 starter 자체를 검사합니다.

```text
$task-delivery로 독서 기록 웹앱을 만들어줘.
docs/environments.md의 웹 환경 사용 순서를 따라 레퍼런스를 먼저 확인해.
내가 읽은 책과 메모를 저장하고 검색할 수 있게 해줘.
프로젝트 목표와 실제 앱 검사 명령을 .vibe/project.json에 등록하고,
빈 목록·저장 실패·모바일 화면까지 Playwright로 확인해줘.
```

## 목적별로 어떻게 쓰나요?

환경을 바꿀 때도 `python scripts/setup.py --profile api`처럼 프로필 이름만 바꿉니다. 자세한 순서와 목적별 요청 예시는 [환경 사용 가이드](docs/environments.md)에 있습니다. 레퍼런스는 복제할 완성품이 아니라 정보 배치·사용 흐름·컴포넌트 동작을 비교할 근거로 사용합니다.

| 만들려는 것 | 환경 | 처음 볼 레퍼런스 | 진행 순서 |
| --- | --- | --- | --- |
| 랜딩 페이지·브랜드 사이트 | `web` | [Lapa Ninja](https://www.lapa.ninja/), [Landbook](https://land-book.com/), [Recent](https://recent.design/) | 사례 2~3개에서 레이아웃·타이포 선택 → 구현 → 모바일·CTA 흐름 확인 |
| SaaS·관리자·대시보드 | `web` | [Mobbin](https://mobbin.com/), [SaaSFrame](https://www.saasframe.io/), [shadcn/ui](https://ui.shadcn.com/) | 목록·검색·필터·빈 상태 비교 → 데이터 연결 → 실제 사용자 흐름 검사 |
| 백엔드·API | `api` | [OpenAPI](https://spec.openapis.org/oas/latest.html), [Swagger 예제](https://petstore.swagger.io/) | 입력·응답 계약 확인 → 구현 → 권한·실패·통합 테스트; 관리 화면이 필요하면 웹 레퍼런스도 사용 |
| 데이터 분석·시각화 | `data` | [Observable Plot](https://observablehq.com/plot/), [Vega-Lite 예제](https://vega.github.io/vega-lite/examples/) | 질문에 맞는 차트 선택 → 스키마·누락 확인 → 분석 → 지표·축·재현성 검증 |
| 업무·브라우저 자동화 | `automation` | [n8n 워크플로 사례](https://n8n.io/workflows/), [Mobbin](https://mobbin.com/) | 입력·분기·결과 흐름 조사 → dry-run → 재실행·실패 복구 확인 |
| 작은 수정·CLI·기존 코드 조사 | `minimal` | 해당 도구 공식 문서; UI 수정이면 [Radix Primitives](https://www.radix-ui.com/primitives) | 실패 재현 → 최소 수정 → 변경된 동작 확인 |

디자인 사이트별 특징, 공개 범위와 선택 기준은 [디자인 레퍼런스 가이드](docs/design-references.md)를 참고하세요. 유료·로그인 전용 화면의 접근 권한은 이 저장소에 포함되지 않습니다.

## 이미 들어 있는 구성

| 구성 | 실제 파일 | 하는 일 |
| --- | --- | --- |
| 작업 하네스 | [AGENTS.md](AGENTS.md), [.vibe/project.json](.vibe/project.json) | 요청 범위, 완료 조건, 검증 명령과 결과 기준 |
| Codex 설정 | [.codex/config.toml](.codex/config.toml) | 프로젝트 범위 권한, 필요 시 승인, MCP 연결 |
| 오케스트레이션 | [.codex/agents](.codex/agents), [운영 방식](docs/orchestration.md) | 주 에이전트 + 조사·검토·테스트 보조 최대 3개; 파일 담당 분리 |
| 활성 스킬 | [.agents/skills](.agents/skills) | 현재 web 프로필의 실제 발견 경로 |
| 전체 스킬 원본 | [skills](skills), [skills.lock.json](skills.lock.json) | 프로필별 설치 원본, 출처·고정 커밋·파일 해시 |
| MCP 설정 | [mcp](mcp), [연결 가이드](docs/mcp.md) | 공식 문서 검색, 격리된 브라우저 자동화, 선택적 GitHub 연결 |
| 검증과 CI | [scripts](scripts), [GitHub Actions](.github/workflows/validate.yml) | 파일 보존·환경 전환·오류 처리·스킬 무결성·실제 브라우저 검사 |

에이전트 역할은 작업 분담 지침입니다. 별도 OS 권한 격리를 만들지 않으며, 실제 권한은 부모 세션과 조직 정책을 따릅니다. 작은 작업은 주 에이전트가 직접 처리합니다.

## 어떤 스킬을 가져왔나요?

| 스킬 | 출처 | 쓰는 상황 | 포함 프로필 |
| --- | --- | --- | --- |
| `task-delivery` | 이 저장소에서 작성 · MIT | 요청을 완료 조건·구현·검증으로 연결 | 전체 |
| `parallel-work` | 이 저장소에서 작성 · MIT | 독립 작업 분담, 파일 충돌 방지, 결과 통합 | 전체 |
| `release-check` | 이 저장소에서 작성 · MIT | 게시 범위·검사·원격 결과 확인 | 전체 |
| `playwright` | [OpenAI 공식 스킬](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/playwright) · Apache-2.0 | 브라우저 조작·UI 확인의 작업 절차 | web, automation |
| `gh-fix-ci` | [OpenAI 공식 스킬](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/gh-fix-ci) · Apache-2.0 | 실패한 GitHub Actions 원인 조사·수정 | web, api |
| `gh-address-comments` | [OpenAI 공식 스킬](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/gh-address-comments) · Apache-2.0 | PR 리뷰 의견 확인·반영 | automation |

외부 스킬은 **`49f948faa9258a0c61caceaf225e179651397431`**의 원본을 가져왔으며 라이선스와 NOTICE를 보존했습니다. 전역 설치된 유료 플러그인이나 개인 스킬을 복사하지 않았습니다. [출처·호환성 설명](docs/skills.md), [외부 라이선스](THIRD_PARTY_NOTICES.md)

원본 Playwright 스킬의 Bash CLI와 이 저장소의 Playwright MCP는 별개입니다. Windows에서는 구성된 MCP를 우선합니다. `gh-*`의 CLI 절차에는 GitHub CLI 설치·로그인이 필요하며, 연결된 GitHub 앱이 있으면 그 도구를 먼저 사용합니다. 이 저장소에 계정 인증 정보는 없습니다.

## MCP는 어디까지 준비되어 있나요?

- **OpenAI Docs:** 키 없이 사용하는 공식 검색 서버. web/api/data/automation에서 활성화합니다.
- **Playwright:** `@playwright/mcp@0.0.85`와 의존성을 고정했습니다. web/automation에서 격리 Chromium을 실행합니다.
- **GitHub:** 현재 Codex에 연결한 GitHub 앱을 우선합니다. 별도 CLI용 원격 MCP 설정도 포함되어 있으며 읽기 전용입니다. 본인 토큰이 필요한 선택 연결이므로 기본으로 켜지 않습니다.

GitHub·배포 서비스·DB의 계정 권한은 fork로 전달되지 않습니다. 사용자의 현재 연결이나 본인 인증을 사용합니다. 추가 MCP는 작업에 필요한 것만 연결합니다. [설정·인증·문제 해결](docs/mcp.md)

## 검사·전환·기존 프로젝트에 적용

```bash
# 현재 환경의 실제 검사 실행
python scripts/vibe.py verify

# MCP 서버의 실제 문서 검색 + 브라우저 조작 시험
node scripts/check_mcp.mjs

# 변경될 파일을 먼저 확인하고 프로필 전환
python scripts/vibe.py init --profile data --dry-run
python scripts/setup.py --profile data

# 기존 프로젝트에 적용하기: 기존 파일과 충돌하면 변경 전에 중단
python scripts/vibe.py init --profile api --target ../my-existing-project --dry-run
python scripts/vibe.py init --profile api --target ../my-existing-project
```

`init`은 파일을 적용하며 네트워크 설치는 하지 않습니다. `setup.py`는 이 starter 안에서 의존성 복원과 실제 연결 검증까지 실행합니다. 기존 프로젝트에 `--target`으로 적용할 때는 해당 프로젝트의 런타임과 검증 명령을 유지하고, 웹 프로필은 대상에서 Node·Chromium도 준비해야 합니다. 상세 내용은 [환경 사용 가이드](docs/environments.md)를 따릅니다.

`--update`는 관리 중인 파일이 이전 설치 해시와 같을 때만 바꿉니다. 직접 수정한 설정과 기존 `AGENTS.md`는 자동 덮어쓰기하지 않습니다. `.vibe/project.json`도 보존합니다. 검사 명령이 비어 있으면 `verify`는 실패합니다.

원본 스킬을 추가·수정하면 해당 프로필과 lock도 함께 갱신해야 합니다. 무결성 검사는 목록에 없는 스킬이나 바뀐 파일도 감지합니다. 이 검사는 저장소 내부 일관성을 확인하며 외부 작성자의 신원을 암호학적으로 인증하는 서명은 아닙니다.

## 검증 범위와 유지보수

설정은 **2026-11-15 / Codex CLI 0.169.0-alpha.11.1**에서 확인했습니다. 확인하지 않은 모델 ID는 고정하지 않았습니다. 새 버전에서 설정 형식이 바뀌면 공식 문서와 실제 설정 로딩 결과를 먼저 확인합니다.

CI는 Windows·macOS·Linux에서 Python 하네스 검사를 실행하고 Linux에서 실제 Chromium MCP 흐름을 실행합니다. 외부 Docs 서버 검사는 수동 온라인 검사에 포함해 네트워크 장애가 코드 회귀와 섞이지 않게 했습니다. [검증 기록](docs/verification.md)

설정과 스킬을 먼저 읽고 사용할 프로젝트를 신뢰하세요. 검사 명령은 실제 프로그램을 실행합니다. 비밀키·토큰·회사 원본·개인 데이터는 커밋하지 않습니다. 자체 파일은 [MIT](LICENSE), 가져온 스킬은 각 원본 라이선스를 따릅니다.
