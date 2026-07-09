# 14_PROVIDER_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Provider Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Provider Engine을 정의한다.

Provider Engine은 Midjourney, Midjourney Video, Typecast 같은 외부 AI 도구와 ADOS 내부 Engine 사이를 연결하는 시스템이다.

ADOS의 Production Engine은 외부 Provider를 직접 호출하지 않는다.

반드시 다음 구조를 사용한다.

```text
Production Engine
↓
Provider Interface
↓
Provider Adapter
↓
External Provider
```

이 문서는 다음을 정의한다.

```text
Provider란 무엇인가
Provider Engine의 책임은 무엇인가
Interface와 Adapter를 왜 분리하는가
Midjourney / Midjourney Video / Typecast를 어떻게 연결하는가
Provider Request와 Response는 어떤 구조인가
Provider 결과물은 어디에 저장하는가
Provider 실패는 어떻게 기록하는가
Manual Provider Workflow는 어떻게 처리하는가
Claude Code가 어떤 구조로 구현해야 하는가
```

이 문서는 다음 문서들과 직접 연결된다.

```text
03_ARCHITECTURE.md
07_PROJECT_SPEC.md
08_TEMPLATE_SYSTEM.md
09_CHANNEL_ENGINE.md
12_PROJECT_ENGINE.md
13_MEMORY_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
16_TIMELINE_ENGINE.md
21_VISUAL_ENGINE.md
22_MOTION_ENGINE.md
23_VOICE_ENGINE.md
24_SUBTITLE_ENGINE.md
25_EDITING_ENGINE.md
26_QUALITY_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Provider는 ADOS 외부에서 특정 제작 기능을 제공하는 도구이다.

예시:

```text
Midjourney
→ 이미지 생성

Midjourney Video
→ 5초 Motion 영상 생성

Typecast
→ 음성 생성

Internal Subtitle
→ 자막 생성

Internal Editing
→ 편집 계획 또는 렌더링 준비
```

Provider Engine은 ADOS 내부 Engine과 외부 Provider 사이의 표준 연결 계층이다.

---

# 3. Provider Philosophy

## 3.1 Provider Independent

ADOS는 특정 Provider에 종속되면 안 된다.

오늘은 Midjourney를 쓰더라도 나중에 다른 이미지 Provider로 교체할 수 있어야 한다.

```text
Visual Engine
→ VisualProviderInterface
→ MidjourneyAdapter
```

나중에 변경 가능:

```text
Visual Engine
→ VisualProviderInterface
→ OtherImageAdapter
```

## 3.2 Engines Must Not Call Providers Directly

금지:

```text
Visual Engine이 Midjourney 직접 호출
Motion Engine이 Midjourney Video 직접 호출
Voice Engine이 Typecast 직접 호출
```

허용:

```text
Visual Engine → VisualProviderInterface → MidjourneyAdapter
Motion Engine → MotionProviderInterface → MidjourneyVideoAdapter
Voice Engine → VoiceProviderInterface → TypecastAdapter
```

## 3.3 Manual and Automated Modes Must Both Work

일부 Provider는 완전 자동 API가 아닐 수 있다.

따라서 v1.0에서는 다음 두 모드를 모두 지원해야 한다.

```text
manual
semi_automated
automated
```

예시:

```text
Midjourney Prompt를 생성하고
사용자가 Midjourney에 붙여넣고
결과 이미지를 assets/images/에 저장하면
Provider Engine이 결과 파일을 등록한다.
```

## 3.4 Provider Results Must Be Traceable

모든 Provider 결과물은 다음과 연결되어야 한다.

```text
project_id
channel_id
stage
scene_id
language
provider_name
request_id
input_prompt
output_file
status
created_at
```

---

# 4. Provider Engine Responsibilities

Provider Engine의 책임은 다음과 같다.

```text
Provider 설정 로드
Provider Interface 제공
Provider Adapter 선택
Provider Request 생성
Provider Request 검증
Provider 실행 모드 관리
Provider Response 저장
Provider 결과물 등록
Provider 실패 기록
Provider Retry 정보 관리
Provider Cost / Usage 기록
Provider Memory Update Candidate 생성
Provider Secret 직접 노출 방지
Engine이 Provider를 직접 호출하지 못하게 구조 분리
```

Provider Engine이 하지 않는 것:

```text
Story를 작성하지 않는다.
Visual Prompt를 직접 설계하지 않는다.
Voice Script를 직접 작성하지 않는다.
Quality Score를 직접 계산하지 않는다.
Template을 직접 변경하지 않는다.
Provider 결과 품질을 최종 승인하지 않는다.
```

Provider 결과 품질 판단은 해당 Production Engine과 Quality Engine이 수행한다.

---

# 5. Supported Providers in v1.0

v1.0 기본 Provider:

```text
visual:
  Midjourney

motion:
  Midjourney Video

voice:
  Typecast

subtitle:
  Internal Subtitle

editing:
  Internal Editing
```

Provider별 역할:

```text
Midjourney
→ Scene별 이미지 생성

Midjourney Video
→ 선택된 Scene의 5초 Motion 생성

Typecast
→ 언어별 Voice 생성

Internal Subtitle
→ SRT 자막 생성 또는 검증

Internal Editing
→ Edit Plan, Render Plan, Final Timeline 생성
```

---

# 6. Provider Configuration

Provider 설정은 다음 파일에서 온다.

```text
channels/{channel_id}/provider.yaml
templates/{template_id}/provider.yaml
config/providers.yaml
```

우선순위:

```text
Global Provider Config
↓
Template Provider Config
↓
Channel Provider Config
↓
Project Runtime Option
```

단, Provider Interface 구조는 임의로 깨면 안 된다.

---

# 7. provider.yaml Schema

```yaml
providers:
  visual:
    interface: VisualProviderInterface
    default_adapter: MidjourneyAdapter
    provider_name: midjourney
    mode: manual
    enabled: true

  motion:
    interface: MotionProviderInterface
    default_adapter: MidjourneyVideoAdapter
    provider_name: midjourney_video
    mode: manual
    enabled: true

  voice:
    interface: VoiceProviderInterface
    default_adapter: TypecastAdapter
    provider_name: typecast
    mode: semi_automated
    enabled: true

  subtitle:
    interface: SubtitleProviderInterface
    default_adapter: InternalSubtitleAdapter
    provider_name: internal_subtitle
    mode: automated
    enabled: true

  editing:
    interface: EditingProviderInterface
    default_adapter: InternalEditingAdapter
    provider_name: internal_editing
    mode: automated
    enabled: true

rules:
  engine_must_not_call_provider_directly: true
  require_adapter: true
  require_request_log: true
  require_response_log: true
  require_asset_registration: true
  log_provider_failures: true

retry:
  max_retry_per_request: 3
  retry_requires_reason: true
  prefer_prompt_revision_before_retry: true

secrets:
  use_env: true
  never_commit_keys: true
```

---

# 8. Provider Modes

Provider Mode는 다음을 사용한다.

```text
manual
semi_automated
automated
disabled
```

## 8.1 manual

시스템이 Prompt 또는 Request를 생성하고, 사용자가 외부 Provider에 직접 입력한다.

예시:

```text
Midjourney Prompt 생성
↓
사용자가 Midjourney에 붙여넣기
↓
이미지 다운로드
↓
assets/images/에 저장
↓
Provider Result 등록
```

## 8.2 semi_automated

일부 과정은 자동화하고 일부 과정은 사용자가 확인한다.

예시:

```text
Typecast용 narration.txt 생성
↓
사용자가 Typecast에서 Voice 생성
↓
결과 파일 저장
↓
Provider Result 등록
```

## 8.3 automated

시스템이 내부 로직 또는 API로 자동 처리한다.

예시:

```text
Subtitle SRT 생성
Edit Plan 생성
```

## 8.4 disabled

Provider 사용 안 함.

---

# 9. Provider Interface Types

v1.0에서 필요한 Interface:

```text
VisualProviderInterface
MotionProviderInterface
VoiceProviderInterface
SubtitleProviderInterface
EditingProviderInterface
```

각 Interface는 공통적으로 다음 기능을 가져야 한다.

```text
validate_request
create_request
submit_request
register_result
validate_result
build_response
log_request
log_response
```

---

# 10. Provider Request Schema

모든 Provider Request는 공통 구조를 가진다.

```json
{
  "request_id": "PROV-REQ-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "VISUAL",

  "provider": {
    "type": "visual",
    "name": "midjourney",
    "adapter": "MidjourneyAdapter",
    "mode": "manual"
  },

  "target": {
    "scene_id": "SC001",
    "language": null,
    "asset_type": "image",
    "output_expected": "assets/images/SC001_image_v001.png"
  },

  "input": {
    "prompt": "cinematic realistic future city, deep blue lighting...",
    "source_file": "prompts/midjourney_image_prompts.json"
  },

  "constraints": {
    "aspect_ratio": "16:9",
    "style": "cinematic realistic",
    "avoid": [
      "text",
      "watermark",
      "logo",
      "distorted anatomy"
    ]
  },

  "status": "CREATED",
  "created_at": "2026-07-10T10:00:00",
  "updated_at": "2026-07-10T10:00:00"
}
```

---

# 11. Provider Response Schema

Provider Response는 다음 구조를 따른다.

```json
{
  "response_id": "PROV-RES-000001",
  "request_id": "PROV-REQ-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "provider": {
    "type": "visual",
    "name": "midjourney",
    "adapter": "MidjourneyAdapter",
    "mode": "manual"
  },

  "target": {
    "scene_id": "SC001",
    "language": null,
    "asset_type": "image"
  },

  "result": {
    "status": "SUCCESS",
    "output_files": [
      "assets/images/SC001_image_v001.png"
    ],
    "metadata": {
      "width": null,
      "height": null,
      "duration_seconds": null
    }
  },

  "quality": {
    "requires_review": true,
    "initial_result_valid": true,
    "issues": []
  },

  "usage": {
    "cost_estimate": null,
    "credits_used": null,
    "retry_count": 0
  },

  "created_at": "2026-07-10T10:10:00"
}
```

---

# 12. Provider Request Status

Provider Request는 다음 상태를 가진다.

```text
CREATED
VALIDATED
WAITING_FOR_MANUAL_ACTION
SUBMITTED
IN_PROGRESS
RESULT_REGISTERED
SUCCESS
FAILED
RETRY_REQUIRED
CANCELLED
```

Manual Mode에서는 다음 흐름을 사용할 수 있다.

```text
CREATED
↓
VALIDATED
↓
WAITING_FOR_MANUAL_ACTION
↓
RESULT_REGISTERED
↓
SUCCESS
```

Automated Mode에서는 다음 흐름을 사용할 수 있다.

```text
CREATED
↓
VALIDATED
↓
SUBMITTED
↓
IN_PROGRESS
↓
SUCCESS
```

---

# 13. Visual Provider: Midjourney

Midjourney는 이미지 생성 Provider이다.

## 13.1 Responsibilities

```text
Scene별 이미지 Prompt를 외부 생성 가능한 형식으로 준비
Aspect Ratio 적용
Brand Visual Rule 반영
Negative Prompt 또는 Avoid Rule 반영
Manual 실행용 Prompt Package 생성
결과 이미지 파일 등록
Scene ID와 Asset 연결
```

## 13.2 Input

```text
timeline/timeline.json
direction/scene_plan.json
prompts/midjourney_image_prompts.json
brand.yaml
visual.yaml
provider.yaml
```

## 13.3 Output

```text
provider_requests/visual_requests.jsonl
assets/images/SC001_image_v001.png
provider_responses/visual_responses.jsonl
```

## 13.4 Request Example

```json
{
  "provider": "midjourney",
  "scene_id": "SC001",
  "prompt": "cinematic realistic future human city, deep blue lighting, dramatic scale, high detail --ar 16:9 --style raw",
  "output_expected": "assets/images/SC001_image_v001.png"
}
```

## 13.5 Rules

```text
Prompt에는 Scene 목적이 반영되어야 한다.
Brand 색감과 분위기가 반영되어야 한다.
이미지에 텍스트, 로고, 워터마크를 넣지 않는다.
Scene ID와 파일명이 일치해야 한다.
이미지 결과는 Visual Review 대상이다.
```

---

# 14. Motion Provider: Midjourney Video

Midjourney Video는 선택된 Scene의 Motion Clip을 만드는 Provider이다.

## 14.1 Responsibilities

```text
Motion이 필요한 Scene만 선택
Source Image 연결
5초 Motion 한계 반영
Motion Prompt 생성
Manual 실행용 Prompt Package 생성
결과 Motion 파일 등록
Timeline Scene과 Motion Asset 연결
```

## 14.2 Input

```text
timeline/timeline.json
assets/images/
prompts/midjourney_video_prompts.json
motion.yaml
provider.yaml
```

## 14.3 Output

```text
provider_requests/motion_requests.jsonl
assets/motion/SC001_motion_v001.mp4
provider_responses/motion_responses.jsonl
```

## 14.4 Rules

```text
모든 Scene을 Motion화하지 않는다.
Hook, Climax, Emotional Turn, World Reveal Scene을 우선한다.
Source Image가 없으면 Motion Request를 만들지 않는다.
5초 Motion 기준을 지킨다.
Motion 결과는 Timeline과 연결되어야 한다.
```

---

# 15. Voice Provider: Typecast

Typecast는 언어별 Voice 생성 Provider이다.

## 15.1 Responsibilities

```text
언어별 narration.txt 준비
Voice 설정 적용
Typecast 실행용 Request 생성
결과 Audio 파일 등록
언어별 Voice Metadata 저장
Timeline 길이 검증 지원
```

## 15.2 Input

```text
languages/{lang}/narration.txt
languages/{lang}/script.json
voice.yaml
timeline/timeline.json
provider.yaml
```

## 15.3 Output

```text
provider_requests/voice_requests.jsonl
assets/audio/SC001_voice_ko_v001.wav
assets/audio/SC001_voice_en_v001.wav
languages/{lang}/voice.json
provider_responses/voice_responses.jsonl
```

## 15.4 Rules

```text
Voice는 언어별로 분리한다.
Voice Tone은 Brand와 맞아야 한다.
속도가 너무 빠르면 안 된다.
Audio 파일은 language code를 포함해야 한다.
Voice 결과는 Timeline Fit Check 대상이다.
```

---

# 16. Subtitle Provider: Internal Subtitle

Internal Subtitle Provider는 자막 파일을 생성하거나 검증한다.

## 16.1 Responsibilities

```text
언어별 narration 또는 script 기반 SRT 생성
자막 길이 규칙 적용
Line Break 규칙 적용
Voice Timing과 연결
Subtitle 파일 등록
```

## 16.2 Input

```text
languages/{lang}/narration.txt
languages/{lang}/voice.json
timeline/timeline.json
subtitle.yaml
provider.yaml
```

## 16.3 Output

```text
languages/{lang}/subtitle.srt
assets/subtitles/subtitle_{lang}_v001.srt
provider_responses/subtitle_responses.jsonl
```

## 16.4 Rules

```text
자막은 의미 단위로 줄바꿈한다.
너무 긴 줄을 만들지 않는다.
언어별 자연스러운 표현을 유지한다.
Voice와 Sync를 맞춘다.
```

---

# 17. Editing Provider: Internal Editing

Internal Editing Provider는 편집 계획과 렌더링 준비를 담당한다.

v1.0에서 실제 고급 렌더링 자동화는 필수 아니다.

## 17.1 Responsibilities

```text
Timeline 기반 Edit Plan 생성
Asset Mapping 확인
Render Plan 생성
Final Timeline 생성
Package에 필요한 파일 목록 정리
```

## 17.2 Input

```text
timeline/timeline.json
assets/images/
assets/motion/
assets/audio/
assets/subtitles/
edit rules
provider.yaml
```

## 17.3 Output

```text
edit/edit_plan.json
edit/render_plan.json
edit/final_timeline.json
provider_responses/editing_responses.jsonl
```

## 17.4 Rules

```text
Timeline을 기준으로 Asset을 연결한다.
언어별 Voice와 Subtitle을 분리한다.
Missing Asset이 있으면 렌더링 준비 완료로 표시하지 않는다.
```

---

# 18. Provider Directory Structure in Project

Project 안에서 Provider 관련 파일은 다음 위치에 저장한다.

```text
projects/{channel_id}/{year}/{month}/{project_id}/
├── provider_requests/
│   ├── visual_requests.jsonl
│   ├── motion_requests.jsonl
│   ├── voice_requests.jsonl
│   ├── subtitle_requests.jsonl
│   └── editing_requests.jsonl
│
├── provider_responses/
│   ├── visual_responses.jsonl
│   ├── motion_responses.jsonl
│   ├── voice_responses.jsonl
│   ├── subtitle_responses.jsonl
│   └── editing_responses.jsonl
│
└── assets/
    ├── images/
    ├── motion/
    ├── audio/
    ├── subtitles/
    └── thumbnails/
```

v1.0에서는 `provider_requests/`와 `provider_responses/` 폴더를 Project 생성 시 만들어도 된다.

---

# 19. Asset Registration

Provider 결과물은 반드시 Asset Registry에 등록되어야 한다.

v1.0에서는 다음 파일을 사용할 수 있다.

```text
assets/asset_registry.json
```

Asset Registry 예시:

```json
{
  "assets": [
    {
      "asset_id": "ASSET-000001",
      "project_id": "20260710-093500-future-million-year-human",
      "scene_id": "SC001",
      "language": null,
      "asset_type": "image",
      "provider": "midjourney",
      "file": "assets/images/SC001_image_v001.png",
      "request_id": "PROV-REQ-000001",
      "response_id": "PROV-RES-000001",
      "status": "REGISTERED",
      "created_at": "2026-07-10T10:10:00"
    }
  ]
}
```

규칙:

```text
Provider 결과 파일만 있다고 완료가 아니다.
Asset Registry에 등록되어야 Timeline과 Quality에서 추적 가능하다.
Scene ID와 파일명이 일치해야 한다.
언어별 Asset은 language code를 포함해야 한다.
```

---

# 20. Manual Provider Workflow

Manual Provider는 ADOS가 외부 작업을 직접 실행하지 않고, 사용자가 외부 도구에서 결과를 만든 뒤 등록하는 방식이다.

흐름:

```text
Provider Request 생성
↓
Manual Action Guide 생성
↓
사용자가 외부 Provider에서 작업
↓
결과 파일을 지정 폴더에 저장
↓
Provider Engine이 결과 등록
↓
Asset Registry 업데이트
↓
Response Log 저장
```

Manual Action Guide 예시:

```json
{
  "request_id": "PROV-REQ-000001",
  "provider": "midjourney",
  "action": "Copy the prompt into Midjourney and save the selected result to assets/images/SC001_image_v001.png.",
  "prompt": "cinematic realistic future city...",
  "expected_output": "assets/images/SC001_image_v001.png"
}
```

---

# 21. Provider Retry Rules

Provider 실패 시 Retry는 제한적으로 수행한다.

규칙:

```text
같은 Request는 최대 3회 Retry
Retry 전 실패 원인 기록
Prompt 문제면 Prompt 수정 후 Retry
Provider 장애면 시간 후 Retry 또는 Manual 처리
같은 Scene에서 3회 실패 시 Escalation
Full Regeneration 금지
부분 재생성 우선
```

Retry 기록:

```json
{
  "request_id": "PROV-REQ-000001",
  "retry_count": 1,
  "reason": "Generated image did not match brand style.",
  "action": "Revise prompt with stronger brand color and lighting direction.",
  "created_at": "2026-07-10T10:20:00"
}
```

---

# 22. Provider Failure Types

Provider 실패 유형:

```text
PROMPT_VALIDATION_FAILED
PROVIDER_DISABLED
MANUAL_RESULT_MISSING
OUTPUT_FILE_MISSING
OUTPUT_FILE_INVALID
SCENE_ID_MISMATCH
LANGUAGE_MISMATCH
BRAND_MISMATCH
TIMELINE_MISMATCH
QUALITY_REVIEW_FAILED
PROVIDER_RATE_LIMIT
PROVIDER_AUTH_FAILED
PROVIDER_UNKNOWN_ERROR
```

---

# 23. Provider Logs

Provider Engine은 다음 로그를 남긴다.

```text
provider_requests/*.jsonl
provider_responses/*.jsonl
logs/provider.log
logs/error_log.jsonl
```

로그 대상:

```text
Provider Request 생성
Provider Request 검증
Manual Action Guide 생성
Provider Result 등록
Asset Registry 업데이트
Provider Retry
Provider Failure
Provider Response 저장
Provider Cost / Usage 기록
```

Event 예시:

```json
{
  "event_type": "PROVIDER_RESULT_REGISTERED",
  "project_id": "20260710-093500-future-million-year-human",
  "provider": "midjourney",
  "scene_id": "SC001",
  "asset_type": "image",
  "file": "assets/images/SC001_image_v001.png",
  "created_at": "2026-07-10T10:10:00"
}
```

---

# 24. Provider Secrets

Provider Key나 로그인 정보는 코드와 문서에 직접 저장하지 않는다.

금지:

```text
API Key를 Python 파일에 직접 작성
API Key를 Markdown 문서에 작성
API Key를 Git에 커밋
로그에 Secret 출력
Provider Response에 Secret 저장
```

허용 방향:

```text
.env
environment variables
local config
secret manager
```

v1.0에서는 최소한 `.env` 기반 구조를 사용한다.

예시:

```text
TYPECAST_API_KEY=
MIDJOURNEY_MODE=manual
```

Midjourney가 manual mode인 경우 API Key가 필요하지 않을 수 있다.

---

# 25. Provider Cost and Usage Tracking

Provider 사용량은 기록할 수 있어야 한다.

v1.0에서는 추정값 또는 수동 입력도 허용한다.

Usage Schema:

```json
{
  "provider": "typecast",
  "request_id": "PROV-REQ-000101",
  "project_id": "20260710-093500-future-million-year-human",
  "asset_type": "voice",
  "language": "ko",
  "credits_used": null,
  "cost_estimate": null,
  "manual_cost_input": false,
  "created_at": "2026-07-10T11:00:00"
}
```

사용 목적:

```text
제작 비용 추적
Provider 효율 비교
Channel별 제작 비용 추정
수익성 분석
Learning Engine에 비용 데이터 제공
```

---

# 26. Provider Memory

Provider 실패와 성공 패턴은 Memory에 저장될 수 있다.

저장 대상:

```text
Midjourney에서 잘 먹힌 Prompt 구조
Midjourney에서 실패한 스타일 표현
Midjourney Video에서 실패한 Motion Prompt
Typecast에서 좋은 Voice 설정
Typecast에서 실패한 속도나 감정 설정
Provider별 반복 오류
```

Memory Update Candidate 예시:

```json
{
  "target_memory": "provider_memory",
  "provider": "midjourney",
  "update_type": "failure_pattern",
  "summary": "Prompts containing too many abstract concepts produced weak images.",
  "evidence": [
    "provider_responses/visual_responses.jsonl",
    "reports/quality_report.json"
  ],
  "confidence": "MEDIUM"
}
```

Provider Engine은 Memory를 직접 확정하지 않는다.

Memory Engine에 Update Candidate를 전달한다.

---

# 27. Provider Validation Rules

Provider Request Validator는 다음을 확인해야 한다.

```text
request_id 존재
project_id 존재
channel_id 존재
provider.type 존재
provider.name 존재
adapter 존재
mode 유효
target.asset_type 존재
target.output_expected 존재
scene_id 필요 시 존재
language 필요 시 존재
input.prompt 또는 input.source_file 존재
output path가 허용된 assets/ 하위인지 확인
```

Provider Result Validator는 다음을 확인해야 한다.

```text
response_id 존재
request_id 존재
output_files 존재
output_files가 실제 존재하거나 manual pending 상태인지 확인
Scene ID와 파일명 일치
language와 파일명 일치
asset_type과 저장 위치 일치
```

---

# 28. Error Types

Provider Engine의 Error Type은 다음과 같다.

```text
ProviderConfigNotFoundError
InvalidProviderConfigError
ProviderInterfaceNotFoundError
ProviderAdapterNotFoundError
ProviderDisabledError
ProviderRequestValidationError
ProviderResponseValidationError
ProviderResultMissingError
ProviderOutputFileMissingError
ProviderOutputFileInvalidError
ProviderAssetRegistrationError
ProviderSecretError
ProviderRetryLimitError
ProviderManualActionRequiredError
ProviderUnknownError
```

Error 예시:

```json
{
  "error_type": "ProviderOutputFileMissingError",
  "message": "Expected Midjourney output file is missing.",
  "project_id": "20260710-093500-future-million-year-human",
  "request_id": "PROV-REQ-000001",
  "provider": "midjourney",
  "expected_file": "assets/images/SC001_image_v001.png",
  "severity": "MEDIUM",
  "suggested_fix": "Save the selected Midjourney image to the expected path and register result again.",
  "created_at": "2026-07-10T10:30:00"
}
```

---

# 29. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
ProviderEngine
ProviderConfigLoader
ProviderValidator
ProviderRequestBuilder
ProviderResponseBuilder
ProviderModeResolver
ProviderAdapterRegistry
ProviderRequestLogger
ProviderResponseLogger
ProviderAssetRegistrar
ProviderRetryManager
ProviderUsageTracker
ProviderMemoryReporter
ProviderErrorReporter
```

Interface Classes:

```text
VisualProviderInterface
MotionProviderInterface
VoiceProviderInterface
SubtitleProviderInterface
EditingProviderInterface
```

Adapter Classes:

```text
MidjourneyAdapter
MidjourneyVideoAdapter
TypecastAdapter
InternalSubtitleAdapter
InternalEditingAdapter
ManualProviderAdapter
```

---

# 30. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/14_PROVIDER_ENGINE.md
→ engines/provider/
→ providers/interfaces/
→ providers/adapters/
```

예시 구조:

```text
engines/
└── provider/
    ├── provider_engine.py
    ├── provider_config_loader.py
    ├── provider_validator.py
    ├── provider_request_builder.py
    ├── provider_response_builder.py
    ├── provider_mode_resolver.py
    ├── provider_adapter_registry.py
    ├── provider_asset_registrar.py
    ├── provider_retry_manager.py
    ├── provider_usage_tracker.py
    ├── provider_memory_reporter.py
    └── provider_error_reporter.py

providers/
├── interfaces/
│   ├── visual_provider_interface.py
│   ├── motion_provider_interface.py
│   ├── voice_provider_interface.py
│   ├── subtitle_provider_interface.py
│   └── editing_provider_interface.py
│
└── adapters/
    ├── midjourney_adapter.py
    ├── midjourney_video_adapter.py
    ├── typecast_adapter.py
    ├── internal_subtitle_adapter.py
    ├── internal_editing_adapter.py
    └── manual_provider_adapter.py
```

---

# 31. Main Public Operations

Provider Engine은 최소 다음 작업을 제공해야 한다.

```text
load_provider_config(channel_id)
resolve_provider(stage, provider_type)
build_provider_request(project_id, provider_type, target)
validate_provider_request(request)
submit_provider_request(request)
create_manual_action_guide(request)
register_provider_result(request_id, output_files)
validate_provider_result(response)
register_asset(response)
track_provider_usage(response)
create_provider_memory_candidate(response)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
Provider 설정 확인
Mode 확인
Adapter 확인
결과 파일 검증
Asset Registry 업데이트
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 32. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
provider.yaml 로드
Provider 설정 검증
Provider Interface 기본 클래스 정의
Provider Adapter 기본 클래스 정의
Manual Provider Request 생성
Manual Action Guide 생성
Provider Result 등록
Asset Registry 업데이트
Provider Request / Response 로그 저장
Provider Error 기록
Provider Retry Count 관리
```

v1.0에서 하지 않아도 되는 것:

```text
Midjourney 완전 자동 API 연동
Typecast 완전 자동 API 연동
복잡한 결제/비용 자동 추적
실시간 Provider Dashboard
고급 Provider 성능 비교
자동 Provider 교체
```

v1.0에서는 Manual / Semi-Automated Workflow를 안정적으로 지원하는 것이 우선이다.

---

# 33. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
provider.yaml을 로드할 수 있다.
Provider 설정을 검증할 수 있다.
Provider Interface와 Adapter를 분리할 수 있다.
Visual Engine이 Midjourney를 직접 호출하지 않게 할 수 있다.
Motion Engine이 Midjourney Video를 직접 호출하지 않게 할 수 있다.
Voice Engine이 Typecast를 직접 호출하지 않게 할 수 있다.
Manual Provider Request를 만들 수 있다.
Manual Action Guide를 만들 수 있다.
Provider Result를 등록할 수 있다.
Provider 결과물을 Asset Registry에 등록할 수 있다.
Provider Request와 Response를 로그로 남길 수 있다.
Provider 실패를 구조화해서 기록할 수 있다.
Retry Count를 관리할 수 있다.
Provider Memory Update Candidate를 만들 수 있다.
Secret을 코드나 문서에 저장하지 않게 할 수 있다.
```

---

# 34. Non Goals

v1.0에서 Provider Engine이 하지 않는 것:

```text
모든 외부 Provider 완전 자동화
비공식 Provider API에 강하게 의존
외부 계정 로그인 자동화
Secret을 코드에 저장
Provider 결과물 최종 품질 승인
Provider별 고급 비용 최적화
자동 Provider Marketplace 연동
```

v1.0에서는 Provider를 안전하게 분리하고, Manual / Semi-Automated 결과물을 추적 가능한 구조로 등록하는 것이 우선이다.

---

# 35. Critical Provider Rules

반드시 지켜야 할 규칙:

```text
1. Production Engine은 Provider를 직접 호출하지 않는다.

2. 모든 Provider 호출은 Interface와 Adapter를 거친다.

3. Provider 결과물은 Asset Registry에 등록해야 한다.

4. Provider Request와 Response는 로그로 남긴다.

5. Manual Provider Workflow를 지원해야 한다.

6. Midjourney는 기본적으로 Manual Mode로 시작한다.

7. Midjourney Video는 기본적으로 Manual Mode로 시작한다.

8. Typecast는 Manual 또는 Semi-Automated Mode로 시작한다.

9. Provider Secret은 코드나 문서에 저장하지 않는다.

10. 같은 Request Retry는 최대 3회로 제한한다.

11. Provider 실패는 구조화해서 기록한다.

12. Provider 결과 품질은 Quality Engine에서 검토한다.

13. Provider 실패 패턴은 Memory Candidate가 될 수 있다.

14. Provider Engine은 Template을 직접 수정하지 않는다.

15. Provider Engine은 Final Publish를 수행하지 않는다.
```

---

# 36. Final Principle

Provider Engine은 ADOS와 외부 AI 도구 사이의 안전한 연결 계층이다.

좋은 Provider Engine은 특정 도구에 종속되지 않는다.

좋은 Provider Engine은 Request와 Result를 추적할 수 있게 만든다.

좋은 Provider Engine은 실패를 기록하고, Retry를 제한하고, Asset을 정확히 등록한다.

Midjourney, Midjourney Video, Typecast는 중요한 도구이다.

하지만 ADOS의 핵심은 특정 Provider가 아니다.

ADOS의 핵심은 어떤 Provider를 쓰더라도 Template, Channel, Project, Timeline, Quality, Learning 구조가 유지되는 것이다.
