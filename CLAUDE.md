# CLAUDE.md — CHUNG COMPANY / ADOS

## 먼저 읽을 것

코드를 쓰기 전에 `docs/00_AI_CONTEXT.md`를 기준으로 프로젝트를 이해한다.
전체 계획은 `docs/MASTER_PLAN.md`, 개발 규칙은 `docs/02_DEVELOPMENT_RULES.md`.

---

## 디자인 스킬 라우팅

이 저장소는 **웹 UI가 없는 파이썬 영상 파이프라인**이다 (HTML/CSS/JSX/package.json 0개).
웹 대시보드는 `docs/MASTER_PLAN.md` §27 Non Goals — v1.0에서 하지 않는다.

따라서 설치돼 있는 프론트엔드 스킬은 **기본적으로 쓰지 않는다.** 아래 표에 있는 것만 쓴다.

### 지금 쓰는 것

| 작업 | 쓸 스킬 | 대상 |
|---|---|---|
| 신규 채널 브랜드 정체성 확정 · 브랜드 보드 · 로고/컬러 시안 | `brandkit` | `channels/<id>/brand_profile.yaml`, `docs/10_BRAND_SYSTEM.md` |
| 썸네일 · 자막 번인 프레임 시각 검수 | `visual-critique:critique-visual-hierarchy`<br>`visual-critique:critique-typography`<br>`visual-critique:critique-color` | 채널 `assets/`, `config/subtitle_styles.yaml` |
| Midjourney · 경쟁 채널 브라우저 자동화 | playwright MCP / chrome-devtools MCP | `providers/`, `engines/research/` |

**visual-critique 사용 시 주의** — 원래 웹 화면용 스킬이다. 썸네일에 쓸 때는
WCAG 대비비·버튼/포커스링·상태색·정보밀도 항목은 **무시**하고,
시각 위계 · 타이포 · 팔레트 일관성 세 항목만 본다.
`critique-brand-consistency`는 `mood.md`/`voice.md`/`tokens.md`를 찾으므로 쓰지 않는다.
브랜드 일관성 기준은 `channels/<id>/brand_profile.yaml`이 유일한 근거다.

### 쓰지 않는 것 (대시보드 착수 전까지)

```text
frontend-design            design-taste-frontend
animate                    design-motion-principles
theme-factory              impeccable
ui-design:*                interaction-design:*
prototyping-testing:*      ux-strategy:*
design-research:*          design-ops:*
design-systems:*
```

붙일 화면이 없어서 잘못 발동하기만 한다. 웹 대시보드를 시작하는 시점에 이 목록을 해제한다.

대시보드의 진입 계약은 이미 존재한다 — `engines/project/project_view_builder.py`가
`ui/project_view.json`(render-neutral view model)을 생성하고, 프론트엔드는 이 파일 하나만 읽는다.
착수하게 되면 이 파일이 출발점이다.

### 영상 모션에는 프론트엔드 스킬을 쓰지 않는다

컷 전환·모션 그래픽·타이틀은 `hyperframes-animation`, `motion-graphics`, `media-use`를 쓴다.
`animate`와 `design-motion-principles`는 React/Framer Motion/CSS **UI 모션** 전용이라
영상 파이프라인에는 해당 없음.

### 설치하지 않은 것

- `impeccable` — `npx impeccable install`은 Node 프로젝트(package.json) 대상. 여기는 파이썬이라 설치 대상이 아니다.
- `figma-context` MCP — claude.ai Figma 커넥터가 이미 연결돼 있어 중복.

---

## 이미지·영상 스킬 라우팅

### 먼저: 스킬은 파이프라인에 꽂히지 않는다

ADOS의 외부 호출 경로는 **Engine → Provider Interface → Adapter** 하나뿐이다 (`providers/README.md`).
스킬과 MCP는 이 경로에 들어가지 않는다. 둘은 **Claude Code가 대화 중에 사람 대신 작업할 때만** 쓴다.
파이프라인이 자동으로 호출하게 하려면 `providers/`에 파이썬 adapter를 추가해야 한다.
이 구분을 흐리지 말 것.

### 지금 쓰는 것

| 작업 | 쓸 것 |
|---|---|
| 본편 컷 이미지 | Midjourney — `providers/midjourney_provider.py` (CDP 자동화). 채널 화풍이 `brand_profile.yaml`의 `locked_suffix`에 lock돼 있다 |
| 썸네일 그래픽 (텍스트 오버레이·카드형) | `canvas-design` 스킬 |
| 단발 이미지 생성·수정 (MJ 검열 회피, 부분 수정) | 힉스필드 MCP `generate_image` |
| 업스케일 · 배경 제거 · 아웃페인트 | 힉스필드 MCP `upscale_image` / `remove_background` / `outpaint_image` |
| 영상 합성 | `engines/composition/video_composer.py` (ffmpeg) |
| 코드 기반 모션·타이틀 | `hyperframes` 계열 스킬 |

### 설치하지 않는 것

- **nano-banana / banana-claude** — 힉스필드 MCP `generate_image`에 `nano_banana`,
  `nano_banana_2`, `nano_banana_pro`, `nano_banana_2_lite`가 이미 전부 있다.
  스킬을 깔면 별도 API 키와 과금 경로만 하나 더 생긴다.
- **remotion-superpowers / `npx create-video`** — 영상 프레임워크가 이미 둘이다
  (ffmpeg 합성 + hyperframes). 세 번째를 들이지 않는다.
- **blender-motion / aftereffects-motion** — Blender와 After Effects 본체가 이 PC에 없다.
  MCP만 붙여도 동작하지 않는다.
- **data 플러그인** — `dataviz` 스킬이 이미 있고, `engines/reporting`은 `run_report.json`만
  만든다. 차트 수요가 생기면 `dataviz`로 먼저 해본다.
- **algorithmic-art** — 채널 화풍이 실사 시네마틱 다큐다. 추상 패턴 배경은 쓰지 않는다.
- **svg-logo-designer** — `brand_profile.yaml`에 로고 필드가 아직 없다. 필요해지면 그때 판단하고,
  급하면 힉스필드 `recraft_v4_1`의 `model_type: vector`로 먼저 뽑아본다.

### 썸네일 경로

`providers/thumbnail_provider.py`의 `ThumbnailProvider.build_work_pack(brand_profile, content_strategy)`가
채널 `brand_profile.yaml`의 `thumbnail_style`과 `research/content_strategy.json`의
`thumbnail_hypotheses`를 하나의 수동 작업 팩으로 합친다. 이 둘은 그전까지 각각 생산만 되고
소비처가 없는 막다른 데이터였다.

이미지 자체는 여전히 사람이 만든다 — provider는 외부를 호출하지 않는다.
팩의 `brand_rules`를 읽고 `canvas-design` 또는 힉스필드 `generate_image`로 후보를 만든 뒤,
`ManualAssetImporter`로 등록하고 `AssetRegistry`에 연결한다.

근거가 없으면 팩을 만들지 않고 `ADOSValidationError`를 낸다. 빈 팩도, 지어낸 안도 만들지 않는다.

---

## 테스트 실행법

`tests/`에 `__init__.py`가 없어서 **`python -m unittest discover`는 실패한다.**
모듈 이름을 직접 넘긴다.

```bash
# 전체 (30개 모듈 · 391 테스트 · 약 65초)
python -m unittest $(ls tests/test_*.py | sed 's|tests/|tests.|; s|\.py$||')

# 하나만
python -m unittest tests.test_thumbnail_provider -v
```

pytest는 설치돼 있지 않다. 표준 `unittest`만 쓴다.
테스트가 실제로 필요로 하는 외부 패키지는 **PyYAML 하나뿐**이다 (clean venv로 실측).
`requirements.txt`의 requests·playwright·yt-dlp는 선택이며 테스트는 이들 없이 통과해야 한다.

`.github/workflows/tests.yml`이 push·PR마다 같은 명령을 ubuntu·windows에서 돌린다.

---

## 실패하는 테스트를 지워서 통과시키지 않는다

테스트가 깨지면 **먼저 계약이 깨진 건지 테스트가 낡은 건지 판별한다.**
`git show HEAD:<file>`로 커밋된 버전과 비교하면 대개 바로 갈린다.

- 계약이 깨진 경우 → 코드를 고친다. 테스트는 손대지 않는다.
- 테스트가 낡은 경우 → 지우기 전에, 그 테스트가 지키던 보장을 **무엇이 대신 지키는지** 먼저 세운다.

실제 사례 (2026-08-08): WIP가 `TypecastProvider`를 실제 API 호출용으로 갈아끼우며
`PlaceholderProvider` 상속을 떼어냈고, 테스트 2개가 `create_job` 없음으로 깨졌다.
테스트를 지우는 게 빨랐지만 그건 계약이 깨진 쪽이었다 — 수동 작업 팩 안내와
데모 스크립트도 같이 죽어 있었다. 계약을 복구하는 것이 정답이었다.

이 규칙은 `everything-claude-code`(ECC)의 `pre:config-protection` 훅에서 가져왔다.
훅 자체는 도입하지 않는다 (아래 참조).

---

## AI 설계·프롬프트·안전 스킬 — 도입하지 않는다

`Owl-Listener/ai-design-skills` 계열(model-interaction-design, design-agent-orchestration,
prompt-architecture, system-behavior-shaping, ai-alignment-reasoning, evaluation)은 **설치하지 않는다.**

이유는 "이미 있어서"가 아니라 **이 저장소의 확정된 설계와 충돌하기 때문**이다. 충돌 지점 셋:

1. **"Agent" 어휘 금지** — `employees/README.md`: *"ADOS에서는 'Agent'라는 단어를 쓰지 않는다.
   AI Employee를 사용한다."* `agent-role-design`은 금지된 어휘를 그대로 들여온다.

2. **자유 대화형 멀티에이전트 거부** — `templates/*/roles.yaml` 첫 줄:
   *"role은 책임과 권한을 표현한다 — 서로 자유롭게 대화하는 독립 AI 프로세스가 아니다.
   creative_workflow 단계만 AI 판단을 사용할 수 있고, 렌더링·파일 변환·자막·비용·상태 변경은
   deterministic code가 처리한다."* `agent-role-design`·`mixed-initiative-flow`·`handoff-protocols`는
   정확히 이 프로젝트가 기각한 모델을 권한다.

3. **임의 점수 생성 금지** — `templates/*/quality.yaml` 첫 줄:
   *"검증 근거가 없는 검사 항목은 UNASSESSED로 남는다 — 임의의 숫자 점수를 만들지 않는다."*
   `output-quality-rubrics`·`task-success-metrics`는 점수화를 권한다. 품질 게이트 점수 조작은
   이 프로젝트의 최상위 금지 사항이다.

나머지도 자리가 없다. `context-window-design`·`conversation-patterns`·`progressive-disclosure`·
`frustration-detection`·`feedback-loops`는 **최종 사용자와 대화하는 AI 제품**용인데,
ADOS는 챗봇이 아니라 내부 운영 시스템이고 사람 접점은 `scripts/ados.py` CLI와 승인 게이트뿐이다.
`generative-ui`는 웹 대시보드 Non-Goal과 충돌한다.
`persona-architecture`·`tone-calibration`은 채널 톤이 이미 `brand_profile.yaml`에 lock돼 있어 중복이다.

### 같은 일을 이미 하는 곳 (여기를 고쳐라)

| 이 목록의 스킬 | 이 저장소의 실제 구현 |
|---|---|
| agent-role-design | `templates/*/roles.yaml` (role_id · responsibility · allowed_step_kinds · can_approve · kpi · failure_conditions) |
| human-in-the-loop · escalation-design | `engines/review/human_review_engine.py`, `engines/workflow/executors.py` (WAITING_APPROVAL / APPROVE · REQUEST_REVISION · REJECT) |
| guardrail-design | `engines/workflow/executor_registry.py` allowlist, roles.yaml의 `can_trigger_external_action: false` |
| output-quality-rubrics · failure-taxonomy | `templates/*/quality.yaml` (rule_id · severity BLOCKER/MAJOR/MINOR), roles.yaml `failure_conditions` |
| trust-calibration · transparency-patterns | quality.yaml의 `UNASSESSED` 규칙 |
| system-prompt-structure · template-design | `engines/workflow/executors.py`의 work order `instructions` |

### 빈 폴더 두 개는 버그가 아니다

`prompts/`와 `employees/`는 README만 있는 빈 폴더인데, **의도된 상태다.** 각 README에 이유를 적어 뒀다.

`prompts/` — production 경로에 LLM adapter가 아직 없다. creative 단계는 프롬프트를 생성하지 않고
work order를 만들어 사람이 결과를 import한다. 채울 템플릿이 아직 없는 것.

`employees/` — `docs/04` §38이 제안하는 `base/`·`departments/`·`managers/` 구조는 미구현이고,
실제로 도는 역할 정의는 `templates/*/roles.yaml`이다.

**`executors.py`의 `CREATIVE_SPECS.instructions`를 `prompts/`로 빼내지 말 것.**
같은 dict의 키가 `build_default_registry()`에서 executor allowlist를 만들고,
`instructions`는 그 단계의 `schema`·`output_rel`과 한 계약을 이룬다.
분리하면 allowlist 경계가 데이터로 새고 계약이 두 곳으로 갈라진다.

---

## everything-claude-code (ECC) — 도입하지 않는다

`affaan-m/ECC` (구 `everything-claude-code`, 스타 23.8만·포크 3.6만). 규모와 활성도는 진짜지만 우리에겐 안 맞는다.

- **중복** — ECC의 핵심(TDD 게이트·계획·리뷰·검증)은 `superpowers`가, 세션 지속은
  `agentmemory`가 이미 차지하고 있다.
- **규모 역행** — 스킬 284개 + 에이전트 67개. designer-skills 86개를 덜어낸 직후에 정반대 방향이다.
- **스택 불일치** — 훅 상당수가 JS/TS 전용(`stop:format-typecheck`, `stop:check-console-log`)이고
  `stop:desktop-notify`는 macOS/WSL 전용인데 여기는 Windows다.
- **이름만 겹치는 도메인** — ECC의 `seo`는 웹 SEO(crawlability·canonical·sitemap·Core Web Vitals)로
  우리의 유튜브 메타데이터 SEO와 다르다. `video-editing`은 실사 푸티지 편집이라
  AI 이미지+TTS 합성인 우리 파이프라인과 다르고, `content-engine`은 소셜 포스팅이다.
- **공급망** — 훅은 매 도구 호출마다 서드파티 Node 스크립트를 조용히 실행한다.
  스타 수와는 별개의 고려사항이다.

가져온 것은 아이디어 하나뿐이다 — 위의 "실패하는 테스트를 지워서 통과시키지 않는다"
(ECC `pre:config-protection` 훅에서).
