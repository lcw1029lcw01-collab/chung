# 23_VOICE_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Voice Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Voice Engine을 정의한다.

Voice Engine은 Story Script와 Timeline을 기반으로 언어별 나레이션 텍스트, Typecast용 Voice Request, Voice 설정, Audio Asset 연결, Timeline Fit Check를 생성하는 엔진이다.

Voice Engine은 음성을 직접 생성하지 않는다.

Voice Engine은 다음을 담당한다.

```text
Timeline 로드
언어별 Script 로드
Voice Rule 로드
Brand Tone 로드
언어별 narration.txt 생성
언어별 voice.json 생성
Typecast용 Voice Request 생성
Provider Engine에 Voice Request 전달
Manual / Semi-Automated Typecast Workflow 지원
Voice Result 등록 확인
Audio Asset Registry 연결
Timeline voice_ref 업데이트
Voice Length / Timeline Fit Check
Voice Review 생성
Subtitle Engine에 Handoff 생성
Editing Engine에 Handoff 생성
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
24_SUBTITLE_ENGINE.md
25_EDITING_ENGINE.md
26_QUALITY_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Voice Engine은 대본을 실제 음성 제작 가능한 언어별 Voice Package로 바꾸는 엔진이다.

전체 흐름:

```text
Story Script
↓
Language Script
↓
Timeline
↓
Voice Engine
↓
Narration Text
↓
Provider Engine
↓
Typecast
↓
Audio Assets
↓
Voice Review
↓
Subtitle / Editing / Quality
```

Voice Engine의 핵심 목표는 다음이다.

```text
언어별 자연스러운 나레이션을 준비한다.
Brand Tone에 맞는 Voice 방향을 유지한다.
Typecast에서 사용할 수 있는 입력 구조를 만든다.
Audio 파일을 Scene / Language와 연결한다.
Voice 길이가 Timeline과 맞는지 확인한다.
Subtitle Engine이 Sync를 만들 수 있게 한다.
Editing Engine이 Audio Track을 사용할 수 있게 한다.
```

---

# 3. Voice Philosophy

## 3.1 Voice Carries Trust

Voice는 단순한 읽기가 아니다.

Voice는 Channel의 신뢰감, 몰입감, 감정, 속도를 결정한다.

나쁜 Voice:

```text
너무 빠른 읽기
기계적인 말투
Brand와 맞지 않는 과장된 감정
문장 끊김이 부자연스러움
언어별 직역 느낌
```

좋은 Voice:

```text
Brand Tone과 맞는 속도
문장 의미에 맞는 호흡
Hook에서 몰입감 있는 낮은 긴장
설명부에서 명확한 전달
Ending에서 여운 있는 톤
```

## 3.2 Language-Specific Voice

Voice는 언어별로 분리되어야 한다.

```text
ko Voice
en Voice
ja Voice
...
```

같은 Timeline을 공유하더라도 언어별 문장 길이와 발화 시간이 다를 수 있다.

## 3.3 Voice Must Fit Timeline

Voice는 Timeline과 맞아야 한다.

Voice가 너무 길거나 짧으면 Editing, Subtitle, Retention이 흔들린다.

## 3.4 Provider Independent

Voice Engine은 Typecast를 직접 실행하지 않는다.

반드시 Provider Engine을 통해 Request를 만든다.

```text
Voice Engine
↓
Provider Engine
↓
VoiceProviderInterface
↓
TypecastAdapter
```

---

# 4. Voice Engine Responsibilities

Voice Engine의 책임:

```text
Timeline 로드
Story Script 로드
Language Script 로드
Voice Rule 로드
Brand Voice Tone 로드
Scene별 Narration 분리
언어별 narration.txt 생성
언어별 voice.json 생성
Typecast용 Request 생성
Voice Provider Request 생성 요청
Manual Action Guide 생성 지원
Audio Result 등록 확인
Audio Asset Registry 업데이트
Timeline Voice Reference 업데이트
Voice Duration Check
Timeline Fit Check
Voice Review 생성
Subtitle Engine Handoff 생성
Editing Engine Handoff 생성
```

Voice Engine이 하지 않는 것:

```text
음성을 직접 생성하지 않는다.
Typecast를 직접 호출하지 않는다.
Script의 핵심 내용을 임의 변경하지 않는다.
Timeline Scene ID를 변경하지 않는다.
Subtitle을 최종 생성하지 않는다.
Final Editing을 수행하지 않는다.
Quality Score를 최종 계산하지 않는다.
```

---

# 5. Inputs

Voice Engine의 입력:

```text
project.json
channel_snapshot.json
template_snapshot.json
timeline/timeline.json
timeline/timeline_lock.json
story/script_master.json
story/script_master.md
languages/{lang}/script.json
channels/{channel_id}/voice.yaml
channels/{channel_id}/brand.yaml
channels/{channel_id}/provider.yaml
workflow/memory_context_VOICE.json
```

필수 입력:

```text
project.json
timeline/timeline.json
timeline/timeline_lock.json
story/script_master.json
channel_snapshot.json
```

언어별 입력:

```text
languages/ko/script.json
languages/en/script.json
```

선택 입력:

```text
Voice Success Memory
Voice Failure Memory
Typecast Provider Memory
Language Localization Memory
Retention Voice Pace Memory
Brand Voice Memory
```

---

# 6. Outputs

Voice Engine의 출력:

```text
languages/{lang}/narration.txt
languages/{lang}/voice.json
reports/voice_review.json
assets/asset_registry.json
workflow/stage_results/VOICE_result.json
workflow/handoffs/VOICE_to_SUBTITLE.json
workflow/handoffs/VOICE_to_EDITING.json
```

Provider Engine과 연결되는 파일:

```text
provider_requests/voice_requests.jsonl
provider_responses/voice_responses.jsonl
```

실제 Audio 결과물 위치:

```text
assets/audio/voice_ko_v001.wav
assets/audio/voice_en_v001.wav
```

또는 Scene별 분할 방식:

```text
assets/audio/SC001_voice_ko_v001.wav
assets/audio/SC002_voice_ko_v001.wav
assets/audio/SC001_voice_en_v001.wav
assets/audio/SC002_voice_en_v001.wav
```

v1.0 최소 출력:

```text
languages/{lang}/narration.txt
languages/{lang}/voice.json
reports/voice_review.json
```

---

# 7. Voice Creation Flow

Voice Engine 실행 흐름:

```text
Load Project Context
↓
Load Timeline
↓
Load Timeline Lock
↓
Load Master Script
↓
Load Language Scripts
↓
Load Brand / Voice Rules
↓
Load Memory Context
↓
Validate Voice Inputs
↓
Build Language Narration Text
↓
Map Narration to Timeline Scenes
↓
Build Voice Settings
↓
Create Typecast Voice Requests
↓
Request Provider Engine
↓
Wait for Manual or Registered Results
↓
Register Audio Assets
↓
Measure or Record Audio Duration
↓
Check Timeline Fit
↓
Update Timeline Voice References
↓
Build Voice Review
↓
Handoff to Subtitle / Editing
```

---

# 8. Voice Strategy

Voice Strategy는 Channel과 Template에서 정의된다.

예시:

```yaml
voice:
  default_provider: typecast
  default_mode: semi_automated

  tone:
    primary: calm
    secondary:
      - cinematic
      - intelligent
      - mysterious
      - trustworthy

  pace:
    default: medium_slow
    hook: slow
    explanation: medium
    climax: medium_slow
    ending: slow

  emotion:
    avoid:
      - exaggerated
      - comedic
      - childish
      - advertisement_like

  language_policy:
    preserve_story_structure: true
    allow_localization: true
    avoid_direct_translation: true
```

---

# 9. Narration Rules

Narration은 Voice가 읽기 쉬운 형태로 정리되어야 한다.

규칙:

```text
문장이 너무 길면 나눈다.
문장마다 자연스러운 호흡이 있어야 한다.
Hook은 몰입감 있게 시작한다.
설명부는 명확하고 차분해야 한다.
Ending은 여운이 있어야 한다.
언어별 자연스러운 표현을 유지한다.
Speculative Claim의 조심스러운 표현을 유지한다.
```

금지:

```text
너무 긴 문장
의미 없는 반복
광고 말투
과도한 감탄
기계 번역 느낌
Fact Risk를 바꾸는 의역
```

---

# 10. narration.txt Format

언어별 narration.txt는 사람이 Typecast에 붙여넣기 쉽게 만들어야 한다.

파일:

```text
languages/{lang}/narration.txt
```

예시:

```text
100만 년 뒤, 지구가 아닌 다른 별에서 한 아이가 태어난다.

그 아이의 눈은 우리와 같은 빛을 볼까?

그 아이의 뼈와 심장은 지구의 중력을 기억할까?

아니면 우리는 그 아이를 더 이상 같은 인간이라고 부를 수 없게 될까?
```

권장 규칙:

```text
문단 사이에 빈 줄을 둔다.
Scene 구분이 필요한 경우 주석을 사용할 수 있다.
Typecast 입력에 방해되는 불필요한 마크다운은 피한다.
```

Scene 구분이 필요한 경우:

```text
[SC001]

100만 년 뒤, 지구가 아닌 다른 별에서 한 아이가 태어난다.

[SC002]

하지만 이 장면은 확정된 미래가 아니다.
```

---

# 11. voice.json Schema

`languages/{lang}/voice.json`은 언어별 Voice 제작 정보를 담는다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "language": "ko",
  "stage": "VOICE",

  "provider": {
    "name": "typecast",
    "mode": "semi_automated",
    "adapter": "TypecastAdapter"
  },

  "voice_profile": {
    "voice_id": null,
    "voice_name": "calm_cinematic_male",
    "gender": "male",
    "tone": [
      "calm",
      "cinematic",
      "trustworthy",
      "mysterious"
    ],
    "pace": "medium_slow",
    "emotion_level": "controlled"
  },

  "narration": {
    "file": "languages/ko/narration.txt",
    "total_character_count": 0,
    "estimated_duration_seconds": 900,
    "actual_duration_seconds": null
  },

  "scene_tracks": [
    {
      "scene_id": "SC001",
      "text": "100만 년 뒤, 지구가 아닌 다른 별에서 한 아이가 태어난다.",
      "estimated_duration_seconds": 8,
      "actual_duration_seconds": null,
      "audio_ref": null,
      "status": "READY_FOR_PROVIDER"
    }
  ],

  "timeline_fit": {
    "status": "NOT_CHECKED",
    "issues": []
  },

  "created_at": "2026-07-10T13:00:00",
  "updated_at": "2026-07-10T13:00:00"
}
```

---

# 12. Typecast Request Rules

Typecast Request는 Provider Engine을 통해 생성한다.

Request에 포함할 정보:

```text
project_id
channel_id
language
provider = typecast
narration_file
voice_profile
expected_audio_output
pace
tone
scene_track_mapping
```

Provider Request 예시:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "VOICE",
  "provider_type": "voice",
  "provider_name": "typecast",
  "language": "ko",
  "narration_ref": "languages/ko/narration.txt",
  "voice_config_ref": "languages/ko/voice.json",
  "expected_output": "assets/audio/voice_ko_v001.wav"
}
```

---

# 13. Voice Asset Naming Rules

전체 언어별 Audio 방식:

```text
assets/audio/voice_{lang}_v001.wav
```

예시:

```text
assets/audio/voice_ko_v001.wav
assets/audio/voice_en_v001.wav
```

Scene별 Audio 방식:

```text
assets/audio/{scene_id}_voice_{lang}_v001.wav
```

예시:

```text
assets/audio/SC001_voice_ko_v001.wav
assets/audio/SC001_voice_en_v001.wav
```

v1.0 기본값:

```text
전체 언어별 Audio 1개를 우선 지원한다.
Scene별 Audio는 옵션으로 지원한다.
```

---

# 14. Provider Engine Integration

Voice Engine은 Provider Engine을 통해 Voice Request를 만든다.

흐름:

```text
Narration 생성
↓
Voice Settings 생성
↓
Provider Engine에 Request 생성 요청
↓
TypecastAdapter가 Manual / Semi-Automated Action Guide 생성
↓
사용자가 Typecast에서 음성 생성
↓
결과 Audio를 assets/audio/에 저장
↓
Provider Engine이 Result 등록
↓
Voice Engine이 Audio Asset 연결 확인
```

Voice Engine은 Typecast를 직접 호출하지 않는다.

---

# 15. Manual / Semi-Automated Typecast Workflow

v1.0에서는 Typecast를 Manual 또는 Semi-Automated 방식으로 사용할 수 있다.

Manual Action Guide 예시:

```json
{
  "request_id": "PROV-REQ-VOICE-000001",
  "provider": "typecast",
  "language": "ko",
  "action": "Copy languages/ko/narration.txt into Typecast, select the configured voice profile, export audio, and save it to assets/audio/voice_ko_v001.wav.",
  "narration_file": "languages/ko/narration.txt",
  "voice_config_file": "languages/ko/voice.json",
  "expected_output": "assets/audio/voice_ko_v001.wav"
}
```

---

# 16. Asset Registry Integration

Voice 결과물은 반드시 Asset Registry에 등록되어야 한다.

파일:

```text
assets/asset_registry.json
```

Voice Asset Entry 예시:

```json
{
  "asset_id": "ASSET-VOICE-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "language": "ko",
  "asset_type": "voice",
  "provider": "typecast",
  "file": "assets/audio/voice_ko_v001.wav",
  "voice_config_ref": "languages/ko/voice.json",
  "request_id": "PROV-REQ-VOICE-000001",
  "response_id": "PROV-RES-VOICE-000001",
  "duration_seconds": 902,
  "status": "REGISTERED",
  "selected": true,
  "created_at": "2026-07-10T13:30:00"
}
```

Scene별 Audio인 경우:

```json
{
  "asset_id": "ASSET-VOICE-000101",
  "project_id": "20260710-093500-future-million-year-human",
  "scene_id": "SC001",
  "language": "ko",
  "asset_type": "voice",
  "provider": "typecast",
  "file": "assets/audio/SC001_voice_ko_v001.wav",
  "duration_seconds": 8,
  "status": "REGISTERED"
}
```

---

# 17. Timeline Voice Update Rules

Voice Asset이 등록되면 Timeline의 voice field를 업데이트할 수 있다.

허용 업데이트:

```text
timeline.scenes[].voice.language_tracks.{lang}.voice_ref
timeline.scenes[].voice.language_tracks.{lang}.actual_duration_seconds
timeline.scenes[].quality.issues
```

금지 업데이트:

```text
scene_id 변경
scene_order 변경
scene_purpose 변경
visual asset_ref 무단 변경
motion asset_ref 무단 변경
language_tracks 삭제
```

Timeline Lock을 위반하면 안 된다.

---

# 18. Timeline Fit Check

Voice Engine은 Voice 길이와 Timeline 길이를 비교해야 한다.

검사 항목:

```text
전체 Voice 길이
Scene별 추정 Voice 길이
Scene별 Timeline Duration
언어별 길이 차이
Hook 길이
Ending 길이
과도하게 빠른 읽기 필요 여부
```

Timeline Fit 상태:

```text
PASS
PASS_WITH_NOTES
ADJUSTMENT_REQUIRED
FAIL
```

예시:

```json
{
  "timeline_fit": {
    "status": "PASS_WITH_NOTES",
    "language": "en",
    "total_timeline_duration_seconds": 900,
    "actual_voice_duration_seconds": 935,
    "difference_seconds": 35,
    "issues": [
      {
        "type": "VOICE_TOO_LONG",
        "severity": "MEDIUM",
        "suggested_fix": "Shorten English narration or allow editing adjustment."
      }
    ]
  }
}
```

---

# 19. Voice Review Schema

`reports/voice_review.json`은 Voice Stage의 검토 결과이다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "VOICE",

  "score": 92,
  "status": "PASS_WITH_NOTES",

  "summary": {
    "languages": [
      "ko",
      "en"
    ],
    "audio_registered": true,
    "timeline_fit_status": "PASS_WITH_NOTES"
  },

  "language_reviews": [
    {
      "language": "ko",
      "narration_file": "languages/ko/narration.txt",
      "voice_config_file": "languages/ko/voice.json",
      "audio_ref": "assets/audio/voice_ko_v001.wav",

      "checks": {
        "narration_exists": true,
        "voice_config_exists": true,
        "audio_exists": true,
        "brand_tone_fit": 94,
        "voice_readability": 95,
        "pace_fit": 92,
        "timeline_fit": 90,
        "speculation_framing_preserved": true,
        "asset_registry_integrity": true
      },

      "issues": []
    }
  ],

  "handoff_notes": [
    "Subtitle Engine should use voice duration for sync.",
    "English version may need minor timing adjustment in Editing."
  ]
}
```

---

# 20. Voice Scoring

Voice Score 기준:

```yaml
voice_score:
  narration_completeness: 15
  language_naturalness: 15
  brand_tone_fit: 15
  voice_readability: 15
  pace_fit: 10
  timeline_fit: 15
  factual_framing_preserved: 10
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
Voice fail
```

Hard Fail 조건:

```text
필수 언어 Narration 누락
필수 언어 Audio 누락
Audio Asset Registry 누락
Voice가 Brand와 심각하게 불일치
Speculative Claim 표현이 바뀜
Timeline보다 지나치게 길거나 짧음
음성 파일 손상
```

---

# 21. Voice Validation Rules

Voice Validator는 다음을 확인해야 한다.

```text
languages/{lang}/narration.txt 존재
languages/{lang}/voice.json 존재
reports/voice_review.json 존재
project_id 일치
channel_id 일치
target_languages와 voice files 일치
narration이 비어 있지 않음
voice.json에 scene_tracks 존재
Timeline Scene ID와 scene_tracks 연결
Audio Result가 등록되었는지 확인
Asset Registry 연결 확인
Timeline Lock 위반 없음
Speculative Claim 표현 유지
```

Manual Provider Result가 아직 없으면 Workflow는 `WAITING_FOR_MANUAL_ACTION` 상태가 될 수 있다.

---

# 22. Subtitle Engine Handoff

Voice Engine은 Subtitle Engine에 Handoff를 생성해야 한다.

Handoff 파일:

```text
workflow/handoffs/VOICE_to_SUBTITLE.json
```

포함 내용:

```text
언어별 narration.txt
언어별 voice.json
언어별 audio_ref
Audio duration
Scene track mapping
Timeline Fit Issues
Subtitle Sync Notes
```

예시:

```json
{
  "from_stage": "VOICE",
  "to_stage": "SUBTITLE",
  "project_id": "20260710-093500-future-million-year-human",

  "languages": [
    {
      "language": "ko",
      "narration_ref": "languages/ko/narration.txt",
      "voice_config_ref": "languages/ko/voice.json",
      "audio_ref": "assets/audio/voice_ko_v001.wav",
      "duration_seconds": 902,
      "sync_notes": []
    }
  ],

  "subtitle_notes": [
    "Use voice duration as primary sync source.",
    "Preserve meaning-based line breaks."
  ]
}
```

---

# 23. Editing Engine Handoff

Voice Engine은 Editing Engine에 Audio Asset 정보를 넘긴다.

Handoff 파일:

```text
workflow/handoffs/VOICE_to_EDITING.json
```

포함 내용:

```text
언어별 Audio Asset
Audio Duration
Timeline Fit Status
Scene Track Mapping
Editing Adjustment Notes
```

---

# 24. Auto Fix Rules

Voice 문제 발생 시 부분 수정이 우선이다.

수정 대상:

```text
특정 언어 narration
특정 Scene narration
Voice pace
Voice profile
Audio 재생성
Timeline Fit 조정 요청
```

금지:

```text
전체 Project 재생성
Story 핵심 의미 변경
Forbidden Claim 추가
Scene ID 변경
Timeline 구조 무단 변경
```

Auto Fix 예시:

```text
Issue:
English voice is 60 seconds longer than target timeline.

Fix:
Shorten only English narration while preserving meaning and speculative framing.
```

---

# 25. Memory Integration

Voice Engine은 작업 전 Memory Context를 사용한다.

사용 가능한 Memory:

```text
Successful Voice Tone Memory
Failed Voice Tone Memory
Typecast Voice Setting Memory
Language Pace Memory
Subtitle Sync Failure Memory
Brand Voice Memory
Retention Voice Pace Memory
```

Voice Engine은 작업 후 Memory Candidate를 만들 수 있다.

예시:

```text
특정 Channel에서 좋은 Voice 속도
특정 Typecast Voice Profile 성공
영어 번역에서 자주 길어지는 문장 패턴
Timeline Fit 문제를 만드는 Narration 패턴
```

Memory 확정은 Memory Engine 또는 Learning Engine이 담당한다.

---

# 26. Error Types

Voice Engine의 Error Type:

```text
VoiceInputMissingError
LanguageScriptMissingError
NarrationCreationError
VoiceConfigError
VoiceProviderRequestError
VoiceAssetMissingError
VoiceAssetRegistrationError
VoiceTimelineFitError
VoiceSceneTrackMismatchError
VoiceBrandMismatchError
VoiceSpeculationFramingError
VoiceReviewError
VoiceValidationError
VoiceHandoffError
```

Error 예시:

```json
{
  "error_type": "VoiceTimelineFitError",
  "message": "English voice duration exceeds target timeline by 60 seconds.",
  "project_id": "20260710-093500-future-million-year-human",
  "language": "en",
  "stage": "VOICE",
  "severity": "MEDIUM",
  "suggested_fix": "Shorten English narration or create editing adjustment plan.",
  "created_at": "2026-07-10T13:30:00"
}
```

---

# 27. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
VoiceEngine
VoiceInputLoader
VoiceInputValidator
NarrationBuilder
LanguageNarrationBuilder
VoiceConfigBuilder
TypecastRequestBuilder
VoiceProviderRequestBuilder
VoiceAssetRegistryUpdater
VoiceTimelineUpdater
VoiceDurationAnalyzer
TimelineFitChecker
BrandVoiceChecker
SpeculationVoiceChecker
VoiceReviewBuilder
VoiceValidator
VoiceHandoffBuilder
VoiceErrorReporter
```

---

# 28. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/23_VOICE_ENGINE.md
→ engines/voice/
```

예시 구조:

```text
engines/
└── voice/
    ├── voice_engine.py
    ├── voice_input_loader.py
    ├── voice_input_validator.py
    ├── narration_builder.py
    ├── language_narration_builder.py
    ├── voice_config_builder.py
    ├── typecast_request_builder.py
    ├── voice_provider_request_builder.py
    ├── voice_asset_registry_updater.py
    ├── voice_timeline_updater.py
    ├── voice_duration_analyzer.py
    ├── timeline_fit_checker.py
    ├── brand_voice_checker.py
    ├── speculation_voice_checker.py
    ├── voice_review_builder.py
    ├── voice_validator.py
    ├── voice_handoff_builder.py
    └── voice_error_reporter.py
```

---

# 29. Main Public Operations

Voice Engine은 최소 다음 작업을 제공해야 한다.

```text
run_voice(project_id)
load_voice_inputs(project_id)
validate_voice_inputs(project_id)
build_narration(project_id, language)
build_all_language_narrations(project_id)
build_voice_config(project_id, language)
create_voice_provider_requests(project_id)
register_voice_assets(project_id)
analyze_voice_duration(project_id)
check_timeline_fit(project_id)
update_timeline_voice_refs(project_id)
build_voice_review(project_id)
validate_voice_outputs(project_id)
build_handoff_to_subtitle(project_id)
build_handoff_to_editing(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
언어별 Script 유지
Brand Voice Tone 유지
Speculative Framing 유지
Provider Engine 경유
Asset Registry 연결
Timeline Lock 준수
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 30. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Timeline 로드
Story Script 로드
언어별 Script 로드
Voice 입력 검증
언어별 narration.txt 생성
언어별 voice.json 생성
Typecast Request 생성용 데이터 준비
Manual / Semi-Automated Action Guide 지원
Voice Asset 등록 확인
Timeline Fit 기본 검사
voice_review.json 생성
Subtitle Engine Handoff 생성
Editing Engine Handoff 생성
Voice Validation 수행
```

v1.0에서 하지 않아도 되는 것:

```text
Typecast 완전 자동 API 호출
음성 직접 생성
고급 음성 감정 분석
정밀 음소 단위 Sync
실시간 더빙 UI
Final Editing 수행
Subtitle 직접 생성
Provider 직접 호출
```

v1.0에서는 Typecast Workflow를 안정적으로 지원하고, 언어별 Audio Asset과 Timeline을 연결하는 구조를 만드는 것이 우선이다.

---

# 31. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Timeline과 Story Script를 로드할 수 있다.
Voice 입력을 검증할 수 있다.
언어별 narration.txt를 생성할 수 있다.
언어별 voice.json을 생성할 수 있다.
Typecast용 Voice Request 데이터를 준비할 수 있다.
Provider Engine을 통해 Voice Request를 만들 수 있다.
Voice Asset을 Asset Registry와 연결할 수 있다.
Voice 길이와 Timeline 길이를 비교할 수 있다.
Timeline의 voice_ref를 업데이트할 수 있다.
voice_review.json을 생성할 수 있다.
Subtitle Engine으로 Handoff를 만들 수 있다.
Editing Engine으로 Handoff를 만들 수 있다.
Voice Validation 실패 시 다음 Stage 진행을 막을 수 있다.
```

---

# 32. Non Goals

v1.0에서 Voice Engine이 하지 않는 것:

```text
음성 직접 생성
Typecast 직접 호출
Script 핵심 의미 변경
Timeline Scene ID 변경
Subtitle 최종 생성
Final Editing
Quality Score 최종 계산
Provider Secret 관리 직접 수행
```

v1.0에서는 언어별 Narration, Voice Config, Audio Asset 연결, Timeline Fit 구조를 안정적으로 만드는 것이 핵심이다.

---

# 33. Critical Voice Rules

반드시 지켜야 할 규칙:

```text
1. Voice Engine은 Timeline 없이 실행하지 않는다.

2. Voice Engine은 Story Script 없이 실행하지 않는다.

3. Voice Engine은 언어별 Script를 유지해야 한다.

4. Voice Engine은 Scene ID를 변경하지 않는다.

5. Voice는 Brand Tone과 맞아야 한다.

6. Voice는 너무 빠르거나 기계적이면 안 된다.

7. Speculative Claim의 조심스러운 표현을 바꾸면 안 된다.

8. Voice Engine은 Typecast를 직접 호출하지 않는다.

9. Provider Engine을 통해 Voice Request를 만든다.

10. Audio 결과물은 Asset Registry에 등록해야 한다.

11. Voice 길이는 Timeline과 비교해야 한다.

12. Subtitle Engine이 Sync할 수 있도록 Voice 정보를 넘겨야 한다.

13. Timeline Lock을 위반하지 않는다.

14. Voice Validation 실패 시 Subtitle / Editing Stage로 넘어가지 않는다.

15. 중요한 Voice 판단은 Self Review와 Handoff에 기록한다.
```

---

# 34. Final Principle

Voice Engine은 대본에 생명과 신뢰를 주는 엔진이다.

좋은 Voice는 정보를 읽는 것이 아니라, 이야기를 전달한다.

좋은 Voice는 Brand의 톤을 지키고,

시청자의 집중을 유지하고,

Timeline과 맞고,

Subtitle과 Editing이 안정적으로 이어지게 만든다.

Voice Engine의 목적은 단순히 음성 파일을 만드는 것이 아니라, 언어별로 자연스럽고 신뢰감 있는 시청 경험을 만드는 것이다.
