# 22_MOTION_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Motion Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Motion Engine을 정의한다.

Motion Engine은 Timeline, Direction, Visual Asset을 기반으로 영상에서 움직임이 필요한 Scene을 선별하고, Midjourney Video용 Motion Prompt와 Motion Asset 연결 구조를 생성하는 엔진이다.

Motion Engine은 모든 Scene을 영상화하지 않는다.

Motion Engine의 목적은 중요한 장면에만 움직임을 부여해서 Retention, 몰입감, 감정 전환, 시각적 임팩트를 높이는 것이다.

Motion Engine은 다음을 담당한다.

```text
Timeline 로드
Visual Asset 로드
Direction Motion Hint 로드
Motion 적용 Scene 선별
Source Image 확인
Scene별 Motion Prompt 생성
Midjourney Video용 Prompt Package 생성
5초 Motion 기준 적용
Provider Engine에 Motion Request 전달
Manual Provider Workflow 준비
Motion Result 등록 확인
Motion Asset Registry 연결
Timeline motion.asset_ref 업데이트
Motion Review 생성
Editing Engine에 Motion Asset Handoff 생성
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
21_VISUAL_ENGINE.md
25_EDITING_ENGINE.md
26_QUALITY_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Motion Engine은 정적인 Visual Asset 중 일부를 Motion Clip으로 확장하는 엔진이다.

전체 흐름:

```text
Timeline
↓
Visual Assets
↓
Motion Scene Selection
↓
Motion Prompts
↓
Provider Engine
↓
Midjourney Video
↓
Motion Assets
↓
Motion Review
↓
Editing / Quality
```

Motion Engine의 핵심 목표는 다음이다.

```text
Motion이 필요한 Scene만 선별한다.
Visual Source Image와 Motion Prompt를 연결한다.
Scene 목적에 맞는 움직임을 설계한다.
5초 Motion 제한을 반영한다.
Motion이 Story와 Direction을 해치지 않게 한다.
Provider Result를 Asset Registry에 등록한다.
Editing Engine이 사용할 Motion Asset 구조를 만든다.
```

---

# 3. Motion Philosophy

## 3.1 Motion Must Serve Retention

움직임은 장식이 아니다.

Motion은 시청자가 더 오래 보게 만드는 목적을 가져야 한다.

좋은 Motion:

```text
Hook에서 천천히 다가가는 카메라 움직임
세계관 공개 장면에서 공간이 확장되는 느낌
Climax에서 강한 시각 전환
감정적 Reflection에서 느린 움직임
```

나쁜 Motion:

```text
모든 이미지에 의미 없이 흔들림 추가
설명 장면마다 불필요한 카메라 이동
중요하지 않은 장면에 과도한 움직임
빠른 움직임으로 자막과 Voice 집중 방해
```

## 3.2 Not Every Scene Needs Motion

Motion Engine은 필요한 Scene만 선택한다.

기본 원칙:

```text
Motion은 선택적이다.
Motion은 Hook, Climax, Reveal, Emotional Turn 중심이다.
Motion이 Retention에 도움이 되지 않으면 만들지 않는다.
Motion이 Brand Tone을 해치면 만들지 않는다.
```

## 3.3 Source Image First

Motion은 반드시 Source Image가 있어야 한다.

Visual Asset 없이 Motion Request를 만들지 않는다.

```text
Visual Image
↓
Motion Prompt
↓
Midjourney Video
↓
Motion Clip
```

## 3.4 Provider Independent

Motion Engine은 Midjourney Video를 직접 실행하지 않는다.

반드시 Provider Engine을 통해 Request를 만든다.

```text
Motion Engine
↓
Provider Engine
↓
MotionProviderInterface
↓
MidjourneyVideoAdapter
```

---

# 4. Motion Engine Responsibilities

Motion Engine의 책임:

```text
Timeline 로드
Timeline Lock 확인
Visual Review 로드
Asset Registry 로드
Direction Motion Hint 로드
Scene별 Motion 필요성 분석
Motion Candidate 선정
Source Image 존재 확인
Motion Prompt Brief 생성
Midjourney Video Prompt 생성
Motion Provider Request 생성 요청
Manual Action Guide 생성 지원
Motion Result 등록 확인
Motion Asset Registry 업데이트
Timeline motion.asset_ref 업데이트
Motion Review 생성
Editing Engine Handoff 생성
```

Motion Engine이 하지 않는 것:

```text
이미지를 직접 생성하지 않는다.
Motion 영상을 직접 생성하지 않는다.
Midjourney Video를 직접 호출하지 않는다.
Timeline Scene ID를 변경하지 않는다.
Story를 수정하지 않는다.
Direction을 임의 변경하지 않는다.
Voice를 생성하지 않는다.
Subtitle을 생성하지 않는다.
Final Editing을 수행하지 않는다.
Quality Score를 최종 계산하지 않는다.
```

---

# 5. Inputs

Motion Engine의 입력:

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
prompts/midjourney_image_prompts.json
reports/visual_review.json
assets/asset_registry.json
channels/{channel_id}/motion.yaml
channels/{channel_id}/provider.yaml
workflow/handoffs/VISUAL_to_MOTION.json
workflow/memory_context_MOTION.json
```

필수 입력:

```text
timeline/timeline.json
timeline/timeline_lock.json
assets/asset_registry.json
reports/visual_review.json
project.json
channel_snapshot.json
```

선택 입력:

```text
direction/camera_plan.json
direction/director_notes.md
workflow/handoffs/VISUAL_to_MOTION.json
Motion Success Memory
Motion Failure Memory
Midjourney Video Provider Memory
Editing Rhythm Memory
```

---

# 6. Outputs

Motion Engine의 출력:

```text
prompts/motion_prompt_briefs.json
prompts/midjourney_video_prompts.json
reports/motion_review.json
assets/asset_registry.json
workflow/stage_results/MOTION_result.json
workflow/handoffs/MOTION_to_EDITING.json
```

Provider Engine과 연결되는 파일:

```text
provider_requests/motion_requests.jsonl
provider_responses/motion_responses.jsonl
```

실제 Motion 결과물 위치:

```text
assets/motion/SC001_motion_v001.mp4
assets/motion/SC008_motion_v001.mp4
assets/motion/SC014_motion_v001.mp4
```

v1.0 최소 출력:

```text
prompts/midjourney_video_prompts.json
reports/motion_review.json
```

---

# 7. Motion Creation Flow

Motion Engine 실행 흐름:

```text
Load Project Context
↓
Load Timeline
↓
Load Timeline Lock
↓
Load Visual Asset Registry
↓
Load Visual Review
↓
Load Direction Motion Hints
↓
Load Motion Rules
↓
Load Memory Context
↓
Validate Motion Inputs
↓
Select Motion Candidate Scenes
↓
Check Source Images
↓
Build Motion Prompt Briefs
↓
Generate Midjourney Video Prompts
↓
Apply Motion Avoid Rules
↓
Apply Brand and Speculation Safety
↓
Request Provider Engine to Create Motion Requests
↓
Wait for Manual or Registered Results
↓
Register Motion Assets
↓
Update Timeline Motion References
↓
Build Motion Review
↓
Handoff to Editing Engine
```

---

# 8. Motion Selection Rules

Motion은 다음 Scene에 우선 적용한다.

```text
hook
climax
world_reveal
major_reveal
emotional_turn
important_transition
ending_reflection
```

Motion 우선순위 기준:

```yaml
motion_priority:
  scene_importance: 25
  retention_value: 25
  visual_strength: 20
  direction_motion_hint: 15
  editing_value: 10
  provider_feasibility: 5
```

Motion이 필요하지 않은 경우:

```text
Scene importance가 low
단순 설명 장면
Source Image 품질이 낮음
Motion이 Voice 집중을 방해함
Motion이 Brand Tone과 맞지 않음
Motion Prompt가 지나치게 불안정함
```

---

# 9. Motion Candidate Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "motion_candidates": [
    {
      "scene_id": "SC001",
      "order": 1,
      "purpose": "hook",
      "importance": "critical",

      "selection": {
        "selected": true,
        "priority": "high",
        "score": 94,
        "reason": "Opening hook scene with strong retention and visual impact."
      },

      "source_image": {
        "asset_ref": "assets/images/SC001_image_v001.png",
        "asset_id": "ASSET-IMG-000001",
        "valid": true
      },

      "motion_direction": {
        "motion_type": "slow_cinematic_push_in",
        "camera_movement": "slow push-in",
        "subject_motion": "subtle environmental movement",
        "duration_seconds": 5,
        "mood": "mysterious, cinematic, reflective"
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

# 10. Motion Prompt Briefs

Motion Prompt Brief는 Midjourney Video Prompt를 만들기 전 구조화된 지시서이다.

파일:

```text
prompts/motion_prompt_briefs.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",

  "briefs": [
    {
      "scene_id": "SC001",
      "source_image": "assets/images/SC001_image_v001.png",

      "motion_goal": "Make the opening image feel alive while preserving a quiet cinematic mystery.",

      "camera": {
        "movement": "slow push-in",
        "speed": "very slow",
        "stability": "stable cinematic camera"
      },

      "subject_motion": {
        "primary": "subtle atmospheric movement",
        "secondary": "soft light movement across the settlement",
        "avoid": [
          "fast action",
          "shaky camera",
          "distorted human body",
          "sudden transformation"
        ]
      },

      "emotion": {
        "mood": "mysterious, awe, reflective",
        "viewer_feeling": "The viewer should feel they are entering a possible future."
      },

      "duration_seconds": 5,

      "risk": {
        "speculative": true,
        "required_treatment": "simulation-like future scenario"
      }
    }
  ]
}
```

---

# 11. Midjourney Video Prompt Rules

Midjourney Video Prompt는 다음 요소를 포함해야 한다.

```text
Source Image Reference
Motion Goal
Camera Movement
Subject Motion
Speed
Mood
Avoid Rule
Duration Assumption
```

권장 구조:

```text
[slow camera movement], [subtle subject/environment motion], [mood], [preserve original composition], [avoid distortions]
```

예시:

```text
slow cinematic push-in toward the futuristic settlement, subtle atmospheric movement, soft alien sunrise light shifting gently across the scene, preserve the original composition and realistic documentary mood, mysterious and reflective feeling, no fast motion, no shaky camera, no distorted anatomy, no text, no logo
```

---

# 12. midjourney_video_prompts.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "provider": "midjourney_video",

  "prompts": [
    {
      "prompt_id": "MJ-VID-000001",
      "scene_id": "SC001",
      "source_image_ref": "assets/images/SC001_image_v001.png",

      "prompt": "slow cinematic push-in toward the futuristic settlement, subtle atmospheric movement, soft alien sunrise light shifting gently across the scene, preserve the original composition and realistic documentary mood, mysterious and reflective feeling, no fast motion, no shaky camera, no distorted anatomy, no text, no logo",

      "motion_components": {
        "camera_movement": "slow push-in",
        "subject_motion": "subtle atmospheric movement",
        "speed": "slow",
        "mood": "mysterious, cinematic, reflective",
        "avoid": [
          "fast motion",
          "shaky camera",
          "distorted anatomy",
          "warped buildings",
          "text",
          "logo",
          "watermark"
        ]
      },

      "provider_settings": {
        "duration_seconds": 5,
        "mode": "image_to_video"
      },

      "expected_output": {
        "asset_type": "motion",
        "file": "assets/motion/SC001_motion_v001.mp4"
      },

      "status": "READY_FOR_PROVIDER"
    }
  ]
}
```

---

# 13. Motion Quality Rules

좋은 Motion 조건:

```text
Scene Purpose를 강화한다.
Source Image의 구도와 분위기를 유지한다.
움직임이 과하지 않다.
Camera Movement가 Direction과 맞다.
Brand Tone을 해치지 않는다.
Subject가 심하게 왜곡되지 않는다.
Motion이 Voice와 Subtitle 집중을 방해하지 않는다.
Editing에 사용할 수 있다.
```

나쁜 Motion:

```text
Source Image와 다른 장면으로 변함
얼굴이나 몸이 심하게 왜곡됨
건물이나 배경이 녹아내림
너무 빠른 움직임
불필요한 카메라 흔들림
텍스트나 로고 생성
Speculative Scene을 확정된 사실처럼 보이게 함
```

---

# 14. Motion Duration Rules

v1.0 기본 Motion Clip 길이:

```text
5 seconds
```

규칙:

```text
Midjourney Video 결과는 기본 5초 Clip으로 취급한다.
Timeline Scene Duration이 5초보다 길면 Editing에서 Loop, Hold, Cutaway를 고려한다.
Timeline Scene Duration이 5초보다 짧으면 Editing에서 필요한 구간만 사용한다.
Motion Engine은 Timeline 전체 길이를 직접 수정하지 않는다.
```

Motion Clip 길이가 실제 결과와 다르면 Asset Registry와 Motion Review에 기록한다.

---

# 15. Motion Asset Naming Rules

Motion 파일명은 Scene ID를 포함해야 한다.

기본 형식:

```text
assets/motion/{scene_id}_motion_v{version}.mp4
```

예시:

```text
assets/motion/SC001_motion_v001.mp4
assets/motion/SC008_motion_v001.mp4
assets/motion/SC014_motion_v001.mp4
```

대체 후보가 있는 경우:

```text
assets/motion/SC001_motion_v001_a.mp4
assets/motion/SC001_motion_v001_b.mp4
assets/motion/SC001_motion_v001_selected.mp4
```

최종 선택본은 Asset Registry에 등록되어야 한다.

---

# 16. Provider Engine Integration

Motion Engine은 Provider Engine을 통해 Motion Request를 만든다.

흐름:

```text
Motion Prompt 생성
↓
Provider Engine에 Request 생성 요청
↓
Provider Engine이 MotionProviderInterface 사용
↓
MidjourneyVideoAdapter가 Manual Action Guide 생성
↓
사용자가 Midjourney Video에서 Motion 생성
↓
결과 파일을 assets/motion/에 저장
↓
Provider Engine이 Result 등록
↓
Motion Engine이 Asset 연결 확인
```

Motion Engine은 Midjourney Video를 직접 호출하지 않는다.

---

# 17. Motion Provider Request Mapping

Motion Engine은 다음 정보를 Provider Engine에 전달한다.

```text
project_id
channel_id
stage = MOTION
provider_type = motion
provider_name = midjourney_video
scene_id
source_image_ref
prompt
expected_output
duration_seconds = 5
avoid_rules
```

Provider Request 예시:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "MOTION",
  "provider_type": "motion",
  "provider_name": "midjourney_video",
  "scene_id": "SC001",
  "source_image_ref": "assets/images/SC001_image_v001.png",
  "prompt_ref": "prompts/midjourney_video_prompts.json",
  "expected_output": "assets/motion/SC001_motion_v001.mp4"
}
```

---

# 18. Asset Registry Integration

Motion 결과물은 반드시 Asset Registry에 등록되어야 한다.

파일:

```text
assets/asset_registry.json
```

Motion Asset Entry 예시:

```json
{
  "asset_id": "ASSET-MOT-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "scene_id": "SC001",
  "asset_type": "motion",
  "provider": "midjourney_video",
  "source_image_ref": "assets/images/SC001_image_v001.png",
  "file": "assets/motion/SC001_motion_v001.mp4",
  "prompt_id": "MJ-VID-000001",
  "request_id": "PROV-REQ-000101",
  "response_id": "PROV-RES-000101",
  "duration_seconds": 5,
  "status": "REGISTERED",
  "selected": true,
  "created_at": "2026-07-10T12:30:00"
}
```

규칙:

```text
Motion 파일만 있으면 완료가 아니다.
Asset Registry에 등록되어야 한다.
Scene ID와 일치해야 한다.
Source Image와 연결되어야 한다.
Editing Engine은 Asset Registry를 기준으로 Motion Asset을 찾는다.
```

---

# 19. Timeline Update Rules

Motion Asset이 등록되면 Timeline의 해당 Scene에 motion.asset_ref를 업데이트할 수 있다.

허용 업데이트:

```text
timeline.scenes[].motion.source_image_ref
timeline.scenes[].motion.asset_ref
timeline.scenes[].quality.issues
```

금지 업데이트:

```text
scene_id 변경
scene_order 변경
scene_purpose 변경
timing 구조 무단 변경
language_tracks 삭제
```

Timeline Lock을 위반하면 안 된다.

---

# 20. motion_review.json Schema

Motion Review는 Motion Prompt와 등록된 Motion 결과를 함께 검토한다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "MOTION",

  "score": 92,
  "status": "PASS_WITH_NOTES",

  "summary": {
    "total_scenes": 18,
    "motion_candidate_count": 4,
    "motion_created_count": 3,
    "motion_skipped_count": 1
  },

  "scene_reviews": [
    {
      "scene_id": "SC001",
      "prompt_id": "MJ-VID-000001",
      "source_image_ref": "assets/images/SC001_image_v001.png",
      "asset_ref": "assets/motion/SC001_motion_v001.mp4",

      "checks": {
        "asset_exists": true,
        "source_image_valid": true,
        "scene_match": true,
        "motion_purpose_clear": true,
        "brand_fit": 94,
        "direction_fit": 93,
        "motion_quality": 92,
        "no_distortion": true,
        "no_text_or_watermark": true,
        "speculation_safety": true,
        "editing_ready": true
      },

      "issues": []
    }
  ],

  "overall_issues": [],
  "handoff_notes": [
    "SC001 motion is ready for Editing Engine.",
    "Use SC001 motion for the first 5 seconds, then hold or cut to next scene if needed."
  ]
}
```

---

# 21. Motion Scoring

Motion Score 기준:

```yaml
motion_score:
  candidate_selection_quality: 15
  source_image_integrity: 15
  direction_fit: 15
  brand_fit: 10
  motion_quality: 15
  distortion_avoidance: 10
  editing_readiness: 10
  speculation_safety: 5
  asset_registry_integrity: 5
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
Motion fail
```

Hard Fail 조건:

```text
Scene ID 불일치
Source Image 누락
Motion Asset 누락
심각한 영상 왜곡
Brand 심각한 위반
텍스트 / 워터마크 포함
Speculative Scene을 확정 사실처럼 표현
Timeline Lock 위반
Asset Registry 누락
```

---

# 22. Motion Validation Rules

Motion Validator는 다음을 확인해야 한다.

```text
prompts/midjourney_video_prompts.json 존재
reports/motion_review.json 존재
project_id 일치
channel_id 일치
Motion Prompt마다 scene_id 존재
Motion Prompt마다 source_image_ref 존재
Motion Prompt마다 expected_output 존재
Source Image가 Asset Registry에 존재
Scene ID 중복 없음
Motion Prompt가 비어 있지 않음
Avoid Rule 포함
Duration 기본값 존재
Asset Registry 연결 확인
Timeline Lock 위반 없음
```

검증 실패 시 다음 Stage로 이동할 수 없다.

단, Manual Provider Result가 아직 없으면 Workflow는 `WAITING_FOR_MANUAL_ACTION` 상태가 될 수 있다.

---

# 23. Motion Skip Rules

Motion이 필요 없는 Scene은 명시적으로 Skip 처리할 수 있다.

Skip Entry 예시:

```json
{
  "scene_id": "SC006",
  "selected": false,
  "skip_reason": "Informational explanation scene; static image is sufficient.",
  "review_required": false
}
```

Skip은 실패가 아니다.

오히려 불필요한 Motion을 줄이는 것이 좋은 판단일 수 있다.

Motion Review에는 Skip Reason이 기록되어야 한다.

---

# 24. Auto Fix Rules

Motion 문제 발생 시 부분 수정이 우선이다.

수정 대상:

```text
특정 Scene Motion Prompt
특정 Scene Motion Asset
Source Image 재선택
Motion 속도 조정
Motion Direction 수정
Brand 위반 Motion
Distortion 발생 Motion
```

금지:

```text
전체 Project 재생성
전체 Timeline 재생성
Story 임의 수정
Scene ID 변경
필요 없는 Scene까지 Motion 확대
```

Auto Fix 예시:

```text
Issue:
SC001 motion has distorted human silhouette.

Fix:
Revise only SC001 Motion Prompt with stronger "preserve human silhouette, no body distortion" avoid rule and regenerate SC001 motion.
```

---

# 25. Handoff to Editing Engine

Motion Engine은 Editing Engine에 Motion Asset 정보를 넘긴다.

Handoff 파일:

```text
workflow/handoffs/MOTION_to_EDITING.json
```

포함 내용:

```text
Motion 적용 Scene
Motion Asset Ref
Source Image Ref
Duration
Scene Purpose
Editing Usage Note
Motion Quality Issue
Fallback Image
```

예시:

```json
{
  "from_stage": "MOTION",
  "to_stage": "EDITING",
  "project_id": "20260710-093500-future-million-year-human",

  "motion_assets": [
    {
      "scene_id": "SC001",
      "motion_asset_ref": "assets/motion/SC001_motion_v001.mp4",
      "source_image_ref": "assets/images/SC001_image_v001.png",
      "duration_seconds": 5,
      "usage": "Use as opening motion clip.",
      "fallback": "assets/images/SC001_image_v001.png",
      "issues": []
    }
  ],

  "editing_notes": [
    "Use motion clips only where they strengthen retention.",
    "Do not overuse motion in explanation-heavy sections."
  ]
}
```

---

# 26. Memory Integration

Motion Engine은 작업 전 Memory Context를 사용한다.

사용 가능한 Memory:

```text
Successful Motion Prompt Memory
Failed Motion Prompt Memory
Midjourney Video Failure Pattern
Motion Distortion Memory
Editing Motion Usage Memory
Brand Motion Memory
Quality Motion Failure Memory
```

Motion Engine은 작업 후 Memory Candidate를 만들 수 있다.

예시:

```text
특정 Motion Prompt가 잘 작동함
특정 움직임 표현이 왜곡을 자주 만듦
Hook Scene에서 효과적인 Motion 패턴 발견
Brand와 맞지 않는 Motion 스타일 발견
```

Memory 확정은 Memory Engine 또는 Learning Engine이 담당한다.

---

# 27. Error Types

Motion Engine의 Error Type:

```text
MotionInputMissingError
TimelineMissingError
TimelineLockMissingError
VisualAssetMissingError
SourceImageMissingError
MotionCandidateSelectionError
MotionPromptCreationError
MotionPromptValidationError
MotionProviderRequestError
MotionAssetMissingError
MotionAssetRegistrationError
MotionSceneIdMismatchError
MotionDistortionError
MotionBrandMismatchError
MotionSpeculationRiskError
MotionReviewError
MotionValidationError
MotionHandoffError
```

Error 예시:

```json
{
  "error_type": "SourceImageMissingError",
  "message": "Motion candidate SC001 has no valid source image.",
  "project_id": "20260710-093500-future-million-year-human",
  "scene_id": "SC001",
  "stage": "MOTION",
  "severity": "HIGH",
  "suggested_fix": "Complete Visual Stage and register SC001 source image before Motion Stage.",
  "created_at": "2026-07-10T12:30:00"
}
```

---

# 28. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
MotionEngine
MotionInputLoader
MotionInputValidator
MotionCandidateSelector
MotionPromptBriefBuilder
MidjourneyVideoPromptBuilder
MotionAvoidRuleApplier
MotionSourceImageValidator
BrandMotionChecker
SpeculationMotionRiskChecker
MotionProviderRequestBuilder
MotionAssetRegistryUpdater
MotionTimelineUpdater
MotionReviewBuilder
MotionValidator
MotionHandoffBuilder
MotionErrorReporter
```

---

# 29. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/22_MOTION_ENGINE.md
→ engines/motion/
```

예시 구조:

```text
engines/
└── motion/
    ├── motion_engine.py
    ├── motion_input_loader.py
    ├── motion_input_validator.py
    ├── motion_candidate_selector.py
    ├── motion_prompt_brief_builder.py
    ├── midjourney_video_prompt_builder.py
    ├── motion_avoid_rule_applier.py
    ├── motion_source_image_validator.py
    ├── brand_motion_checker.py
    ├── speculation_motion_risk_checker.py
    ├── motion_provider_request_builder.py
    ├── motion_asset_registry_updater.py
    ├── motion_timeline_updater.py
    ├── motion_review_builder.py
    ├── motion_validator.py
    ├── motion_handoff_builder.py
    └── motion_error_reporter.py
```

---

# 30. Main Public Operations

Motion Engine은 최소 다음 작업을 제공해야 한다.

```text
run_motion(project_id)
load_motion_inputs(project_id)
validate_motion_inputs(project_id)
select_motion_candidates(project_id)
validate_source_images(project_id)
build_motion_prompt_briefs(project_id)
build_midjourney_video_prompts(project_id)
apply_motion_avoid_rules(project_id)
check_brand_motion_fit(project_id)
check_speculation_motion_risk(project_id)
create_motion_provider_requests(project_id)
register_motion_assets(project_id)
update_timeline_motion_refs(project_id)
build_motion_review(project_id)
validate_motion_outputs(project_id)
build_handoff_to_editing(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
Timeline Scene ID 유지
Source Image 확인
Motion 필요 Scene만 선택
Direction Motion Hint 반영
Provider Engine 경유
Asset Registry 연결
Timeline Lock 준수
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 31. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Timeline 로드
Visual Asset Registry 로드
Visual Review 로드
Motion 입력 검증
Motion Candidate Scene 선택
Source Image 검증
Scene별 Midjourney Video Prompt 생성
midjourney_video_prompts.json 생성
Provider Request 생성용 데이터 준비
Manual Action Guide 지원
Motion Asset 등록 확인
Timeline motion.asset_ref 업데이트
motion_review.json 생성
Editing Engine Handoff 생성
Motion Validation 수행
```

v1.0에서 하지 않아도 되는 것:

```text
Midjourney Video 완전 자동 호출
Motion 영상 직접 생성
고급 영상 왜곡 자동 판별
복잡한 모션 트래킹
실시간 영상 편집
Frame 단위 Motion 제어
Final Editing 수행
Provider 직접 호출
```

v1.0에서는 Midjourney Video Manual Workflow를 안정적으로 지원하고, 필요한 Scene에만 Motion Asset을 연결하는 구조를 만드는 것이 우선이다.

---

# 32. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Timeline과 Visual Asset Registry를 로드할 수 있다.
Motion 입력을 검증할 수 있다.
Motion이 필요한 Scene을 선별할 수 있다.
Motion이 필요 없는 Scene을 Skip 처리할 수 있다.
Source Image 존재를 확인할 수 있다.
각 Motion Scene의 Midjourney Video Prompt를 만들 수 있다.
Duration 5초 기준을 반영할 수 있다.
Avoid Rule을 Motion Prompt에 반영할 수 있다.
Provider Engine용 Motion Request를 준비할 수 있다.
Motion Asset을 Asset Registry와 연결할 수 있다.
Timeline의 motion.asset_ref를 업데이트할 수 있다.
motion_review.json을 생성할 수 있다.
Editing Engine으로 Motion Asset Handoff를 만들 수 있다.
Motion Validation 실패 시 다음 Stage 진행을 막을 수 있다.
```

---

# 33. Non Goals

v1.0에서 Motion Engine이 하지 않는 것:

```text
Motion 영상 직접 생성
Midjourney Video 직접 호출
이미지 직접 생성
Voice 생성
Subtitle 생성
Final Editing
Quality Score 최종 계산
Timeline Scene ID 변경
Story 임의 수정
Direction 임의 수정
모든 Scene Motion화
```

v1.0에서는 필요한 Scene만 선별하고, Midjourney Video용 Motion Prompt와 Asset 연결 구조를 안정적으로 만드는 것이 핵심이다.

---

# 34. Critical Motion Rules

반드시 지켜야 할 규칙:

```text
1. Motion Engine은 Timeline 없이 실행하지 않는다.

2. Motion Engine은 Visual Asset 없이 실행하지 않는다.

3. Motion Engine은 Scene ID를 변경하지 않는다.

4. Motion은 모든 Scene에 적용하지 않는다.

5. Motion은 Hook, Climax, Reveal, Emotional Turn 중심으로 적용한다.

6. Source Image가 없으면 Motion Request를 만들지 않는다.

7. Motion Prompt는 Direction의 Motion Hint를 반영해야 한다.

8. Motion Prompt는 Avoid Rule을 포함해야 한다.

9. Motion Clip은 기본 5초 기준으로 관리한다.

10. Motion Engine은 Midjourney Video를 직접 호출하지 않는다.

11. Provider Engine을 통해 Motion Request를 만든다.

12. Motion 결과물은 Asset Registry에 등록해야 한다.

13. Timeline Lock을 위반하지 않는다.

14. Motion Validation 실패 시 다음 Stage로 넘어가지 않는다.

15. 중요한 Motion 판단은 Self Review와 Handoff에 기록한다.
```

---

# 35. Final Principle

Motion Engine은 정적인 이미지를 필요한 순간에만 움직이게 만드는 엔진이다.

좋은 Motion은 영상 전체를 요란하게 만들지 않는다.

좋은 Motion은 Hook을 강화하고,

세계관을 열고,

감정 전환을 깊게 만들고,

Editing의 리듬을 살리고,

시청자가 조금 더 오래 보게 만든다.

Motion Engine의 목적은 모든 장면을 움직이게 만드는 것이 아니라, 꼭 움직여야 하는 장면만 정확히 움직이게 만드는 것이다.
