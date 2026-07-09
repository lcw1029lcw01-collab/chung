# 08_TEMPLATE_SYSTEM.md

Version: 1.2.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Template System Specification  

---

# 1. Purpose

이 문서는 CHUNG COMPANY / ADOS의 Template System을 정의한다.

Template System은 새로운 Channel을 생성하고, Channel의 정체성, 제작 방식, 품질 기준, 성장 전략, AI Employee 구성, Provider 설정, Memory 구조를 결정하는 핵심 시스템이다.

Template은 단순 설정 파일이 아니다.

Template은 Channel을 만드는 DNA이다.

CHUNG COMPANY의 핵심 자산은 영상 하나가 아니라 Template이다.

이 문서는 다음을 정의한다.

```text
Template이 무엇인가
Template이 왜 핵심 자산인가
Template 계층 구조는 어떻게 되는가
Template 폴더 구조는 어떻게 되는가
Template 파일은 무엇을 포함하는가
Template Override와 Lock Rule은 어떻게 작동하는가
Template 검증은 어떻게 하는가
Template으로 Channel을 어떻게 생성하는가
Template은 어떻게 학습되고 진화하는가
Claude Code가 어떤 구조로 구현해야 하는가
```

이 문서는 다음 문서들과 직접 연결된다.

```text
03_ARCHITECTURE.md
04_AI_ORGANIZATION.md
05_INTER_AI_COMMUNICATION.md
06_AI_THINKING_FRAMEWORK.md
07_PROJECT_SPEC.md
09_CHANNEL_ENGINE.md
10_BRAND_SYSTEM.md
11_PORTFOLIO_ENGINE.md
13_MEMORY_ENGINE.md
26_QUALITY_ENGINE.md
27_GROWTH_ENGINE.md
30_LEARNING_ENGINE.md
31_AI_EVOLUTION_ENGINE.md
```

---

# 2. Core Definition

Template은 Channel을 생성하기 위한 DNA이다.

Template은 다음을 정의한다.

```text
Channel Identity
Brand
Audience
Story Rules
Visual Rules
Motion Rules
Voice Rules
Subtitle Rules
Quality Rules
Growth Rules
Provider Rules
AI Employee Rules
Communication Rules
Thinking Rules
Memory Rules
Publishing Rules
Learning Rules
```

Template은 Channel보다 먼저 존재한다.

```text
Template
↓
Channel
↓
Project
↓
Video
↓
Analytics
↓
Learning
↓
Template Evolution
```

---

# 3. Template Philosophy

## 3.1 Template First

Channel은 Template에서 생성된다.

Template 없이 Channel을 만들지 않는다.

나쁜 구조:

```text
Channel을 직접 만들고 나중에 설정을 붙인다.
```

좋은 구조:

```text
Template을 검증하고,
Template에서 Channel을 생성하고,
Channel이 Project를 만든다.
```

## 3.2 Template Is Reusable IP

좋은 Template 하나는 여러 Channel과 여러 Project로 확장될 수 있다.

```text
좋은 Template
↓
좋은 Channel
↓
좋은 Project 반복
↓
성과 데이터 축적
↓
Template 개선
↓
더 좋은 Channel 생성 가능
```

## 3.3 Template Is Not Static

Template은 고정된 파일이 아니다.

Project 성과, Quality Report, Learning Report를 통해 개선된다.

단, Template은 무분별하게 바꾸지 않는다.

Template 변경은 버전 관리되어야 한다.

## 3.4 Template Protects Consistency

Template은 Channel의 일관성을 보호한다.

Template이 없으면 매 영상마다 톤, 스타일, 품질 기준이 흔들린다.

---

# 4. Template Hierarchy

Template은 계층 구조를 가진다.

```text
Base Template
↓
Category Template
↓
Channel Template
↓
Project Override
```

## 4.1 Base Template

모든 Channel이 공통으로 따르는 기본 규칙이다.

예시:

```text
품질 기준
공통 파일 구조
기본 AI Employee 구조
공통 Communication 규칙
공통 Thinking 규칙
Provider Interface 규칙
```

## 4.2 Category Template

큰 콘텐츠 카테고리별 규칙이다.

예시:

```text
documentary
education
history
science
finance
fitness
entertainment
```

## 4.3 Channel Template

실제 Channel의 정체성을 정의하는 Template이다.

예시:

```text
future
psychology
civilization
history_reimagined
fitness_body
ai_business
```

## 4.4 Project Override

특정 Project에서만 임시로 적용하는 설정이다.

Project Override는 제한적으로만 허용된다.

Locked Field는 Override할 수 없다.

---

# 5. Template Resolution Order

Template 값은 아래 순서로 합쳐진다.

```text
Global Default
↓
Base Template
↓
Category Template
↓
Channel Template
↓
Project Override
↓
Runtime Option
```

더 아래 단계가 더 높은 우선권을 가진다.

단, Locked Field는 하위 단계에서 변경할 수 없다.

예시:

```text
Base Template에서 quality.pass_score = 95
Channel Template에서 quality.pass_score = 90으로 바꾸려 함
하지만 quality.pass_score가 locked이면 변경 불가
```

---

# 6. Template Directory Structure

Template 기본 구조:

```text
templates/
│
├── base/
│   ├── template.yaml
│   ├── brand.yaml
│   ├── story.yaml
│   ├── visual.yaml
│   ├── motion.yaml
│   ├── voice.yaml
│   ├── subtitle.yaml
│   ├── quality.yaml
│   ├── growth.yaml
│   ├── employees.yaml
│   ├── provider.yaml
│   ├── memory.yaml
│   ├── communication.yaml
│   ├── thinking.yaml
│   ├── publishing.yaml
│   └── learning.yaml
│
├── categories/
│   ├── documentary/
│   │   ├── template.yaml
│   │   ├── story.yaml
│   │   ├── visual.yaml
│   │   └── growth.yaml
│   │
│   ├── education/
│   ├── history/
│   ├── science/
│   ├── finance/
│   └── fitness/
│
└── channels/
    ├── future/
    │   ├── template.yaml
    │   ├── brand.yaml
    │   ├── story.yaml
    │   ├── visual.yaml
    │   ├── motion.yaml
    │   ├── voice.yaml
    │   ├── subtitle.yaml
    │   ├── quality.yaml
    │   ├── growth.yaml
    │   ├── employees.yaml
    │   ├── provider.yaml
    │   ├── memory.yaml
    │   ├── communication.yaml
    │   ├── thinking.yaml
    │   ├── publishing.yaml
    │   └── learning.yaml
    │
    ├── psychology/
    ├── civilization/
    └── history_reimagined/
```

---

# 7. Required Template Files

Channel Template은 다음 파일을 가져야 한다.

```text
template.yaml
brand.yaml
story.yaml
visual.yaml
motion.yaml
voice.yaml
subtitle.yaml
quality.yaml
growth.yaml
employees.yaml
provider.yaml
memory.yaml
communication.yaml
thinking.yaml
publishing.yaml
learning.yaml
```

v1.0에서 최소 필수 파일:

```text
template.yaml
brand.yaml
story.yaml
visual.yaml
voice.yaml
quality.yaml
growth.yaml
employees.yaml
provider.yaml
memory.yaml
communication.yaml
thinking.yaml
```

`motion.yaml`, `subtitle.yaml`, `publishing.yaml`, `learning.yaml`은 v1.0에서도 권장한다.

---

# 8. File Responsibilities

## 8.1 template.yaml

Template의 기본 정보, 상속 구조, 버전, 사용 가능 여부를 정의한다.

## 8.2 brand.yaml

Channel의 이름, 슬로건, 정체성, 톤, 색감, 금지 스타일을 정의한다.

## 8.3 story.yaml

Story 구조, Hook 규칙, Act 구조, 대본 톤, 금지 표현을 정의한다.

## 8.4 visual.yaml

이미지 스타일, Midjourney Prompt 규칙, 색감, 카메라 스타일, 금지 Visual을 정의한다.

## 8.5 motion.yaml

Midjourney Video 사용 기준, Motion 적용 Scene 기준, Motion 비율을 정의한다.

## 8.6 voice.yaml

Typecast 설정, 언어별 나레이션 톤, 속도, 감정, 발화 스타일을 정의한다.

## 8.7 subtitle.yaml

자막 스타일, 줄 길이, 줄바꿈, 언어별 자막 규칙을 정의한다.

## 8.8 quality.yaml

품질 점수 기준, Hard Fail, Auto Fix 기준, 평가 가중치를 정의한다.

## 8.9 growth.yaml

CTR, Retention, Watch Time, Revenue Potential, Topic Selection 기준을 정의한다.

## 8.10 employees.yaml

Channel에 배정될 AI Employee와 Department 구성을 정의한다.

## 8.11 provider.yaml

Midjourney, Midjourney Video, Typecast 등 Provider 설정을 정의한다.

## 8.12 memory.yaml

Channel Memory 초기 구조와 저장/불러오기 규칙을 정의한다.

## 8.13 communication.yaml

AI Employee 간 Message, Review, Handoff, Escalation 규칙을 정의한다.

## 8.14 thinking.yaml

AI Employee의 판단 우선순위, 부서별 사고 기준, Risk 판단 기준을 정의한다.

## 8.15 publishing.yaml

Upload Package, Metadata, Thumbnail, Subtitle, Publish Mode 규칙을 정의한다.

## 8.16 learning.yaml

성과 학습, Memory Update, Template Improvement Proposal 기준을 정의한다.

---

# 9. template.yaml Schema

```yaml
template:
  id: future
  name: Future Channel Template
  version: 1.0.0
  status: active
  type: channel
  owner: CHUNG COMPANY

  inherits:
    - base
    - documentary

  created_at: 2026-01-01
  updated_at: 2026-01-01

compatibility:
  min_ados_version: 1.0.0
  supported_languages:
    - ko
    - en

usage:
  enabled: true
  allow_channel_creation: true
  allow_project_override: true
  allow_template_evolution: true

locks:
  enabled: true
  locked_fields:
    - brand.identity.core
    - quality.pass_score
    - provider.interfaces

metadata:
  description: "A cinematic future documentary channel template."
  tags:
    - future
    - documentary
    - science
    - civilization
```

---

# 10. brand.yaml Schema

```yaml
brand:
  id: future_brand
  name: Beyond Humanity
  korean_name: 비욘드 휴머니티
  slogan: "인간 이후의 미래를 탐험하다"
  english_slogan: "Exploring life beyond humanity"
  version: 1.0.0

identity:
  core:
    - cinematic
    - intelligent
    - mysterious
    - philosophical
    - scientific

audience:
  primary:
    - future technology audience
    - science curious audience
    - AI and civilization audience
  age_range: "18-44"
  interests:
    - AI
    - future
    - science
    - space
    - civilization
    - technology

tone:
  primary: mysterious
  secondary: philosophical
  energy: calm
  pace: slow_to_medium
  emotional_direction:
    - curiosity
    - awe
    - reflection

visual_identity:
  primary_colors:
    - deep_blue
    - black
    - cyan
  secondary_colors:
    - silver
    - orange
  lighting:
    - cinematic
    - dramatic
    - high_contrast
  forbidden_colors:
    - childish_pastel
    - random_rainbow

must_feel_like:
  - premium documentary
  - cinematic future film
  - intelligent science story

must_not_feel_like:
  - cheap slideshow
  - random stock footage
  - childish cartoon
  - loud advertisement
```

---

# 11. story.yaml Schema

```yaml
story:
  structure: cinematic_documentary
  hook_duration_seconds: 30
  target_emotion:
    - curiosity
    - awe
    - reflection

act_structure:
  - hook
  - question
  - current_reality
  - scientific_context
  - future_simulation
  - consequence
  - philosophical_ending

hook_rules:
  must_start_with:
    - strong_question
    - shocking_future_scenario
    - emotional_scene
  must_not_start_with:
    - generic_introduction
    - "오늘은 ~에 대해 알아보겠습니다"

retention_rules:
  first_10_seconds:
    must_create:
      - curiosity
      - visual_interest
      - unanswered_question
  first_30_seconds:
    must_include:
      - main_question
      - emotional_or_visual_hook
      - reason_to_continue

language_rules:
  avoid:
    - cheap_clickbait
    - unsupported_claims
    - childish_tone
    - overly_casual_slang
```

---

# 12. visual.yaml Schema

```yaml
visual:
  provider: midjourney
  style: cinematic_realistic
  aspect_ratio: "16:9"
  default_quality: high

composition:
  preferred:
    - wide cinematic shots
    - dramatic scale
    - clear subject
    - strong depth
    - realistic lighting

color_rules:
  preferred:
    - deep_blue
    - black
    - cyan
    - silver
  avoid:
    - childish_pastel
    - oversaturated_random_colors
    - flat_lighting

prompt_rules:
  must_include:
    - cinematic
    - realistic
    - high detail
    - dramatic lighting
  must_avoid:
    - text in image
    - logo
    - watermark
    - distorted human anatomy
    - generic AI art

thumbnail_rules:
  must_be:
    - clear
    - high contrast
    - emotionally strong
    - readable at small size
```

---

# 13. motion.yaml Schema

```yaml
motion:
  provider: midjourney_video
  default_duration_seconds: 5
  motion_percentage_target: 20

use_motion_when:
  - scene_is_hook
  - scene_is_climax
  - scene_has_emotional_turn
  - scene_has_world_reveal
  - scene_has_character_motion

avoid_motion_when:
  - scene_is_static_explanation
  - scene_has_low_importance
  - motion_does_not_improve_retention

motion_rules:
  source_image_required: true
  max_duration_seconds: 5
  prefer_subtle_cinematic_motion: true
  avoid_fast_chaotic_motion: true
```

---

# 14. voice.yaml Schema

```yaml
voice:
  provider: typecast
  default_style: documentary_narrator

languages:
  ko:
    tone: calm
    emotion: mysterious
    speed: medium_slow
    style: documentary_narrator
    avoid:
      - advertisement_tone
      - exaggerated_emotion
      - robotic_reading

  en:
    tone: calm
    emotion: mysterious
    speed: medium
    style: cinematic_documentary
    avoid:
      - overly_fast_delivery
      - robotic_reading
      - casual_youtube_slang

timeline_rules:
  allow_language_duration_difference: true
  require_timeline_fit_check: true
```

---

# 15. subtitle.yaml Schema

```yaml
subtitle:
  enabled: true
  format: srt

style:
  max_chars_per_line: 26
  max_lines: 2
  reading_speed: comfortable
  tone: clean

rules:
  avoid:
    - too_long_lines
    - broken_meaning_units
    - excessive_emphasis
    - distracting_style

languages:
  ko:
    line_break: meaning_unit
  en:
    line_break: phrase_unit
```

---

# 16. quality.yaml Schema

```yaml
quality:
  pass_score: 95

  score_ranges:
    pass:
      min: 95
      max: 100
    human_review:
      min: 90
      max: 94
    auto_fix:
      min: 80
      max: 89
    partial_regeneration:
      min: 70
      max: 79
    fail:
      below: 70

weights:
  story: 25
  retention: 20
  visual: 15
  voice: 10
  subtitle: 5
  factuality: 10
  brand_consistency: 10
  timeline_integrity: 5

hard_fail:
  - no_clear_hook
  - factual_error
  - broken_timeline
  - missing_required_file
  - brand_mismatch
  - copyright_risk
  - voice_failure
  - subtitle_sync_failure
```

---

# 17. growth.yaml Schema

```yaml
growth:
  north_star_metric: monthly_net_revenue

supporting_metrics:
  - ctr
  - watch_time
  - retention_rate
  - subscriber_conversion
  - rpm
  - upload_consistency

topic_selection:
  allow_ai_recommendation: true
  minimum_topic_score: 85
  preferred_topic_score: 95

title_rules:
  must_be:
    - clear
    - curiosity_driven
    - brand_consistent
  must_not_be:
    - cheap_clickbait
    - misleading
    - too_generic

thumbnail_rules:
  optimize_for:
    - clarity
    - contrast
    - curiosity
    - emotional_strength
```

---

# 18. employees.yaml Schema

```yaml
employees:
  managers:
    - coo_employee
    - portfolio_manager
    - template_manager
    - channel_manager
    - project_manager

  departments:
    research:
      enabled: true
      lead: research_lead
      specialists:
        - trend_research_employee
        - fact_research_employee

    story:
      enabled: true
      lead: story_lead
      specialists:
        - hook_writer
        - script_writer
        - story_reviewer

    visual:
      enabled: true
      lead: visual_lead
      specialists:
        - midjourney_prompt_employee
        - image_reviewer

    quality:
      enabled: true
      lead: quality_lead
      specialists:
        - final_quality_employee
        - brand_consistency_employee
        - factuality_quality_employee
```

---

# 19. provider.yaml Schema

```yaml
providers:
  visual:
    interface: VisualProviderInterface
    default_adapter: MidjourneyAdapter
    provider_name: midjourney
    enabled: true

  motion:
    interface: MotionProviderInterface
    default_adapter: MidjourneyVideoAdapter
    provider_name: midjourney_video
    enabled: true

  voice:
    interface: VoiceProviderInterface
    default_adapter: TypecastAdapter
    provider_name: typecast
    enabled: true

  subtitle:
    interface: SubtitleProviderInterface
    default_adapter: InternalSubtitleAdapter
    provider_name: internal
    enabled: true

rules:
  engine_must_not_call_provider_directly: true
  require_adapter: true
  log_provider_failures: true
```

---

# 20. memory.yaml Schema

```yaml
memory:
  enabled: true

scopes:
  company_memory: true
  template_memory: true
  channel_memory: true
  project_memory: true
  provider_memory: true
  quality_memory: true
  growth_memory: true

initial_memory:
  successful_hooks: []
  failed_hooks: []
  successful_topics: []
  failed_topics: []
  visual_patterns: []
  voice_patterns: []
  quality_failures: []
  provider_failures: []

rules:
  load_before_work: true
  update_after_learning: true
  avoid_overgeneralization: true
```

---

# 21. communication.yaml Schema

```yaml
communication:
  enabled: true
  default_priority: MEDIUM

rules:
  require_task_request: true
  require_task_result: true
  require_handoff_package: true
  require_self_review: true
  require_peer_review_for_major_outputs: true
  require_quality_approval: true

retry_policy:
  max_retry_per_issue: 3
  max_total_retry_per_project: 10
  prefer_partial_regeneration: true
  full_regeneration_requires_coo_approval: true

meeting_rules:
  trigger_quality_below: 80
  trigger_same_issue_count: 3
  require_meeting_for_full_regeneration: true

escalation_rules:
  repeated_failure_count: 3
  critical_issue_to: Project Manager
  template_issue_to: Template Manager
  business_issue_to: COO
```

---

# 22. thinking.yaml Schema

```yaml
thinking:
  enabled: true

decision_priority:
  - factual_accuracy
  - safety_and_copyright_risk
  - template_lock_rules
  - brand_consistency
  - quality_score
  - timeline_integrity
  - retention_potential
  - ctr_potential
  - production_efficiency

records:
  require_decision_record_for_major_decisions: true
  require_self_review: true
  require_risk_register: true
  do_not_store_private_chain_of_thought: true

department_focus:
  story:
    - hook_strength
    - retention
    - emotional_arc
    - visual_potential
    - factual_safety

  visual:
    - scene_clarity
    - cinematic_quality
    - brand_consistency
    - motion_potential

  voice:
    - naturalness
    - emotional_match
    - timeline_fit

  quality:
    - hard_fail_detection
    - score_accuracy
    - brand_consistency
    - factuality

  growth:
    - ctr
    - retention
    - revenue_potential
    - channel_fit
```

---

# 23. publishing.yaml Schema

```yaml
publishing:
  publish_mode: human_review
  auto_publish_allowed: false

package_required_files:
  - upload_package.json
  - thumbnail.png
  - metadata_ko.json
  - metadata_en.json

metadata:
  languages:
    - ko
    - en

rules:
  require_quality_pass_before_package: true
  require_human_review_before_publish: true
  allow_manual_publish_record: true
```

---

# 24. learning.yaml Schema

```yaml
learning:
  enabled: true

inputs:
  - analytics_report
  - quality_report
  - growth_prediction
  - communication_logs
  - error_logs

outputs:
  - learning_report
  - memory_update
  - template_improvement_proposal

rules:
  avoid_overgeneralization: true
  require_evidence_for_template_change: true
  require_approval_for_template_version_change: true
```

---

# 25. Override Rules

Template Override는 제한적으로 허용된다.

허용되는 Override 예시:

```text
Project별 영상 길이 조정
Project별 Motion 비율 조정
Project별 언어 추가
Project별 특정 Scene 스타일 조정
Project별 SEO 방향 조정
```

금지되는 Override 예시:

```text
Locked Brand Identity 변경
Quality Pass Score 낮추기
Provider Interface 직접 변경
Template Version 무단 변경
Channel 핵심 톤 변경
```

---

# 26. Lock Rules

Locked Field는 하위 Template이나 Project Override에서 변경할 수 없다.

예시:

```yaml
locked_fields:
  - brand.identity.core
  - quality.pass_score
  - provider.interfaces
  - communication.retry_policy.full_regeneration_requires_coo_approval
```

Lock 위반 시 Template Validation은 실패해야 한다.

---

# 27. Template Validation Rules

Template Validator는 다음을 확인해야 한다.

```text
template.yaml 존재
template.id 존재
template.version 존재
template.status가 active 또는 draft인지 확인
inherits 구조 유효
필수 Template 파일 존재
supported_languages 존재
quality.pass_score 존재
brand.identity 존재
story.structure 존재
visual.provider 존재
voice.provider 존재
provider.interface 존재
employees 정의 존재
communication 규칙 존재
thinking 규칙 존재
memory 규칙 존재
locked_fields 위반 없음
```

검증 실패 시 Channel 생성 불가.

---

# 28. Template Score

Template Score는 Template 사용 가능성을 판단한다.

```yaml
template_score:
  completeness: 20
  brand_clarity: 20
  story_strength: 15
  visual_strength: 15
  growth_potential: 10
  automation_readiness: 10
  quality_safety: 10
```

점수 기준:

```text
95~100
우수, Channel 생성 가능

90~94
사용 가능, 개선 권장

80~89
검토 필요, Channel 생성 전 수정 권장

80 미만
사용 금지
```

---

# 29. Channel Creation Flow

Template에서 Channel을 생성하는 흐름:

```text
User selects Template
↓
Template Loader loads Base Template
↓
Template Loader loads Category Template
↓
Template Loader loads Channel Template
↓
Template Resolver merges settings
↓
Template Lock Manager checks locked fields
↓
Template Validator validates resolved Template
↓
Template Scorer calculates Template Score
↓
Channel Factory creates Channel Folder
↓
Resolved Template files are copied to Channel
↓
Channel Memory initialized
↓
Channel Reports initialized
↓
Channel Status becomes ACTIVE
```

---

# 30. Channel Output Structure

Template에서 Channel 생성 시 결과 구조:

```text
channels/
└── {channel_id}/
    ├── channel.yaml
    ├── template_snapshot.json
    ├── brand.yaml
    ├── story.yaml
    ├── visual.yaml
    ├── motion.yaml
    ├── voice.yaml
    ├── subtitle.yaml
    ├── quality.yaml
    ├── growth.yaml
    ├── employees.yaml
    ├── provider.yaml
    ├── memory.yaml
    ├── communication.yaml
    ├── thinking.yaml
    ├── publishing.yaml
    ├── learning.yaml
    ├── projects/
    ├── reports/
    └── logs/
```

---

# 31. Template Snapshot

Channel 생성 시 반드시 Template Snapshot을 저장한다.

파일:

```text
channels/{channel_id}/template_snapshot.json
```

Project 생성 시에도 Template Snapshot을 저장한다.

파일:

```text
projects/{channel_id}/{year}/{month}/{project_id}/template_snapshot.json
```

Snapshot 목적:

```text
재현성 확보
버전 추적
Quality 문제 원인 분석
Learning 분석
Template Evolution 기준 확보
```

---

# 32. Template Evolution

Template은 Learning을 통해 개선될 수 있다.

흐름:

```text
Project Published
↓
Analytics Report
↓
Learning Report
↓
Pattern Detection
↓
Template Improvement Proposal
↓
Template Manager Review
↓
COO or CEO Approval if needed
↓
New Template Version
```

Template 개선 대상:

```text
Hook 구조
Story 흐름
Visual Style
Voice 설정
Subtitle 규칙
Quality 가중치
Growth 전략
Provider 설정
Employee 구성
Communication 규칙
Thinking 규칙
```

---

# 33. Template Versioning

Template Version은 다음 형식을 따른다.

```text
Major.Minor.Patch
```

예시:

```text
1.0.0
1.1.0
1.1.1
2.0.0
```

변경 기준:

```text
Patch
오타, 작은 설명, 사소한 규칙 보강

Minor
Story 규칙 개선, Visual 규칙 개선, Growth 전략 개선

Major
Channel 정체성 변경, Brand 핵심 변경, 구조적 Template 변경
```

Major Version 변경은 CEO 또는 COO 승인 필요.

---

# 34. Template Improvement Proposal

Template 개선 제안은 다음 구조를 따른다.

```json
{
  "proposal_id": "TIP-000001",
  "template_id": "future",
  "current_version": "1.0.0",
  "proposed_version": "1.1.0",
  "source": {
    "project_ids": [
      "20260710-093500-future-million-year-human"
    ],
    "reports": [
      "reports/analytics_report.json",
      "reports/learning_report.json",
      "reports/quality_report.json"
    ]
  },
  "proposed_changes": [
    {
      "file": "story.yaml",
      "field": "hook_rules.must_start_with",
      "change_type": "add",
      "value": "future_simulation_scene",
      "reason": "Future scenario hooks showed higher retention potential."
    }
  ],
  "risk": {
    "level": "MEDIUM",
    "notes": [
      "Need more than one Project before making this a global rule."
    ]
  },
  "approval_required": true,
  "status": "PROPOSED"
}
```

---

# 35. Template Status

Template은 다음 상태를 가진다.

```text
DRAFT
ACTIVE
DEPRECATED
ARCHIVED
ERROR
```

## DRAFT

작성 중이며 Channel 생성에 사용하지 않는다.

## ACTIVE

Channel 생성에 사용할 수 있다.

## DEPRECATED

기존 Channel은 유지하지만 신규 Channel 생성에는 권장하지 않는다.

## ARCHIVED

보관 상태.

## ERROR

검증 실패 상태.

---

# 36. Template Error Types

```text
TemplateNotFoundError
TemplateValidationError
MissingTemplateFileError
InvalidTemplateSchemaError
TemplateInheritanceError
TemplateLockViolationError
TemplateVersionError
TemplateScoreTooLowError
TemplateSnapshotError
```

---

# 37. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
TemplateLoader
TemplateResolver
TemplateValidator
TemplateScorer
TemplateFactory
TemplateSnapshotBuilder
TemplateLockManager
TemplateOverrideResolver
TemplateVersionManager
TemplateEvolutionManager
TemplateImprovementProposalBuilder
ChannelFactory
```

---

# 38. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/08_TEMPLATE_SYSTEM.md
→ engines/template/
```

예시 구조:

```text
engines/
└── template/
    ├── template_loader.py
    ├── template_resolver.py
    ├── template_validator.py
    ├── template_scorer.py
    ├── template_factory.py
    ├── template_snapshot_builder.py
    ├── template_lock_manager.py
    ├── template_override_resolver.py
    ├── template_version_manager.py
    ├── template_evolution_manager.py
    └── template_improvement_proposal_builder.py
```

Channel 생성과 연결:

```text
engines/channel/channel_factory.py
```

---

# 39. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Template 폴더 읽기
Base + Category + Channel Template 병합
필수 파일 존재 검증
필수 필드 검증
Locked Field 위반 감지
Template Score 계산
Resolved Template 생성
Channel 생성용 Template Snapshot 생성
```

v1.0에서 실제로 복잡한 Template Evolution 자동 적용은 필수는 아니다.

먼저 제안 파일 생성까지만 가능하면 된다.

---

# 40. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Template을 로드할 수 있다.
Template 상속 구조를 해석할 수 있다.
Base, Category, Channel Template을 병합할 수 있다.
Project Override를 적용할 수 있다.
Locked Field 위반을 감지할 수 있다.
필수 Template 파일 누락을 감지할 수 있다.
필수 Template 필드 누락을 감지할 수 있다.
Template Score를 계산할 수 있다.
Template Snapshot을 생성할 수 있다.
Template에서 Channel 생성 준비를 할 수 있다.
Learning 결과를 기반으로 Template Improvement Proposal을 만들 수 있다.
Template Version을 관리할 수 있다.
```

---

# 41. Non Goals

v1.0에서 하지 않는 것:

```text
외부 Template Marketplace
사용자 판매용 Template Store
복잡한 웹 기반 Template Editor
실시간 Template 공동 편집
외부 사용자용 Template 공유 기능
자동 Major Version 적용
CEO 승인 없는 Template 핵심 변경
```

v1.0에서는 내부 CHUNG COMPANY 운영에 필요한 Template System을 먼저 만든다.

---

# 42. Critical Template Rules

반드시 지켜야 할 규칙:

```text
1. Template은 Channel보다 먼저 존재한다.

2. Channel은 Template에서 생성된다.

3. Template은 CHUNG COMPANY의 핵심 자산이다.

4. Template 없이 Project를 직접 만들지 않는다.

5. Template은 Base, Category, Channel 계층으로 관리한다.

6. Project Override는 제한적으로만 허용한다.

7. Locked Field는 Override할 수 없다.

8. Template Validation 실패 시 Channel 생성 불가.

9. Template Score 80 미만은 사용 금지.

10. Channel 생성 시 Template Snapshot을 저장한다.

11. Project 생성 시 Template Snapshot을 저장한다.

12. Template 변경은 Version 관리한다.

13. Template Evolution은 Learning 근거가 있어야 한다.

14. Major Version 변경은 승인 필요.

15. Provider는 Interface와 Adapter 구조를 유지한다.
```

---

# 43. Final Principle

Template은 설정 파일 묶음이 아니다.

Template은 Channel의 DNA이다.

좋은 Template은 좋은 Channel을 만들고,

좋은 Channel은 좋은 Project를 만들고,

좋은 Project는 좋은 Video를 만들고,

좋은 Video는 좋은 Data를 만들고,

좋은 Data는 좋은 Learning을 만들고,

좋은 Learning은 Template을 성장시킨다.

CHUNG COMPANY의 장기 경쟁력은 Template이 누적되고 진화하는 구조에서 나온다.
