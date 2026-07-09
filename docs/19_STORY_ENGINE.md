# 19_STORY_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Story Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Story Engine을 정의한다.

Story Engine은 Knowledge Engine이 만든 Claim, Context, Risk, Story Material을 시청자가 끝까지 보고 싶은 영상 이야기 구조와 대본으로 변환하는 엔진이다.

Story Engine은 단순 대본 작성기가 아니다.

Story Engine은 다음을 설계한다.

```text
Hook
Core Question
Outline
Act Structure
Retention Flow
Emotional Arc
Master Script
Language Script Base
Story Risk Notes
Story Review
Direction Engine Handoff
```

Story Engine의 결과가 약하면 이후 Direction, Timeline, Visual, Voice, Subtitle, Editing이 모두 약해진다.

```text
Story가 약하면
→ Direction이 약해지고
→ Scene 목적이 흐려지고
→ Visual Prompt가 흔들리고
→ Retention이 떨어지고
→ Quality Gate에서 실패한다.
```

이 문서는 다음 문서들과 직접 연결된다.

```text
06_AI_THINKING_FRAMEWORK.md
07_PROJECT_SPEC.md
10_BRAND_SYSTEM.md
12_PROJECT_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
17_RESEARCH_ENGINE.md
18_KNOWLEDGE_ENGINE.md
20_DIRECTION_ENGINE.md
16_TIMELINE_ENGINE.md
23_VOICE_ENGINE.md
26_QUALITY_ENGINE.md
27_GROWTH_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Story Engine은 구조화된 Knowledge를 영상 대본과 이야기 흐름으로 바꾸는 엔진이다.

전체 흐름:

```text
Knowledge
↓
Story Angle
↓
Hook
↓
Outline
↓
Act Structure
↓
Master Script
↓
Story Review
↓
Direction Engine
```

Story Engine의 핵심 목표는 다음이다.

```text
시청자가 첫 10초 안에 멈추지 않게 한다.
시청자가 첫 30초 안에 계속 볼 이유를 갖게 한다.
정보를 나열하지 않고 이야기로 만든다.
Channel Brand Tone을 유지한다.
Knowledge의 Fact / Speculation / Risk를 지킨다.
Direction Engine이 Scene으로 변환할 수 있게 만든다.
Visual Engine이 장면화할 수 있는 대본을 만든다.
Voice Engine이 자연스럽게 읽을 수 있는 문장을 만든다.
```

---

# 3. Story Philosophy

## 3.1 Story Is Not Information Dump

나쁜 Story:

```text
오늘은 미래 인간에 대해 알아보겠습니다.
인간은 진화합니다.
AI가 발전합니다.
우주로 갈 수 있습니다.
그래서 인간은 변할 수 있습니다.
```

좋은 Story:

```text
100만 년 뒤, 지구가 아닌 다른 별에서 태어난 아이가 있다.
그 아이의 피부, 뼈, 눈, 심장은 지금의 우리와 같을까?
아니면 그 아이는 이미 다른 인간일까?
```

## 3.2 Hook First

영상의 첫 10초와 첫 30초는 가장 중요하다.

Story Engine은 반드시 Hook을 별도 설계해야 한다.

Hook이 약하면 Story Stage는 통과할 수 없다.

## 3.3 Retention Flow

Story는 시청자가 계속 보게 만드는 질문과 전환을 가져야 한다.

```text
Question
↓
Partial Answer
↓
New Question
↓
Tension
↓
Reveal
↓
Reflection
```

## 3.4 Brand Consistency

Story는 Channel Brand를 따라야 한다.

예시:

```text
future Channel
→ cinematic
→ intelligent
→ mysterious
→ philosophical
→ scientific
```

금지:

```text
cheap clickbait
generic intro
unsupported claim
childish tone
random comedy
advertisement tone
```

## 3.5 Factual Safety

Story는 Knowledge Engine의 Fact Check와 Risk Notes를 반드시 따라야 한다.

Speculative Claim은 사실처럼 말하지 않는다.

---

# 4. Story Engine Responsibilities

Story Engine의 책임:

```text
Knowledge Output 로드
Brand Context 로드
Story Rules 로드
Growth Rules 로드
Story Angle 결정
Hook 후보 생성
Hook 선택
Outline 생성
Act Structure 생성
Master Script 생성
Language Script Base 생성
Retention Point 설계
Emotional Arc 설계
Story Risk 반영
Forbidden Claim 회피
Story Review 생성
Self Review 생성
Direction Engine Handoff 생성
```

Story Engine이 하지 않는 것:

```text
Research를 직접 수행하지 않는다.
Claim을 새로 검증 없이 만들지 않는다.
Scene Direction을 최종 작성하지 않는다.
Timeline을 만들지 않는다.
Visual Prompt를 만들지 않는다.
Voice 파일을 생성하지 않는다.
Subtitle을 생성하지 않는다.
Provider를 직접 호출하지 않는다.
Quality Score를 최종 계산하지 않는다.
```

---

# 5. Inputs

Story Engine의 입력:

```text
project.json
topic.json
channel_snapshot.json
template_snapshot.json
knowledge/knowledge.json
knowledge/claims.json
knowledge/fact_check.json
knowledge/risk_notes.json
knowledge/story_materials.json
knowledge/visualizable_ideas.json
channels/{channel_id}/brand.yaml
channels/{channel_id}/story.yaml
channels/{channel_id}/growth.yaml
workflow/memory_context_STORY.json
```

필수 입력:

```text
knowledge/knowledge.json
knowledge/claims.json
knowledge/fact_check.json
knowledge/risk_notes.json
project.json
channel_snapshot.json
```

선택 입력:

```text
knowledge/story_materials.json
knowledge/visualizable_ideas.json
Channel Story Memory
Successful Hook Memory
Failed Hook Memory
Growth Memory
Brand Memory
```

---

# 6. Outputs

Story Engine의 출력:

```text
story/outline.json
story/hook.json
story/script_master.json
story/script_master.md
story/story_review.json
languages/{lang}/script.json
workflow/stage_results/STORY_result.json
workflow/handoffs/STORY_to_DIRECTION.json
```

v1.0 최소 출력:

```text
story/outline.json
story/hook.json
story/script_master.json
story/script_master.md
story/story_review.json
```

Direction Engine은 최소 다음 파일을 입력으로 사용한다.

```text
story/outline.json
story/hook.json
story/script_master.json
story/script_master.md
story/story_review.json
knowledge/fact_check.json
knowledge/risk_notes.json
```

---

# 7. Story Creation Flow

Story Engine 실행 흐름:

```text
Load Project Context
↓
Load Knowledge Outputs
↓
Load Brand / Story / Growth Rules
↓
Load Memory Context
↓
Validate Knowledge Inputs
↓
Build Story Angle Options
↓
Select Story Angle
↓
Create Hook Options
↓
Score Hook Options
↓
Select Hook
↓
Build Outline
↓
Build Act Structure
↓
Write Master Script
↓
Check Fact / Speculation / Risk
↓
Check Brand Tone
↓
Check Retention Flow
↓
Write script_master.json
↓
Write script_master.md
↓
Write story_review.json
↓
Self Review
↓
Handoff to Direction Engine
```

---

# 8. Story Angle

Story Angle은 같은 주제를 어떤 관점으로 풀지 결정한다.

예시 Topic:

```text
100만 년 후 인간은 어떤 모습일까?
```

가능한 Story Angle:

```text
1. 미래 시뮬레이션
한 아이가 먼 행성에서 태어나는 장면으로 시작한다.

2. 과학적 질문
인간 진화를 바꾸는 힘은 자연인가, 기술인가?

3. 철학적 질문
미래 인간이 우리와 너무 달라진다면, 그들은 여전히 인간인가?

4. 문명 시나리오
지구를 떠난 여러 인간 집단이 서로 다른 방향으로 변한다.
```

Story Engine은 최종 Story Angle을 선택하고 Decision Record에 남길 수 있다.

---

# 9. Story Angle Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "selected_angle": {
    "angle_id": "ANGLE-000001",
    "name": "cinematic_future_simulation",
    "summary": "Start with a cinematic future scenario, then explain why the future of humans is uncertain but shaped by biology, technology, and environment.",
    "reason": "This angle has strong hook potential, visual potential, and fits the channel brand.",
    "brand_fit": "HIGH",
    "retention_potential": "HIGH",
    "visual_potential": "HIGH",
    "factual_risk": "MEDIUM",
    "risk_mitigation": "Frame future scenes as possible scenarios, not facts."
  }
}
```

---

# 10. Hook Rules

Hook은 별도 파일로 관리한다.

Hook의 목적:

```text
첫 10초 안에 시청자의 관심을 잡는다.
첫 30초 안에 핵심 질문을 만든다.
영상 전체를 볼 이유를 만든다.
Brand Tone을 즉시 전달한다.
```

좋은 Hook 조건:

```text
시각적으로 강하다.
질문이 명확하다.
궁금증이 생긴다.
너무 설명적이지 않다.
Channel Brand와 맞는다.
Knowledge Risk를 위반하지 않는다.
```

금지 Hook:

```text
오늘은 ~에 대해 알아보겠습니다.
이번 영상에서는 ~를 설명하겠습니다.
여러분은 혹시 ~를 아시나요?
근거 없는 충격 표현
싸구려 클릭bait
사실처럼 말하는 미래 예측
```

---

# 11. hook.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "selected_hook": {
    "hook_id": "HOOK-000001",
    "type": "cinematic_future_scenario",
    "duration_seconds": 30,

    "text": "100만 년 뒤, 지구가 아닌 다른 별에서 한 아이가 태어난다. 그 아이의 눈은 우리와 같은 빛을 볼까? 그 아이의 뼈와 심장은 지구의 중력을 기억할까? 아니면 우리는 그 아이를 더 이상 같은 인간이라고 부를 수 없게 될까?",

    "core_question": "If humans change for one million years under new environments and technologies, will they still be human?",

    "emotion": [
      "curiosity",
      "awe",
      "mystery"
    ],

    "visual_potential": "HIGH",
    "retention_potential": "HIGH",
    "brand_fit": "HIGH",

    "risk": {
      "level": "MEDIUM",
      "notes": [
        "This must be framed as a possible scenario, not a prediction."
      ]
    }
  },

  "rejected_hooks": [
    {
      "hook_id": "HOOK-000002",
      "reason": "Too generic and explanatory."
    }
  ]
}
```

---

# 12. Outline Rules

Outline은 영상의 전체 구조이다.

좋은 Outline은 다음을 가져야 한다.

```text
Hook
Core Question
Context
Development
Tension
Reveal
Reflection
Ending
```

나쁜 Outline:

```text
1. 인간 진화 설명
2. AI 설명
3. 우주 설명
4. 결론
```

좋은 Outline:

```text
1. 먼 미래의 인간을 상상하게 만드는 Hook
2. 인간이 왜 변하는지에 대한 핵심 질문
3. 자연선택과 환경 압력 설명
4. 기술이 진화의 방향을 바꿀 가능성
5. 우주 이주가 인간을 갈라놓을 가능성
6. 인간의 정의에 대한 철학적 결론
```

---

# 13. outline.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "outline": [
    {
      "section_id": "SEC-001",
      "title": "A child born far from Earth",
      "purpose": "hook",
      "summary": "Open with a cinematic future scenario.",
      "estimated_duration_seconds": 30,
      "key_claim_ids": [],
      "emotional_goal": "curiosity",
      "visual_goal": "future human settlement under alien sunlight"
    },
    {
      "section_id": "SEC-002",
      "title": "Why predicting evolution is uncertain",
      "purpose": "context",
      "summary": "Explain that long-term human evolution cannot be predicted with certainty.",
      "estimated_duration_seconds": 90,
      "key_claim_ids": [
        "CLM-000001"
      ],
      "emotional_goal": "trust",
      "visual_goal": "timeline of human change"
    }
  ],

  "story_arc": {
    "start": "mystery",
    "middle": "expanding possibility",
    "end": "philosophical reflection"
  }
}
```

---

# 14. Script Master Rules

`script_master`는 영상의 중심 대본이다.

규칙:

```text
Brand Tone을 유지한다.
Knowledge Claim을 따른다.
Speculative Claim은 가능성으로 표현한다.
첫 30초 Hook을 강하게 유지한다.
시각화 가능한 문장을 사용한다.
Voice가 읽기 쉬운 문장을 사용한다.
너무 긴 문장을 피한다.
각 문단은 Direction Engine이 Scene으로 나눌 수 있어야 한다.
```

금지:

```text
출처 없는 강한 주장 추가
Forbidden Claim 사용
Generic Introduction
과도한 클릭bait
너무 추상적인 문장만 반복
Voice로 읽기 어려운 장문
```

---

# 15. script_master.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "language": "ko",
  "stage": "STORY",

  "script": {
    "title": "100만 년 후 인간은 어떤 모습일까?",
    "core_question": "미래의 인간은 지금의 우리와 얼마나 달라질 수 있을까?",
    "estimated_duration_seconds": 900,

    "sections": [
      {
        "section_id": "SEC-001",
        "purpose": "hook",
        "estimated_duration_seconds": 30,
        "text": "100만 년 뒤, 지구가 아닌 다른 별에서 한 아이가 태어난다. 그 아이의 눈은 우리와 같은 빛을 볼까? 그 아이의 뼈와 심장은 지구의 중력을 기억할까? 아니면 우리는 그 아이를 더 이상 같은 인간이라고 부를 수 없게 될까?",
        "claim_ids": [],
        "risk_notes": [
          "Frame as possible scenario."
        ],
        "visual_notes": [
          "Future colony under alien sunlight."
        ]
      }
    ]
  },

  "story_controls": {
    "brand_tone": [
      "cinematic",
      "mysterious",
      "philosophical",
      "scientific"
    ],
    "forbidden_claims_checked": true,
    "speculative_claims_framed": true
  }
}
```

---

# 16. script_master.md Format

`script_master.md`는 사람이 읽기 좋은 대본 파일이다.

권장 형식:

```markdown
# 100만 년 후 인간은 어떤 모습일까?

## Core Question

미래의 인간은 지금의 우리와 얼마나 달라질 수 있을까?

---

## Hook

100만 년 뒤, 지구가 아닌 다른 별에서 한 아이가 태어난다.

그 아이의 눈은 우리와 같은 빛을 볼까?

그 아이의 뼈와 심장은 지구의 중력을 기억할까?

아니면 우리는 그 아이를 더 이상 같은 인간이라고 부를 수 없게 될까?

---

## Section 1: Why the future is uncertain

...
```

---

# 17. Language Script Rules

Master Script는 기본 언어로 작성된다.

기본 언어:

```text
ko
```

다국어 Project에서는 언어별 Script를 생성할 수 있다.

```text
languages/ko/script.json
languages/en/script.json
```

규칙:

```text
직역하지 않는다.
언어별 자연스러운 표현을 사용한다.
Story Structure는 유지한다.
Voice 길이 차이를 고려한다.
Brand Tone은 언어별로 유지한다.
Speculative Claim의 조심스러운 표현을 유지한다.
```

---

# 18. languages/{lang}/script.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "language": "en",

  "script": {
    "title": "What Will Humans Look Like in One Million Years?",
    "core_question": "How different could humans become in the distant future?",

    "sections": [
      {
        "section_id": "SEC-001",
        "purpose": "hook",
        "text": "One million years from now, a child is born under the light of a star far from Earth. Will their eyes see the world the way ours do? Will their bones and heart remember Earth's gravity? Or will they be so different that we struggle to call them human?",
        "localization_notes": [
          "Preserve cinematic tone.",
          "Do not overstate future predictions."
        ]
      }
    ]
  }
}
```

---

# 19. Retention Design

Story Engine은 Retention을 고려해야 한다.

Retention 장치:

```text
Open Loop
Unanswered Question
Contrast
Escalating Stakes
Surprising Turn
Visual Reveal
Emotional Reflection
```

Story Review에서 확인할 항목:

```text
첫 10초에 궁금증이 있는가
첫 30초에 핵심 질문이 있는가
Section 간 질문이 이어지는가
중반부에 긴장이나 전환이 있는가
마지막에 기억되는 질문이 있는가
```

---

# 20. Emotional Arc

Story는 감정 흐름을 가져야 한다.

예시:

```text
mystery
↓
curiosity
↓
awe
↓
uncertainty
↓
reflection
```

Story Engine은 Outline이나 Script에 Emotional Goal을 기록해야 한다.

감정이 없는 정보 나열식 대본은 통과할 수 없다.

---

# 21. Factual Safety Rules

Story Engine은 Knowledge Engine의 Fact Check를 따라야 한다.

규칙:

```text
Forbidden Claim 사용 금지
Unsupported Claim 사용 금지
Speculative Claim은 가능성으로 표현
Risk Note가 있는 Claim은 조심스럽게 표현
Claim ID를 Script Section에 연결
Quality Engine이 검토할 수 있게 Risk Note 유지
```

금지 표현 예시:

```text
100만 년 뒤 인간은 반드시 이렇게 변한다.
과학자들은 이미 확정했다.
AI는 무조건 인간의 몸을 바꾼다.
```

허용 표현 예시:

```text
어떤 미래에서는 이렇게 변할 수도 있다.
이것은 하나의 가능성이다.
과학은 아직 100만 년 뒤의 모습을 확정할 수 없다.
```

---

# 22. Brand Safety Rules

Story는 Brand System의 규칙을 따라야 한다.

검사 항목:

```text
Channel Tone과 맞는가
Language Style이 맞는가
금지 표현을 피했는가
Cheap Clickbait이 없는가
대본이 Channel의 장기 정체성을 해치지 않는가
```

Brand 위반은 Story Review에서 기록한다.

---

# 23. story_review.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "STORY",

  "score": 94,
  "status": "PASS_WITH_NOTES",

  "checks": {
    "hook_strength": 95,
    "first_30_seconds": 96,
    "retention_flow": 92,
    "brand_fit": 95,
    "factual_safety": 94,
    "visual_potential": 93,
    "voice_readability": 94,
    "direction_readiness": 92
  },

  "issues": [
    {
      "severity": "MEDIUM",
      "issue_type": "FACTUAL_FRAMING",
      "description": "Some future scenarios require careful framing in Direction and Voice.",
      "suggested_fix": "Keep speculative language in all later stages."
    }
  ],

  "handoff_notes": [
    "Direction Engine should preserve cinematic opening.",
    "Future scenarios must be visually presented as simulations, not confirmed predictions."
  ]
}
```

---

# 24. Story Scoring

Story Score 기준:

```yaml
story_score:
  hook_strength: 20
  retention_flow: 20
  brand_fit: 15
  factual_safety: 15
  visual_potential: 10
  emotional_arc: 10
  voice_readability: 5
  direction_readiness: 5
```

점수 기준:

```text
95~100
Pass

90~94
Pass with notes / Peer Review recommended

80~89
Revision required

70~79
Partial rewrite required

70 미만
Story fail
```

Hook Score가 80 미만이면 Story Stage는 통과할 수 없다.

---

# 25. Story Validation Rules

Story Validator는 다음을 확인해야 한다.

```text
story/outline.json 존재
story/hook.json 존재
story/script_master.json 존재
story/script_master.md 존재
story/story_review.json 존재
project_id 일치
channel_id 일치
Hook 존재
Core Question 존재
Outline Section 존재
Script Section 존재
Claim ID 연결 존재
Forbidden Claim 미사용
Speculative Claim Framing 확인
Brand Tone 확인
Direction Engine이 사용할 visual_notes 존재
story_review score 존재
```

검증 실패 시 DIRECTION Stage로 이동할 수 없다.

---

# 26. Self Review

Story Engine은 결과 제출 전 Self Review를 생성한다.

Self Review 항목:

```text
Hook이 강한가
첫 30초가 강한가
Core Question이 명확한가
Retention Flow가 있는가
Brand Tone을 지켰는가
Fact Check를 지켰는가
Forbidden Claim을 사용하지 않았는가
Speculative Claim을 조심스럽게 표현했는가
Direction Engine이 Scene으로 만들 수 있는가
Voice로 읽기 자연스러운가
```

Self Review는 다음 위치에 기록한다.

```text
logs/self_reviews.jsonl
```

---

# 27. Handoff to Direction Engine

Story Engine은 Direction Engine에 Handoff를 생성해야 한다.

Handoff 파일:

```text
workflow/handoffs/STORY_to_DIRECTION.json
```

Handoff에 포함할 내용:

```text
Selected Story Angle
Selected Hook
Core Question
Outline
Master Script
Section별 목적
Visual Notes
Emotion Notes
Risk Notes
Forbidden Claims
Speculative Framing Rules
Direction 주의사항
```

Handoff 예시:

```json
{
  "from_stage": "STORY",
  "to_stage": "DIRECTION",
  "project_id": "20260710-093500-future-million-year-human",

  "summary": "Story created with cinematic future scenario hook and cautious speculative framing.",

  "must_preserve": [
    "Opening future scenario",
    "Core question about what makes humans human",
    "Speculative framing for future predictions"
  ],

  "direction_notes": [
    "Opening should feel cinematic and mysterious.",
    "Do not make future scenarios look like confirmed documentary footage.",
    "Use visual contrast between Earth-born humans and future off-world humans."
  ],

  "required_inputs_for_direction": [
    "story/outline.json",
    "story/hook.json",
    "story/script_master.json",
    "story/script_master.md",
    "knowledge/fact_check.json",
    "knowledge/risk_notes.json"
  ]
}
```

---

# 28. Memory Integration

Story Engine은 작업 전 Memory Context를 사용한다.

사용 가능한 Memory:

```text
Successful Hook Memory
Failed Hook Memory
Channel Story Pattern
Brand Tone Memory
Retention Pattern Memory
Quality Failure Memory
Growth Memory
```

Story Engine은 작업 후 Memory Candidate를 만들 수 있다.

예시:

```text
좋은 Hook 구조 후보
실패한 Hook 구조 후보
Story에서 반복된 Risk 유형
Voice 읽기 좋은 문장 패턴
Retention 가능성이 높은 전환 구조
```

Memory 확정은 Memory Engine 또는 Learning Engine이 담당한다.

---

# 29. Error Types

Story Engine의 Error Type:

```text
StoryInputMissingError
KnowledgeValidationError
HookCreationError
WeakHookError
OutlineCreationError
ScriptCreationError
ForbiddenClaimUsedError
SpeculativeClaimFramingError
BrandToneMismatchError
RetentionFlowError
StoryReviewError
StoryValidationError
StoryHandoffError
```

Error 예시:

```json
{
  "error_type": "WeakHookError",
  "message": "Hook does not create sufficient curiosity in the first 30 seconds.",
  "project_id": "20260710-093500-future-million-year-human",
  "stage": "STORY",
  "severity": "HIGH",
  "suggested_fix": "Rewrite the first 30 seconds using a stronger cinematic scenario or unanswered question.",
  "created_at": "2026-07-10T11:00:00"
}
```

---

# 30. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
StoryEngine
StoryInputLoader
StoryInputValidator
StoryAngleBuilder
StoryAngleSelector
HookBuilder
HookScorer
OutlineBuilder
ActStructureBuilder
ScriptMasterBuilder
LanguageScriptBuilder
RetentionFlowChecker
EmotionalArcBuilder
FactualSafetyChecker
BrandStoryChecker
StoryReviewBuilder
StoryValidator
StoryHandoffBuilder
StoryErrorReporter
```

---

# 31. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/19_STORY_ENGINE.md
→ engines/story/
```

예시 구조:

```text
engines/
└── story/
    ├── story_engine.py
    ├── story_input_loader.py
    ├── story_input_validator.py
    ├── story_angle_builder.py
    ├── story_angle_selector.py
    ├── hook_builder.py
    ├── hook_scorer.py
    ├── outline_builder.py
    ├── act_structure_builder.py
    ├── script_master_builder.py
    ├── language_script_builder.py
    ├── retention_flow_checker.py
    ├── emotional_arc_builder.py
    ├── factual_safety_checker.py
    ├── brand_story_checker.py
    ├── story_review_builder.py
    ├── story_validator.py
    ├── story_handoff_builder.py
    └── story_error_reporter.py
```

---

# 32. Main Public Operations

Story Engine은 최소 다음 작업을 제공해야 한다.

```text
run_story(project_id)
load_story_inputs(project_id)
validate_story_inputs(project_id)
build_story_angles(project_id)
select_story_angle(project_id)
build_hook_options(project_id)
score_hook_options(project_id)
select_hook(project_id)
build_outline(project_id)
build_master_script(project_id)
build_language_scripts(project_id)
check_factual_safety(project_id)
check_brand_fit(project_id)
check_retention_flow(project_id)
build_story_review(project_id)
validate_story_outputs(project_id)
build_handoff_to_direction(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
Knowledge Claim 준수
Forbidden Claim 회피
Speculative Claim Framing
Brand Tone 유지
Retention Flow 확인
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 33. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Knowledge Output 로드
Story 입력 검증
Story Angle 생성
Hook 생성
Outline 생성
Master Script 생성
script_master.json 생성
script_master.md 생성
story_review.json 생성
Forbidden Claim 검사
Speculative Claim Framing 검사
Brand Tone 기본 검사
Story Validation 수행
Direction Engine Handoff 생성
```

v1.0에서 하지 않아도 되는 것:

```text
완전 자동 고급 작가 시스템
실시간 대본 편집 UI
다중 작가 협업 UI
대규모 A/B Hook 자동 테스트
YouTube 성과 기반 실시간 대본 수정
Provider 직접 호출
```

v1.0에서는 Direction과 Timeline이 사용할 수 있는 강한 Story 구조와 대본을 안정적으로 만드는 것이 우선이다.

---

# 34. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Knowledge Output을 로드할 수 있다.
Story 입력을 검증할 수 있다.
Story Angle을 만들 수 있다.
Hook 후보를 만들 수 있다.
Hook을 선택할 수 있다.
Outline을 만들 수 있다.
Master Script를 만들 수 있다.
script_master.json을 생성할 수 있다.
script_master.md를 생성할 수 있다.
Forbidden Claim 사용을 감지할 수 있다.
Speculative Claim이 조심스럽게 표현되었는지 확인할 수 있다.
Brand Tone을 기본 검사할 수 있다.
Retention Flow를 기본 검사할 수 있다.
story_review.json을 생성할 수 있다.
Direction Engine으로 넘길 Handoff를 생성할 수 있다.
Story Validation 실패 시 DIRECTION Stage 진행을 막을 수 있다.
```

---

# 35. Non Goals

v1.0에서 Story Engine이 하지 않는 것:

```text
Research 직접 수행
Claim 새로 검증 없이 추가
Scene Direction 최종 작성
Timeline 생성
Visual Prompt 작성
Voice 파일 생성
Subtitle 생성
Provider 직접 호출
Quality Score 최종 계산
Template 직접 수정
```

v1.0에서는 Knowledge를 기반으로 강한 Hook, Outline, Master Script를 만드는 것이 핵심이다.

---

# 36. Critical Story Rules

반드시 지켜야 할 규칙:

```text
1. Story Engine은 Knowledge 없이 대본을 작성하지 않는다.

2. Story Engine은 Research를 직접 대체하지 않는다.

3. 첫 10초 Hook은 강해야 한다.

4. 첫 30초 안에 핵심 질문이 있어야 한다.

5. Generic Introduction을 사용하지 않는다.

6. Forbidden Claim을 사용하지 않는다.

7. Unsupported Claim을 사용하지 않는다.

8. Speculative Claim은 가능성으로 표현한다.

9. Brand Tone을 유지한다.

10. 정보 나열식 대본을 피한다.

11. Direction Engine이 Scene으로 만들 수 있어야 한다.

12. Voice로 읽기 쉬운 문장이어야 한다.

13. Story Validation 실패 시 DIRECTION Stage로 넘어가지 않는다.

14. Story Engine은 Provider를 직접 호출하지 않는다.

15. 중요한 Story 판단은 Self Review와 Handoff에 기록한다.
```

---

# 37. Final Principle

Story Engine은 ADOS 콘텐츠의 심장이다.

Research는 재료를 모으고,

Knowledge는 재료를 정리하고,

Story는 그 재료를 시청자가 끝까지 보고 싶은 이야기로 만든다.

좋은 Story는 정보를 나열하지 않는다.

좋은 Story는 질문을 만들고,

긴장을 만들고,

장면을 만들고,

감정을 만들고,

마지막까지 보게 만든다.

Story Engine의 목적은 단순한 대본 작성이 아니라, Channel을 성장시킬 수 있는 이야기 구조를 만드는 것이다.
