# 독서 기록 화면의 선택 근거

2026-11-16에 접근 가능한 공개 페이지를 확인했습니다. 읽고 싶은 책과 읽는 책을 찾고, 한 권의 기록을 남기는 흐름을 우선했습니다.

## 공개 사례 비교

| 확인한 페이지 | 관찰한 요소 | 앱에 적용한 요소 |
| --- | --- | --- |
| [SaaSFrame Search](https://www.saasframe.io/patterns/search) | 공개 가이드의 Claude 초기 검색 목록과 Lightdash의 검색어 아래 필터·그룹 사례. 필터를 검색 가까이에 두고 검색 범위를 명확히 설명함 | 제목·저자라고 명시한 검색창, 바로 옆 상태 필터, 조건 초기화. 해당 서비스의 내부 검색 알고리즘·키보드 동작은 추정하지 않음 |
| [SaaSFrame Empty State](https://www.saasframe.io/patterns/empty-state) | 빈 화면에 설명과 다음 행동을 함께 둔 공개 가이드. 일부 상세 사례는 유료이며 개별 공개 예시 링크 조회도 실패함 | 처음 들어온 빈 서재와 검색 결과 없음의 문구·버튼을 분리 |
| [shadcn/ui Empty](https://ui.shadcn.com/docs/components/base/empty) | 공개 No Projects Yet 예시의 제목, 설명, 생성 버튼 구성 | 첫 책 기록 버튼을 빈 서재 안에 배치. UI 패키지를 추가하지 않고 같은 구조를 일반 HTML로 구현 |

[Mobbin 홈](https://mobbin.com/)과 [Discover](https://mobbin.com/discover)는 열었으나 이번 조회에서 개별 제품 화면 본문을 확인할 수 없었습니다. 로그인·구독을 시도하지 않았고 공개 shadcn 예시로 보완했습니다. SaaSFrame의 `latent-datasets-upload`, `caveman-code-new-chat` 상세 조회는 `Cache miss`라서 확인한 개별 화면으로 계산하지 않았습니다.

## UI UX Pro Max 비교

실제 로컬 검색:

```powershell
python .agents/skills/ui-ux-pro-max/scripts/search.py "personal reading library calm editorial" --design-system -p "책갈피"
python .agents/skills/ui-ux-pro-max/scripts/search.py "minimal editorial dashboard" --domain style
python .agents/skills/ui-ux-pro-max/scripts/search.py "empty states search filters" --domain ux
python .agents/skills/ui-ux-pro-max/scripts/search.py "forms state local storage" --stack react
```

첫 디자인 시스템의 Hero + Testimonials 추천은 개인용 기록 화면에 맞지 않아 채택하지 않았습니다. style 도메인으로 좁힌 Minimalism & Swiss Style의 명확한 그리드·여백·위계와 ux 결과의 빈 상태 안내, 검색 결과 없음의 복구 경로를 적용했습니다. 독서 서비스에 어울리는 따뜻한 바탕·갈색 액션·절제된 녹색 상태를 사용하고 영문 전용 추천 폰트 대신 한국어 시스템 글꼴을 사용했습니다.

서재는 넓은 화면에서 2열, 휴대전화에서 1열입니다. 검색과 필터는 작은 화면에서 줄을 나눕니다. 최소 44px 터치 영역, 보이는 포커스, 화면 읽기용 레이블, native dialog의 Escape와 포커스 제한을 사용합니다. 애니메이션은 최소화하고 움직임 감소 설정을 따릅니다. 외부 이미지·폰트 요청은 없으며 표지 형태는 직접 만든 CSS 장식입니다.

## 패키지와 공식 문서

공개 npm 메타데이터에서 확인하고 앱 lockfile에 고정한 버전은 React 19.3.1, Vite 8.3.8, TypeScript 7.0.2, Vitest 5.1.0입니다. jsdom 31.0.1의 조건까지 합친 Node 지원 범위는 `^22.22.2 || ^24.15.0 || >=26.0.0`입니다. Node 24.22.1에서 실제 설치·타입 검사·테스트·빌드를 확인했습니다.

- [Vite 설치·Node 호환성과 React TypeScript 템플릿](https://vite.dev/guide/)
- [React 19.3 useState와 순수 초기화 함수](https://react.dev/reference/react/useState)
- [Vitest 5 설치와 단발 실행 명령](https://vitest.dev/guide/)

프로젝트 React 지침에 따라 파생 목록·개수는 렌더링 때 계산하고 localStorage에는 버전 키와 필요한 필드만 저장합니다. 저장은 effect가 아닌 사용자 저장 이벤트에서 수행합니다. 별도 상태 관리, 서버, UI 프레임워크는 추가하지 않았습니다.
