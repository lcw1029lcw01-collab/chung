# 20_DIRECTION_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Direction Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Direction Engine을 정의한다.

Direction Engine은 Story Engine이 만든 Hook, Outline, Master Script를 실제 영상 제작이 가능한 장면 계획으로 변환하는 엔진이다.

Story Engine이 대본과 이야기 구조를 만든다면, Direction Engine은 그 이야기를 다음 요소로 해석한다.

```text
Scene Plan
Visual Flow
Emotional Flow
Camera Direction
Pacing Direction
Scene Purpose
Director Notes
Timeline Engine Handoff
```

Direction Engine은 영상의 “감독” 역할을 한다.

좋은 Direction이 없으면 Story는 좋아도 영상이 평면적으로 보일 수 있다.

```text
Direction이 약하면
→ Scene 목적이 흐려지고
→ Timeline이 약해지고
→ Visual Prompt가 일반적이 되고
→ Motion 적용 기준이 흔들리고
→ Editing 리듬이 약해지고
→ Retention이 떨어진다.
```

이 문서는 다음 문서들과 직접 연결된다.

```text
06_AI_THINKING_FRAMEWORK.md
07_PROJECT_SPEC.md
10_BRAND_SYSTEM.md
12_PROJECT_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
16_TIMELINE_ENGINE.md
18_KNOWLEDGE_ENGINE.md
19_STORY_ENGINE.md
21_VISUAL_ENGINE.md
22_MOTION_ENGINE.md
25_EDITING_ENGINE.md
26_QUALITY_ENGINE.md
27_GROWTH_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Direction Engine은 Story를 장면 단위의 영상 연출 계획으로 변환하는 엔진이다.

전체 흐름:

```text
Story
↓
Direction
↓
Timeline
↓
Visual
↓
Motion
↓
Voice
↓
Subtitle
↓
Editing
↓
Quality
```

Direction Engine의 핵심 목표는 다음이다.

```text
대본을 장면 단위로 해석한다.
각 장면의 목적을 명확히 한다.
각 장면의 감정과 시각 방향을 정의한다.
카메라와 화면 구성을 제안한다.
Timeline Engine이 Scene 구조를 만들 수 있게 한다.
Visual Engine이 Prompt를 만들 수 있게 한다.
Motion Engine이 움직임이 필요한 장면을 판단할 수 있게 한다.
Editing Engine이 리듬을 이해할 수 있게 한다.
```

---

# 3. Direction Philosophy

## 3.1 Direction Is Visual Interpretation

Direction은 대본을 그대로 나누는 작업이 아니다.

Direction은 대본의 의미를 영상 언어로 번역하는 작업이다.

나쁜 Direction:

```text
Scene 1: 대본 첫 문장
Scene 2: 대본 두 번째 문장
Scene 3: 대본 세 번째 문장
```

좋은 Direction:

```text
Scene 1:
먼 행성의 낯선 빛 아래 태어나는 미래의 아이.
목적: Hook
감정: 신비감, 궁금증
화면: 거대한 외계 태양, 조용한 미래 도시, 인간 실루엣
카메라: 느린 push-in
```

## 3.2 Every Scene Must Have a Purpose

모든 Scene은 목적을 가져야 한다.

```text
hook
question
setup
context
explanation
contrast
simulation
turning_point
climax
reflection
ending
cta
```

목적 없는 Scene은 Timeline으로 넘기지 않는다.

## 3.3 Direction Must Preserve Story Intent

Direction Engine은 Story의 핵심 의도를 임의로 바꾸면 안 된다.

반드시 보존해야 할 것:

```text
Selected Story Angle
Selected Hook
Core Question
Brand Tone
Factual Safety
Speculative Framing
Emotional Arc
```

## 3.4 Direction Must Be Production-Oriented

Direction은 추상적이면 안 된다.

Production Engine이 사용할 수 있는 구체성을 가져야 한다.

```text
visual_goal
camera_direction
emotion
scene_purpose
motion_hint
editing_hint
risk_note
```

---

# 4. Direction Engine Responsibilities

Direction Engine의 책임:

```text
Story Output 로드
Knowledge Risk 로드
Brand / Visual / Motion Rules 로드
Story Section을 Scene 후보로 분해
Scene Purpose 정의
Scene Emotion 정의
Visual Goal 정의
Camera Direction 정의
Pacing Direction 정의
Motion Hint 정의
Editing Hint 정의
Scene Risk Note 반영
Scene Plan 생성
Emotion Plan 생성
Camera Plan 생성
Director Notes 생성
Direction Review 생성
Timeline Engine Handoff 생성
```

Direction Engine이 하지 않는 것:

```text
Timeline을 최종 생성하지 않는다.
Scene ID를 최종 확정하지 않는다.
Visual Prompt를 직접 작성하지 않는다.
이미지를 생성하지 않는다.
Motion 영상을 생성하지 않는다.
Voice 파일을 생성하지 않는다.
Subtitle을 생성하지 않는다.
Final Editing을 수행하지 않는다.
Provider를 직접 호출하지 않는다.
Quality Score를 최종 계산하지 않는다.
```

Scene ID 최종 생성과 시간 구조는 Timeline Engine이 담당한다.

---

# 5. Inputs

Direction Engine의 입력:

```text
project.json
topic.json
channel_snapshot.json
template_snapshot.json
story/outline.json
story/hook.json
story/script_master.json
story/script_master.md
story/story_review.json
knowledge/fact_check.json
knowledge/risk_notes.json
knowledge/visualizable_ideas.json
channels/{channel_id}/brand.yaml
channels/{channel_id}/visual.yaml
channels/{channel_id}/motion.yaml
workflow/memory_context_DIRECTION.json
```

필수 입력:

```text
story/outline.json
story/hook.json
story/script_master.json
story/story_review.json
knowledge/fact_check.json
knowledge/risk_notes.json
project.json
channel_snapshot.json
```

선택 입력:

```text
knowledge/visualizable_ideas.json
Channel Visual Memory
Successful Direction Memory
Motion Pattern Memory
Editing Rhythm Memory
Brand Visual Memory
```

---

# 6. Outputs

Direction Engine의 출력:

```text
direction/scene_plan.json
direction/emotion_plan.json
direction/camera_plan.json
direction/director_notes.md
direction/direction_review.json
workflow/stage_results/DIRECTION_result.json
workflow/handoffs/DIRECTION_to_TIMELINE.json
```

v1.0 최소 출력:

```text
direction/scene_plan.json
direction/emotion_plan.json
direction/camera_plan.json
direction/director_notes.md
direction/direction_review.json
```

Timeline Engine은 최소 다음 파일을 입력으로 사용한다.

```text
direction/scene_plan.json
direction/emotion_plan.json
direction/camera_plan.json
direction/director_notes.md
story/script_master.json
story/outline.json
```

---

# 7. Direction Creation Flow

Direction Engine 실행 흐름:

```text
Load Project Context
↓
Load Story Outputs
↓
Load Knowledge Risk Notes
↓
Load Brand / Visual / Motion Rules
↓
Load Memory Context
↓
Validate Story Inputs
↓
Analyze Story Sections
↓
Break Story into Scene Candidates
↓
Assign Scene Purpose
↓
Assign Emotional Direction
↓
Assign Visual Goal
↓
Assign Camera Direction
↓
Assign Motion Hint
↓
Assign Editing Hint
↓
Apply Risk and Speculation Notes
↓
Write scene_plan.json
↓
Write emotion_plan.json
↓
Write camera_plan.json
↓
Write director_notes.md
↓
Write direction_review.json
↓
Self Review
↓
Handoff to Timeline Engine
```

---

# 8. Scene Plan

Scene Plan은 Story를 장면 단위로 나눈 제작용 계획이다.

Direction Engine은 Scene ID를 최종 확정하지 않는다.

대신 `scene_candidate_id`를 만든다.

최종 Scene ID는 Timeline Engine이 `SC001`, `SC002` 형태로 생성한다.

---

# 9. scene_plan.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "DIRECTION",

  "scene_candidates": [
    {
      "scene_candidate_id": "SCN-CAND-001",
      "source_section_id": "SEC-001",
      "purpose": "hook",
      "importance": "critical",

      "story": {
        "summary": "A child is born under the light of a star far from Earth.",
        "script_excerpt": "100만 년 뒤, 지구가 아닌 다른 별에서 한 아이가 태어난다.",
        "core_question_connection": "Will future humans still be human?"
      },

      "direction": {
        "visual_goal": "Create immediate mystery and curiosity through a cinematic future birth scene.",
        "scene_description": "A quiet futuristic settlement beneath an alien sun, with a newborn child suggested through atmosphere rather than direct close-up.",
        "mood": [
          "mysterious",
          "cinematic",
          "awe"
        ],
        "pacing": "slow_opening",
        "viewer_feeling": "The viewer should feel that they are looking at a possible future, not a confirmed prediction."
      },

      "visual": {
        "visual_style": "cinematic realistic future documentary",
        "key_elements": [
          "alien sunlight",
          "future settlement",
          "human silhouette",
          "quiet atmosphere"
        ],
        "avoid": [
          "cheap sci-fi",
          "cartoon look",
          "text on screen",
          "confirmed prediction feeling"
        ],
        "visual_risk": "Must feel speculative, not factual."
      },

      "motion": {
        "recommended": true,
        "priority": "high",
        "reason": "Opening hook scene with high retention value.",
        "motion_idea": "Slow cinematic push-in toward the settlement under alien sunlight."
      },

      "editing": {
        "rhythm": "slow_cinematic",
        "transition_in": "fade_from_black",
        "transition_out": "slow_fade",
        "notes": [
          "Give this scene enough breathing room.",
          "Do not cut too quickly in the first 5 seconds."
        ]
      },

      "risk": {
        "speculative": true,
        "required_framing": "possible future scenario",
        "forbidden_treatment": "Do not present this as a confirmed future."
      }
    }
  ]
}
```

---

# 10. Scene Purpose Rules

Scene Purpose는 Story와 Timeline의 연결 기준이다.

사용 가능한 Purpose:

```text
hook
question
setup
context
explanation
evidence
simulation
contrast
turning_point
climax
reflection
ending
cta
```

목적별 기본 방향:

```text
hook
강한 시각적 궁금증과 첫 이탈 방지

question
영상 전체를 끌고 가는 질문 제시

setup
맥락을 짧고 명확하게 설정

context
시청자가 이해해야 하는 배경 제공

explanation
핵심 개념을 쉽게 설명

evidence
Claim을 뒷받침하는 근거 제시

simulation
가능한 시나리오를 시각화

contrast
두 관점 또는 두 미래를 비교

turning_point
이야기의 방향을 바꾸는 전환

climax
가장 강한 시각/감정/정보 장면

reflection
철학적, 감정적 여운

ending
핵심 메시지 정리

cta
구독, 다음 영상, 질문 유도
```

---

# 11. Scene Importance Rules

Scene 중요도:

```text
critical
high
medium
low
```

기준:

```text
critical
Hook, Core Question, Climax, Ending

high
중요 전환, 핵심 설명, 강한 시각 장면

medium
일반 설명, 연결 장면

low
짧은 보조 장면, 단순 전환
```

중요도는 Timeline, Motion, Editing에 영향을 준다.

```text
critical / high
→ Motion 후보
→ 더 강한 Visual 필요
→ Quality Review 우선

medium / low
→ 정적 이미지 가능
→ 짧은 설명 가능
```

---

# 12. Emotion Plan

Emotion Plan은 영상 전체의 감정 흐름을 정의한다.

Story Engine의 Emotional Arc를 장면 단위로 구체화한다.

---

# 13. emotion_plan.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "overall_arc": [
    "mystery",
    "curiosity",
    "awe",
    "uncertainty",
    "reflection"
  ],

  "scene_emotions": [
    {
      "scene_candidate_id": "SCN-CAND-001",
      "primary_emotion": "mystery",
      "secondary_emotion": "awe",
      "intensity": "high",
      "viewer_response_goal": "Make the viewer wonder what future humans might become.",
      "voice_direction": "calm, cinematic, slightly mysterious",
      "visual_direction": "quiet scale, unfamiliar light, human presence implied"
    }
  ],

  "emotional_risks": [
    {
      "risk": "Too much spectacle may make the topic feel like fantasy instead of speculative science.",
      "mitigation": "Keep visuals cinematic but grounded."
    }
  ]
}
```

---

# 14. Camera Plan

Camera Plan은 Visual Engine과 Motion Engine이 장면을 구체화할 때 참고하는 화면 구성 계획이다.

카메라 방향은 실제 촬영 명령이 아니라 AI 이미지/영상 생성과 편집을 위한 연출 언어이다.

---

# 15. camera_plan.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "camera_plan": [
    {
      "scene_candidate_id": "SCN-CAND-001",
      "shot_type": "wide_establishing_shot",
      "camera_movement": "slow_push_in",
      "composition": "large alien sun in background, futuristic settlement in midground, small human silhouette in foreground",
      "lens_feel": "cinematic wide angle",
      "lighting": "soft alien sunrise, deep blue shadows, warm rim light",
      "depth": "deep cinematic scale",
      "motion_hint": "slow atmospheric movement only",
      "avoid": [
        "shaky camera",
        "overly busy frame",
        "text overlays",
        "cartoon style"
      ]
    }
  ]
}
```

---

# 16. Director Notes

`director_notes.md`는 사람이 읽기 좋은 연출 지시서이다.

포함 내용:

```text
전체 연출 방향
Hook 연출 방향
감정 흐름
시각 스타일
Motion 사용 기준
Editing 리듬
주의해야 할 Factual Risk
Visual Engine 주의사항
Timeline Engine 주의사항
```

---

# 17. director_notes.md Format

권장 형식:

```markdown
# Director Notes

## Overall Direction

This video should feel cinematic, intelligent, mysterious, and reflective.

The topic is speculative, so future scenes must feel like possible simulations, not confirmed documentary footage.

---

## Opening Direction

Start with a quiet but powerful future scenario.

A child is born far from Earth, under unfamiliar light.

Do not show this as a certain future. It should feel like a question.

---

## Visual Style

- Cinematic realism
- Deep shadows
- Blue and subtle warm contrast
- Large-scale futuristic environments
- Avoid cheap sci-fi clichés

---

## Motion Strategy

Use motion only for hook, major reveal, and emotional turning points.

---

## Risk Notes

Future predictions must be framed as possibilities.
```

---

# 18. Visual Direction Rules

Direction Engine은 Visual Engine이 사용할 시각 목표를 제공해야 한다.

Visual Direction 필수 요소:

```text
visual_goal
scene_description
key_elements
mood
style
avoid
visual_risk
```

좋은 Visual Direction:

```text
A quiet future city under alien sunlight, seen from a wide cinematic perspective, with a small human silhouette that makes the viewer feel scale and uncertainty.
```

나쁜 Visual Direction:

```text
미래 도시 보여주기
인간 진화 이미지
AI 느낌
```

---

# 19. Motion Direction Rules

Motion Direction은 Motion Engine이 어떤 Scene을 5초 영상으로 만들지 판단하는 기준이다.

Motion 추천 기준:

```text
hook
climax
major reveal
emotional turning point
world reveal
important transition
```

Motion을 추천하지 않는 경우:

```text
단순 설명 장면
정보 전달만 있는 장면
이미지 하나로 충분한 장면
장면 중요도가 low인 경우
Motion이 오히려 산만한 경우
```

Motion 필드:

```text
recommended
priority
reason
motion_idea
source_visual_requirement
```

---

# 20. Editing Direction Rules

Editing Direction은 Editing Engine이 리듬을 이해하기 위한 기준이다.

Editing Direction 요소:

```text
rhythm
transition_in
transition_out
breathing_room
cut_density
emphasis_point
notes
```

리듬 예시:

```text
slow_cinematic
medium_documentary
fast_tension_build
quiet_reflection
dramatic_reveal
```

Hook에서는 너무 빠른 컷보다 강한 몰입이 중요할 수 있다.

설명 장면에서는 너무 느리면 이탈이 발생할 수 있다.

Direction Engine은 장면별 리듬을 표시해야 한다.

---

# 21. Factual and Speculation Direction Rules

Direction Engine은 Knowledge와 Story의 Risk를 지켜야 한다.

규칙:

```text
Speculative Scene은 simulation 느낌으로 연출한다.
미래 예측 장면을 확정된 다큐멘터리처럼 연출하지 않는다.
과학적 사실 장면과 상상 시나리오 장면을 구분한다.
Unsupported Claim을 시각적으로 확정하지 않는다.
Forbidden Claim이 암시되지 않게 한다.
```

예시:

```text
나쁜 연출:
100만 년 뒤 인간의 실제 모습이라고 단정하는 이미지

좋은 연출:
가능한 미래 시나리오를 보여주는 시뮬레이션 이미지
```

---

# 22. Brand Direction Rules

Direction은 Brand System을 따라야 한다.

검사 항목:

```text
Channel Tone과 맞는가
Visual Identity와 맞는가
금지된 스타일을 피했는가
Audience에게 맞는가
장기 Channel 정체성을 해치지 않는가
```

예시 Future Channel:

```text
Allowed:
cinematic
intelligent
mysterious
scientific
philosophical

Forbidden:
cheap sci-fi
random meme
cartoonish
low-effort AI look
overly sensational
```

---

# 23. direction_review.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "DIRECTION",

  "score": 93,
  "status": "PASS_WITH_NOTES",

  "checks": {
    "story_intent_preserved": 95,
    "scene_purpose_clear": 94,
    "visual_direction_strength": 93,
    "emotion_flow_clear": 92,
    "camera_direction_usable": 91,
    "motion_guidance_clear": 90,
    "editing_guidance_clear": 90,
    "brand_fit": 95,
    "factual_safety": 94,
    "timeline_readiness": 92
  },

  "issues": [
    {
      "severity": "MEDIUM",
      "issue_type": "SPECULATION_VISUAL_RISK",
      "description": "Future scenes must not look like confirmed predictions.",
      "suggested_fix": "Mark speculative scenes clearly in scene_plan and director_notes."
    }
  ],

  "handoff_notes": [
    "Timeline Engine should preserve the cinematic opening as a critical scene.",
    "Motion should be prioritized for hook and climax scenes.",
    "Speculative future visuals must remain framed as possible scenarios."
  ]
}
```

---

# 24. Direction Scoring

Direction Score 기준:

```yaml
direction_score:
  story_intent_preserved: 15
  scene_purpose_clear: 15
  visual_direction_strength: 15
  emotion_flow_clear: 10
  camera_direction_usable: 10
  motion_guidance_clear: 10
  editing_guidance_clear: 10
  brand_fit: 10
  factual_safety: 5
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
Partial rewrite required

70 미만
Direction fail
```

다음 조건이면 Direction Stage는 통과할 수 없다.

```text
scene_purpose_clear < 80
factual_safety < 85
brand_fit < 85
timeline_readiness < 80
```

---

# 25. Direction Validation Rules

Direction Validator는 다음을 확인해야 한다.

```text
direction/scene_plan.json 존재
direction/emotion_plan.json 존재
direction/camera_plan.json 존재
direction/director_notes.md 존재
direction/direction_review.json 존재
project_id 일치
channel_id 일치
scene_candidates 배열 존재
scene_candidate_id 중복 없음
각 scene_candidate에 purpose 존재
각 scene_candidate에 importance 존재
각 scene_candidate에 visual_goal 존재
각 scene_candidate에 emotion 또는 mood 존재
각 scene_candidate에 visual avoid 존재
Speculative Scene에 risk 표시 존재
Motion 추천 사유 존재
Camera Plan과 Scene Candidate 연결
Emotion Plan과 Scene Candidate 연결
direction_review score 존재
```

검증 실패 시 TIMELINE Stage로 이동할 수 없다.

---

# 26. Self Review

Direction Engine은 결과 제출 전 Self Review를 생성한다.

Self Review 항목:

```text
Story 의도를 지켰는가
Hook 연출이 강한가
각 Scene 목적이 명확한가
감정 흐름이 이어지는가
Visual Engine이 사용할 수 있을 만큼 구체적인가
Motion Engine이 사용할 수 있을 만큼 기준이 있는가
Editing Engine이 리듬을 이해할 수 있는가
Brand Tone을 지켰는가
Speculative Risk를 지켰는가
Timeline Engine이 Scene 구조로 변환할 수 있는가
```

Self Review는 다음 위치에 기록한다.

```text
logs/self_reviews.jsonl
```

---

# 27. Handoff to Timeline Engine

Direction Engine은 Timeline Engine에 Handoff를 생성해야 한다.

Handoff 파일:

```text
workflow/handoffs/DIRECTION_to_TIMELINE.json
```

Handoff에 포함할 내용:

```text
Scene Candidates
Scene Purpose
Scene Importance
Visual Goals
Emotion Plan
Camera Plan
Motion Recommendations
Editing Rhythm
Speculation Risk Notes
Timeline 주의사항
```

Handoff 예시:

```json
{
  "from_stage": "DIRECTION",
  "to_stage": "TIMELINE",
  "project_id": "20260710-093500-future-million-year-human",

  "summary": "Direction created with cinematic future hook, clear scene purposes, and speculative risk controls.",

  "must_preserve": [
    "Opening future birth scenario as critical hook",
    "Speculative framing",
    "Mystery to reflection emotional arc"
  ],

  "timeline_notes": [
    "Assign stable Scene IDs from scene_candidates.",
    "Keep the first scene short but visually strong.",
    "Mark hook and climax scenes as high priority for Motion.",
    "Preserve language track requirements for future Voice and Subtitle."
  ],

  "required_inputs_for_timeline": [
    "direction/scene_plan.json",
    "direction/emotion_plan.json",
    "direction/camera_plan.json",
    "direction/director_notes.md",
    "story/script_master.json"
  ]
}
```

---

# 28. Integration with Timeline Engine

Timeline Engine uses Direction Output to create:

```text
timeline/timeline.json
timeline/timeline_review.json
timeline/timeline_lock.json
```

Direction Engine provides:

```text
scene candidates
purpose
importance
visual goal
emotion
camera direction
motion recommendation
editing hint
risk note
```

Timeline Engine decides:

```text
final Scene ID
scene order
scene timing
language tracks
asset mapping placeholders
timeline lock
```

Direction Engine must not override Timeline Lock after Timeline Stage.

---

# 29. Integration with Visual Engine

Visual Engine uses Direction Output to build prompts.

Visual Engine uses:

```text
scene_description
visual_goal
key_elements
visual_style
mood
lighting
composition
avoid
visual_risk
```

Direction Engine must provide enough specificity so Visual Engine does not create generic prompts.

---

# 30. Integration with Motion Engine

Motion Engine uses Direction Output to select motion scenes.

Motion Engine uses:

```text
motion.recommended
motion.priority
motion.reason
motion.motion_idea
camera_movement
scene importance
scene purpose
```

Direction Engine should not recommend Motion for every Scene.

---

# 31. Integration with Editing Engine

Editing Engine uses Direction Output to understand rhythm.

Editing Engine uses:

```text
editing.rhythm
transition_in
transition_out
breathing_room
emphasis_point
director_notes.md
emotion_plan.json
```

Direction Engine should mark which scenes need breathing room and which scenes can move faster.

---

# 32. Memory Integration

Direction Engine은 작업 전 Memory Context를 사용한다.

사용 가능한 Memory:

```text
Successful Visual Direction Memory
Failed Visual Direction Memory
Motion Success Pattern
Editing Rhythm Memory
Brand Visual Memory
Quality Failure Memory
Retention Pattern Memory
```

Direction Engine은 작업 후 Memory Candidate를 만들 수 있다.

예시:

```text
좋은 Hook 연출 패턴
실패한 Visual Direction 패턴
Motion이 효과적인 Scene 유형
Brand 위반을 자주 만드는 연출 유형
```

Memory 확정은 Memory Engine 또는 Learning Engine이 담당한다.

---

# 33. Error Types

Direction Engine의 Error Type:

```text
DirectionInputMissingError
StoryOutputInvalidError
ScenePlanCreationError
ScenePurposeMissingError
VisualGoalMissingError
EmotionPlanError
CameraPlanError
SpeculativeRiskMissingError
BrandDirectionMismatchError
MotionRecommendationError
DirectionReviewError
DirectionValidationError
DirectionHandoffError
```

Error 예시:

```json
{
  "error_type": "VisualGoalMissingError",
  "message": "Scene candidate SCN-CAND-004 has no visual_goal.",
  "project_id": "20260710-093500-future-million-year-human",
  "stage": "DIRECTION",
  "severity": "HIGH",
  "suggested_fix": "Add a concrete visual goal before Timeline Stage.",
  "created_at": "2026-07-10T11:30:00"
}
```

---

# 34. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
DirectionEngine
DirectionInputLoader
DirectionInputValidator
ScenePlanBuilder
ScenePurposeMapper
SceneImportanceAssigner
VisualDirectionBuilder
EmotionPlanBuilder
CameraPlanBuilder
MotionDirectionBuilder
EditingDirectionBuilder
SpeculationRiskMapper
BrandDirectionChecker
DirectionReviewBuilder
DirectionValidator
DirectionHandoffBuilder
DirectionErrorReporter
```

---

# 35. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/20_DIRECTION_ENGINE.md
→ engines/direction/
```

예시 구조:

```text
engines/
└── direction/
    ├── direction_engine.py
    ├── direction_input_loader.py
    ├── direction_input_validator.py
    ├── scene_plan_builder.py
    ├── scene_purpose_mapper.py
    ├── scene_importance_assigner.py
    ├── visual_direction_builder.py
    ├── emotion_plan_builder.py
    ├── camera_plan_builder.py
    ├── motion_direction_builder.py
    ├── editing_direction_builder.py
    ├── speculation_risk_mapper.py
    ├── brand_direction_checker.py
    ├── direction_review_builder.py
    ├── direction_validator.py
    ├── direction_handoff_builder.py
    └── direction_error_reporter.py
```

---

# 36. Main Public Operations

Direction Engine은 최소 다음 작업을 제공해야 한다.

```text
run_direction(project_id)
load_direction_inputs(project_id)
validate_direction_inputs(project_id)
build_scene_plan(project_id)
map_scene_purposes(project_id)
assign_scene_importance(project_id)
build_visual_direction(project_id)
build_emotion_plan(project_id)
build_camera_plan(project_id)
build_motion_direction(project_id)
build_editing_direction(project_id)
map_speculation_risks(project_id)
check_brand_direction(project_id)
build_direction_review(project_id)
validate_direction_outputs(project_id)
build_handoff_to_timeline(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
Story Intent 보존
Scene Purpose 명확화
Visual Goal 구체화
Brand Tone 유지
Speculation Risk 표시
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 37. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Story Output 로드
Direction 입력 검증
Scene Candidate 생성
Scene Purpose 지정
Scene Importance 지정
Visual Goal 생성
Emotion Plan 생성
Camera Plan 생성
Motion Recommendation 생성
Editing Hint 생성
Speculation Risk 표시
scene_plan.json 생성
emotion_plan.json 생성
camera_plan.json 생성
director_notes.md 생성
direction_review.json 생성
Direction Validation 수행
Timeline Engine Handoff 생성
```

v1.0에서 하지 않아도 되는 것:

```text
Timeline 최종 생성
Visual Prompt 최종 작성
이미지 생성
Motion 영상 생성
고급 3D 카메라 설계
실시간 Storyboard UI
Final Editing 수행
Provider 직접 호출
```

v1.0에서는 Timeline과 Visual Engine이 사용할 수 있는 구체적인 연출 계획을 안정적으로 만드는 것이 우선이다.

---

# 38. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Story Output을 로드할 수 있다.
Direction 입력을 검증할 수 있다.
Story Section을 Scene Candidate로 변환할 수 있다.
각 Scene Candidate에 Purpose를 지정할 수 있다.
각 Scene Candidate에 Importance를 지정할 수 있다.
각 Scene Candidate에 Visual Goal을 지정할 수 있다.
Emotion Plan을 생성할 수 있다.
Camera Plan을 생성할 수 있다.
Motion 추천 여부와 사유를 기록할 수 있다.
Editing 리듬 힌트를 기록할 수 있다.
Speculative Risk를 Scene 단위로 표시할 수 있다.
director_notes.md를 생성할 수 있다.
direction_review.json을 생성할 수 있다.
Timeline Engine으로 넘길 Handoff를 생성할 수 있다.
Direction Validation 실패 시 TIMELINE Stage 진행을 막을 수 있다.
```

---

# 39. Non Goals

v1.0에서 Direction Engine이 하지 않는 것:

```text
Timeline 최종 생성
Scene ID 최종 확정
Visual Prompt 최종 작성
이미지 직접 생성
Motion 영상 직접 생성
Voice 생성
Subtitle 생성
Final Editing
Provider 직접 호출
Quality Score 최종 계산
```

v1.0에서는 Story를 Production 가능한 장면 연출 계획으로 변환하는 것이 핵심이다.

---

# 40. Critical Direction Rules

반드시 지켜야 할 규칙:

```text
1. Direction Engine은 Story 없이 실행하지 않는다.

2. Direction Engine은 Story의 핵심 의도를 바꾸지 않는다.

3. 모든 Scene Candidate는 목적을 가져야 한다.

4. 모든 Scene Candidate는 Visual Goal을 가져야 한다.

5. 모든 Scene Candidate는 감정 또는 분위기를 가져야 한다.

6. Speculative Scene은 Risk 표시를 가져야 한다.

7. 미래 예측 장면을 확정된 사실처럼 연출하지 않는다.

8. Brand Tone을 유지한다.

9. Motion은 필요한 Scene에만 추천한다.

10. Direction Engine은 Timeline을 최종 생성하지 않는다.

11. Direction Engine은 Scene ID를 최종 확정하지 않는다.

12. Direction Engine은 Visual Prompt를 최종 작성하지 않는다.

13. Direction Engine은 Provider를 직접 호출하지 않는다.

14. Direction Validation 실패 시 TIMELINE Stage로 넘어가지 않는다.

15. 중요한 연출 판단은 Self Review와 Handoff에 기록한다.
```

---

# 41. Final Principle

Direction Engine은 Story를 영상 언어로 바꾸는 감독 엔진이다.

Story가 “무엇을 말할 것인가”라면,

Direction은 “그것을 어떻게 보이게 할 것인가”이다.

좋은 Direction은 대본을 장면으로 만들고,

장면에 감정을 주고,

Visual과 Motion의 기준을 만들고,

Editing의 리듬을 준비한다.

Direction Engine의 목적은 멋있는 장면을 많이 만드는 것이 아니다.

Direction Engine의 목적은 Story의 의도, Brand의 정체성, Factual Safety, Retention 흐름을 지키면서 실제 제작 가능한 장면 계획을 만드는 것이다.
