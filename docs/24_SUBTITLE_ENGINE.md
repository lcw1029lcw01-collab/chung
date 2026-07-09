# 24_SUBTITLE_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Subtitle Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Subtitle Engine을 정의한다.

Subtitle Engine은 Voice Engine이 생성한 언어별 Narration, Voice Config, Audio Asset, Timeline 정보를 기반으로 언어별 자막 파일을 생성하고 검증하는 엔진이다.

Subtitle Engine은 단순히 텍스트를 줄 단위로 자르는 엔진이 아니다.

Subtitle Engine은 다음을 담당한다.

```text
Timeline 로드
언어별 Narration 로드
언어별 Voice 정보 로드
Audio Asset 정보 확인
언어별 Subtitle 구조 생성
SRT 파일 생성
자막 줄바꿈 규칙 적용
읽기 속도 검증
Voice Sync 기준 생성
Timeline Scene과 Subtitle 연결
Subtitle Asset Registry 등록
Subtitle Review 생성
Editing Engine에 Handoff 생성
Quality Engine이 검사할 Subtitle 구조 제공
```

이 문서는 다음 문서들과 직접 연결된다.

```text
07_PROJECT_SPEC.md
10_BRAND_SYSTEM.md
12_PROJECT_ENGINE.md
14_PROVIDER_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
16_TIMELINE_ENGINE.md
19_STORY_ENGINE.md
23_VOICE_ENGINE.md
25_EDITING_ENGINE.md
26_QUALITY_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Subtitle Engine은 언어별 대본과 음성을 시청자가 읽기 좋은 자막 구조로 변환하는 엔진이다.

전체 흐름:

```text
Voice Engine
↓
Narration / Audio / Voice Timing
↓
Subtitle Engine
↓
Subtitle Tracks
↓
SRT Files
↓
Subtitle Review
↓
Editing / Quality
```

Subtitle Engine의 핵심 목표는 다음이다.

```text
언어별 자연스러운 자막을 만든다.
Voice와 Timeline에 맞는 자막 타이밍을 만든다.
너무 긴 자막 줄을 방지한다.
읽기 속도를 관리한다.
Scene ID와 자막을 연결한다.
Editing Engine이 사용할 수 있는 자막 파일을 만든다.
Quality Engine이 Sync와 가독성을 검사할 수 있게 한다.
```

---

# 3. Subtitle Philosophy

## 3.1 Subtitle Is Part of Viewing Experience

자막은 보조 텍스트가 아니다.

자막은 시청자가 내용을 이해하고, 몰입을 유지하고, 영상의 흐름을 따라가는 핵심 요소이다.

나쁜 자막:

```text
한 줄이 너무 김
읽을 시간이 부족함
Voice와 맞지 않음
문장 중간에서 이상하게 끊김
언어별 표현이 어색함
Scene 전환과 맞지 않음
```

좋은 자막:

```text
의미 단위로 끊김
Voice와 자연스럽게 맞음
짧고 읽기 쉬움
언어별 표현이 자연스러움
중요한 문장에 적절한 여백이 있음
```

## 3.2 Voice Sync First

Subtitle은 Voice와 맞아야 한다.

Voice가 있으면 Subtitle은 Voice Timing을 우선으로 한다.

```text
Voice Audio
↓
Subtitle Timing
↓
Editing Placement
```

## 3.3 Meaning-Based Line Break

자막 줄바꿈은 글자 수만 기준으로 하지 않는다.

의미 단위가 우선이다.

나쁜 줄바꿈:

```text
100만 년 뒤, 지구가 아닌 다른 별에서 한
아이가 태어난다.
```

좋은 줄바꿈:

```text
100만 년 뒤,
지구가 아닌 다른 별에서 한 아이가 태어난다.
```

## 3.4 Language-Specific Subtitle

자막은 언어별로 분리되어야 한다.

```text
ko subtitle
en subtitle
ja subtitle
...
```

직역보다 자연스러운 표현을 우선한다.

단, Story의 의미와 Factual Safety는 유지해야 한다.

---

# 4. Subtitle Engine Responsibilities

Subtitle Engine의 책임:

```text
Timeline 로드
Timeline Lock 확인
Voice Handoff 로드
언어별 Narration 로드
언어별 Voice Config 로드
Audio Asset 확인
Scene별 Subtitle Segment 생성
SRT Timestamp 생성
언어별 Line Break 적용
Reading Speed 검증
Voice Sync 검증
Subtitle File 생성
Subtitle Asset Registry 업데이트
Timeline Subtitle Reference 업데이트
Subtitle Review 생성
Editing Engine Handoff 생성
```

Subtitle Engine이 하지 않는 것:

```text
Voice를 직접 생성하지 않는다.
Typecast를 직접 호출하지 않는다.
Story 핵심 의미를 임의 변경하지 않는다.
Timeline Scene ID를 변경하지 않는다.
Final Video에 자막을 직접 입히지 않는다.
Final Editing을 수행하지 않는다.
Quality Score를 최종 계산하지 않는다.
Provider를 직접 호출하지 않는다.
```

---

# 5. Inputs

Subtitle Engine의 입력:

```text
project.json
channel_snapshot.json
template_snapshot.json
timeline/timeline.json
timeline/timeline_lock.json
languages/{lang}/narration.txt
languages/{lang}/voice.json
assets/asset_registry.json
reports/voice_review.json
channels/{channel_id}/subtitle.yaml
channels/{channel_id}/brand.yaml
workflow/handoffs/VOICE_to_SUBTITLE.json
workflow/memory_context_SUBTITLE.json
```

필수 입력:

```text
project.json
timeline/timeline.json
timeline/timeline_lock.json
languages/{lang}/narration.txt
languages/{lang}/voice.json
reports/voice_review.json
channel_snapshot.json
```

선택 입력:

```text
Audio Asset Duration
Scene별 Voice Track
Subtitle Success Memory
Subtitle Failure Memory
Language Line Break Memory
Reading Speed Memory
Brand Language Memory
```

---

# 6. Outputs

Subtitle Engine의 출력:

```text
languages/{lang}/subtitle.srt
languages/{lang}/subtitle.json
assets/subtitles/subtitle_{lang}_v001.srt
reports/subtitle_review.json
assets/asset_registry.json
workflow/stage_results/SUBTITLE_result.json
workflow/handoffs/SUBTITLE_to_EDITING.json
```

예시:

```text
languages/ko/subtitle.srt
languages/en/subtitle.srt
languages/ko/subtitle.json
languages/en/subtitle.json
assets/subtitles/subtitle_ko_v001.srt
assets/subtitles/subtitle_en_v001.srt
```

v1.0 최소 출력:

```text
languages/{lang}/subtitle.srt
languages/{lang}/subtitle.json
reports/subtitle_review.json
workflow/handoffs/SUBTITLE_to_EDITING.json
```

---

# 7. Subtitle Creation Flow

Subtitle Engine 실행 흐름:

```text
Load Project Context
↓
Load Timeline
↓
Load Timeline Lock
↓
Load Voice Handoff
↓
Load Language Narration
↓
Load Voice Config
↓
Load Subtitle Rules
↓
Load Memory Context
↓
Validate Subtitle Inputs
↓
Build Subtitle Segments
↓
Generate Timestamps
↓
Apply Line Break Rules
↓
Check Reading Speed
↓
Check Voice Sync
↓
Write subtitle.json
↓
Write subtitle.srt
↓
Copy or Register to assets/subtitles/
↓
Update Asset Registry
↓
Update Timeline Subtitle References
↓
Build Subtitle Review
↓
Handoff to Editing Engine
```

---

# 8. Subtitle Strategy

Subtitle Strategy는 Channel과 Template에서 정의된다.

예시:

```yaml
subtitle:
  default_format: srt
  supported_formats:
    - srt
    - vtt

  line_rules:
    max_lines_per_caption: 2
    max_chars_per_line_ko: 22
    max_chars_per_line_en: 42
    prefer_meaning_based_break: true

  timing:
    min_duration_seconds: 1.0
    max_duration_seconds: 6.0
    min_gap_seconds: 0.05
    sync_with_voice: true

  readability:
    avoid_too_fast: true
    max_cps_ko: 13
    max_cps_en: 18

  style:
    burn_in: false
    editing_engine_handles_style: true
```

---

# 9. Subtitle Segment Schema

Subtitle Segment는 자막의 최소 단위이다.

```json
{
  "segment_id": "SUB-KO-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "language": "ko",
  "scene_id": "SC001",

  "index": 1,

  "time": {
    "start": "00:00:00,000",
    "end": "00:00:03,500",
    "duration_seconds": 3.5
  },

  "text": {
    "raw": "100만 년 뒤, 지구가 아닌 다른 별에서 한 아이가 태어난다.",
    "lines": [
      "100만 년 뒤,",
      "지구가 아닌 다른 별에서 한 아이가 태어난다."
    ]
  },

  "readability": {
    "char_count": 31,
    "chars_per_second": 8.9,
    "status": "PASS"
  },

  "sync": {
    "source": "voice_estimated",
    "confidence": "MEDIUM",
    "issues": []
  }
}
```

---

# 10. subtitle.json Schema

`languages/{lang}/subtitle.json`은 SRT보다 구조화된 자막 기준 파일이다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "language": "ko",
  "stage": "SUBTITLE",

  "source": {
    "narration_ref": "languages/ko/narration.txt",
    "voice_ref": "assets/audio/voice_ko_v001.wav",
    "voice_config_ref": "languages/ko/voice.json",
    "timeline_ref": "timeline/timeline.json"
  },

  "subtitle": {
    "format": "srt",
    "file": "languages/ko/subtitle.srt",
    "asset_file": "assets/subtitles/subtitle_ko_v001.srt",
    "total_segments": 0,
    "total_duration_seconds": 900
  },

  "segments": [
    {
      "segment_id": "SUB-KO-000001",
      "scene_id": "SC001",
      "index": 1,
      "start": "00:00:00,000",
      "end": "00:00:03,500",
      "text": "100만 년 뒤,\n지구가 아닌 다른 별에서 한 아이가 태어난다.",
      "readability_status": "PASS",
      "sync_status": "PASS_WITH_ESTIMATE"
    }
  ],

  "validation": {
    "line_length_valid": true,
    "reading_speed_valid": true,
    "sync_valid": true,
    "scene_mapping_valid": true,
    "issues": []
  },

  "created_at": "2026-07-10T14:00:00",
  "updated_at": "2026-07-10T14:00:00"
}
```

---

# 11. SRT Format Rules

SRT 파일은 다음 형식을 따라야 한다.

```text
1
00:00:00,000 --> 00:00:03,500
100만 년 뒤,
지구가 아닌 다른 별에서 한 아이가 태어난다.

2
00:00:03,500 --> 00:00:06,800
그 아이의 눈은
우리와 같은 빛을 볼까?
```

규칙:

```text
Index는 1부터 시작한다.
Timestamp 형식은 HH:MM:SS,mmm 이다.
Start는 End보다 빨라야 한다.
Segment 사이에는 빈 줄이 있어야 한다.
한 Caption은 최대 2줄을 권장한다.
```

---

# 12. Timestamp Rules

Timestamp는 Voice와 Timeline을 기준으로 만든다.

우선순위:

```text
1. 실제 Audio Timestamp
2. Scene별 actual_duration_seconds
3. Voice Engine의 estimated_duration_seconds
4. Timeline Scene Duration
```

v1.0에서는 실제 음소 단위 정밀 Sync가 없어도 된다.

대신 다음을 보장해야 한다.

```text
시간이 겹치지 않는다.
전체 자막 길이가 Voice 길이와 크게 어긋나지 않는다.
Scene 순서와 자막 순서가 맞다.
자막이 너무 빠르게 지나가지 않는다.
```

---

# 13. Line Break Rules

자막 줄바꿈은 의미 단위로 한다.

공통 규칙:

```text
한 Caption 최대 2줄 권장
문장 중간의 어색한 끊김 방지
조사, 전치사, 관사만 단독 줄에 두지 않음
숫자와 단위는 되도록 함께 유지
강조 문장은 짧게 유지
```

한국어 권장:

```text
한 줄 18~22자 내외 권장
의미 단위 우선
조사만 다음 줄로 넘기지 않음
```

영어 권장:

```text
한 줄 32~42자 내외 권장
전치사만 다음 줄로 넘기지 않음
관사만 단독으로 두지 않음
```

---

# 14. Reading Speed Rules

Subtitle Engine은 읽기 속도를 검사해야 한다.

기준:

```yaml
reading_speed:
  ko:
    target_cps: 10
    max_cps: 13
  en:
    target_cps: 15
    max_cps: 18
```

CPS:

```text
Characters Per Second
```

Reading Speed가 너무 빠른 경우:

```text
Caption을 나눈다.
표현을 짧게 수정한다.
Duration을 조정한다.
Voice / Editing 조정 요청을 만든다.
```

---

# 15. Voice Sync Rules

Subtitle은 Voice와 맞아야 한다.

검사 항목:

```text
Subtitle 전체 길이와 Voice 길이 비교
Scene별 Subtitle 길이와 Scene Voice 길이 비교
자막 시작이 Voice보다 너무 늦지 않은지
자막 종료가 Voice보다 너무 빠르지 않은지
Caption 전환이 너무 촘촘하지 않은지
```

Sync 상태:

```text
PASS
PASS_WITH_ESTIMATE
ADJUSTMENT_REQUIRED
FAIL
```

v1.0에서는 `PASS_WITH_ESTIMATE`를 허용한다.

정밀 Audio Timestamp가 없는 경우 추정 Sync를 사용한다.

---

# 16. Language Rules

언어별 자막은 자연스러워야 한다.

규칙:

```text
직역 느낌을 줄인다.
언어별 자연스러운 문장 길이를 사용한다.
Story 의미를 유지한다.
Speculative Claim의 조심스러운 표현을 유지한다.
Brand Tone을 유지한다.
Voice와 동일한 의미를 유지한다.
```

금지:

```text
자막에서 의미를 임의로 바꿈
Speculative Claim을 확정 표현으로 바꿈
Voice에는 없는 강한 주장 추가
기계 번역 느낌
너무 긴 영어 자막
너무 긴 한국어 자막
```

---

# 17. Subtitle Asset Naming Rules

Subtitle 파일명은 언어 코드를 포함해야 한다.

기본 형식:

```text
assets/subtitles/subtitle_{lang}_v{version}.srt
```

예시:

```text
assets/subtitles/subtitle_ko_v001.srt
assets/subtitles/subtitle_en_v001.srt
```

언어 폴더 내부 기본 파일:

```text
languages/ko/subtitle.srt
languages/en/subtitle.srt
```

두 위치는 같은 내용을 가질 수 있다.

```text
languages/{lang}/subtitle.srt
→ 언어별 작업 파일

assets/subtitles/subtitle_{lang}_v001.srt
→ Editing / Package용 Asset 파일
```

---

# 18. Asset Registry Integration

Subtitle 결과물은 Asset Registry에 등록되어야 한다.

파일:

```text
assets/asset_registry.json
```

Subtitle Asset Entry 예시:

```json
{
  "asset_id": "ASSET-SUB-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "language": "ko",
  "asset_type": "subtitle",
  "file": "assets/subtitles/subtitle_ko_v001.srt",
  "source_file": "languages/ko/subtitle.srt",
  "format": "srt",
  "status": "REGISTERED",
  "selected": true,
  "created_at": "2026-07-10T14:00:00"
}
```

규칙:

```text
Subtitle 파일만 있으면 완료가 아니다.
Asset Registry에 등록되어야 한다.
언어 코드가 일치해야 한다.
Editing Engine은 Asset Registry를 기준으로 Subtitle을 찾는다.
```

---

# 19. Timeline Subtitle Update Rules

Subtitle Asset이 등록되면 Timeline의 subtitle field를 업데이트할 수 있다.

허용 업데이트:

```text
timeline.scenes[].subtitle.language_tracks.{lang}.subtitle_ref
timeline.scenes[].subtitle.language_tracks.{lang}.sync_status
timeline.scenes[].quality.issues
```

금지 업데이트:

```text
scene_id 변경
scene_order 변경
scene_purpose 변경
voice_ref 무단 변경
visual asset_ref 무단 변경
motion asset_ref 무단 변경
language_tracks 삭제
```

Timeline Lock을 위반하면 안 된다.

---

# 20. Subtitle Review Schema

`reports/subtitle_review.json`은 Subtitle Stage의 검토 결과이다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "SUBTITLE",

  "score": 93,
  "status": "PASS_WITH_NOTES",

  "summary": {
    "languages": [
      "ko",
      "en"
    ],
    "subtitle_files_created": true,
    "asset_registry_updated": true,
    "sync_status": "PASS_WITH_ESTIMATE"
  },

  "language_reviews": [
    {
      "language": "ko",
      "subtitle_file": "languages/ko/subtitle.srt",
      "asset_file": "assets/subtitles/subtitle_ko_v001.srt",

      "checks": {
        "subtitle_exists": true,
        "srt_format_valid": true,
        "line_length_valid": true,
        "reading_speed_valid": true,
        "voice_sync_valid": true,
        "scene_mapping_valid": true,
        "speculation_framing_preserved": true,
        "asset_registry_integrity": true
      },

      "issues": []
    }
  ],

  "handoff_notes": [
    "Editing Engine should use subtitle_ko_v001.srt for Korean render.",
    "Sync is estimated from voice duration and should be checked during final editing."
  ]
}
```

---

# 21. Subtitle Scoring

Subtitle Score 기준:

```yaml
subtitle_score:
  subtitle_completeness: 15
  srt_format_validity: 15
  line_break_quality: 15
  reading_speed: 15
  voice_sync: 20
  language_naturalness: 10
  factual_framing_preserved: 5
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
Subtitle fail
```

Hard Fail 조건:

```text
필수 언어 Subtitle 누락
SRT 형식 오류
Timestamp 겹침
Voice와 심각한 Sync 불일치
읽기 속도 과도
Speculative Claim 표현 변경
Asset Registry 누락
Timeline Lock 위반
```

---

# 22. Subtitle Validation Rules

Subtitle Validator는 다음을 확인해야 한다.

```text
languages/{lang}/subtitle.srt 존재
languages/{lang}/subtitle.json 존재
reports/subtitle_review.json 존재
project_id 일치
channel_id 일치
target_languages와 subtitle files 일치
SRT Index 순서 유효
Timestamp 형식 유효
Timestamp 겹침 없음
Start < End
Line 길이 규칙 준수
Reading Speed 기준 준수
Voice Sync 상태 확인
Scene ID 연결 확인
Asset Registry 연결 확인
Timeline Lock 위반 없음
Speculative Claim 표현 유지
```

검증 실패 시 EDITING Stage로 이동할 수 없다.

---

# 23. Editing Engine Handoff

Subtitle Engine은 Editing Engine에 Subtitle Asset 정보를 넘긴다.

Handoff 파일:

```text
workflow/handoffs/SUBTITLE_to_EDITING.json
```

포함 내용:

```text
언어별 Subtitle File
Subtitle Asset Ref
Format
Sync Status
Line Break Notes
Reading Speed Issues
Editing Usage Notes
```

예시:

```json
{
  "from_stage": "SUBTITLE",
  "to_stage": "EDITING",
  "project_id": "20260710-093500-future-million-year-human",

  "subtitle_assets": [
    {
      "language": "ko",
      "subtitle_ref": "assets/subtitles/subtitle_ko_v001.srt",
      "source_file": "languages/ko/subtitle.srt",
      "format": "srt",
      "sync_status": "PASS_WITH_ESTIMATE",
      "issues": []
    },
    {
      "language": "en",
      "subtitle_ref": "assets/subtitles/subtitle_en_v001.srt",
      "source_file": "languages/en/subtitle.srt",
      "format": "srt",
      "sync_status": "PASS_WITH_ESTIMATE",
      "issues": []
    }
  ],

  "editing_notes": [
    "Use language-specific subtitles for each render.",
    "Final sync should be reviewed during Editing stage."
  ]
}
```

---

# 24. Auto Fix Rules

Subtitle 문제 발생 시 부분 수정이 우선이다.

수정 대상:

```text
특정 언어 Subtitle
특정 Scene Subtitle
특정 Caption Timestamp
Line Break
Reading Speed
Sync Offset
SRT Format
```

금지:

```text
전체 Project 재생성
Story 핵심 의미 변경
Voice 무단 변경
Scene ID 변경
Timeline 구조 무단 변경
Speculative Framing 변경
```

Auto Fix 예시:

```text
Issue:
SC004 Korean subtitle is too long and exceeds reading speed.

Fix:
Split only SC004 subtitle into two captions and adjust timestamps.
```

---

# 25. Provider Engine Integration

v1.0에서 Subtitle은 기본적으로 Internal Subtitle Provider를 사용한다.

구조:

```text
Subtitle Engine
↓
Provider Engine
↓
SubtitleProviderInterface
↓
InternalSubtitleAdapter
```

단, Subtitle Engine은 외부 Provider가 아닌 내부 로직으로 생성할 수 있다.

그래도 Provider Engine 규칙과 로그 구조를 유지할 수 있다.

```text
provider_name = internal_subtitle
mode = automated
```

---

# 26. Memory Integration

Subtitle Engine은 작업 전 Memory Context를 사용한다.

사용 가능한 Memory:

```text
Subtitle Line Break Memory
Subtitle Sync Failure Memory
Language Naturalness Memory
Reading Speed Memory
Brand Language Memory
Quality Subtitle Failure Memory
```

Subtitle Engine은 작업 후 Memory Candidate를 만들 수 있다.

예시:

```text
한국어 자막에서 좋은 줄바꿈 패턴
영어 자막에서 자주 길어지는 문장 패턴
Sync 문제를 자주 만드는 Voice 길이 패턴
특정 Channel에서 읽기 좋은 자막 속도
```

Memory 확정은 Memory Engine 또는 Learning Engine이 담당한다.

---

# 27. Error Types

Subtitle Engine의 Error Type:

```text
SubtitleInputMissingError
NarrationMissingError
VoiceConfigMissingError
AudioAssetMissingError
SubtitleCreationError
SRTFormatError
TimestampError
LineBreakError
ReadingSpeedError
VoiceSyncError
SubtitleSceneMappingError
SubtitleAssetRegistrationError
SubtitleTimelineUpdateError
SubtitleSpeculationFramingError
SubtitleReviewError
SubtitleValidationError
SubtitleHandoffError
```

Error 예시:

```json
{
  "error_type": "ReadingSpeedError",
  "message": "Subtitle segment SUB-KO-000014 exceeds maximum reading speed.",
  "project_id": "20260710-093500-future-million-year-human",
  "language": "ko",
  "segment_id": "SUB-KO-000014",
  "stage": "SUBTITLE",
  "severity": "MEDIUM",
  "suggested_fix": "Split the subtitle into shorter segments or extend display duration.",
  "created_at": "2026-07-10T14:00:00"
}
```

---

# 28. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
SubtitleEngine
SubtitleInputLoader
SubtitleInputValidator
SubtitleSegmentBuilder
SRTBuilder
SubtitleJSONBuilder
TimestampBuilder
LineBreakOptimizer
ReadingSpeedChecker
VoiceSyncChecker
LanguageSubtitleChecker
SpeculationSubtitleChecker
SubtitleAssetRegistryUpdater
SubtitleTimelineUpdater
SubtitleReviewBuilder
SubtitleValidator
SubtitleHandoffBuilder
SubtitleErrorReporter
```

---

# 29. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/24_SUBTITLE_ENGINE.md
→ engines/subtitle/
```

예시 구조:

```text
engines/
└── subtitle/
    ├── subtitle_engine.py
    ├── subtitle_input_loader.py
    ├── subtitle_input_validator.py
    ├── subtitle_segment_builder.py
    ├── srt_builder.py
    ├── subtitle_json_builder.py
    ├── timestamp_builder.py
    ├── line_break_optimizer.py
    ├── reading_speed_checker.py
    ├── voice_sync_checker.py
    ├── language_subtitle_checker.py
    ├── speculation_subtitle_checker.py
    ├── subtitle_asset_registry_updater.py
    ├── subtitle_timeline_updater.py
    ├── subtitle_review_builder.py
    ├── subtitle_validator.py
    ├── subtitle_handoff_builder.py
    └── subtitle_error_reporter.py
```

---

# 30. Main Public Operations

Subtitle Engine은 최소 다음 작업을 제공해야 한다.

```text
run_subtitle(project_id)
load_subtitle_inputs(project_id)
validate_subtitle_inputs(project_id)
build_subtitle_segments(project_id, language)
build_srt(project_id, language)
build_subtitle_json(project_id, language)
optimize_line_breaks(project_id, language)
check_reading_speed(project_id, language)
check_voice_sync(project_id, language)
register_subtitle_assets(project_id)
update_timeline_subtitle_refs(project_id)
build_subtitle_review(project_id)
validate_subtitle_outputs(project_id)
build_handoff_to_editing(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
언어별 Subtitle 생성
Voice Sync 확인
Line Break 규칙 적용
Reading Speed 확인
Speculative Framing 유지
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
Voice Handoff 로드
언어별 narration.txt 로드
언어별 voice.json 로드
Subtitle 입력 검증
언어별 Subtitle Segment 생성
SRT Timestamp 생성
Line Break 규칙 적용
Reading Speed 기본 검사
Voice Sync 기본 검사
languages/{lang}/subtitle.srt 생성
languages/{lang}/subtitle.json 생성
assets/subtitles/subtitle_{lang}_v001.srt 생성
Asset Registry 등록
subtitle_review.json 생성
Editing Engine Handoff 생성
Subtitle Validation 수행
```

v1.0에서 하지 않아도 되는 것:

```text
정밀 음소 단위 Sync
자동 음성 인식 기반 자막 생성
고급 자막 스타일링
Final Video에 자막 Burn-in
실시간 자막 편집 UI
외부 자막 Provider 자동 연동
Final Editing 수행
```

v1.0에서는 언어별 SRT 파일과 Editing / Quality가 사용할 수 있는 Subtitle 구조를 안정적으로 만드는 것이 우선이다.

---

# 32. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Timeline과 Voice 정보를 로드할 수 있다.
Subtitle 입력을 검증할 수 있다.
언어별 Subtitle Segment를 만들 수 있다.
언어별 subtitle.json을 생성할 수 있다.
언어별 subtitle.srt를 생성할 수 있다.
SRT Timestamp 형식을 지킬 수 있다.
자막 줄바꿈 규칙을 적용할 수 있다.
Reading Speed를 검사할 수 있다.
Voice Sync를 기본 검사할 수 있다.
Subtitle Asset을 Asset Registry와 연결할 수 있다.
Timeline의 subtitle_ref를 업데이트할 수 있다.
subtitle_review.json을 생성할 수 있다.
Editing Engine으로 Handoff를 만들 수 있다.
Subtitle Validation 실패 시 EDITING Stage 진행을 막을 수 있다.
```

---

# 33. Non Goals

v1.0에서 Subtitle Engine이 하지 않는 것:

```text
Voice 직접 생성
Typecast 직접 호출
Story 핵심 의미 변경
Timeline Scene ID 변경
Final Video 렌더링
자막 Burn-in
고급 스타일 디자인
Quality Score 최종 계산
Provider Secret 관리 직접 수행
```

v1.0에서는 언어별 자막 파일, Sync 기준, Asset Registry 연결, Editing Handoff 구조를 만드는 것이 핵심이다.

---

# 34. Critical Subtitle Rules

반드시 지켜야 할 규칙:

```text
1. Subtitle Engine은 Timeline 없이 실행하지 않는다.

2. Subtitle Engine은 Voice 정보 없이 실행하지 않는다.

3. Subtitle Engine은 언어별 자막을 분리해야 한다.

4. Subtitle Engine은 Scene ID를 변경하지 않는다.

5. Subtitle은 Voice와 Sync되어야 한다.

6. Subtitle은 읽기 쉬워야 한다.

7. 한 Caption은 최대 2줄을 권장한다.

8. Line Break는 의미 단위로 한다.

9. Reading Speed가 과도하면 안 된다.

10. Speculative Claim의 표현을 바꾸면 안 된다.

11. Subtitle 결과물은 Asset Registry에 등록해야 한다.

12. Timeline Lock을 위반하지 않는다.

13. Subtitle Engine은 Final Video에 자막을 직접 입히지 않는다.

14. Subtitle Validation 실패 시 Editing Stage로 넘어가지 않는다.

15. 중요한 Subtitle 판단은 Self Review와 Handoff에 기록한다.
```

---

# 35. Final Principle

Subtitle Engine은 시청자가 영상을 이해하고 끝까지 따라오게 만드는 가독성 엔진이다.

좋은 자막은 보이지 않게 자연스럽다.

좋은 자막은 Voice와 맞고,

의미 단위로 끊기고,

읽기 쉽고,

언어별로 자연스럽고,

Editing과 Quality가 안정적으로 사용할 수 있다.

Subtitle Engine의 목적은 단순히 SRT 파일을 만드는 것이 아니라, 언어별 시청 경험을 완성하는 것이다.
