# 10_BRAND_SYSTEM.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Brand System Specification  

---

# 1. Purpose

이 문서는 ADOS의 Brand System을 정의한다.

Brand System은 Channel의 정체성, 톤, 시각 스타일, 언어 스타일, 자막 스타일, 썸네일 스타일, 금지 스타일을 일관되게 유지하기 위한 시스템이다.

CHUNG COMPANY는 영상을 하나씩 만드는 회사가 아니다.

CHUNG COMPANY는 Channel을 운영하는 AI 콘텐츠 회사이다.

따라서 Brand는 영상 하나의 장식 요소가 아니라 Channel의 장기 자산이다.

이 문서는 다음을 정의한다.

```text
Brand란 무엇인가
Brand가 Channel에서 어떤 역할을 하는가
Brand 설정 파일 구조는 어떻게 되는가
Brand Context는 어떻게 생성되는가
Story, Visual, Voice, Subtitle, Publishing에 Brand가 어떻게 적용되는가
Brand Consistency는 어떻게 검사되는가
Brand Score는 어떻게 계산되는가
Brand 위반은 어떻게 처리되는가
Claude Code가 어떤 구조로 구현해야 하는가
```

이 문서는 다음 문서들과 직접 연결된다.

```text
03_ARCHITECTURE.md
07_PROJECT_SPEC.md
08_TEMPLATE_SYSTEM.md
09_CHANNEL_ENGINE.md
12_PROJECT_ENGINE.md
16_TIMELINE_ENGINE.md
19_STORY_ENGINE.md
21_VISUAL_ENGINE.md
23_VOICE_ENGINE.md
24_SUBTITLE_ENGINE.md
26_QUALITY_ENGINE.md
27_GROWTH_ENGINE.md
28_PUBLISHING_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Brand는 Channel의 정체성이다.

Brand는 다음을 결정한다.

```text
Channel Name
Slogan
Audience
Personality
Tone
Emotion
Visual Identity
Color Direction
Story Style
Narration Style
Subtitle Style
Thumbnail Style
Language Style
Forbidden Style
Brand Consistency Rules
```

Brand는 모든 Project에 적용되어야 한다.

```text
Brand
↓
Channel
↓
Project
↓
Story
↓
Visual
↓
Voice
↓
Subtitle
↓
Publishing
↓
Quality Review
```

---

# 3. Brand Philosophy

## 3.1 Brand Is Not Decoration

Brand는 로고나 색상만 의미하지 않는다.

Brand는 시청자가 Channel을 기억하게 만드는 일관된 경험이다.

## 3.2 Brand Protects Long-Term Value

단기 클릭률을 위해 Brand를 훼손하면 안 된다.

CTR이 높아 보이더라도 Channel 정체성과 맞지 않으면 사용하지 않는다.

## 3.3 Brand Comes From Template

Brand는 Template에서 시작된다.

```text
Template brand.yaml
↓
Resolved Channel brand.yaml
↓
Project channel_snapshot.json
↓
Production Engines
↓
Quality Engine
```

## 3.4 Brand Must Be Checkable

Brand는 추상적인 감각만으로 관리하지 않는다.

Brand System은 Brand Context, Brand Rules, Brand Score, Brand Violation을 구조화해야 한다.

---

# 4. Brand System Responsibilities

Brand System의 책임은 다음과 같다.

```text
brand.yaml 로드
Brand Schema 검증
Brand Context Package 생성
Production Engine에 Brand Context 제공
Story Tone 검증
Visual Style 검증
Voice Style 검증
Subtitle Style 검증
Thumbnail Style 검증
Publishing Metadata Tone 검증
Brand Consistency Score 계산
Brand Violation 감지
Brand Report 생성
Brand Memory Update Candidate 생성
```

Brand System이 하지 않는 것:

```text
Project 상태를 직접 변경하지 않는다.
Final Quality Approval을 직접 수행하지 않는다.
Provider를 직접 호출하지 않는다.
영상을 직접 생성하지 않는다.
Growth만 보고 Brand를 임의 변경하지 않는다.
```

Brand 위반 판단은 Quality Engine과 연결되어 Project 진행을 막을 수 있다.

---

# 5. Brand Source

Brand의 원천은 다음 순서를 따른다.

```text
templates/{template_id}/brand.yaml
↓
channels/{channel_id}/brand.yaml
↓
projects/{project_id}/channel_snapshot.json
↓
Project Production Files
↓
Quality Report
↓
Learning Report
```

Project 생성 시 Brand는 Channel Snapshot에 포함되어야 한다.

이유:

```text
Project 생성 당시 Brand 기준 보존
Channel Brand 변경 후에도 Project 재현 가능
Quality 문제 원인 분석 가능
Learning 분석 가능
```

---

# 6. brand.yaml Schema

Channel의 Brand 설정 파일은 다음 구조를 따른다.

```yaml
brand:
  id: future_brand
  channel_id: future
  name: Beyond Humanity
  korean_name: 비욘드 휴머니티
  slogan: "인간 이후의 미래를 탐험하다"
  english_slogan: "Exploring life beyond humanity"
  status: active
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
  composition:
    - wide cinematic shots
    - strong depth
    - clear subject
    - large scale environments

language_style:
  must_use:
    - clear sentences
    - cinematic narration
    - thoughtful questions
    - precise wording
  must_avoid:
    - generic intro
    - cheap clickbait
    - unsupported claims
    - childish tone
    - overly casual slang

must_feel_like:
  - premium documentary
  - cinematic future film
  - intelligent science story

must_not_feel_like:
  - cheap slideshow
  - random stock footage
  - childish cartoon
  - loud advertisement
  - generic AI content

forbidden:
  colors:
    - childish_pastel
    - random_rainbow
  visual_styles:
    - cheap_stock_photo
    - low_quality_ai_art
    - cartoonish_random_style
  language_patterns:
    - "오늘은 ~에 대해 알아보겠습니다"
    - exaggerated_clickbait
    - unsupported_certainty
```

---

# 7. Brand Context Package

Production Engine은 전체 `brand.yaml`을 매번 직접 해석하기보다 Brand Context Package를 받아야 한다.

Brand Context Package는 특정 작업 단계에서 필요한 Brand 정보만 정리한 객체이다.

## 7.1 Brand Context Package Schema

```json
{
  "brand_id": "future_brand",
  "channel_id": "future",
  "channel_name": "Beyond Humanity",

  "identity": {
    "core": [
      "cinematic",
      "intelligent",
      "mysterious",
      "philosophical",
      "scientific"
    ]
  },

  "tone": {
    "primary": "mysterious",
    "secondary": "philosophical",
    "energy": "calm",
    "pace": "slow_to_medium"
  },

  "visual_identity": {
    "primary_colors": [
      "deep_blue",
      "black",
      "cyan"
    ],
    "lighting": [
      "cinematic",
      "dramatic",
      "high_contrast"
    ],
    "composition": [
      "wide cinematic shots",
      "strong depth",
      "clear subject"
    ]
  },

  "language_style": {
    "must_use": [
      "clear sentences",
      "cinematic narration",
      "thoughtful questions"
    ],
    "must_avoid": [
      "generic intro",
      "cheap clickbait",
      "unsupported claims"
    ]
  },

  "forbidden": {
    "visual_styles": [
      "cheap slideshow",
      "random stock footage",
      "childish cartoon"
    ],
    "language_patterns": [
      "오늘은 ~에 대해 알아보겠습니다",
      "exaggerated_clickbait"
    ]
  }
}
```

---

# 8. Brand Application Points

Brand는 다음 단계에 적용된다.

```text
Topic Selection
Story Writing
Direction Planning
Timeline Design
Visual Prompt Generation
Motion Prompt Generation
Voice Style Selection
Subtitle Formatting
Thumbnail Creation
Title Writing
Description Writing
Tag Selection
Publishing Package
Quality Review
Learning
```

각 Engine은 자신에게 필요한 Brand Context를 받아야 한다.

---

# 9. Brand and Story

Story Engine은 Brand를 기준으로 대본 톤을 결정한다.

미래 다큐멘터리 Channel 예시:

```text
철학적 질문
미스터리한 오프닝
과학적 맥락
영화 같은 장면 묘사
성찰적인 엔딩
차분하지만 강한 긴장감
```

금지:

```text
Generic Introduction
가벼운 농담 중심
선정적 과장
광고 같은 말투
정보 나열식 설명
근거 없는 미래 단정
```

Story Brand Check 항목:

```text
Hook이 Brand Tone과 맞는가
대본 톤이 Channel 정체성과 맞는가
언어 스타일이 너무 가볍지 않은가
금지 표현을 사용하지 않았는가
시청자가 같은 Channel 콘텐츠로 인식할 수 있는가
```

---

# 10. Brand and Direction

Direction Engine은 Brand를 기준으로 Scene의 분위기와 연출을 결정한다.

검사 항목:

```text
Scene 감정이 Brand와 맞는가
Camera Direction이 Channel 스타일과 맞는가
장면 전환이 지나치게 가볍지 않은가
세계관과 분위기가 유지되는가
Visual Department가 Brand에 맞게 만들 수 있는가
```

금지:

```text
Channel 톤과 맞지 않는 코미디 연출
과도하게 빠른 광고식 연출
브랜드와 무관한 장면 분위기
Scene마다 스타일이 심하게 바뀌는 구성
```

---

# 11. Brand and Visual

Visual Engine은 Brand를 기준으로 이미지 프롬프트와 이미지 자산을 만든다.

미래 다큐멘터리 Channel 예시:

```text
cinematic realism
deep blue
black
cyan highlights
dramatic lighting
large scale environments
futuristic but believable
strong depth
clear subject
```

금지:

```text
random robot image
generic AI art
flat composition
childish cartoon
cheap stock photo 느낌
텍스트가 들어간 이미지
브랜드 색감과 무관한 이미지
```

Visual Brand Check 항목:

```text
색감이 Brand와 맞는가
조명이 Brand와 맞는가
프롬프트에 Brand Style이 반영되었는가
Scene 목적과 이미지가 맞는가
이미지가 싸구려 AI 이미지처럼 보이지 않는가
Thumbnail로 쓸 수 있는 명확성이 있는가
```

---

# 12. Brand and Motion

Motion Engine은 Brand와 Scene 중요도를 기준으로 Motion 적용 여부를 판단한다.

Motion 적용 우선순위:

```text
Hook Scene
Climax Scene
World Reveal Scene
Emotional Turn Scene
Character Motion Scene
```

Brand 기준:

```text
subtle cinematic motion
slow controlled movement
dramatic reveal
immersive camera movement
```

금지:

```text
빠르고 산만한 움직임
의미 없는 카메라 흔들림
Scene 감정과 맞지 않는 Motion
모든 Scene을 무리하게 Motion화
```

---

# 13. Brand and Voice

Voice Engine은 Brand를 기준으로 언어별 나레이션 스타일을 결정한다.

미래 다큐멘터리 Channel 예시:

```text
calm
intelligent
mysterious
medium_slow
documentary narrator
cinematic delivery
```

금지:

```text
광고 톤
너무 빠른 말투
과도한 흥분
로봇 같은 낭독
가벼운 예능 톤
```

Voice Brand Check 항목:

```text
Voice Tone이 Brand와 맞는가
언어별 감정이 일관적인가
속도가 Channel 분위기와 맞는가
과장된 감정 표현이 없는가
Timeline과 맞는가
```

---

# 14. Brand and Subtitle

Subtitle Engine은 Brand를 기준으로 자막 스타일을 결정한다.

기본 규칙:

```text
읽기 쉬워야 한다.
의미 단위로 줄바꿈한다.
과도한 강조를 피한다.
화면 몰입을 방해하지 않는다.
언어별 의미가 자연스러워야 한다.
```

금지:

```text
너무 긴 자막
의미가 끊기는 줄바꿈
과도한 이모지
광고식 강조
브랜드와 맞지 않는 캐주얼 표현
```

---

# 15. Brand and Thumbnail

Thumbnail은 Brand와 CTR이 만나는 지점이다.

Thumbnail은 클릭 가능해야 하지만, Channel 정체성을 깨면 안 된다.

좋은 Thumbnail 조건:

```text
Brand 색감 유지
작은 화면에서도 명확함
강한 궁금증
명확한 주제
과도한 낚시 없음
시각적 중심이 분명함
```

금지:

```text
저가형 클릭bait
과장된 표정 남발
채널과 무관한 색감
텍스트 과다
혼란스러운 구도
이미지 품질 저하
```

---

# 16. Brand and Publishing Metadata

Publishing Engine은 제목, 설명, 태그, 고정 댓글을 만들 때 Brand를 유지해야 한다.

Title 규칙:

```text
궁금증을 만든다.
주제를 명확히 한다.
Brand Tone을 유지한다.
Cheap Clickbait을 피한다.
```

Description 규칙:

```text
영상 내용을 정확히 설명한다.
과장하지 않는다.
Brand Tone을 유지한다.
언어별 자연스러운 표현을 사용한다.
```

금지 제목 예시:

```text
이걸 보면 충격받습니다!!!
과학자들이 숨긴 진실!!!
절대 믿을 수 없는 미래!!!
```

좋은 방향 예시:

```text
100만 년 후 인간은 어떤 모습일까?
AI 이후, 인간의 몸은 어떻게 변할까?
우리가 사라진 뒤에도 문명은 계속될까?
```

---

# 17. Brand Consistency Check

Brand System은 결과물이 Brand와 일관적인지 검사한다.

검사 대상:

```text
Story
Hook
Script
Scene Direction
Visual Prompt
Generated Image
Motion Prompt
Voice Style
Subtitle Style
Thumbnail
Title
Description
Tags
Upload Package
```

검사 기준:

```text
Identity Match
Tone Match
Visual Match
Language Match
Audience Fit
Forbidden Style Avoidance
Brand Memory Fit
```

---

# 18. Brand Score

Brand Score는 다음 기준으로 계산한다.

```yaml
brand_score:
  identity_match: 20
  tone_consistency: 20
  visual_consistency: 20
  language_consistency: 15
  audience_fit: 10
  forbidden_style_avoidance: 10
  cross_language_consistency: 5
```

점수 기준:

```text
95~100
Brand Excellent

90~94
Brand Pass, Human Review Recommended

80~89
Brand Revision Required

70~79
Partial Regeneration Required

70 미만
Brand Fail
```

Quality Engine은 Brand Score를 최종 Quality Score에 반영해야 한다.

---

# 19. Brand Hard Fail

다음은 Brand Hard Fail이다.

```text
Channel 정체성과 완전히 다른 톤
금지 색상 또는 금지 스타일 사용
저가형 AI 슬라이드쇼 느낌
채널 브랜드와 맞지 않는 제목
대본 톤과 영상 톤 불일치
Visual Style이 Channel과 완전히 다름
Voice Tone이 Channel과 맞지 않음
언어별 Brand Tone 불일치
Thumbnail이 Cheap Clickbait처럼 보임
```

Brand Hard Fail이 발생하면 Project는 Quality Gate를 통과할 수 없다.

---

# 20. Brand Violation Schema

Brand 위반은 구조화해서 기록한다.

```json
{
  "violation_id": "BRAND-VIO-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "VISUAL",
  "target_file": "prompts/midjourney_image_prompts.json",
  "scene_id": "SC004",
  "severity": "HIGH",
  "violation_type": "VISUAL_STYLE_MISMATCH",
  "description": "The prompt uses a colorful cartoon style that violates the channel brand.",
  "expected_brand_rule": "cinematic realistic, deep blue, black, cyan, dramatic lighting",
  "suggested_fix": "Rewrite the prompt using cinematic realism and approved brand colors.",
  "requires_regeneration": true,
  "created_at": "2026-07-10T10:00:00"
}
```

---

# 21. Brand Report

Brand System은 Brand 검사 결과를 Report로 남긴다.

파일 위치:

```text
reports/brand_report.json
```

예시:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "brand_score": 94,
  "status": "PASS_WITH_NOTES",
  "checks": {
    "story": 96,
    "visual": 92,
    "voice": 95,
    "subtitle": 94,
    "thumbnail": 90,
    "metadata": 95
  },
  "violations": [
    {
      "violation_id": "BRAND-VIO-000001",
      "severity": "MEDIUM",
      "stage": "VISUAL",
      "summary": "Some image prompts need stronger brand color direction."
    }
  ],
  "recommended_actions": [
    "Strengthen visual prompts with approved color palette."
  ]
}
```

---

# 22. Brand Auto Fix Rules

Brand 문제가 발생하면 전체 Project를 다시 만들지 않는다.

부분 수정이 우선이다.

예시:

```text
Title이 Brand와 맞지 않음
→ metadata_ko.json title만 수정

Scene 4 이미지가 Brand와 맞지 않음
→ SC004 Visual Prompt만 수정
→ SC004 Image만 재생성

Voice Tone이 너무 광고 같음
→ Typecast Voice 설정만 수정
→ 해당 언어 Voice만 재생성

Subtitle 표현이 너무 캐주얼함
→ 해당 언어 Subtitle만 수정
```

Brand Auto Fix 흐름:

```text
Brand Violation Detection
↓
Target Scope Identification
↓
Revision Request
↓
Partial Regeneration
↓
Brand Recheck
↓
Quality Recheck
```

---

# 23. Brand Memory

Brand 관련 학습은 Channel Memory에 저장될 수 있다.

저장 대상:

```text
성공한 Thumbnail 스타일
좋은 Title Tone
좋은 Hook Tone
좋은 Visual Color Pattern
좋은 Voice Setting
반복 Brand Violation
시청자 반응이 좋았던 분위기
```

Memory Update Candidate 예시:

```json
{
  "target_memory": "channel_memory",
  "update_type": "brand_success_pattern",
  "summary": "Deep blue cinematic world-reveal thumbnails fit this channel well.",
  "evidence": [
    "brand_report.json",
    "quality_report.json",
    "analytics_report.json"
  ],
  "confidence": "MEDIUM",
  "requires_approval": false
}
```

---

# 24. Brand and Growth Conflict

Growth와 Brand가 충돌할 수 있다.

예시:

```text
Growth Department:
더 자극적인 제목이 CTR이 높을 것이라고 판단

Brand System:
해당 제목은 Channel의 premium documentary tone을 훼손한다고 판단
```

충돌 시 우선순위:

```text
1. 사실 정확성
2. 안전 / 저작권 / 정책 위험
3. Template Lock Rules
4. Channel Brand Rules
5. Quality Rules
6. Growth Strategy
```

즉, Brand를 심하게 훼손하는 Growth 제안은 사용하지 않는다.

---

# 25. Brand Validation Rules

Brand Validator는 다음을 확인해야 한다.

```text
brand.id 존재
brand.channel_id 존재
brand.name 존재
identity.core 존재
audience.primary 존재
tone.primary 존재
visual_identity.primary_colors 존재
language_style.must_use 존재
language_style.must_avoid 존재
must_feel_like 존재
must_not_feel_like 존재
forbidden 규칙 존재
```

검증 실패 시 Channel은 ACTIVE 상태가 될 수 없다.

---

# 26. Error Types

Brand System의 Error Type은 다음과 같다.

```text
BrandFileNotFoundError
InvalidBrandSchemaError
MissingBrandFieldError
BrandContextBuildError
BrandValidationError
BrandViolationError
BrandScoreTooLowError
BrandHardFailError
BrandMemoryUpdateError
```

---

# 27. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
BrandSystem
BrandLoader
BrandValidator
BrandContextBuilder
BrandConsistencyChecker
BrandScoreCalculator
BrandViolationDetector
BrandReportBuilder
BrandAutoFixPlanner
BrandMemoryWriter
BrandGrowthConflictResolver
```

---

# 28. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/10_BRAND_SYSTEM.md
→ engines/brand/
```

예시 구조:

```text
engines/
└── brand/
    ├── brand_system.py
    ├── brand_loader.py
    ├── brand_validator.py
    ├── brand_context_builder.py
    ├── brand_consistency_checker.py
    ├── brand_score_calculator.py
    ├── brand_violation_detector.py
    ├── brand_report_builder.py
    ├── brand_auto_fix_planner.py
    ├── brand_memory_writer.py
    └── brand_growth_conflict_resolver.py
```

---

# 29. Main Public Operations

Brand System은 최소 다음 작업을 제공해야 한다.

```text
load_brand(channel_id)
validate_brand(channel_id)
build_brand_context(channel_id, stage)
check_brand_consistency(project_id, target)
calculate_brand_score(project_id)
detect_brand_violations(project_id)
build_brand_report(project_id)
plan_brand_auto_fix(violation)
create_brand_memory_candidate(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
Brand 파일 존재 확인
Schema 검증
결과 로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 30. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
brand.yaml 로드
Brand 필수 필드 검증
Brand Context Package 생성
Story / Visual / Voice / Subtitle / Metadata용 Context 분리
Brand Consistency Check 기본 구현
Brand Score 기본 계산
Brand Violation 기록
Brand Report 생성
Quality Engine이 사용할 Brand Result 제공
```

v1.0에서 하지 않아도 되는 것:

```text
복잡한 이미지 자동 판독
실시간 Brand Dashboard
자동 Brand 리디자인
외부 사용자용 Brand Editor
정교한 A/B Test 자동화
```

---

# 31. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Channel의 brand.yaml을 로드할 수 있다.
brand.yaml 필수 필드를 검증할 수 있다.
Stage별 Brand Context를 생성할 수 있다.
Story 결과물이 Brand와 맞는지 검사할 수 있다.
Visual Prompt가 Brand와 맞는지 검사할 수 있다.
Voice 설정이 Brand와 맞는지 검사할 수 있다.
Subtitle 스타일이 Brand와 맞는지 검사할 수 있다.
Publishing Metadata가 Brand와 맞는지 검사할 수 있다.
Brand Score를 계산할 수 있다.
Brand Hard Fail을 감지할 수 있다.
Brand Report를 생성할 수 있다.
Brand Auto Fix 범위를 제안할 수 있다.
Brand 관련 Memory Update Candidate를 만들 수 있다.
```

---

# 32. Non Goals

v1.0에서 Brand System이 하지 않는 것:

```text
외부 사용자용 브랜드 관리 SaaS
복잡한 로고 디자인 자동화
상표권 검사 자동화
실시간 디자인 편집 UI
완전 자동 Brand Repositioning
CEO 승인 없는 핵심 Brand Identity 변경
```

v1.0에서는 내부 ADOS 운영에 필요한 Brand 일관성 유지와 검사 구조를 먼저 완성한다.

---

# 33. Critical Brand Rules

반드시 지켜야 할 규칙:

```text
1. Brand는 Channel의 정체성이다.

2. Brand는 Template에서 시작된다.

3. Project 생성 시 Brand는 Channel Snapshot에 포함되어야 한다.

4. Production Engine은 Brand Context를 사용해야 한다.

5. Story, Visual, Voice, Subtitle, Publishing은 Brand를 따라야 한다.

6. Brand Hard Fail은 Quality Gate를 통과할 수 없다.

7. 단기 CTR을 위해 Brand를 훼손하지 않는다.

8. Brand 위반은 구조화해서 기록한다.

9. Brand 문제는 부분 수정이 우선이다.

10. Brand 관련 학습은 Channel Memory에 반영될 수 있다.

11. 핵심 Brand Identity 변경은 승인 없이 수행하지 않는다.

12. Brand System은 Provider를 직접 호출하지 않는다.
```

---

# 34. Final Principle

Brand는 Channel이 기억되는 방식이다.

좋은 Brand는 모든 Project를 하나의 Channel 경험으로 묶는다.

Brand가 흔들리면 영상은 많아져도 Channel은 강해지지 않는다.

CHUNG COMPANY는 단순히 영상을 많이 만드는 것이 아니라, 기억되는 Channel을 만든다.

Brand System의 목적은 모든 Project가 Channel의 정체성을 지키면서 성장하도록 만드는 것이다.
