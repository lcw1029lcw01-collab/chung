# 21_VISUAL_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Visual Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Visual Engine을 정의한다.

Visual Engine은 Timeline과 Direction을 기반으로 각 Scene에 필요한 이미지 제작 지시, Midjourney Prompt, Visual Asset Plan, Visual Review를 생성하는 엔진이다.

Visual Engine은 이미지를 직접 생성하지 않는다.

Visual Engine은 다음을 담당한다.

```text
Timeline 로드
Direction 로드
Brand Visual Rule 로드
Scene별 Visual Requirement 분석
Scene별 이미지 Prompt 생성
Midjourney용 Prompt Package 생성
Negative / Avoid Rule 적용
Scene ID와 Image Asset 연결 계획 생성
Manual Provider Workflow 준비
Provider Engine에 Visual Request 전달
Visual Result 등록 확인
Visual Review 생성
Visual Quality Issue 기록
Motion Engine에 Source Image 기준 제공
Editing Engine에 Visual Asset 기준 제공
```

이 문서는 다음 문서들과 직접 연결된다.

```text
07_PROJECT_SPEC.md
10_BRAND_SYSTEM.md
12_PROJECT_ENGINE.md
14_PROVIDER_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
16_TIMELINE_ENGINE.md
20_DIRECTION_ENGINE.md
22_MOTION_ENGINE.md
25_EDITING_ENGINE.md
26_QUALITY_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Visual Engine은 영상의 장면별 시각 자산을 설계하는 엔진이다.

전체 흐름:

```text
Direction
↓
Timeline
↓
Visual Engine
↓
Visual Prompts
↓
Provider Engine
↓
Midjourney
↓
Image Assets
↓
Visual Review
↓
Motion / Editing / Quality
```

Visual Engine의 핵심 목표는 다음이다.

```text
각 Scene의 목적에 맞는 이미지 방향을 만든다.
Brand와 Channel Tone을 유지한다.
Midjourney에서 사용할 수 있는 구체적인 Prompt를 만든다.
Scene ID와 이미지 파일을 안정적으로 연결한다.
Generic AI Look을 피한다.
Motion Engine이 사용할 Source Image를 준비한다.
Quality Engine이 검사할 수 있는 Visual 구조를 만든다.
```

---

# 3. Visual Philosophy

## 3.1 Visuals Must Serve Story

이미지는 예쁘기만 하면 안 된다.

각 이미지는 Story와 Scene Purpose를 수행해야 한다.

나쁜 Visual:

```text
멋진 미래 도시
멋진 사람
AI 느낌
우주 배경
```

좋은 Visual:

```text
SC001 Hook Scene:
A quiet futuristic settlement under alien sunlight, a small human silhouette in the foreground, cinematic wide shot, mysterious and reflective mood, grounded speculative science tone.
```

## 3.2 Avoid Generic AI Look

Visual Engine은 흔한 AI 이미지 느낌을 피해야 한다.

피해야 할 것:

```text
generic sci-fi city
random glowing robot
overly smooth plastic skin
meaningless neon background
text on image
watermark
logo
distorted anatomy
cheap fantasy look
```

## 3.3 Scene ID Is Sacred

Visual Engine은 Timeline의 Scene ID를 변경하지 않는다.

Visual Prompt, Asset, Review는 반드시 Scene ID와 연결되어야 한다.

## 3.4 Provider Independent

Visual Engine은 Midjourney를 직접 실행하지 않는다.

반드시 Provider Engine을 통해 Request를 만든다.

```text
Visual Engine
↓
Provider Engine
↓
VisualProviderInterface
↓
MidjourneyAdapter
```

---

# 4. Visual Engine Responsibilities

Visual Engine의 책임:

```text
Timeline Context 로드
Direction Output 로드
Brand Visual Rule 로드
Visual Memory 로드
Scene별 Visual Requirement 확인
Scene별 Prompt Brief 생성
Scene별 Midjourney Prompt 생성
Scene별 Avoid Rule 적용
Prompt Review 생성
Provider Request 생성 요청
Manual Action Guide 생성 지원
Visual Asset Registry 연결 확인
Visual Review 생성
Visual Issue 감지
Visual Handoff 생성
Motion Engine용 Source Image 목록 생성
Editing Engine용 Visual Asset 목록 생성
```

Visual Engine이 하지 않는 것:

```text
이미지를 직접 생성하지 않는다.
Midjourney를 직접 호출하지 않는다.
Motion 영상을 만들지 않는다.
Timeline Scene ID를 변경하지 않는다.
Story를 수정하지 않는다.
Direction을 임의 변경하지 않는다.
Quality Score를 최종 계산하지 않는다.
Final Editing을 수행하지 않는다.
```

---

# 5. Inputs

Visual Engine의 입력:

```text
project.json
channel_snapshot.json
template_snapshot.json
timeline/timeline.json
timeline/timeline_lock.json
direction/scene_plan.json
direction/camera_plan.json
direction/emotion_plan.json
direction/director_notes.md
channels/{channel_id}/brand.yaml
channels/{channel_id}/visual.yaml
channels/{channel_id}/provider.yaml
knowledge/risk_notes.json
workflow/memory_context_VISUAL.json
```

필수 입력:

```text
timeline/timeline.json
timeline/timeline_lock.json
direction/scene_plan.json
direction/camera_plan.json
project.json
channel_snapshot.json
```

선택 입력:

```text
direction/director_notes.md
knowledge/visualizable_ideas.json
Visual Success Memory
Visual Failure Memory
Provider Memory
Brand Violation Memory
Midjourney Prompt Memory
```

---

# 6. Outputs

Visual Engine의 출력:

```text
prompts/visual_prompt_briefs.json
prompts/midjourney_image_prompts.json
prompts/prompt_review.json
assets/asset_registry.json
reports/visual_review.json
workflow/stage_results/VISUAL_result.json
workflow/handoffs/VISUAL_to_MOTION.json
workflow/handoffs/VISUAL_to_EDITING.json
```

Provider Engine과 연결되는 파일:

```text
provider_requests/visual_requests.jsonl
provider_responses/visual_responses.jsonl
```

실제 이미지 결과물 위치:

```text
assets/images/SC001_image_v001.png
assets/images/SC002_image_v001.png
assets/images/SC003_image_v001.png
```

v1.0 최소 출력:

```text
prompts/midjourney_image_prompts.json
prompts/prompt_review.json
reports/visual_review.json
```

---

# 7. Visual Creation Flow

Visual Engine 실행 흐름:

```text
Load Project Context
↓
Load Timeline
↓
Load Timeline Lock
↓
Load Direction Outputs
↓
Load Brand / Visual Rules
↓
Load Memory Context
↓
Validate Visual Inputs
↓
Analyze Scene Visual Requirements
↓
Build Visual Prompt Briefs
↓
Generate Midjourney Prompts
↓
Apply Brand Style Rules
↓
Apply Avoid Rules
↓
Apply Factual / Speculation Risk Rules
↓
Build Prompt Review
↓
Request Provider Engine to Create Visual Requests
↓
Wait for Manual or Registered Results
↓
Register Visual Assets
↓
Build Visual Review
↓
Handoff to Motion / Editing
```

---

# 8. Visual Requirement Rules

Visual Engine은 Timeline의 각 Scene을 확인한다.

기본 규칙:

```text
visual.required = true인 Scene은 반드시 Visual Prompt가 필요하다.
Scene ID는 Timeline의 Scene ID를 그대로 사용한다.
Scene Purpose와 Visual Goal이 Prompt에 반영되어야 한다.
Direction의 camera_plan이 Prompt에 반영되어야 한다.
Brand Visual Rule이 Prompt에 반영되어야 한다.
Avoid Rule이 Prompt에 반영되어야 한다.
```

Visual이 필요하지 않은 Scene은 v1.0에서는 거의 없다.

기본값:

```text
모든 Scene은 최소 1개의 이미지가 필요하다.
```

---

# 9. visual_prompt_briefs.json Schema

Prompt Brief는 Midjourney Prompt를 만들기 전의 구조화된 지시서이다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "briefs": [
    {
      "scene_id": "SC001",
      "order": 1,
      "purpose": "hook",
      "importance": "critical",

      "story_context": {
        "summary": "A child is born under the light of a star far from Earth.",
        "emotion": "mystery",
        "viewer_feeling": "The viewer should feel curiosity and awe."
      },

      "visual_direction": {
        "visual_goal": "Create immediate mystery through a cinematic future settlement under alien sunlight.",
        "key_elements": [
          "alien sunlight",
          "future settlement",
          "small human silhouette",
          "quiet atmosphere"
        ],
        "composition": "wide establishing shot, alien sun in background, human silhouette in foreground",
        "lighting": "soft alien sunrise, deep blue shadows, subtle warm rim light",
        "camera": "cinematic wide angle, slow push-in feeling"
      },

      "brand_rules": {
        "style": "cinematic realistic future documentary",
        "tone": [
          "mysterious",
          "intelligent",
          "philosophical"
        ],
        "avoid": [
          "cheap sci-fi",
          "cartoon style",
          "random neon",
          "text",
          "watermark"
        ]
      },

      "risk": {
        "speculative": true,
        "required_treatment": "possible future simulation, not confirmed reality"
      }
    }
  ]
}
```

---

# 10. Midjourney Prompt Rules

Midjourney Prompt는 다음 요소를 포함해야 한다.

```text
Scene Subject
Environment
Composition
Lighting
Mood
Camera / Lens Feel
Style
Quality Detail
Aspect Ratio
Avoid Rule
```

권장 구조:

```text
[subject], [environment], [composition], [lighting], [mood], [camera/lens], [style], [quality], --ar 16:9 --style raw --v 6
```

예시:

```text
quiet futuristic settlement under alien sunlight, small human silhouette in the foreground, large alien sun in the background, cinematic wide establishing shot, soft alien sunrise, deep blue shadows, subtle warm rim light, mysterious and reflective mood, realistic future documentary style, high detail, grounded speculative science, no text, no logo, no watermark --ar 16:9 --style raw --v 6
```

---

# 11. midjourney_image_prompts.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "provider": "midjourney",

  "prompts": [
    {
      "prompt_id": "MJ-IMG-000001",
      "scene_id": "SC001",
      "order": 1,
      "purpose": "hook",
      "importance": "critical",

      "prompt": "quiet futuristic settlement under alien sunlight, small human silhouette in the foreground, large alien sun in the background, cinematic wide establishing shot, soft alien sunrise, deep blue shadows, subtle warm rim light, mysterious and reflective mood, realistic future documentary style, high detail, grounded speculative science, no text, no logo, no watermark --ar 16:9 --style raw --v 6",

      "prompt_components": {
        "subject": "futuristic settlement under alien sunlight",
        "environment": "distant planet, quiet future colony",
        "composition": "wide establishing shot with human silhouette in foreground",
        "lighting": "soft alien sunrise, deep blue shadows, warm rim light",
        "mood": "mysterious, cinematic, reflective",
        "style": "realistic future documentary",
        "avoid": [
          "cheap sci-fi",
          "cartoon",
          "text",
          "logo",
          "watermark",
          "distorted anatomy"
        ]
      },

      "provider_settings": {
        "aspect_ratio": "16:9",
        "version": "6",
        "style": "raw"
      },

      "expected_output": {
        "asset_type": "image",
        "file": "assets/images/SC001_image_v001.png"
      },

      "status": "READY_FOR_PROVIDER"
    }
  ]
}
```

---

# 12. Prompt Quality Rules

좋은 Prompt 조건:

```text
Scene Purpose가 명확하다.
Visual Goal이 구체적이다.
구도와 조명이 있다.
Brand Tone이 반영되어 있다.
Avoid Rule이 포함되어 있다.
Scene ID와 expected_output이 연결되어 있다.
너무 짧거나 일반적이지 않다.
너무 많은 개념을 한 Prompt에 넣지 않는다.
```

나쁜 Prompt:

```text
future city, cinematic
AI human evolution
cool sci-fi scene
beautiful futuristic image
```

좋은 Prompt:

```text
a quiet future city built inside a low-gravity habitat, long shadows across curved glass architecture, small human figures walking slowly, cinematic wide shot, realistic documentary lighting, mysterious and intelligent tone, no text, no logo --ar 16:9 --style raw --v 6
```

---

# 13. Brand Visual Rules

Visual Engine은 Brand System을 따라야 한다.

검사 항목:

```text
Channel Visual Identity와 맞는가
Tone이 맞는가
색감이 맞는가
금지 스타일을 피했는가
Audience에게 맞는가
Thumbnail / 영상 전체 정체성과 충돌하지 않는가
```

예시 Future Channel 방향:

```text
Allowed:
cinematic realism
deep blue shadows
soft contrast
mysterious scale
future documentary
philosophical atmosphere

Forbidden:
cheap neon sci-fi
random robots
cartoon rendering
meme style
low-quality AI face
overly sensational horror
```

---

# 14. Factual and Speculation Visual Rules

Visual은 Knowledge와 Direction의 Risk를 지켜야 한다.

규칙:

```text
Speculative Scene은 가능한 미래 시뮬레이션처럼 보여야 한다.
확정된 사실처럼 보이면 안 된다.
과학적 설명 Scene과 상상 Scene의 톤을 구분한다.
Unsupported Claim을 이미지로 확정하지 않는다.
Forbidden Claim을 시각적으로 암시하지 않는다.
```

예시:

```text
금지:
100만 년 뒤 인간의 실제 모습이라고 단정하는 이미지

허용:
가능한 미래 시나리오를 보여주는 추상적, 시뮬레이션 느낌의 장면
```

---

# 15. Scene Image Naming Rules

이미지 파일명은 Scene ID를 포함해야 한다.

기본 형식:

```text
assets/images/{scene_id}_image_v{version}.png
```

예시:

```text
assets/images/SC001_image_v001.png
assets/images/SC002_image_v001.png
assets/images/SC003_image_v001.png
```

대체 후보가 있는 경우:

```text
assets/images/SC001_image_v001_a.png
assets/images/SC001_image_v001_b.png
assets/images/SC001_image_v001_selected.png
```

최종 선택본은 Asset Registry에 등록되어야 한다.

---

# 16. Provider Engine Integration

Visual Engine은 Provider Engine을 통해 Visual Request를 만든다.

흐름:

```text
Visual Prompt 생성
↓
Provider Engine에 Request 생성 요청
↓
Provider Engine이 VisualProviderInterface 사용
↓
MidjourneyAdapter가 Manual Action Guide 생성
↓
사용자가 Midjourney에서 이미지 생성
↓
결과 파일을 assets/images/에 저장
↓
Provider Engine이 Result 등록
↓
Visual Engine이 Asset 연결 확인
```

Visual Engine은 Midjourney를 직접 호출하지 않는다.

---

# 17. Visual Provider Request Mapping

Visual Engine은 다음 정보를 Provider Engine에 전달한다.

```text
project_id
channel_id
stage = VISUAL
provider_type = visual
provider_name = midjourney
scene_id
prompt
expected_output
aspect_ratio
avoid_rules
```

Provider Request 예시:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "VISUAL",
  "provider_type": "visual",
  "provider_name": "midjourney",
  "scene_id": "SC001",
  "prompt_ref": "prompts/midjourney_image_prompts.json",
  "expected_output": "assets/images/SC001_image_v001.png"
}
```

---

# 18. Asset Registry Integration

Visual 결과물은 반드시 Asset Registry에 등록되어야 한다.

파일:

```text
assets/asset_registry.json
```

Visual Asset Entry 예시:

```json
{
  "asset_id": "ASSET-IMG-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "scene_id": "SC001",
  "asset_type": "image",
  "provider": "midjourney",
  "file": "assets/images/SC001_image_v001.png",
  "prompt_id": "MJ-IMG-000001",
  "request_id": "PROV-REQ-000001",
  "response_id": "PROV-RES-000001",
  "status": "REGISTERED",
  "selected": true,
  "created_at": "2026-07-10T12:00:00"
}
```

규칙:

```text
이미지 파일만 있으면 완료가 아니다.
Asset Registry에 등록되어야 한다.
Timeline의 scene_id와 일치해야 한다.
Editing과 Motion은 Asset Registry를 기준으로 이미지를 찾는다.
```

---

# 19. Timeline Update Rules

Visual Asset이 등록되면 Timeline의 해당 Scene에 asset_ref를 업데이트할 수 있다.

허용 업데이트:

```text
timeline.scenes[].visual.prompt_ref
timeline.scenes[].visual.asset_ref
timeline.scenes[].quality.issues
```

금지 업데이트:

```text
scene_id 변경
scene_order 변경
scene_purpose 변경
language_tracks 삭제
```

Timeline Lock을 위반하면 안 된다.

---

# 20. prompt_review.json Schema

Prompt Review는 생성된 Prompt의 품질을 검사한다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "VISUAL",

  "score": 92,
  "status": "PASS_WITH_NOTES",

  "checks": {
    "scene_coverage": 100,
    "scene_id_consistency": 100,
    "brand_fit": 94,
    "direction_fit": 93,
    "prompt_specificity": 90,
    "avoid_rules_applied": 95,
    "speculation_safety": 92,
    "provider_readiness": 90
  },

  "issues": [
    {
      "scene_id": "SC004",
      "severity": "MEDIUM",
      "issue_type": "PROMPT_TOO_GENERIC",
      "description": "Prompt may produce generic sci-fi visuals.",
      "suggested_fix": "Add more specific composition and lighting details."
    }
  ]
}
```

---

# 21. visual_review.json Schema

Visual Review는 Prompt와 등록된 이미지 결과를 함께 검토한다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "VISUAL",

  "score": 93,
  "status": "PASS_WITH_NOTES",

  "scene_reviews": [
    {
      "scene_id": "SC001",
      "prompt_id": "MJ-IMG-000001",
      "asset_ref": "assets/images/SC001_image_v001.png",

      "checks": {
        "asset_exists": true,
        "scene_match": true,
        "brand_fit": 95,
        "direction_fit": 94,
        "visual_quality": 93,
        "no_text_or_watermark": true,
        "speculation_safety": true,
        "motion_ready": true
      },

      "issues": []
    }
  ],

  "overall_issues": [],
  "handoff_notes": [
    "SC001 is suitable as source image for Motion Engine.",
    "Maintain speculative future tone in motion prompts."
  ]
}
```

---

# 22. Visual Scoring

Visual Score 기준:

```yaml
visual_score:
  scene_coverage: 15
  scene_id_consistency: 15
  direction_fit: 15
  brand_fit: 15
  prompt_specificity: 10
  visual_quality: 10
  speculation_safety: 10
  asset_registry_integrity: 5
  motion_readiness: 5
```

점수 기준:

```text
95~100
Pass

90~94
Pass with notes

80~89
Revision required

70~79
Partial regeneration required

70 미만
Visual fail
```

Hard Fail 조건:

```text
Scene ID 불일치
필수 이미지 누락
Brand 심각한 위반
텍스트 / 워터마크 포함
Speculative Scene을 확정 사실처럼 표현
Timeline Lock 위반
Asset Registry 누락
```

---

# 23. Visual Validation Rules

Visual Validator는 다음을 확인해야 한다.

```text
prompts/midjourney_image_prompts.json 존재
prompts/prompt_review.json 존재
reports/visual_review.json 존재
project_id 일치
channel_id 일치
Timeline Scene 수와 Prompt 수 일치
Prompt마다 scene_id 존재
Prompt마다 expected_output 존재
Scene ID 중복 없음
Prompt가 비어 있지 않음
Avoid Rule 포함
Brand Rule 반영
Provider Settings 존재
Asset Registry 연결 확인
Timeline Lock 위반 없음
```

검증 실패 시 MOTION 또는 EDITING Stage로 이동할 수 없다.

단, Manual Provider Result가 아직 없으면 Workflow는 `WAITING_FOR_MANUAL_ACTION` 상태가 될 수 있다.

---

# 24. Auto Fix Rules

Visual 문제 발생 시 부분 수정이 우선이다.

수정 대상:

```text
특정 Scene Prompt
특정 Scene Image
Brand 위반 Scene
Generic Visual Scene
Motion Source로 부적합한 Scene
Speculation Risk Scene
```

금지:

```text
전체 Project 재생성
전체 Timeline 재생성
Story 임의 수정
Scene ID 변경
```

Auto Fix 예시:

```text
Issue:
SC007 image looks too cartoonish.

Fix:
Revise only SC007 Midjourney prompt with stronger realistic documentary style and regenerate SC007 image.
```

---

# 25. Handoff to Motion Engine

Visual Engine은 Motion Engine에 Source Image 정보를 넘긴다.

Handoff 파일:

```text
workflow/handoffs/VISUAL_to_MOTION.json
```

포함 내용:

```text
Motion 추천 Scene
Source Image Asset
Scene Purpose
Direction Motion Hint
Camera Movement
Risk Notes
Prompt Ref
Asset Ref
```

예시:

```json
{
  "from_stage": "VISUAL",
  "to_stage": "MOTION",
  "project_id": "20260710-093500-future-million-year-human",

  "motion_candidates": [
    {
      "scene_id": "SC001",
      "asset_ref": "assets/images/SC001_image_v001.png",
      "priority": "high",
      "reason": "Opening hook scene",
      "motion_hint": "slow cinematic push-in",
      "risk_note": "Maintain possible future simulation feeling."
    }
  ]
}
```

---

# 26. Handoff to Editing Engine

Visual Engine은 Editing Engine에 Visual Asset 목록을 넘긴다.

Handoff 파일:

```text
workflow/handoffs/VISUAL_to_EDITING.json
```

포함 내용:

```text
Scene별 selected image
Asset Registry reference
Missing Asset 여부
Visual Issue 여부
Scene별 editing note
```

---

# 27. Memory Integration

Visual Engine은 작업 전 Memory Context를 사용한다.

사용 가능한 Memory:

```text
Successful Visual Prompt Memory
Failed Visual Prompt Memory
Brand Visual Memory
Midjourney Failure Pattern
Midjourney Style Pattern
Quality Visual Failure Memory
Motion Source Image Memory
```

Visual Engine은 작업 후 Memory Candidate를 만들 수 있다.

예시:

```text
특정 Channel에서 잘 작동한 이미지 스타일
반복 실패한 Midjourney 표현
Brand 위반을 자주 만드는 Prompt 패턴
Motion에 적합한 Source Image 패턴
```

Memory 확정은 Memory Engine 또는 Learning Engine이 담당한다.

---

# 28. Error Types

Visual Engine의 Error Type:

```text
VisualInputMissingError
TimelineMissingError
TimelineLockMissingError
DirectionOutputMissingError
VisualRequirementMissingError
PromptCreationError
PromptValidationError
PromptTooGenericError
BrandVisualMismatchError
SpeculationVisualRiskError
ProviderRequestCreationError
VisualAssetMissingError
AssetRegistryError
SceneIdMismatchError
VisualReviewError
VisualValidationError
VisualHandoffError
```

Error 예시:

```json
{
  "error_type": "PromptTooGenericError",
  "message": "Prompt for SC004 is too generic and may produce weak AI visuals.",
  "project_id": "20260710-093500-future-million-year-human",
  "scene_id": "SC004",
  "stage": "VISUAL",
  "severity": "MEDIUM",
  "suggested_fix": "Add concrete subject, composition, lighting, and brand-specific mood.",
  "created_at": "2026-07-10T12:00:00"
}
```

---

# 29. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
VisualEngine
VisualInputLoader
VisualInputValidator
VisualRequirementAnalyzer
VisualPromptBriefBuilder
MidjourneyPromptBuilder
PromptComponentBuilder
VisualAvoidRuleApplier
BrandVisualChecker
SpeculationVisualRiskChecker
PromptReviewBuilder
VisualProviderRequestBuilder
VisualAssetRegistryUpdater
VisualReviewBuilder
VisualValidator
VisualHandoffBuilder
VisualErrorReporter
```

---

# 30. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/21_VISUAL_ENGINE.md
→ engines/visual/
```

예시 구조:

```text
engines/
└── visual/
    ├── visual_engine.py
    ├── visual_input_loader.py
    ├── visual_input_validator.py
    ├── visual_requirement_analyzer.py
    ├── visual_prompt_brief_builder.py
    ├── midjourney_prompt_builder.py
    ├── prompt_component_builder.py
    ├── visual_avoid_rule_applier.py
    ├── brand_visual_checker.py
    ├── speculation_visual_risk_checker.py
    ├── prompt_review_builder.py
    ├── visual_provider_request_builder.py
    ├── visual_asset_registry_updater.py
    ├── visual_review_builder.py
    ├── visual_validator.py
    ├── visual_handoff_builder.py
    └── visual_error_reporter.py
```

---

# 31. Main Public Operations

Visual Engine은 최소 다음 작업을 제공해야 한다.

```text
run_visual(project_id)
load_visual_inputs(project_id)
validate_visual_inputs(project_id)
analyze_visual_requirements(project_id)
build_visual_prompt_briefs(project_id)
build_midjourney_prompts(project_id)
apply_visual_avoid_rules(project_id)
check_brand_visual_fit(project_id)
check_speculation_visual_risk(project_id)
build_prompt_review(project_id)
create_visual_provider_requests(project_id)
register_visual_assets(project_id)
build_visual_review(project_id)
validate_visual_outputs(project_id)
build_handoff_to_motion(project_id)
build_handoff_to_editing(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
Timeline Scene ID 유지
Direction 반영
Brand Rule 반영
Avoid Rule 반영
Provider Engine 경유
Asset Registry 연결
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 32. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Timeline 로드
Direction Output 로드
Visual 입력 검증
Scene별 Prompt Brief 생성
Scene별 Midjourney Prompt 생성
Avoid Rule 적용
midjourney_image_prompts.json 생성
prompt_review.json 생성
Provider Request 생성용 데이터 준비
Manual Action Guide 지원
Visual Asset 등록 확인
visual_review.json 생성
Motion Engine Handoff 생성
Editing Engine Handoff 생성
Visual Validation 수행
```

v1.0에서 하지 않아도 되는 것:

```text
Midjourney 완전 자동 호출
이미지 직접 생성
이미지 고급 품질 자동 판별
실시간 이미지 편집
고급 이미지 업스케일 자동화
Final Thumbnail 제작
Motion 영상 생성
Provider 직접 호출
```

v1.0에서는 Midjourney Manual Workflow를 안정적으로 지원하고, Scene별 Visual Prompt와 Asset 연결 구조를 만드는 것이 우선이다.

---

# 33. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Timeline과 Direction을 로드할 수 있다.
Visual 입력을 검증할 수 있다.
각 Scene의 Visual Requirement를 분석할 수 있다.
각 Scene의 Prompt Brief를 만들 수 있다.
각 Scene의 Midjourney Prompt를 만들 수 있다.
Avoid Rule을 Prompt에 반영할 수 있다.
Brand Visual Rule을 반영할 수 있다.
Speculative Scene의 시각 위험을 표시할 수 있다.
midjourney_image_prompts.json을 생성할 수 있다.
prompt_review.json을 생성할 수 있다.
Provider Engine용 Visual Request를 준비할 수 있다.
Visual Asset을 Asset Registry와 연결할 수 있다.
visual_review.json을 생성할 수 있다.
Motion Engine으로 Source Image Handoff를 만들 수 있다.
Editing Engine으로 Visual Asset Handoff를 만들 수 있다.
Visual Validation 실패 시 다음 Stage 진행을 막을 수 있다.
```

---

# 34. Non Goals

v1.0에서 Visual Engine이 하지 않는 것:

```text
이미지 직접 생성
Midjourney 직접 호출
Motion 영상 생성
Voice 생성
Subtitle 생성
Final Editing
Thumbnail 최종 제작
Quality Score 최종 계산
Timeline Scene ID 변경
Story 임의 수정
Direction 임의 수정
```

v1.0에서는 이미지 제작을 위한 Prompt와 Asset 연결 구조를 안정적으로 만드는 것이 핵심이다.

---

# 35. Critical Visual Rules

반드시 지켜야 할 규칙:

```text
1. Visual Engine은 Timeline 없이 실행하지 않는다.

2. Visual Engine은 Direction 없이 실행하지 않는다.

3. Visual Engine은 Scene ID를 변경하지 않는다.

4. 모든 required Scene은 Visual Prompt를 가져야 한다.

5. Visual Prompt는 Scene Purpose를 반영해야 한다.

6. Visual Prompt는 Brand Rule을 반영해야 한다.

7. Visual Prompt는 Avoid Rule을 포함해야 한다.

8. Generic AI Look을 피한다.

9. Speculative Scene을 확정 사실처럼 보이게 만들지 않는다.

10. Visual Engine은 Midjourney를 직접 호출하지 않는다.

11. Provider Engine을 통해 Visual Request를 만든다.

12. 이미지 결과물은 Asset Registry에 등록해야 한다.

13. Timeline Lock을 위반하지 않는다.

14. Visual Validation 실패 시 Motion / Editing Stage로 넘어가지 않는다.

15. 중요한 Visual 판단은 Self Review와 Handoff에 기록한다.
```

---

# 36. Final Principle

Visual Engine은 Story와 Direction을 눈에 보이는 장면으로 바꾸는 엔진이다.

좋은 Visual은 단순히 예쁜 이미지가 아니다.

좋은 Visual은 Scene의 목적을 수행하고,

Brand를 지키고,

시청자의 감정을 움직이고,

Motion과 Editing이 사용할 수 있는 자산이 된다.

Visual Engine의 목적은 이미지를 많이 만드는 것이 아니라, 영상 전체의 의미와 품질을 지탱하는 시각 구조를 만드는 것이다.
