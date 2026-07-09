# 18_KNOWLEDGE_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Knowledge Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Knowledge Engine을 정의한다.

Knowledge Engine은 Research Engine이 수집한 자료, 출처, 사실, 위험 요소를 Story Engine이 사용할 수 있는 구조화된 지식으로 변환하는 엔진이다.

Research Engine이 자료를 모은다면, Knowledge Engine은 그 자료를 영상 제작에 사용할 수 있는 Claim, Context, Evidence, Risk, Story Material로 정리한다.

Knowledge Engine은 다음을 담당한다.

```text
Research Output 로드
Source와 Fact 검증
Fact / Interpretation / Speculation 구분
Claim 후보 생성
Claim과 Source 연결
Claim 신뢰도 평가
Context 정리
Risk 정리
Story Material 추출
Visualizable Idea 정리
Fact Check 결과 생성
Knowledge Report 생성
Story Engine에 전달할 Handoff 생성
```

이 문서는 다음 문서들과 직접 연결된다.

```text
06_AI_THINKING_FRAMEWORK.md
07_PROJECT_SPEC.md
12_PROJECT_ENGINE.md
13_MEMORY_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
17_RESEARCH_ENGINE.md
19_STORY_ENGINE.md
20_DIRECTION_ENGINE.md
26_QUALITY_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Knowledge Engine은 Research 자료를 영상 제작 가능한 지식 구조로 바꾸는 엔진이다.

전체 흐름:

```text
Research
↓
Sources
↓
Facts
↓
Evidence Classification
↓
Claims
↓
Context
↓
Risk Notes
↓
Story Materials
↓
Knowledge Package
↓
Story Engine
```

Knowledge Engine의 핵심 목표는 다음이다.

```text
Story Engine이 사용할 수 있는 Claim 정리
검증 가능한 Fact와 추측 분리
Claim마다 Source 연결
위험한 Claim 사전 표시
영상 구조에 쓸 수 있는 지식 패키지 생성
Quality Engine이 검토할 수 있는 Fact Check 기반 생성
```

---

# 3. Knowledge Philosophy

## 3.1 Knowledge Is Not Raw Research

Knowledge는 자료 더미가 아니다.

Knowledge는 Story, Direction, Quality가 사용할 수 있도록 정리된 제작용 지식이다.

나쁜 Knowledge:

```text
미래 인간은 달라질 수 있다.
AI가 인간을 바꿀 수 있다.
우주는 인간 진화에 영향을 줄 수 있다.
```

좋은 Knowledge:

```text
Claim:
장기적인 인간 진화는 자연선택뿐 아니라 기술, 환경, 사회 구조의 영향을 받을 수 있다.

Evidence:
Research Fact FACT-000001, FACT-000004

Evidence Level:
MEDIUM

Risk:
100만 년 뒤의 구체적 모습은 확정할 수 없으므로 시나리오로 표현해야 한다.

Story Use:
중반부에서 "미래 인간을 바꾸는 힘은 자연이 아니라 기술일 수 있다"는 전환점으로 사용.
```

## 3.2 Claims Must Be Traceable

모든 중요한 Claim은 Source 또는 Fact와 연결되어야 한다.

Source 없는 강한 Claim은 Story Engine에 전달하지 않는다.

## 3.3 Separate Usable Story Material from Verified Fact

Story에 강하게 사용할 수 있는 소재라도 사실처럼 말하면 안 되는 경우가 있다.

Knowledge Engine은 다음을 구분한다.

```text
verified_fact
supported_context
reasonable_interpretation
speculative_scenario
unsafe_claim
```

## 3.4 Knowledge Must Protect Quality

Knowledge Engine은 Story가 과장되거나 사실 오류를 만들지 않도록 사전 방어선을 만든다.

---

# 4. Knowledge Engine Responsibilities

Knowledge Engine의 책임:

```text
Research Output 로드
Research Output 검증
Source 신뢰도 확인
Fact와 Source 연결 확인
Claim 후보 생성
Claim Type 분류
Evidence Level 분류
Claim Risk 분류
Fact Check Report 생성
Story Material 생성
Visualizable Knowledge 생성
Forbidden Claim 목록 생성
Knowledge Summary 생성
Knowledge Output 저장
Self Review 생성
Story Engine Handoff 생성
```

Knowledge Engine이 하지 않는 것:

```text
대본을 작성하지 않는다.
Hook 문장을 최종 작성하지 않는다.
Scene Direction을 만들지 않는다.
Visual Prompt를 만들지 않는다.
Quality Score를 최종 계산하지 않는다.
Provider를 직접 호출하지 않는다.
Template을 직접 수정하지 않는다.
```

---

# 5. Inputs

Knowledge Engine의 입력:

```text
project.json
topic.json
channel_snapshot.json
template_snapshot.json
research/research.json
research/sources.json
research/facts.json
research/risk_notes.json
research/competitors.json
research/trend.json
research/audience_questions.json
workflow/memory_context_KNOWLEDGE.json
```

필수 입력:

```text
research/research.json
research/sources.json
research/facts.json
research/risk_notes.json
project.json
channel_snapshot.json
```

선택 입력:

```text
research/competitors.json
research/trend.json
research/audience_questions.json
Channel Memory
Template Memory
Quality Memory
Growth Memory
```

---

# 6. Outputs

Knowledge Engine의 출력:

```text
knowledge/knowledge.json
knowledge/claims.json
knowledge/fact_check.json
knowledge/risk_notes.json
knowledge/story_materials.json
knowledge/visualizable_ideas.json
workflow/stage_results/KNOWLEDGE_result.json
workflow/handoffs/KNOWLEDGE_to_STORY.json
```

v1.0 최소 출력:

```text
knowledge/knowledge.json
knowledge/claims.json
knowledge/fact_check.json
knowledge/risk_notes.json
```

Story Engine은 최소 다음 파일을 입력으로 사용한다.

```text
knowledge/knowledge.json
knowledge/claims.json
knowledge/fact_check.json
knowledge/risk_notes.json
```

---

# 7. Knowledge Creation Flow

Knowledge Engine 실행 흐름:

```text
Load Project Context
↓
Load Research Outputs
↓
Validate Research Files
↓
Check Source-Fact Links
↓
Classify Facts
↓
Build Claim Candidates
↓
Classify Claim Types
↓
Assign Evidence Levels
↓
Detect Risky Claims
↓
Build Fact Check Report
↓
Build Story Materials
↓
Build Visualizable Ideas
↓
Write knowledge.json
↓
Write claims.json
↓
Write fact_check.json
↓
Write risk_notes.json
↓
Self Review
↓
Handoff to Story Engine
```

---

# 8. Knowledge Types

Knowledge Engine은 지식을 다음 유형으로 분류한다.

```text
verified_fact
supported_context
reasonable_interpretation
speculative_scenario
audience_question
visualizable_idea
story_opportunity
risk_note
forbidden_claim
```

## 8.1 verified_fact

Source와 연결된 검증 가능한 사실.

## 8.2 supported_context

사실을 이해하기 위한 배경 지식.

## 8.3 reasonable_interpretation

근거를 바탕으로 한 해석.

## 8.4 speculative_scenario

미래, 가능성, 가정 기반 시나리오.

## 8.5 audience_question

시청자가 궁금해할 질문.

## 8.6 visualizable_idea

영상 장면으로 만들 수 있는 아이디어.

## 8.7 story_opportunity

Hook, 전환점, 엔딩 등에 사용할 수 있는 소재.

## 8.8 risk_note

사실 오류, 과장, 오해 가능성.

## 8.9 forbidden_claim

대본에 사용하면 안 되는 주장.

---

# 9. Claim Types

Claim은 다음 유형 중 하나로 분류한다.

```text
FACTUAL
CONTEXTUAL
INTERPRETIVE
SPECULATIVE
COMPARATIVE
CAUSAL
RISKY
FORBIDDEN
```

## FACTUAL

검증 가능한 사실.

## CONTEXTUAL

이해를 돕는 배경 설명.

## INTERPRETIVE

사실을 바탕으로 한 해석.

## SPECULATIVE

미래 예측 또는 가능성.

## COMPARATIVE

두 대상의 비교.

## CAUSAL

원인과 결과를 설명하는 주장.

## RISKY

잘못 표현하면 오해나 오류가 생길 수 있는 주장.

## FORBIDDEN

사용하면 안 되는 주장.

---

# 10. Evidence Levels

Claim의 Evidence Level은 다음을 사용한다.

```text
HIGH
Source와 Fact가 강하게 뒷받침함

MEDIUM
근거가 있으나 표현 주의 필요

LOW
약한 근거. 대본에서 강하게 말하면 안 됨

SPECULATIVE
가능성 또는 시나리오. 반드시 불확실성 표시 필요

UNSUPPORTED
근거 없음. 사용 금지
```

규칙:

```text
HIGH / MEDIUM Claim만 핵심 설명에 사용한다.
LOW Claim은 보조 설명 또는 질문 형태로만 사용한다.
SPECULATIVE Claim은 반드시 가능성으로 표현한다.
UNSUPPORTED Claim은 Story Engine에 사용 금지로 전달한다.
```

---

# 11. claims.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "KNOWLEDGE",

  "claims": [
    {
      "claim_id": "CLM-000001",
      "claim": "Long-term human evolution may be shaped not only by natural selection, but also by technology and future environments.",
      "claim_type": "INTERPRETIVE",
      "evidence_level": "MEDIUM",

      "source_fact_ids": [
        "FACT-000001",
        "FACT-000004"
      ],

      "source_ids": [
        "SRC-000001"
      ],

      "story_use": {
        "recommended": true,
        "use_as": "turning_point",
        "notes": "Use as a transition from biological evolution to technology-driven future change."
      },

      "risk": {
        "level": "MEDIUM",
        "reason": "Future impact of technology cannot be stated as certainty.",
        "required_framing": "may, could, possible scenario"
      },

      "allowed_language": [
        "could",
        "may",
        "one possible future",
        "scientists cannot know for certain"
      ],

      "forbidden_language": [
        "will definitely",
        "certainly",
        "guaranteed"
      ]
    }
  ],

  "forbidden_claims": [
    {
      "claim": "Humans will definitely evolve into a specific body shape in one million years.",
      "reason": "Unsupported certainty about long-term future evolution."
    }
  ]
}
```

---

# 12. knowledge.json Schema

`knowledge/knowledge.json`은 Knowledge 결과의 중심 요약 파일이다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "KNOWLEDGE",

  "topic": {
    "title": "100만 년 후 인간은 어떤 모습일까?",
    "category": "future"
  },

  "knowledge_summary": {
    "core_message": "The future of humanity cannot be predicted with certainty, but biology, technology, and environment could all shape what humans become.",
    "main_knowledge_points": [
      "Long-term evolution is uncertain.",
      "Natural selection depends on environmental pressures.",
      "Technology may change the direction of human change.",
      "Space settlement could create new adaptation pressures."
    ],
    "main_risks": [
      "Avoid presenting speculative future scenarios as confirmed facts.",
      "Avoid unsupported body-shape predictions."
    ]
  },

  "story_direction_suggestions": {
    "best_hook_angle": "A cinematic future scenario showing a human born far from Earth.",
    "recommended_structure": [
      "Start with a future scenario",
      "Explain why prediction is uncertain",
      "Show forces that could shape future humans",
      "End with a philosophical question"
    ],
    "emotional_direction": [
      "curiosity",
      "awe",
      "reflection"
    ]
  },

  "visualizable_ideas": [
    {
      "idea_id": "VIS-KNW-000001",
      "summary": "A future human colony under alien sunlight.",
      "story_use": "opening hook",
      "risk": "Do not present as actual prediction."
    }
  ]
}
```

---

# 13. fact_check.json Schema

`knowledge/fact_check.json`은 Story와 Quality가 사실 검토에 사용할 기준 파일이다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "fact_check_summary": {
    "total_claims": 12,
    "high_evidence_claims": 4,
    "medium_evidence_claims": 5,
    "low_evidence_claims": 1,
    "speculative_claims": 2,
    "unsupported_claims": 0
  },

  "claim_checks": [
    {
      "claim_id": "CLM-000001",
      "status": "PASS_WITH_CAUTION",
      "evidence_level": "MEDIUM",
      "source_ids": [
        "SRC-000001"
      ],
      "risk_level": "MEDIUM",
      "required_framing": "Must be presented as possibility, not certainty."
    }
  ],

  "quality_notes": [
    "Quality Engine should check that speculative claims are not stated as facts."
  ]
}
```

---

# 14. risk_notes.json Schema

`knowledge/risk_notes.json`은 Research Risk를 Story 작성용으로 더 구체화한 파일이다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "risks": [
    {
      "risk_id": "KNW-RISK-000001",
      "risk_type": "SPECULATION_AS_FACT",
      "severity": "HIGH",
      "description": "Future human appearance predictions must not be stated as confirmed facts.",
      "affected_claim_ids": [
        "CLM-000003",
        "CLM-000004"
      ],
      "story_instruction": "Use phrases like 'one possible future' or 'could happen under certain conditions'.",
      "quality_check_required": true
    }
  ],

  "forbidden_patterns": [
    "인류는 반드시 이렇게 변한다",
    "과학자들은 이미 확정했다",
    "100만 년 뒤 인간은 무조건 이런 모습이다"
  ]
}
```

---

# 15. story_materials.json Schema

Story Engine이 사용할 수 있는 소재를 정리한다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",

  "hook_materials": [
    {
      "material_id": "HOOK-MAT-000001",
      "summary": "A child born under an alien sun may not look like Earth-born humans.",
      "evidence_level": "SPECULATIVE",
      "use_rule": "Use as cinematic scenario, not fact.",
      "emotional_value": "curiosity"
    }
  ],

  "turning_points": [
    {
      "material_id": "TURN-000001",
      "summary": "The future of human evolution may be driven more by technology than nature.",
      "evidence_level": "MEDIUM",
      "use_rule": "Use after explaining natural selection."
    }
  ],

  "ending_materials": [
    {
      "material_id": "END-000001",
      "summary": "The biggest question may not be what humans become, but who decides what humans become.",
      "evidence_level": "INTERPRETIVE",
      "use_rule": "Use as philosophical ending."
    }
  ]
}
```

---

# 16. visualizable_ideas.json Schema

Direction과 Visual Engine이 참고할 수 있는 지식 기반 장면 아이디어를 정리한다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",

  "ideas": [
    {
      "idea_id": "VIDEA-000001",
      "summary": "A future human settlement on a low-gravity planet.",
      "related_claim_ids": [
        "CLM-000004"
      ],
      "visual_potential": "HIGH",
      "risk_level": "MEDIUM",
      "visual_instruction": "Show as speculative future simulation, not confirmed future reality."
    }
  ]
}
```

---

# 17. Claim Validation Rules

Knowledge Engine은 Claim을 검증해야 한다.

검증 항목:

```text
claim_id 존재
claim 내용 존재
claim_type 유효
evidence_level 유효
source_fact_ids 존재 또는 risk 표시
source_ids 존재 또는 speculative 표시
UNSUPPORTED Claim이 핵심 Claim에 포함되지 않았는지 확인
SPECULATIVE Claim에 required_framing 존재
RISKY Claim에 mitigation 존재
FORBIDDEN Claim이 story_materials에 포함되지 않았는지 확인
```

검증 실패 시 STORY Stage로 넘어갈 수 없다.

---

# 18. Source-Fact-Claim Mapping

Knowledge Engine은 Source, Fact, Claim의 연결을 유지해야 한다.

구조:

```text
Source
↓
Fact
↓
Claim
↓
Story Material
```

예시:

```json
{
  "mapping": [
    {
      "source_id": "SRC-000001",
      "fact_id": "FACT-000001",
      "claim_id": "CLM-000001",
      "story_material_id": "TURN-000001"
    }
  ]
}
```

이 연결은 Quality Engine이 사실 검토를 할 때 사용한다.

---

# 19. Risk Handling

Knowledge Engine은 위험한 Claim을 다음 중 하나로 처리한다.

```text
allow_with_framing
use_as_question
use_as_speculation
send_to_quality_review
forbid
```

예시:

```text
Claim:
미래 인간은 화성에서 더 키가 커질 수 있다.

처리:
use_as_speculation

표현:
낮은 중력 환경이 오래 지속된다면, 인간의 몸은 지금과 다른 압력을 받을 수 있다.
```

금지 처리 예시:

```text
Claim:
100만 년 뒤 인간은 반드시 키가 3미터가 된다.

처리:
forbid
```

---

# 20. Knowledge Quality Rules

좋은 Knowledge의 조건:

```text
Claim이 명확하다.
Claim과 Source가 연결되어 있다.
Fact와 Speculation이 구분되어 있다.
Risk가 표시되어 있다.
Story Engine이 바로 사용할 수 있다.
Visualizable Idea가 있다.
Quality Engine이 검토할 수 있다.
금지 Claim이 분리되어 있다.
```

나쁜 Knowledge:

```text
Research 문장을 그대로 복사
Source 없는 Claim
Speculation을 Fact로 정리
위험한 Claim을 표시하지 않음
Story에 사용할 수 없는 일반론
Fact Check 파일 누락
Forbidden Claim 누락
```

---

# 21. Knowledge Validation Rules

Knowledge Validator는 다음을 확인해야 한다.

```text
knowledge/knowledge.json 존재
knowledge/claims.json 존재
knowledge/fact_check.json 존재
knowledge/risk_notes.json 존재
project_id 일치
channel_id 일치
claims 배열 존재
claim_id 중복 없음
claim_type 유효
evidence_level 유효
중요 Claim에 source 연결 존재
SPECULATIVE Claim에 required_framing 존재
UNSUPPORTED Claim이 사용 가능 Claim에 포함되지 않음
forbidden_claims 존재
fact_check_summary 존재
```

검증 실패 시 STORY Stage로 이동할 수 없다.

---

# 22. Self Review

Knowledge Engine은 결과 제출 전 Self Review를 생성한다.

Self Review 항목:

```text
필수 파일 생성 여부
Research Output 사용 여부
Source-Fact-Claim 연결 여부
Fact와 Speculation 구분 여부
Risk Note 생성 여부
Forbidden Claim 분리 여부
Story Engine 사용 가능성
Quality Engine 검토 가능성
```

Self Review는 다음 위치에 기록한다.

```text
logs/self_reviews.jsonl
```

---

# 23. Handoff to Story Engine

Knowledge Engine은 Story Engine에 Handoff를 생성해야 한다.

Handoff 파일:

```text
workflow/handoffs/KNOWLEDGE_to_STORY.json
```

Handoff에 포함할 내용:

```text
Core Message
Main Claims
High Confidence Claims
Speculative Claims
Forbidden Claims
Required Framing
Hook Materials
Turning Points
Ending Materials
Visualizable Ideas
Quality Notes
Risk Notes
```

Handoff 예시:

```json
{
  "from_stage": "KNOWLEDGE",
  "to_stage": "STORY",
  "project_id": "20260710-093500-future-million-year-human",
  "summary": "Knowledge package prepared with speculative future claims clearly separated.",
  "must_follow": [
    "Do not present future scenarios as facts.",
    "Use cautious language for long-term predictions."
  ],
  "recommended_story_angle": "Start with a cinematic future scenario, then explain uncertainty.",
  "required_inputs_for_story": [
    "knowledge/knowledge.json",
    "knowledge/claims.json",
    "knowledge/fact_check.json",
    "knowledge/risk_notes.json"
  ]
}
```

---

# 24. Memory Integration

Knowledge Engine은 작업 전 Memory Context를 사용할 수 있다.

사용 가능한 Memory:

```text
Factuality Risk Memory
Successful Claim Pattern
Failed Claim Pattern
Channel Story Memory
Quality Failure Memory
Template Knowledge Pattern
```

Knowledge Engine은 작업 후 Memory Candidate를 만들 수 있다.

예시:

```text
반복적으로 위험한 Claim 유형 발견
특정 Channel에서 좋은 Core Message 구조 발견
특정 Template에서 자주 필요한 Fact Check 기준 발견
```

Memory 확정은 Memory Engine 또는 Learning Engine이 담당한다.

---

# 25. Error Types

Knowledge Engine의 Error Type:

```text
KnowledgeInputMissingError
ResearchOutputInvalidError
SourceFactMappingError
ClaimCreationError
ClaimValidationError
UnsupportedClaimError
SpeculationFramingMissingError
ForbiddenClaimError
FactCheckReportError
KnowledgeOutputValidationError
KnowledgeHandoffError
```

Error 예시:

```json
{
  "error_type": "SpeculationFramingMissingError",
  "message": "Speculative claim is missing required framing instructions.",
  "project_id": "20260710-093500-future-million-year-human",
  "claim_id": "CLM-000004",
  "stage": "KNOWLEDGE",
  "severity": "HIGH",
  "suggested_fix": "Add required_framing such as 'possible scenario' or 'could'.",
  "created_at": "2026-07-10T10:30:00"
}
```

---

# 26. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
KnowledgeEngine
ResearchOutputLoader
ResearchOutputValidator
SourceFactMapper
ClaimBuilder
ClaimValidator
ClaimEvidenceClassifier
ClaimRiskClassifier
FactCheckReportBuilder
KnowledgeSummaryBuilder
StoryMaterialBuilder
VisualizableIdeaBuilder
ForbiddenClaimDetector
KnowledgeReportBuilder
KnowledgeHandoffBuilder
KnowledgeErrorReporter
```

---

# 27. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/18_KNOWLEDGE_ENGINE.md
→ engines/knowledge/
```

예시 구조:

```text
engines/
└── knowledge/
    ├── knowledge_engine.py
    ├── research_output_loader.py
    ├── research_output_validator.py
    ├── source_fact_mapper.py
    ├── claim_builder.py
    ├── claim_validator.py
    ├── claim_evidence_classifier.py
    ├── claim_risk_classifier.py
    ├── fact_check_report_builder.py
    ├── knowledge_summary_builder.py
    ├── story_material_builder.py
    ├── visualizable_idea_builder.py
    ├── forbidden_claim_detector.py
    ├── knowledge_report_builder.py
    ├── knowledge_handoff_builder.py
    └── knowledge_error_reporter.py
```

---

# 28. Main Public Operations

Knowledge Engine은 최소 다음 작업을 제공해야 한다.

```text
run_knowledge(project_id)
load_research_outputs(project_id)
validate_research_outputs(project_id)
map_sources_to_facts(project_id)
build_claims(project_id)
classify_claim_evidence(project_id)
detect_claim_risks(project_id)
build_fact_check_report(project_id)
build_knowledge_summary(project_id)
build_story_materials(project_id)
build_visualizable_ideas(project_id)
detect_forbidden_claims(project_id)
validate_knowledge_outputs(project_id)
build_handoff_to_story(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
Source-Fact-Claim 연결 유지
Evidence Level 표시
Speculation 표시
Risk 표시
Forbidden Claim 분리
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 29. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Research Output 로드
Research Output 기본 검증
Source-Fact 연결 확인
Claim 구조 생성
Evidence Level 분류
Speculative Claim 표시
Forbidden Claim 분리
Fact Check Report 생성
knowledge.json 생성
claims.json 생성
fact_check.json 생성
risk_notes.json 생성
Knowledge Validation 수행
Story Engine Handoff 생성
```

v1.0에서 하지 않아도 되는 것:

```text
완전 자동 사실 검증 보장
논문 수준의 심층 지식 그래프 구축
복잡한 온톨로지 시스템
외부 Knowledge Base 연동
실시간 Source Revalidation
자동 법률/의학/금융 전문 검토 대체
```

v1.0에서는 Story와 Quality가 사용할 수 있는 구조화된 Knowledge Package를 안정적으로 만드는 것이 우선이다.

---

# 30. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Research Output을 로드할 수 있다.
Research Output을 검증할 수 있다.
Source와 Fact 연결을 확인할 수 있다.
Fact를 Claim으로 변환할 수 있다.
Claim Type을 분류할 수 있다.
Evidence Level을 표시할 수 있다.
Speculative Claim을 구분할 수 있다.
Unsupported Claim을 사용 금지 처리할 수 있다.
Forbidden Claim 목록을 만들 수 있다.
Fact Check Report를 생성할 수 있다.
knowledge.json을 생성할 수 있다.
claims.json을 생성할 수 있다.
fact_check.json을 생성할 수 있다.
risk_notes.json을 생성할 수 있다.
Story Engine으로 넘길 Handoff를 생성할 수 있다.
Knowledge Validation 실패 시 STORY Stage 진행을 막을 수 있다.
```

---

# 31. Non Goals

v1.0에서 Knowledge Engine이 하지 않는 것:

```text
대본 작성
Hook 문장 최종 작성
Scene Direction 작성
Visual Prompt 작성
Provider 직접 호출
Quality Score 최종 계산
Analytics 직접 분석
Template 직접 수정
```

v1.0에서는 Research를 Story가 사용할 수 있는 Claim / Context / Risk 구조로 변환하는 것이 핵심이다.

---

# 32. Critical Knowledge Rules

반드시 지켜야 할 규칙:

```text
1. Knowledge Engine은 Research를 그대로 복사하지 않는다.

2. Knowledge Engine은 Claim을 구조화한다.

3. 중요한 Claim은 Source 또는 Fact와 연결한다.

4. Fact와 Speculation을 구분한다.

5. Unsupported Claim은 Story Engine에 사용 가능 상태로 넘기지 않는다.

6. Speculative Claim은 required_framing을 가져야 한다.

7. Forbidden Claim은 명확히 분리한다.

8. Fact Check Report를 생성한다.

9. Risk Note 없이 위험한 Claim을 넘기지 않는다.

10. Knowledge Output은 Story Engine이 바로 사용할 수 있어야 한다.

11. Knowledge Validation 실패 시 STORY Stage로 넘어가지 않는다.

12. Knowledge Engine은 대본을 작성하지 않는다.

13. Knowledge Engine은 Provider를 직접 호출하지 않는다.

14. 중요한 판단은 Self Review와 Handoff에 기록한다.
```

---

# 33. Final Principle

Knowledge Engine은 Research와 Story 사이의 품질 필터이다.

Research는 자료를 모으고,

Knowledge는 그 자료를 Claim, Context, Risk로 정리하고,

Story는 그 지식을 시청자가 끝까지 보고 싶은 이야기로 만든다.

Knowledge Engine의 목적은 똑똑해 보이는 정보를 많이 만드는 것이 아니다.

Knowledge Engine의 목적은 정확하고, 추적 가능하고, Story에 쓸 수 있고, 위험이 표시된 지식 패키지를 만드는 것이다.
