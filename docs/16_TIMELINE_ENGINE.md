# 16_TIMELINE_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Timeline Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Timeline Engine을 정의한다.

Timeline Engine은 Story와 Direction을 실제 영상 제작 가능한 시간 구조로 변환하는 엔진이다.

ADOS에서 Timeline은 단순한 장면 목록이 아니다.

Timeline은 다음 요소를 하나로 연결하는 영상 제작의 중심 설계도이다.

```text
Scene
Narration
Subtitle
Image
Motion
Audio
Transition
Timing
Asset Mapping
Language Version
Quality Check
Editing Plan
```

Timeline Engine은 다음을 담당한다.

```text
Scene 구조 생성
Scene ID 관리
Scene 순서 관리
Scene별 목적 정의
Scene별 시간 구조 설계
Visual / Motion / Voice / Subtitle 연결
언어별 길이 차이 대응
Asset Mapping 기준 생성
Timeline Validation
Timeline Lock 생성
Editing Engine이 사용할 Final Timeline 준비
Quality Engine이 검사할 Timeline Integrity 제공
```

이 문서는 다음 문서들과 직접 연결된다.

```text
03_ARCHITECTURE.md
07_PROJECT_SPEC.md
12_PROJECT_ENGINE.md
14_PROVIDER_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
19_STORY_ENGINE.md
20_DIRECTION_ENGINE.md
21_VISUAL_ENGINE.md
22_MOTION_ENGINE.md
23_VOICE_ENGINE.md
24_SUBTITLE_ENGINE.md
25_EDITING_ENGINE.md
26_QUALITY_ENGINE.md
```

---

# 2. Core Definition

Timeline은 Project의 핵심 제작 설계도이다.

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

Timeline은 다음 질문에 답해야 한다.

```text
영상은 몇 개의 Scene으로 구성되는가?
각 Scene의 목적은 무엇인가?
각 Scene은 몇 초인가?
각 Scene에는 어떤 이미지가 필요한가?
어떤 Scene에 Motion이 필요한가?
각 Scene에는 어떤 나레이션이 들어가는가?
자막은 어디에 연결되는가?
언어별 Voice 길이 차이는 어떻게 처리하는가?
Editing Engine은 어떤 순서로 Asset을 배치해야 하는가?
Quality Engine은 어떤 기준으로 Timeline을 검사해야 하는가?
```

---

# 3. Timeline Philosophy

## 3.1 Timeline First

영상 제작의 중심은 최종 mp4 파일이 아니다.

중심은 Timeline이다.

Timeline이 명확해야 다음 엔진들이 안정적으로 작업할 수 있다.

```text
Timeline이 약하면
→ Visual Prompt가 흔들림
→ Motion 적용 기준이 흔들림
→ Voice 길이가 안 맞음
→ Subtitle Sync가 깨짐
→ Editing이 불안정함
→ Quality Fail 발생
```

## 3.2 Scene ID Must Be Stable

Scene ID는 Project 안에서 변하면 안 된다.

금지:

```text
SC001을 중간에 SC003으로 변경
Scene 순서 수정 후 기존 Scene ID 재사용
Visual 생성 후 Scene ID 변경
```

허용:

```text
Scene 추가 시 새 Scene ID 부여
Scene 삭제 시 삭제 기록 남김
Scene 수정 시 기존 Scene ID 유지
```

## 3.3 Timeline Must Be Production-Ready

Timeline은 창작 아이디어 메모가 아니다.

Timeline은 Production Engine이 바로 사용할 수 있는 구조여야 한다.

## 3.4 Shared Visual, Language-Specific Audio

다국어 Project에서는 기본적으로 Visual과 Motion은 공유하고, Voice와 Subtitle은 언어별로 분리한다.

```text
Shared:
Scene Structure
Visual
Motion
Thumbnail Base

Language-Specific:
Voice
Subtitle
Script Localization
Metadata
Final Video
```

---

# 4. Timeline Engine Responsibilities

Timeline Engine의 책임은 다음과 같다.

```text
Direction 결과 로드
Story Script 로드
Scene Plan 검증
Scene ID 생성
Scene 순서 정리
Scene별 목적 정의
Scene별 중요도 정의
Scene별 예상 시간 배정
Visual Requirement 정의
Motion Requirement 정의
Voice Requirement 정의
Subtitle Requirement 정의
Language Track 정의
Asset Mapping Placeholder 생성
Timeline JSON 생성
Timeline Review 생성
Timeline Lock 생성
Timeline Validation 수행
Editing Engine용 Timeline Context 제공
Quality Engine용 Timeline Integrity 결과 제공
```

Timeline Engine이 하지 않는 것:

```text
이미지를 직접 생성하지 않는다.
Motion 영상을 직접 생성하지 않는다.
Voice 파일을 직접 생성하지 않는다.
Subtitle 파일을 직접 생성하지 않는다.
Final Video를 직접 렌더링하지 않는다.
Quality Score를 최종 계산하지 않는다.
Provider를 직접 호출하지 않는다.
```

---

# 5. Timeline Inputs

Timeline Engine의 주요 입력:

```text
project.json
topic.json
channel_snapshot.json
template_snapshot.json
story/script_master.json
story/script_master.md
direction/scene_plan.json
direction/emotion_plan.json
direction/camera_plan.json
direction/director_notes.md
visual.yaml
motion.yaml
voice.yaml
subtitle.yaml
quality.yaml
```

필수 입력:

```text
story/script_master.json
direction/scene_plan.json
channel_snapshot.json
project.json
```

선택 입력:

```text
direction/emotion_plan.json
direction/camera_plan.json
direction/director_notes.md
languages/{lang}/script.json
```

---

# 6. Timeline Outputs

Timeline Engine의 주요 출력:

```text
timeline/timeline.json
timeline/timeline_review.json
timeline/timeline_lock.json
workflow/stage_results/TIMELINE_result.json
```

추가로 생성 가능:

```text
timeline/scene_index.json
timeline/asset_mapping_plan.json
timeline/language_timing_plan.json
timeline/motion_selection_plan.json
```

v1.0 최소 출력:

```text
timeline/timeline.json
timeline/timeline_review.json
timeline/timeline_lock.json
```

---

# 7. Timeline Creation Flow

Timeline 생성 흐름:

```text
Load Project Context
↓
Load Story Script
↓
Load Direction Scene Plan
↓
Validate Scene Plan
↓
Generate Stable Scene IDs
↓
Assign Scene Order
↓
Assign Scene Purpose
↓
Estimate Scene Duration
↓
Map Visual Requirements
↓
Map Motion Requirements
↓
Map Voice Requirements
↓
Map Subtitle Requirements
↓
Build Language Tracks
↓
Create timeline.json
↓
Validate Timeline
↓
Create timeline_review.json
↓
Create timeline_lock.json
↓
Handoff to Visual / Motion / Voice / Subtitle
```

---

# 8. timeline.json Schema

`timeline/timeline.json`은 다음 구조를 따른다.

```json
{
  "timeline_id": "TL-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "version": "1.0.0",
  "status": "DRAFT",

  "video": {
    "format": "youtube_longform",
    "aspect_ratio": "16:9",
    "fps": 30,
    "target_duration_seconds": null,
    "estimated_total_duration_seconds": 900
  },

  "languages": {
    "base_language": "ko",
    "target_languages": [
      "ko",
      "en"
    ],
    "visual_shared": true,
    "motion_shared": true,
    "voice_per_language": true,
    "subtitle_per_language": true
  },

  "scenes": [
    {
      "scene_id": "SC001",
      "order": 1,
      "status": "PLANNED",

      "timing": {
        "start_time": "00:00:00",
        "end_time": "00:00:08",
        "duration_seconds": 8,
        "estimated": true
      },

      "purpose": "hook",
      "importance": "critical",
      "emotion": "mystery",

      "story": {
        "script_ref": "story/script_master.json",
        "summary": "Opening future scenario.",
        "narration_ref": null
      },

      "direction": {
        "scene_plan_ref": "direction/scene_plan.json",
        "camera": "slow cinematic push-in",
        "visual_goal": "Create immediate curiosity about the future of humanity."
      },

      "visual": {
        "required": true,
        "asset_type": "image",
        "prompt_ref": null,
        "asset_ref": null,
        "provider": "midjourney"
      },

      "motion": {
        "required": true,
        "reason": "hook_scene",
        "source_image_ref": null,
        "asset_ref": null,
        "duration_seconds": 5,
        "provider": "midjourney_video"
      },

      "voice": {
        "required": true,
        "language_tracks": {
          "ko": {
            "script_ref": "languages/ko/script.json",
            "voice_ref": null,
            "estimated_duration_seconds": 8
          },
          "en": {
            "script_ref": "languages/en/script.json",
            "voice_ref": null,
            "estimated_duration_seconds": 9
          }
        }
      },

      "subtitle": {
        "required": true,
        "language_tracks": {
          "ko": {
            "subtitle_ref": null
          },
          "en": {
            "subtitle_ref": null
          }
        }
      },

      "editing": {
        "transition_in": "cut",
        "transition_out": "slow_fade",
        "notes": []
      },

      "quality": {
        "requires_review": true,
        "scene_score": null,
        "hard_fail": false,
        "issues": []
      }
    }
  ],

  "validation": {
    "scene_id_valid": true,
    "timing_valid": true,
    "asset_mapping_ready": true,
    "language_tracks_valid": true,
    "issues": []
  },

  "created_at": "2026-07-10T10:00:00",
  "updated_at": "2026-07-10T10:00:00"
}
```

---

# 9. Scene ID Rules

Scene ID 형식:

```text
SC001
SC002
SC003
```

규칙:

```text
Scene ID는 Project 안에서 유일해야 한다.
Scene ID는 3자리 숫자를 사용한다.
Scene ID는 생성 후 임의 변경하지 않는다.
Scene 순서 변경 시에도 기존 Scene ID를 유지한다.
삭제된 Scene ID는 재사용하지 않는다.
추가 Scene은 새 ID를 부여한다.
```

잘못된 예:

```text
scene1
S1
001
SC1
SC-001
```

올바른 예:

```text
SC001
SC002
SC003
```

---

# 10. Scene Purpose Types

Scene은 목적을 가져야 한다.

기본 Purpose:

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

Purpose는 다음 Engine에 영향을 준다.

```text
Visual Engine
→ 어떤 이미지가 필요한지 판단

Motion Engine
→ Motion 적용 여부 판단

Voice Engine
→ 감정과 속도 판단

Editing Engine
→ 전환과 리듬 판단

Quality Engine
→ Scene 역할 수행 여부 검사
```

---

# 11. Scene Importance Levels

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
Hook, Climax, Major Reveal, Ending

high
중요한 설명, 감정 전환, 핵심 근거

medium
일반 설명, 연결 장면

low
보조 장면, 짧은 전환
```

Motion 적용은 보통 `critical` 또는 `high` Scene을 우선한다.

---

# 12. Timing Rules

Timeline은 각 Scene의 시간 정보를 가져야 한다.

기본 필드:

```text
start_time
end_time
duration_seconds
estimated
```

규칙:

```text
duration_seconds는 0보다 커야 한다.
Scene 순서상 시간이 겹치면 안 된다.
start_time은 이전 Scene의 end_time과 연결되어야 한다.
estimated가 true인 경우 Voice 생성 후 조정 가능하다.
Voice 생성 후 실제 Audio 길이에 맞춰 조정할 수 있다.
```

v1.0에서는 완벽한 프레임 단위 정확도보다 논리적 시간 구조가 우선이다.

---

# 13. Duration Strategy

영상 길이는 고정값보다 Retention 중심으로 설계한다.

Timeline Engine은 다음을 고려한다.

```text
Topic Complexity
Story Structure
Channel Style
Target Audience
Voice Speed
Language Difference
Scene Density
Retention Risk
```

권장 기준:

```text
Hook
5~30초

Core Explanation Scene
20~90초

Visual Reveal Scene
5~15초

Reflection / Ending
20~60초
```

Scene이 너무 길면 분할을 고려한다.

---

# 14. Language Timing Rules

다국어 Project에서는 언어별 Voice 길이가 다를 수 있다.

규칙:

```text
Base Timeline은 공유한다.
Voice와 Subtitle은 언어별로 분리한다.
언어별 길이 차이는 language_tracks에 기록한다.
큰 길이 차이가 있으면 Timeline Review에서 표시한다.
Final Editing에서 언어별 조정이 가능해야 한다.
```

언어별 길이 차이 예시:

```json
{
  "scene_id": "SC001",
  "ko_duration_seconds": 8,
  "en_duration_seconds": 10,
  "difference_seconds": 2,
  "requires_timing_adjustment": true
}
```

---

# 15. Visual Mapping Rules

Timeline은 Visual Engine이 사용할 기준을 제공해야 한다.

각 Scene의 Visual 필드:

```text
required
asset_type
prompt_ref
asset_ref
provider
visual_goal
```

규칙:

```text
모든 Scene은 기본적으로 이미지가 필요하다.
설명 Scene도 최소 하나의 Visual 방향을 가져야 한다.
prompt_ref는 Visual Engine 실행 후 채워질 수 있다.
asset_ref는 Provider 결과 등록 후 채워진다.
Scene 목적과 Visual Goal이 불일치하면 Validation Issue로 기록한다.
```

---

# 16. Motion Mapping Rules

Motion은 모든 Scene에 적용하지 않는다.

Motion 적용 기준:

```text
hook
climax
world_reveal
emotional_turn
important_transition
character_or_object_motion
```

Timeline의 Motion 필드:

```text
required
reason
source_image_ref
asset_ref
duration_seconds
provider
```

규칙:

```text
Motion이 required이면 source_image_ref가 필요하다.
Midjourney Video 기준 기본 duration은 5초이다.
Motion Scene 비율이 과도하면 Review Issue로 기록한다.
Motion이 Retention에 도움이 되지 않으면 required=false로 둔다.
```

---

# 17. Voice Mapping Rules

Voice는 언어별로 관리한다.

Voice 필드:

```text
required
language_tracks
script_ref
voice_ref
estimated_duration_seconds
actual_duration_seconds
```

규칙:

```text
target_languages에 있는 모든 언어는 Voice Track을 가져야 한다.
Voice 생성 전에는 estimated_duration_seconds를 사용한다.
Voice 생성 후 actual_duration_seconds를 기록한다.
actual_duration_seconds가 Scene duration과 크게 다르면 Timeline Adjustment가 필요하다.
```

---

# 18. Subtitle Mapping Rules

Subtitle은 언어별로 관리한다.

Subtitle 필드:

```text
required
language_tracks
subtitle_ref
sync_status
```

규칙:

```text
Voice가 있으면 Subtitle도 필요하다.
Subtitle은 language별로 분리한다.
Subtitle 파일은 languages/{lang}/subtitle.srt에 저장한다.
Subtitle Sync 문제는 Quality에서 Hard Fail이 될 수 있다.
```

---

# 19. Editing Mapping Rules

Timeline은 Editing Engine이 사용할 구조를 제공해야 한다.

Editing 필드:

```text
transition_in
transition_out
notes
asset_order
language_variants
```

Editing Engine은 Timeline을 기준으로 다음을 만든다.

```text
edit/edit_plan.json
edit/render_plan.json
edit/final_timeline.json
```

Timeline에 Asset Mapping이 부족하면 Editing은 진행하지 않는다.

---

# 20. Timeline Review

Timeline Engine은 `timeline_review.json`을 생성해야 한다.

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "timeline_id": "TL-000001",
  "score": 94,
  "status": "PASS_WITH_NOTES",

  "checks": {
    "scene_id_consistency": true,
    "scene_order_valid": true,
    "timing_valid": true,
    "visual_mapping_ready": true,
    "motion_mapping_reasonable": true,
    "voice_tracks_ready": true,
    "subtitle_tracks_ready": true,
    "language_difference_checked": true
  },

  "issues": [
    {
      "severity": "MEDIUM",
      "scene_id": "SC004",
      "issue_type": "LONG_SCENE",
      "description": "Scene duration may be too long for retention.",
      "suggested_fix": "Consider splitting into two scenes."
    }
  ],

  "created_at": "2026-07-10T10:00:00"
}
```

---

# 21. Timeline Lock

Timeline이 검증되면 `timeline_lock.json`을 생성한다.

Timeline Lock은 이후 Engine들이 Scene ID와 기본 구조를 임의 변경하지 못하게 한다.

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "timeline_id": "TL-000001",
  "locked": true,
  "locked_at": "2026-07-10T10:00:00",
  "locked_by": "timeline_engine",

  "locked_fields": [
    "scene_id",
    "scene_order",
    "scene_purpose",
    "language_tracks"
  ],

  "allowed_updates": [
    "asset_ref",
    "prompt_ref",
    "voice_ref",
    "subtitle_ref",
    "actual_duration_seconds",
    "quality.scene_score"
  ],

  "requires_revision_for": [
    "scene_id_change",
    "scene_order_change",
    "scene_deletion",
    "scene_split",
    "scene_merge"
  ]
}
```

---

# 22. Timeline Update Rules

Timeline은 Lock 이후에도 일부 필드가 업데이트될 수 있다.

허용되는 업데이트:

```text
prompt_ref
asset_ref
source_image_ref
motion asset_ref
voice_ref
actual_duration_seconds
subtitle_ref
quality.scene_score
quality.issues
```

Revision이 필요한 업데이트:

```text
Scene ID 변경
Scene 순서 변경
Scene 삭제
Scene 병합
Scene 분할
Scene 목적 변경
언어 Track 삭제
```

Revision이 필요한 경우 Workflow Orchestrator가 Revision Request를 생성해야 한다.

---

# 23. Timeline Validation Rules

Timeline Validator는 다음을 확인해야 한다.

```text
timeline.json 존재
timeline_id 존재
project_id 존재
channel_id 존재
scenes 배열 존재
Scene ID 형식 유효
Scene ID 중복 없음
Scene order 중복 없음
duration_seconds > 0
Scene purpose 존재
Scene importance 존재
Visual 필드 존재
Motion 필드 존재
Voice language_tracks 존재
Subtitle language_tracks 존재
Target Language와 language_tracks 일치
Scene 시간 겹침 없음
Asset Mapping Placeholder 존재
timeline_review.json 생성 가능
timeline_lock.json 생성 가능
```

검증 실패 시 다음 Stage로 넘어갈 수 없다.

---

# 24. Timeline and Visual Engine

Visual Engine은 Timeline을 기준으로 이미지 프롬프트를 만든다.

Visual Engine이 사용하는 필드:

```text
scene_id
order
purpose
importance
emotion
direction.visual_goal
visual.required
visual.provider
```

Visual Engine은 Timeline의 Scene ID를 변경하면 안 된다.

Visual 결과 생성 후 업데이트 가능한 필드:

```text
visual.prompt_ref
visual.asset_ref
quality.issues
```

---

# 25. Timeline and Motion Engine

Motion Engine은 Timeline을 기준으로 Motion 적용 Scene을 결정한다.

Motion Engine이 사용하는 필드:

```text
scene_id
purpose
importance
motion.required
motion.reason
visual.asset_ref
motion.duration_seconds
```

Motion 결과 생성 후 업데이트 가능한 필드:

```text
motion.source_image_ref
motion.asset_ref
```

Motion Engine은 Motion이 필요 없는 Scene에 불필요한 Motion Request를 만들면 안 된다.

---

# 26. Timeline and Voice Engine

Voice Engine은 Timeline과 언어별 Script를 기준으로 Voice를 만든다.

Voice Engine이 사용하는 필드:

```text
target_languages
scene_id
voice.language_tracks
voice.estimated_duration_seconds
```

Voice 생성 후 업데이트 가능한 필드:

```text
voice.language_tracks.{lang}.voice_ref
voice.language_tracks.{lang}.actual_duration_seconds
```

Actual Voice 길이가 Timeline과 크게 다르면 Timeline Review Issue를 생성해야 한다.

---

# 27. Timeline and Subtitle Engine

Subtitle Engine은 Timeline과 Voice 결과를 기준으로 자막을 만든다.

Subtitle Engine이 사용하는 필드:

```text
scene_id
language_tracks
voice_ref
actual_duration_seconds
subtitle.required
```

Subtitle 생성 후 업데이트 가능한 필드:

```text
subtitle.language_tracks.{lang}.subtitle_ref
subtitle.language_tracks.{lang}.sync_status
```

---

# 28. Timeline and Editing Engine

Editing Engine은 Timeline을 기준으로 최종 편집 구조를 만든다.

Editing Engine이 사용하는 필드:

```text
scene order
timing
visual.asset_ref
motion.asset_ref
voice.language_tracks
subtitle.language_tracks
editing.transition_in
editing.transition_out
```

Editing Engine은 Timeline에 필요한 Asset이 누락되면 Final Timeline을 생성하지 않는다.

---

# 29. Timeline and Quality Engine

Quality Engine은 Timeline Integrity를 검사한다.

검사 항목:

```text
Scene ID 일관성
Scene 순서
Timing 구조
Visual Asset 연결
Motion Asset 연결
Voice Track 연결
Subtitle Track 연결
언어별 Track 완성도
Asset 누락
Scene 목적과 결과물 일치
```

Timeline 관련 Hard Fail:

```text
Scene ID 불일치
필수 Scene 누락
Voice와 Subtitle Sync 붕괴
Asset Mapping 누락
Final Timeline 생성 불가
언어별 Track 누락
```

---

# 30. Timeline Directory Structure

Timeline 관련 파일은 다음 위치에 저장한다.

```text
timeline/
├── timeline.json
├── timeline_review.json
├── timeline_lock.json
├── scene_index.json
├── asset_mapping_plan.json
├── language_timing_plan.json
└── motion_selection_plan.json
```

v1.0 최소 파일:

```text
timeline/timeline.json
timeline/timeline_review.json
timeline/timeline_lock.json
```

---

# 31. Error Types

Timeline Engine의 Error Type은 다음과 같다.

```text
TimelineInputMissingError
TimelineCreationError
TimelineValidationError
SceneIdInvalidError
SceneIdDuplicateError
SceneOrderError
SceneTimingError
ScenePurposeMissingError
LanguageTrackMissingError
AssetMappingError
MotionMappingError
TimelineLockError
TimelineUpdateViolationError
TimelineReviewError
```

Error 예시:

```json
{
  "error_type": "SceneIdDuplicateError",
  "message": "Duplicate scene_id SC004 found in timeline.",
  "project_id": "20260710-093500-future-million-year-human",
  "stage": "TIMELINE",
  "severity": "HIGH",
  "suggested_fix": "Assign a unique Scene ID and regenerate timeline_review.json.",
  "created_at": "2026-07-10T10:00:00"
}
```

---

# 32. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
TimelineEngine
TimelineBuilder
TimelineValidator
SceneIdManager
SceneOrderManager
SceneTimingPlanner
ScenePurposeMapper
AssetMappingPlanner
LanguageTimingPlanner
MotionSelectionPlanner
TimelineReviewBuilder
TimelineLockManager
TimelineUpdater
TimelineContextBuilder
TimelineErrorReporter
```

---

# 33. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/16_TIMELINE_ENGINE.md
→ engines/timeline/
```

예시 구조:

```text
engines/
└── timeline/
    ├── timeline_engine.py
    ├── timeline_builder.py
    ├── timeline_validator.py
    ├── scene_id_manager.py
    ├── scene_order_manager.py
    ├── scene_timing_planner.py
    ├── scene_purpose_mapper.py
    ├── asset_mapping_planner.py
    ├── language_timing_planner.py
    ├── motion_selection_planner.py
    ├── timeline_review_builder.py
    ├── timeline_lock_manager.py
    ├── timeline_updater.py
    ├── timeline_context_builder.py
    └── timeline_error_reporter.py
```

---

# 34. Main Public Operations

Timeline Engine은 최소 다음 작업을 제공해야 한다.

```text
create_timeline(project_id)
load_timeline(project_id)
validate_timeline(project_id)
create_scene_ids(scene_plan)
build_scene_timing(project_id)
map_visual_requirements(project_id)
map_motion_requirements(project_id)
map_voice_tracks(project_id)
map_subtitle_tracks(project_id)
build_timeline_review(project_id)
lock_timeline(project_id)
update_timeline_asset_ref(project_id, scene_id, asset_type, asset_ref)
build_timeline_context(project_id, target_engine)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
Scene ID 안정성 유지
Timeline Lock 확인
파일 존재 확인
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 35. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
direction/scene_plan.json 로드
story/script_master.json 로드
Scene ID 생성
Scene 순서 생성
Scene 목적 매핑
기본 Duration 추정
Visual Requirement 생성
Motion Requirement 생성
Voice Language Track 생성
Subtitle Language Track 생성
timeline.json 생성
timeline_review.json 생성
timeline_lock.json 생성
Timeline Validation 수행
Visual / Motion / Voice / Subtitle / Editing용 Timeline Context 제공
```

v1.0에서 하지 않아도 되는 것:

```text
프레임 단위 정밀 편집
자동 고급 렌더링
복잡한 영상 편집 UI
실시간 Timeline 편집기
고급 음악 비트 싱크
자동 컷 편집 최적화
```

v1.0에서는 Production Engine들이 안정적으로 사용할 수 있는 구조화된 Timeline을 만드는 것이 우선이다.

---

# 36. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Story와 Direction 결과를 기반으로 Timeline을 만들 수 있다.
Scene ID를 안정적으로 생성할 수 있다.
Scene 순서를 관리할 수 있다.
Scene별 목적과 중요도를 기록할 수 있다.
Scene별 예상 Duration을 기록할 수 있다.
Visual Requirement를 만들 수 있다.
Motion Requirement를 만들 수 있다.
언어별 Voice Track을 만들 수 있다.
언어별 Subtitle Track을 만들 수 있다.
timeline.json을 생성할 수 있다.
timeline_review.json을 생성할 수 있다.
timeline_lock.json을 생성할 수 있다.
Scene ID 중복을 감지할 수 있다.
언어별 Track 누락을 감지할 수 있다.
Asset Mapping 누락을 감지할 수 있다.
Visual / Motion / Voice / Subtitle / Editing Engine에 Timeline Context를 제공할 수 있다.
Quality Engine이 Timeline Integrity를 검사할 수 있게 만들 수 있다.
```

---

# 37. Non Goals

v1.0에서 Timeline Engine이 하지 않는 것:

```text
이미지 직접 생성
Motion 영상 직접 생성
Voice 파일 직접 생성
Subtitle 직접 생성
Final Video 직접 렌더링
Provider 직접 호출
프레임 단위 고급 편집
실시간 Timeline UI 제공
```

v1.0에서는 영상 제작 엔진들이 공통으로 사용할 수 있는 Timeline 구조와 검증 기준을 먼저 완성한다.

---

# 38. Critical Timeline Rules

반드시 지켜야 할 규칙:

```text
1. Timeline은 Project 제작의 중심 설계도이다.

2. Timeline 없이 Visual / Motion / Voice / Subtitle / Editing을 최종 연결하지 않는다.

3. Scene ID는 Project 안에서 유일해야 한다.

4. Scene ID는 생성 후 임의 변경하지 않는다.

5. 모든 Scene은 purpose를 가져야 한다.

6. 모든 Scene은 timing 정보를 가져야 한다.

7. 모든 Scene은 Visual Requirement를 가져야 한다.

8. Motion은 필요한 Scene에만 적용한다.

9. Voice와 Subtitle은 언어별로 관리한다.

10. Timeline Lock 이후 구조 변경은 Revision Request가 필요하다.

11. Asset Mapping은 Timeline 기준으로 연결한다.

12. Timeline Validation 실패 시 다음 Stage로 넘어가지 않는다.

13. Timeline Engine은 Provider를 직접 호출하지 않는다.

14. Timeline 관련 Hard Fail은 Quality Gate를 막을 수 있다.

15. Timeline 변경은 로그로 남긴다.
```

---

# 39. Final Principle

Timeline Engine은 ADOS의 영상 제작을 하나로 묶는 중심 엔진이다.

좋은 Timeline은 Story를 Production으로 바꾼다.

좋은 Timeline은 Visual, Motion, Voice, Subtitle, Editing이 같은 방향으로 움직이게 만든다.

Timeline이 명확하면 제작은 안정된다.

Timeline이 흔들리면 모든 Engine이 흔들린다.

Timeline Engine의 목적은 단순한 장면 목록을 만드는 것이 아니라, 고품질 영상 제작이 가능한 시간 설계도를 만드는 것이다.
