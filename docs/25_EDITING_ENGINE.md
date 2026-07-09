# 25_EDITING_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Editing Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Editing Engine을 정의한다.

Editing Engine은 Timeline, Visual Asset, Motion Asset, Voice Asset, Subtitle Asset을 하나의 최종 편집 구조로 연결하는 엔진이다.

Editing Engine은 v1.0에서 반드시 실제 mp4를 자동 렌더링할 필요는 없다.

v1.0의 핵심은 다음이다.

```text
Timeline 기반 편집 설계
Scene별 Asset Mapping
언어별 Render Plan 생성
Missing Asset 감지
Final Timeline 생성
Package 단계로 넘길 편집 준비 상태 검증
Quality Engine이 검사할 수 있는 편집 구조 제공
```

Editing Engine은 다음을 담당한다.

```text
Timeline 로드
Timeline Lock 확인
Asset Registry 로드
Visual / Motion / Voice / Subtitle Handoff 로드
Scene별 Asset Mapping 검증
Edit Plan 생성
Render Plan 생성
Final Timeline 생성
언어별 영상 출력 계획 생성
Missing Asset Report 생성
Editing Review 생성
Quality Engine에 Handoff 생성
Publishing / Package 단계에 필요한 파일 구조 제공
```

이 문서는 다음 문서들과 직접 연결된다.

```text
07_PROJECT_SPEC.md
10_BRAND_SYSTEM.md
12_PROJECT_ENGINE.md
14_PROVIDER_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
16_TIMELINE_ENGINE.md
21_VISUAL_ENGINE.md
22_MOTION_ENGINE.md
23_VOICE_ENGINE.md
24_SUBTITLE_ENGINE.md
26_QUALITY_ENGINE.md
28_PUBLISHING_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Editing Engine은 제작된 모든 Asset을 Timeline 기준으로 연결하는 엔진이다.

전체 흐름:

```text
Timeline
↓
Visual Assets
↓
Motion Assets
↓
Voice Assets
↓
Subtitle Assets
↓
Editing Engine
↓
Edit Plan
↓
Render Plan
↓
Final Timeline
↓
Quality Engine
↓
Package
```

Editing Engine의 핵심 목표는 다음이다.

```text
모든 Scene에 필요한 Asset이 연결되어 있는지 확인한다.
언어별 Voice와 Subtitle을 올바르게 분리한다.
Motion이 있는 Scene과 정적 이미지 Scene을 구분한다.
최종 편집자가 바로 사용할 수 있는 편집 계획을 만든다.
자동 렌더링 시스템이 나중에 붙을 수 있는 Render Plan을 만든다.
Quality Engine이 검사할 수 있는 Final Timeline을 만든다.
```

---

# 3. Editing Philosophy

## 3.1 Editing Is Assembly Control

Editing Engine은 단순히 파일을 모으는 엔진이 아니다.

Editing Engine은 Story, Timeline, Asset, Voice, Subtitle을 하나의 시청 경험으로 조립하는 통제 엔진이다.

## 3.2 Timeline Is the Source of Truth

Editing Engine은 Timeline을 기준으로 움직인다.

Scene 순서, Scene ID, Scene 목적은 Timeline을 따른다.

Editing Engine은 Scene ID를 변경하지 않는다.

## 3.3 Missing Asset Must Stop the Flow

필수 Asset이 누락되면 Quality Stage로 넘어가면 안 된다.

```text
필수 이미지 누락
필수 Voice 누락
필수 Subtitle 누락
Scene ID 불일치
언어별 Asset 누락
```

이런 문제가 있으면 Editing Stage는 실패하거나 Revision Request를 생성해야 한다.

## 3.4 Language-Specific Render Plan

Visual과 Motion은 기본적으로 공유한다.

Voice와 Subtitle은 언어별로 분리한다.

```text
Shared:
Visual
Motion
Scene Structure
Timeline

Language-Specific:
Voice
Subtitle
Metadata
Final Render Output
```

---

# 4. Editing Engine Responsibilities

Editing Engine의 책임:

```text
Timeline 로드
Timeline Lock 확인
Asset Registry 로드
Visual Handoff 로드
Motion Handoff 로드
Voice Handoff 로드
Subtitle Handoff 로드
Scene별 Asset Mapping 생성
Missing Asset 감지
Edit Plan 생성
Render Plan 생성
Final Timeline 생성
언어별 Render Variant 생성
Editing Review 생성
Quality Engine Handoff 생성
Package 준비 상태 확인
```

Editing Engine이 하지 않는 것:

```text
이미지를 직접 생성하지 않는다.
Motion 영상을 직접 생성하지 않는다.
Voice를 직접 생성하지 않는다.
Subtitle을 직접 생성하지 않는다.
Timeline Scene ID를 변경하지 않는다.
Story를 수정하지 않는다.
Quality Score를 최종 계산하지 않는다.
Publishing을 직접 수행하지 않는다.
```

---

# 5. Inputs

Editing Engine의 입력:

```text
project.json
channel_snapshot.json
template_snapshot.json
timeline/timeline.json
timeline/timeline_lock.json
assets/asset_registry.json
reports/visual_review.json
reports/motion_review.json
reports/voice_review.json
reports/subtitle_review.json
workflow/handoffs/VISUAL_to_EDITING.json
workflow/handoffs/MOTION_to_EDITING.json
workflow/handoffs/VOICE_to_EDITING.json
workflow/handoffs/SUBTITLE_to_EDITING.json
channels/{channel_id}/brand.yaml
workflow/memory_context_EDITING.json
```

필수 입력:

```text
project.json
timeline/timeline.json
timeline/timeline_lock.json
assets/asset_registry.json
reports/visual_review.json
reports/voice_review.json
reports/subtitle_review.json
```

선택 입력:

```text
reports/motion_review.json
workflow/handoffs/MOTION_to_EDITING.json
Editing Rhythm Memory
Motion Usage Memory
Subtitle Sync Memory
Quality Failure Memory
```

Motion은 선택 Asset일 수 있다.

하지만 Visual, Voice, Subtitle은 기본적으로 필수이다.

---

# 6. Outputs

Editing Engine의 출력:

```text
edit/edit_plan.json
edit/render_plan.json
edit/final_timeline.json
reports/editing_review.json
reports/missing_asset_report.json
workflow/stage_results/EDITING_result.json
workflow/handoffs/EDITING_to_QUALITY.json
```

v1.0에서 실제 Render Output이 있는 경우:

```text
package/final_video_ko.mp4
package/final_video_en.mp4
```

하지만 v1.0에서 mp4 자동 생성은 필수 아니다.

v1.0 최소 출력:

```text
edit/edit_plan.json
edit/render_plan.json
edit/final_timeline.json
reports/editing_review.json
workflow/handoffs/EDITING_to_QUALITY.json
```

---

# 7. Editing Creation Flow

Editing Engine 실행 흐름:

```text
Load Project Context
↓
Load Timeline
↓
Load Timeline Lock
↓
Load Asset Registry
↓
Load Production Reviews
↓
Load Editing Handoffs
↓
Validate Editing Inputs
↓
Build Scene Asset Mapping
↓
Detect Missing Assets
↓
Build Edit Plan
↓
Build Language Render Variants
↓
Build Render Plan
↓
Build Final Timeline
↓
Build Editing Review
↓
Handoff to Quality Engine
```

---

# 8. Asset Mapping Rules

Editing Engine은 모든 Scene에 필요한 Asset을 매핑해야 한다.

Scene별 기본 Asset:

```text
image
motion optional
voice by language
subtitle by language
```

Mapping 규칙:

```text
Scene ID는 Timeline과 일치해야 한다.
Image는 모든 required Scene에 있어야 한다.
Motion은 motion.required=true인 Scene에만 필요하다.
Voice는 target language마다 있어야 한다.
Subtitle은 target language마다 있어야 한다.
Asset Registry에 등록되지 않은 파일은 공식 Asset으로 보지 않는다.
```

---

# 9. edit_plan.json Schema

`edit/edit_plan.json`은 편집자가 이해할 수 있는 편집 계획이다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "EDITING",

  "video": {
    "format": "youtube_longform",
    "aspect_ratio": "16:9",
    "fps": 30,
    "target_languages": [
      "ko",
      "en"
    ]
  },

  "editing_strategy": {
    "style": "cinematic_documentary",
    "pacing": "medium_cinematic",
    "motion_policy": "use_motion_only_for_selected_scenes",
    "subtitle_policy": "language_specific_srt",
    "voice_policy": "language_specific_audio"
  },

  "scenes": [
    {
      "scene_id": "SC001",
      "order": 1,
      "purpose": "hook",
      "duration_seconds": 8,

      "visual": {
        "type": "motion_preferred",
        "image_ref": "assets/images/SC001_image_v001.png",
        "motion_ref": "assets/motion/SC001_motion_v001.mp4",
        "fallback_ref": "assets/images/SC001_image_v001.png"
      },

      "audio": {
        "ko": {
          "voice_ref": "assets/audio/voice_ko_v001.wav",
          "scene_timing_ref": "languages/ko/voice.json"
        },
        "en": {
          "voice_ref": "assets/audio/voice_en_v001.wav",
          "scene_timing_ref": "languages/en/voice.json"
        }
      },

      "subtitle": {
        "ko": {
          "subtitle_ref": "assets/subtitles/subtitle_ko_v001.srt"
        },
        "en": {
          "subtitle_ref": "assets/subtitles/subtitle_en_v001.srt"
        }
      },

      "editing": {
        "transition_in": "fade_from_black",
        "transition_out": "slow_fade",
        "notes": [
          "Use motion clip for opening 5 seconds.",
          "If scene duration exceeds motion duration, hold final frame or cut to still."
        ]
      }
    }
  ],

  "created_at": "2026-07-10T15:00:00",
  "updated_at": "2026-07-10T15:00:00"
}
```

---

# 10. render_plan.json Schema

`edit/render_plan.json`은 언어별 최종 출력 계획이다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "EDITING",

  "render_variants": [
    {
      "language": "ko",
      "output_file": "package/final_video_ko.mp4",
      "voice_ref": "assets/audio/voice_ko_v001.wav",
      "subtitle_ref": "assets/subtitles/subtitle_ko_v001.srt",
      "visual_shared": true,
      "motion_shared": true,
      "status": "READY_FOR_RENDER"
    },
    {
      "language": "en",
      "output_file": "package/final_video_en.mp4",
      "voice_ref": "assets/audio/voice_en_v001.wav",
      "subtitle_ref": "assets/subtitles/subtitle_en_v001.srt",
      "visual_shared": true,
      "motion_shared": true,
      "status": "READY_FOR_RENDER"
    }
  ],

  "render_settings": {
    "aspect_ratio": "16:9",
    "resolution": "1920x1080",
    "fps": 30,
    "format": "mp4",
    "subtitle_mode": "burn_in_or_sidecar",
    "audio_normalization": true
  },

  "manual_render_instructions": [
    "Use final_timeline.json as the assembly guide.",
    "Render one final video per target language.",
    "Use shared visual and motion assets.",
    "Use language-specific voice and subtitle assets."
  ]
}
```

---

# 11. final_timeline.json Schema

`edit/final_timeline.json`은 Quality Engine이 검사할 최종 편집 기준 파일이다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "EDITING",

  "timeline_ref": "timeline/timeline.json",
  "asset_registry_ref": "assets/asset_registry.json",

  "tracks": {
    "visual_track": [
      {
        "scene_id": "SC001",
        "start_time": "00:00:00",
        "end_time": "00:00:08",
        "primary_asset": "assets/motion/SC001_motion_v001.mp4",
        "fallback_asset": "assets/images/SC001_image_v001.png",
        "asset_type": "motion"
      }
    ],

    "voice_tracks": {
      "ko": "assets/audio/voice_ko_v001.wav",
      "en": "assets/audio/voice_en_v001.wav"
    },

    "subtitle_tracks": {
      "ko": "assets/subtitles/subtitle_ko_v001.srt",
      "en": "assets/subtitles/subtitle_en_v001.srt"
    }
  },

  "validation": {
    "scene_order_valid": true,
    "visual_assets_complete": true,
    "voice_assets_complete": true,
    "subtitle_assets_complete": true,
    "motion_assets_valid": true,
    "language_variants_ready": true,
    "issues": []
  },

  "status": "READY_FOR_QUALITY"
}
```

---

# 12. Missing Asset Report

Missing Asset이 있으면 `reports/missing_asset_report.json`을 생성한다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "stage": "EDITING",

  "missing_assets": [
    {
      "scene_id": "SC004",
      "asset_type": "image",
      "severity": "HIGH",
      "required": true,
      "expected": "assets/images/SC004_image_v001.png",
      "blocking": true,
      "suggested_fix": "Return to VISUAL stage and generate/register SC004 image."
    }
  ],

  "blocking": true,
  "can_continue_to_quality": false
}
```

Missing Asset이 없으면:

```json
{
  "missing_assets": [],
  "blocking": false,
  "can_continue_to_quality": true
}
```

---

# 13. Language Variant Rules

Editing Engine은 언어별 Render Variant를 생성해야 한다.

규칙:

```text
Visual Track은 기본적으로 공유한다.
Motion Track은 기본적으로 공유한다.
Voice Track은 언어별로 다르다.
Subtitle Track은 언어별로 다르다.
각 언어는 독립적인 final_video output을 가질 수 있다.
```

언어별 Render Variant가 준비되려면:

```text
해당 언어 voice asset 존재
해당 언어 subtitle asset 존재
shared visual asset 존재
shared motion asset 존재 또는 fallback image 존재
render_plan에 output_file 존재
```

---

# 14. Motion Fallback Rules

Motion Asset이 없어도 모든 경우에 실패는 아니다.

다음 경우에는 Image Fallback을 사용할 수 있다.

```text
motion.required = false
motion asset 생성 실패하지만 scene importance가 낮음
motion review에서 fallback 허용
editing note에서 still image 사용 허용
```

다음 경우에는 실패 또는 Review 필요:

```text
hook scene motion required
climax scene motion required
motion.required = true인데 asset 누락
motion asset이 심각하게 왜곡됨
fallback 사용 시 retention 영향이 큼
```

Fallback은 `final_timeline.json`에 명시되어야 한다.

---

# 15. Subtitle Usage Rules

Editing Engine은 Subtitle을 다음 방식으로 사용할 수 있다.

```text
burn_in
sidecar
manual_overlay
```

v1.0 기본값:

```text
subtitle_mode = burn_in_or_sidecar
```

규칙:

```text
언어별 Subtitle 파일을 구분한다.
Subtitle Sync Issue가 있으면 Editing Review에 기록한다.
Final Render 전에 Subtitle이 누락되면 안 된다.
```

---

# 16. Audio Usage Rules

Voice Audio는 언어별로 연결한다.

검사 항목:

```text
언어별 audio file 존재
Asset Registry 등록
duration 존재
voice_review 통과
timeline_fit status 확인
```

Audio 길이가 Timeline과 크게 다르면 Editing Review에 Issue로 기록한다.

---

# 17. Editing Review Schema

`reports/editing_review.json`은 Editing Stage의 검토 결과이다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "EDITING",

  "score": 93,
  "status": "PASS_WITH_NOTES",

  "checks": {
    "timeline_loaded": true,
    "asset_registry_loaded": true,
    "scene_mapping_complete": true,
    "visual_assets_complete": true,
    "motion_assets_valid": true,
    "voice_assets_complete": true,
    "subtitle_assets_complete": true,
    "language_variants_ready": true,
    "missing_asset_blocking": false,
    "quality_handoff_ready": true
  },

  "issues": [
    {
      "severity": "MEDIUM",
      "issue_type": "VOICE_TIMELINE_DIFFERENCE",
      "language": "en",
      "description": "English voice is slightly longer than estimated timeline.",
      "suggested_fix": "Quality Engine should review pacing and subtitle sync."
    }
  ],

  "handoff_notes": [
    "Final Timeline is ready for Quality Engine.",
    "English variant needs pacing review."
  ]
}
```

---

# 18. Editing Scoring

Editing Score 기준:

```yaml
editing_score:
  timeline_integrity: 15
  scene_asset_mapping: 20
  visual_asset_completeness: 15
  voice_asset_completeness: 15
  subtitle_asset_completeness: 15
  language_variant_readiness: 10
  render_plan_readiness: 5
  quality_handoff_readiness: 5
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
Partial fix required

70 미만
Editing fail
```

Hard Fail 조건:

```text
Timeline 누락
Asset Registry 누락
필수 Scene Image 누락
필수 언어 Voice 누락
필수 언어 Subtitle 누락
Scene ID 불일치
Final Timeline 생성 실패
Quality Handoff 생성 실패
```

---

# 19. Editing Validation Rules

Editing Validator는 다음을 확인해야 한다.

```text
edit/edit_plan.json 존재
edit/render_plan.json 존재
edit/final_timeline.json 존재
reports/editing_review.json 존재
project_id 일치
channel_id 일치
Timeline Scene ID와 Edit Plan Scene ID 일치
Asset Registry와 Edit Plan Asset 일치
필수 Visual Asset 존재
필수 Voice Asset 존재
필수 Subtitle Asset 존재
언어별 Render Variant 존재
Final Timeline validation 통과
Missing Asset Report blocking=false
Timeline Lock 위반 없음
```

검증 실패 시 QUALITY Stage로 이동할 수 없다.

---

# 20. Quality Engine Handoff

Editing Engine은 Quality Engine에 Handoff를 생성해야 한다.

Handoff 파일:

```text
workflow/handoffs/EDITING_to_QUALITY.json
```

포함 내용:

```text
edit_plan.json
render_plan.json
final_timeline.json
editing_review.json
missing_asset_report.json
Asset Registry
언어별 Render Variant
Known Issues
Quality Check 요청 사항
```

예시:

```json
{
  "from_stage": "EDITING",
  "to_stage": "QUALITY",
  "project_id": "20260710-093500-future-million-year-human",

  "required_inputs_for_quality": [
    "edit/edit_plan.json",
    "edit/render_plan.json",
    "edit/final_timeline.json",
    "reports/editing_review.json",
    "assets/asset_registry.json"
  ],

  "quality_focus": [
    "Timeline integrity",
    "Scene asset mapping",
    "Voice and subtitle sync",
    "Language variant readiness",
    "Missing asset check"
  ],

  "known_issues": [
    {
      "language": "en",
      "issue": "Voice slightly longer than estimated timeline.",
      "severity": "MEDIUM"
    }
  ]
}
```

---

# 21. Internal Editing Provider

v1.0에서 Editing은 기본적으로 Internal Editing Provider를 사용한다.

구조:

```text
Editing Engine
↓
Provider Engine
↓
EditingProviderInterface
↓
InternalEditingAdapter
```

Provider 설정:

```yaml
editing:
  provider_name: internal_editing
  mode: automated
```

v1.0에서 Internal Editing은 실제 렌더링보다 다음을 담당한다.

```text
Edit Plan 생성
Render Plan 생성
Final Timeline 생성
Missing Asset 검증
```

---

# 22. Auto Fix Rules

Editing 문제 발생 시 부분 수정이 우선이다.

수정 대상:

```text
특정 Scene Asset Mapping
Missing Asset 연결
언어별 Render Variant
Subtitle Ref
Voice Ref
Motion Fallback
Final Timeline Validation Issue
```

금지:

```text
전체 Project 재생성
Story 임의 수정
Scene ID 변경
Timeline 구조 무단 변경
Asset Registry 무단 삭제
언어별 Script 의미 변경
```

Auto Fix 예시:

```text
Issue:
SC005 motion asset missing, but fallback image exists.

Fix:
Update final_timeline.json to use SC005 image fallback and record issue in editing_review.json.
```

---

# 23. Memory Integration

Editing Engine은 작업 전 Memory Context를 사용한다.

사용 가능한 Memory:

```text
Editing Rhythm Memory
Motion Usage Memory
Subtitle Sync Memory
Voice Timeline Fit Memory
Quality Editing Failure Memory
Language Render Memory
```

Editing Engine은 작업 후 Memory Candidate를 만들 수 있다.

예시:

```text
Motion을 과하게 사용하면 Retention에 방해됨
특정 언어 Voice가 자주 Timeline보다 길어짐
Subtitle Sync 문제가 자주 나는 구간
Image Fallback이 효과적이었던 Scene 유형
```

Memory 확정은 Memory Engine 또는 Learning Engine이 담당한다.

---

# 24. Error Types

Editing Engine의 Error Type:

```text
EditingInputMissingError
TimelineMissingError
TimelineLockMissingError
AssetRegistryMissingError
AssetMappingError
VisualAssetMissingError
MotionAssetMissingError
VoiceAssetMissingError
SubtitleAssetMissingError
LanguageVariantError
RenderPlanCreationError
FinalTimelineCreationError
FinalTimelineValidationError
MissingAssetBlockingError
EditingReviewError
EditingValidationError
EditingHandoffError
```

Error 예시:

```json
{
  "error_type": "VoiceAssetMissingError",
  "message": "Required English voice asset is missing.",
  "project_id": "20260710-093500-future-million-year-human",
  "language": "en",
  "stage": "EDITING",
  "severity": "HIGH",
  "suggested_fix": "Return to VOICE stage and register English voice asset.",
  "created_at": "2026-07-10T15:00:00"
}
```

---

# 25. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
EditingEngine
EditingInputLoader
EditingInputValidator
AssetMappingBuilder
MissingAssetDetector
EditPlanBuilder
RenderPlanBuilder
FinalTimelineBuilder
LanguageVariantBuilder
MotionFallbackResolver
SubtitleUsagePlanner
AudioUsagePlanner
EditingReviewBuilder
EditingValidator
EditingHandoffBuilder
EditingErrorReporter
```

---

# 26. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/25_EDITING_ENGINE.md
→ engines/editing/
```

예시 구조:

```text
engines/
└── editing/
    ├── editing_engine.py
    ├── editing_input_loader.py
    ├── editing_input_validator.py
    ├── asset_mapping_builder.py
    ├── missing_asset_detector.py
    ├── edit_plan_builder.py
    ├── render_plan_builder.py
    ├── final_timeline_builder.py
    ├── language_variant_builder.py
    ├── motion_fallback_resolver.py
    ├── subtitle_usage_planner.py
    ├── audio_usage_planner.py
    ├── editing_review_builder.py
    ├── editing_validator.py
    ├── editing_handoff_builder.py
    └── editing_error_reporter.py
```

---

# 27. Main Public Operations

Editing Engine은 최소 다음 작업을 제공해야 한다.

```text
run_editing(project_id)
load_editing_inputs(project_id)
validate_editing_inputs(project_id)
build_asset_mapping(project_id)
detect_missing_assets(project_id)
build_edit_plan(project_id)
build_render_plan(project_id)
build_language_variants(project_id)
resolve_motion_fallbacks(project_id)
build_final_timeline(project_id)
build_editing_review(project_id)
validate_editing_outputs(project_id)
build_handoff_to_quality(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
Timeline Scene ID 유지
Asset Registry 기준 사용
언어별 Voice / Subtitle 분리
Motion Fallback 명시
Missing Asset 감지
Timeline Lock 준수
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 28. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Timeline 로드
Asset Registry 로드
Production Review 로드
Editing 입력 검증
Scene별 Asset Mapping 생성
Missing Asset 감지
edit_plan.json 생성
render_plan.json 생성
final_timeline.json 생성
언어별 Render Variant 생성
Motion Fallback 처리
editing_review.json 생성
Quality Engine Handoff 생성
Editing Validation 수행
```

v1.0에서 하지 않아도 되는 것:

```text
실제 mp4 자동 렌더링
고급 영상 편집 UI
프레임 단위 컷 편집
음악 자동 믹싱
효과음 자동 생성
색보정 자동화
자막 Burn-in 자동 렌더링
YouTube 직접 업로드
```

v1.0에서는 Final Video 생성 전 단계의 편집 구조와 검증 가능한 계획을 만드는 것이 우선이다.

---

# 29. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Timeline과 Asset Registry를 로드할 수 있다.
Editing 입력을 검증할 수 있다.
Scene별 Asset Mapping을 만들 수 있다.
Missing Asset을 감지할 수 있다.
edit_plan.json을 생성할 수 있다.
render_plan.json을 생성할 수 있다.
final_timeline.json을 생성할 수 있다.
언어별 Render Variant를 만들 수 있다.
Motion Fallback을 명시할 수 있다.
editing_review.json을 생성할 수 있다.
Quality Engine으로 넘길 Handoff를 만들 수 있다.
Editing Validation 실패 시 QUALITY Stage 진행을 막을 수 있다.
```

---

# 30. Non Goals

v1.0에서 Editing Engine이 하지 않는 것:

```text
실제 영상 자동 렌더링 필수 구현
Final Video 직접 업로드
Story 수정
Timeline Scene ID 변경
Voice 생성
Subtitle 생성
Image 생성
Motion 생성
Quality Score 최종 계산
YouTube Publishing
```

v1.0에서는 편집 계획, 렌더 계획, 최종 타임라인, Asset 완성도 검증이 핵심이다.

---

# 31. Critical Editing Rules

반드시 지켜야 할 규칙:

```text
1. Editing Engine은 Timeline 없이 실행하지 않는다.

2. Editing Engine은 Asset Registry 없이 실행하지 않는다.

3. Editing Engine은 Scene ID를 변경하지 않는다.

4. Timeline을 기준으로 Scene을 조립한다.

5. 필수 Visual Asset이 없으면 Quality Stage로 넘어가지 않는다.

6. 필수 Voice Asset이 없으면 Quality Stage로 넘어가지 않는다.

7. 필수 Subtitle Asset이 없으면 Quality Stage로 넘어가지 않는다.

8. Motion은 선택 Asset일 수 있지만 required Motion 누락은 Issue로 기록한다.

9. Motion Fallback은 명시적으로 기록한다.

10. 언어별 Render Variant를 분리한다.

11. Visual / Motion은 공유하고 Voice / Subtitle은 언어별로 분리한다.

12. Final Timeline은 Quality Engine이 검사할 수 있어야 한다.

13. Timeline Lock을 위반하지 않는다.

14. Editing Validation 실패 시 Quality Stage로 넘어가지 않는다.

15. 중요한 Editing 판단은 Self Review와 Handoff에 기록한다.
```

---

# 32. Final Principle

Editing Engine은 모든 제작 결과를 하나의 영상 구조로 조립하는 엔진이다.

좋은 Editing Engine은 단순히 파일을 모으지 않는다.

좋은 Editing Engine은 Timeline을 지키고,

Scene별 Asset을 정확히 연결하고,

언어별 Voice와 Subtitle을 분리하고,

Missing Asset을 막고,

Quality Engine이 검사할 수 있는 Final Timeline을 만든다.

Editing Engine의 목적은 멋대로 영상을 완성하는 것이 아니라, 고품질 최종 영상이 만들어질 수 있는 안정적인 편집 구조를 만드는 것이다.
