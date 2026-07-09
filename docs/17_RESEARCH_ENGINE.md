# 17_RESEARCH_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Research Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Research Engine을 정의한다.

Research Engine은 Project의 주제에 대해 영상 제작에 필요한 기초 정보, 사실, 출처, 맥락, 경쟁 콘텐츠, 트렌드, 위험 요소를 수집하고 정리하는 엔진이다.

Research Engine의 결과가 약하면 이후 모든 단계가 약해진다.

```text
Research가 약하면
→ Knowledge가 부정확해지고
→ Story가 얕아지고
→ Visual Direction이 흔들리고
→ Factuality Risk가 커지고
→ Quality Fail 가능성이 높아진다.
```

Research Engine은 다음을 담당한다.

```text
Project Topic 분석
Research 질문 생성
Source 수집
Source 신뢰도 평가
Fact 수집
Claim 후보 수집
Trend 정보 수집
Competitor 콘텐츠 분석
Audience 관심 포인트 수집
Risk Note 생성
Uncertainty 표시
Research Report 생성
Knowledge Engine에 전달할 Handoff 생성
```

이 문서는 다음 문서들과 직접 연결된다.

```text
06_AI_THINKING_FRAMEWORK.md
07_PROJECT_SPEC.md
12_PROJECT_ENGINE.md
13_MEMORY_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
18_KNOWLEDGE_ENGINE.md
19_STORY_ENGINE.md
26_QUALITY_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Research Engine은 Project의 주제를 영상 제작에 사용할 수 있는 근거 기반 자료로 바꾸는 엔진이다.

전체 흐름:

```text
Topic
↓
Research Questions
↓
Sources
↓
Facts
↓
Context
↓
Risks
↓
Research Report
↓
Knowledge Engine
```

Research Engine의 핵심 목표는 다음이다.

```text
정확한 정보 확보
출처가 있는 정보 확보
Story에 사용할 수 있는 정보 확보
위험한 주장 사전 감지
시청자가 궁금해할 맥락 확보
경쟁 콘텐츠와 차별점 확보
```

---

# 3. Research Philosophy

## 3.1 Evidence First

Research Engine은 근거 없는 내용을 만들지 않는다.

모든 중요한 사실, 수치, 역사적 사건, 과학적 설명, 최신 정보는 Source와 연결되어야 한다.

## 3.2 Separate Fact, Interpretation, and Speculation

Research Engine은 다음을 구분해야 한다.

```text
Fact
검증 가능한 사실

Interpretation
사실을 바탕으로 한 해석

Speculation
가능성 또는 미래 예측

Opinion
특정 사람이나 집단의 의견
```

특히 미래, 과학, 건강, 금융, 법률, 역사 논쟁 주제는 불확실성을 명확히 표시한다.

## 3.3 Research Is Not Story Writing

Research Engine은 대본을 쓰지 않는다.

Research Engine은 Story Engine이 좋은 대본을 쓸 수 있도록 재료를 준비한다.

## 3.4 Research Must Be Useful for Video

Research는 논문 요약만 하는 것이 아니다.

영상 제작에 필요한 다음 요소를 찾아야 한다.

```text
강한 Hook 소재
시청자가 궁금해할 질문
시각화 가능한 장면
놀라운 사실
감정적 전환점
논쟁점
주의해야 할 과장 위험
```

---

# 4. Research Engine Responsibilities

Research Engine의 책임:

```text
Topic 분석
Research Scope 정의
Research Question 생성
Source 수집
Source 신뢰도 평가
Fact 수집
Fact와 Source 연결
Trend 정보 수집
Competitor 콘텐츠 분석
Audience Interest 분석
Visualizable Ideas 수집
Risk Note 생성
Uncertainty 표시
Research Output 저장
Self Review 생성
Knowledge Engine Handoff 생성
```

Research Engine이 하지 않는 것:

```text
최종 Claim을 확정하지 않는다.
대본을 작성하지 않는다.
Scene Direction을 만들지 않는다.
Visual Prompt를 만들지 않는다.
Quality Score를 최종 계산하지 않는다.
Provider를 직접 호출하지 않는다.
```

최종 Claim 정리는 Knowledge Engine이 담당한다.

---

# 5. Inputs

Research Engine의 입력:

```text
project.json
topic.json
channel_snapshot.json
template_snapshot.json
channels/{channel_id}/brand.yaml
channels/{channel_id}/growth.yaml
channels/{channel_id}/memory.yaml
workflow/memory_context_RESEARCH.json
```

필수 입력:

```text
project.json
topic.json
channel_snapshot.json
template_snapshot.json
```

선택 입력:

```text
Channel Memory
Template Memory
Growth Memory
Previous Research Patterns
User-provided source list
Manual research notes
```

---

# 6. Outputs

Research Engine의 출력:

```text
research/research.json
research/sources.json
research/facts.json
research/competitors.json
research/trend.json
research/audience_questions.json
research/risk_notes.json
workflow/stage_results/RESEARCH_result.json
```

v1.0 최소 출력:

```text
research/research.json
research/sources.json
research/facts.json
research/risk_notes.json
```

Knowledge Engine은 최소 다음 파일을 입력으로 사용한다.

```text
research/research.json
research/sources.json
research/facts.json
research/risk_notes.json
```

---

# 7. Research Creation Flow

Research Engine 실행 흐름:

```text
Load Project Context
↓
Load Topic
↓
Load Channel / Template Rules
↓
Load Memory Context
↓
Define Research Scope
↓
Create Research Questions
↓
Collect Sources
↓
Evaluate Sources
↓
Extract Facts
↓
Classify Evidence Level
↓
Collect Competitor / Trend Data
↓
Identify Audience Questions
↓
Identify Risks and Uncertainties
↓
Write research.json
↓
Write sources.json
↓
Write facts.json
↓
Write risk_notes.json
↓
Self Review
↓
Handoff to Knowledge Engine
```

---

# 8. Research Scope

Research Scope는 주제의 조사 범위를 정의한다.

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "topic": "100만 년 후 인간은 어떤 모습일까?",

  "research_scope": {
    "main_question": "What could humans look like one million years in the future?",
    "sub_questions": [
      "What drives human evolution?",
      "How could technology affect human biology?",
      "How could space migration change human bodies?",
      "Which claims are speculative and must be framed carefully?"
    ],
    "must_cover": [
      "evolutionary pressure",
      "genetic engineering",
      "AI and cybernetics",
      "space adaptation",
      "uncertainty of long-term prediction"
    ],
    "must_avoid": [
      "presenting speculation as fact",
      "unsupported scientific certainty",
      "cheap sensational claims"
    ]
  }
}
```

---

# 9. Research Question Types

Research Engine은 다음 유형의 질문을 생성할 수 있다.

```text
Core Question
영상의 중심 질문

Fact Question
검증 가능한 사실을 찾기 위한 질문

Context Question
배경과 맥락을 이해하기 위한 질문

Visual Question
시각화 가능한 장면을 찾기 위한 질문

Risk Question
오류, 과장, 논란을 방지하기 위한 질문

Audience Question
시청자가 실제로 궁금해할 질문

Growth Question
CTR, Retention, Topic Appeal과 연결되는 질문
```

예시:

```json
{
  "questions": [
    {
      "type": "core",
      "question": "What could humans look like one million years from now?"
    },
    {
      "type": "risk",
      "question": "Which parts of this topic are speculative and should not be stated as fact?"
    },
    {
      "type": "visual",
      "question": "Which future scenarios can be visualized cinematically?"
    }
  ]
}
```

---

# 10. Source Policy

Research Engine은 Source를 구조화해서 관리해야 한다.

Source 종류:

```text
academic
official
government
institution
news
book
documentary
expert_interview
industry_report
competitor_video
manual_note
unknown
```

Source 신뢰도:

```text
HIGH
공식 기관, 논문, 정부/연구기관, 검증된 1차 자료

MEDIUM
신뢰할 만한 언론, 전문 매체, 전문가 인터뷰, 잘 알려진 기관 보고서

LOW
출처가 약한 블로그, 커뮤니티, 불명확한 요약 자료

UNKNOWN
검증 불가
```

규칙:

```text
중요한 Fact는 Source와 연결한다.
LOW Source는 단독 근거로 사용하지 않는다.
UNKNOWN Source는 Claim 근거로 사용하지 않는다.
최신성이 중요한 주제는 retrieved_at을 기록한다.
논쟁적 주제는 반대 관점도 기록한다.
```

---

# 11. sources.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "sources": [
    {
      "source_id": "SRC-000001",
      "title": "Example scientific source title",
      "source_type": "academic",
      "url": "",
      "author": "",
      "publisher": "",
      "published_at": "",
      "retrieved_at": "2026-07-10T10:00:00",

      "reliability": "HIGH",
      "relevance": "HIGH",

      "used_for": [
        "evolutionary pressure",
        "human adaptation"
      ],

      "notes": "Use for general evolutionary principles, not specific million-year predictions."
    }
  ]
}
```

---

# 12. facts.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "facts": [
    {
      "fact_id": "FACT-000001",
      "summary": "Human evolution is influenced by selection pressures, mutation, genetic drift, and gene flow.",
      "fact_type": "scientific_context",
      "evidence_level": "HIGH",

      "source_ids": [
        "SRC-000001"
      ],

      "use_in_video": true,
      "visual_potential": "MEDIUM",
      "story_potential": "HIGH",

      "risk": {
        "level": "LOW",
        "notes": []
      }
    }
  ]
}
```

---

# 13. research.json Schema

`research/research.json`은 Research 결과의 중심 요약 파일이다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "RESEARCH",

  "topic": {
    "title": "100만 년 후 인간은 어떤 모습일까?",
    "category": "future"
  },

  "summary": {
    "main_findings": [
      "Long-term human evolution is highly uncertain.",
      "Technology may become a stronger driver than natural selection.",
      "Space settlement could create different adaptation pressures."
    ],

    "best_hook_materials": [
      "A future human born on a distant planet may not look like us.",
      "The biggest force shaping future humans may not be nature, but technology."
    ],

    "visualizable_ideas": [
      "A human colony under alien sunlight.",
      "A future body adapted to low gravity.",
      "A city where biology and machine are merged."
    ],

    "important_uncertainties": [
      "One-million-year predictions cannot be stated as fact.",
      "Technological development path is unknown."
    ]
  },

  "research_questions": [
    {
      "type": "core",
      "question": "What could humans look like one million years from now?",
      "status": "answered_with_uncertainty"
    }
  ],

  "handoff_notes": {
    "for_knowledge_engine": [
      "Separate facts from speculative scenarios.",
      "Use cautious language for future predictions."
    ],
    "for_story_engine": [
      "The strongest hook is a cinematic future scenario, not a generic explanation."
    ]
  }
}
```

---

# 14. risk_notes.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "risks": [
    {
      "risk_id": "RISK-RESEARCH-000001",
      "risk_type": "SPECULATION_RISK",
      "severity": "HIGH",
      "description": "Predictions about humans one million years in the future cannot be treated as confirmed facts.",
      "affected_topics": [
        "future body shape",
        "space adaptation",
        "AI-driven evolution"
      ],
      "mitigation": "Frame future scenarios as possibilities and clearly distinguish them from established science.",
      "must_pass_to_quality": true
    }
  ]
}
```

---

# 15. competitors.json Schema

Competitor 분석은 선택 출력이지만 Growth와 Story에 도움이 된다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",

  "competitors": [
    {
      "competitor_id": "COMP-000001",
      "platform": "youtube",
      "title": "What Will Humans Look Like in 1 Million Years?",
      "url": "",
      "channel_name": "",
      "observed_strengths": [
        "Strong curiosity title",
        "Clear future visuals"
      ],
      "observed_weaknesses": [
        "Speculation presented too confidently",
        "Generic AI visuals"
      ],
      "differentiation_opportunity": [
        "Use more cinematic and philosophical framing.",
        "Clearly separate science from speculation."
      ]
    }
  ]
}
```

---

# 16. trend.json Schema

Trend 분석은 선택 출력이다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",

  "trend": {
    "topic_interest": "MEDIUM",
    "growth_potential": "HIGH",
    "seasonality": "NONE",
    "related_topics": [
      "AI evolution",
      "space colonization",
      "genetic engineering",
      "post-human future"
    ],
    "notes": [
      "Future human evolution can connect with AI, space, and civilization topics."
    ]
  }
}
```

---

# 17. audience_questions.json Schema

Audience 질문은 Story와 Growth에 도움이 된다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",

  "audience_questions": [
    {
      "question": "Will humans still look human in one million years?",
      "interest_level": "HIGH",
      "story_use": "hook"
    },
    {
      "question": "Could humans split into different species on different planets?",
      "interest_level": "HIGH",
      "story_use": "middle_section"
    }
  ]
}
```

---

# 18. Evidence Levels

Research Engine은 Evidence Level을 표시해야 한다.

```text
HIGH
신뢰 가능한 출처에 의해 강하게 뒷받침됨

MEDIUM
합리적 근거가 있으나 추가 확인 필요

LOW
근거가 약하거나 맥락이 제한적임

SPECULATIVE
가능성 또는 시나리오이며 사실처럼 말하면 안 됨

UNKNOWN
확인되지 않음
```

사용 규칙:

```text
HIGH / MEDIUM
Knowledge Engine으로 전달 가능

LOW
주의 표시 후 전달 가능

SPECULATIVE
반드시 시나리오로 표시

UNKNOWN
Claim으로 사용 금지
```

---

# 19. Research Quality Rules

좋은 Research의 조건:

```text
Topic의 핵심 질문이 명확하다.
중요 Fact가 Source와 연결되어 있다.
Fact와 Speculation이 분리되어 있다.
Story에 사용할 Hook 소재가 있다.
Visualizable Idea가 있다.
Risk Note가 있다.
Knowledge Engine이 Claim을 만들 수 있다.
Quality Engine이 검토할 수 있는 근거가 있다.
```

나쁜 Research:

```text
출처 없는 사실 나열
검증 불가한 주장
Story에 쓸 수 없는 일반론
시청자 관심 포인트 없음
Risk Note 없음
경쟁 콘텐츠와 차별점 없음
Speculation을 Fact처럼 정리
```

---

# 20. Research Validation Rules

Research Validator는 다음을 확인해야 한다.

```text
research/research.json 존재
research/sources.json 존재
research/facts.json 존재
research/risk_notes.json 존재
project_id 일치
channel_id 일치
research questions 존재
sources 배열 존재
facts 배열 존재
중요 fact에 source_ids 존재
risk_notes 배열 존재
evidence_level 유효
SPECULATIVE 항목이 fact처럼 표시되지 않았는지 확인
```

검증 실패 시 KNOWLEDGE Stage로 넘어갈 수 없다.

---

# 21. Self Review

Research Engine은 결과 제출 전 Self Review를 생성한다.

Self Review 항목:

```text
필수 파일 생성 여부
Source와 Fact 연결 여부
불확실성 표시 여부
위험 주장 표시 여부
Story 활용 가능성
Knowledge Engine 사용 가능성
Channel Brand 적합성
```

Self Review 결과는 다음 위치에 기록한다.

```text
logs/self_reviews.jsonl
```

---

# 22. Handoff to Knowledge Engine

Research Engine은 Knowledge Engine에 Handoff를 생성해야 한다.

Handoff에 포함할 내용:

```text
핵심 Findings
Source 목록
Fact 목록
Speculative 항목
Risk Notes
추천 Claim 후보
주의해야 할 Claim
Story에 쓸 만한 Hook 소재
Visualizable Ideas
```

Handoff 파일 예시:

```text
workflow/handoffs/RESEARCH_to_KNOWLEDGE.json
```

---

# 23. Memory Integration

Research Engine은 작업 전 Memory Context를 사용한다.

사용할 수 있는 Memory:

```text
Channel Topic Success Memory
Channel Topic Failure Memory
Previous Research Patterns
Factuality Risk Memory
Growth Topic Memory
Competitor Pattern Memory
```

Research Engine은 작업 후 Memory Candidate를 만들 수 있다.

예시:

```text
반복적으로 좋은 Topic Source 발견
반복적으로 위험한 Claim 유형 발견
경쟁 콘텐츠에서 자주 쓰이는 약한 패턴 발견
```

Memory 확정은 Memory Engine 또는 Learning Engine이 담당한다.

---

# 24. Error Types

Research Engine의 Error Type:

```text
ResearchInputMissingError
TopicMissingError
ResearchScopeError
SourceCollectionError
SourceValidationError
FactExtractionError
UnsupportedClaimError
EvidenceLevelError
RiskNoteMissingError
ResearchOutputValidationError
ResearchHandoffError
```

Error 예시:

```json
{
  "error_type": "UnsupportedClaimError",
  "message": "A future prediction was recorded as a confirmed fact without source or uncertainty label.",
  "project_id": "20260710-093500-future-million-year-human",
  "stage": "RESEARCH",
  "severity": "HIGH",
  "suggested_fix": "Move the item to speculative scenarios and add risk note.",
  "created_at": "2026-07-10T10:00:00"
}
```

---

# 25. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
ResearchEngine
ResearchScopeBuilder
ResearchQuestionBuilder
SourceCollector
SourceValidator
SourceReliabilityScorer
FactExtractor
EvidenceClassifier
CompetitorResearcher
TrendResearcher
AudienceQuestionBuilder
ResearchRiskDetector
ResearchReportBuilder
ResearchValidator
ResearchHandoffBuilder
ResearchErrorReporter
```

---

# 26. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/17_RESEARCH_ENGINE.md
→ engines/research/
```

예시 구조:

```text
engines/
└── research/
    ├── research_engine.py
    ├── research_scope_builder.py
    ├── research_question_builder.py
    ├── source_collector.py
    ├── source_validator.py
    ├── source_reliability_scorer.py
    ├── fact_extractor.py
    ├── evidence_classifier.py
    ├── competitor_researcher.py
    ├── trend_researcher.py
    ├── audience_question_builder.py
    ├── research_risk_detector.py
    ├── research_report_builder.py
    ├── research_validator.py
    ├── research_handoff_builder.py
    └── research_error_reporter.py
```

---

# 27. Main Public Operations

Research Engine은 최소 다음 작업을 제공해야 한다.

```text
run_research(project_id)
build_research_scope(project_id)
build_research_questions(project_id)
collect_sources(project_id)
validate_sources(project_id)
extract_facts(project_id)
classify_evidence(project_id)
build_competitor_research(project_id)
build_trend_research(project_id)
build_audience_questions(project_id)
detect_research_risks(project_id)
build_research_report(project_id)
validate_research_outputs(project_id)
build_handoff_to_knowledge(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
Source와 Fact 연결
Evidence Level 표시
Risk 표시
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 28. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Project Topic 로드
Research Scope 생성
Research Questions 생성
Manual Source 입력 또는 Source Placeholder 구조 지원
Source Schema 저장
Fact Schema 저장
Evidence Level 분류
Risk Notes 생성
research.json 생성
sources.json 생성
facts.json 생성
risk_notes.json 생성
Research Validation 수행
Knowledge Engine Handoff 생성
```

v1.0에서 하지 않아도 되는 것:

```text
완전 자동 웹 크롤링
유료 데이터베이스 연동
실시간 트렌드 API 연동
복잡한 경쟁 채널 자동 분석
논문 전문 자동 분석
자동 팩트체크 완전 보장
```

v1.0에서는 Research 구조를 안정적으로 만들고, 수동 Source 입력도 받을 수 있게 하는 것이 우선이다.

---

# 29. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Project Topic을 기반으로 Research Scope를 만들 수 있다.
Research Questions를 생성할 수 있다.
Source 정보를 구조화해서 저장할 수 있다.
Fact 정보를 구조화해서 저장할 수 있다.
Fact와 Source를 연결할 수 있다.
Evidence Level을 표시할 수 있다.
Speculation과 Fact를 구분할 수 있다.
Risk Notes를 생성할 수 있다.
research.json을 생성할 수 있다.
sources.json을 생성할 수 있다.
facts.json을 생성할 수 있다.
risk_notes.json을 생성할 수 있다.
Research Output을 검증할 수 있다.
Knowledge Engine으로 넘길 Handoff를 생성할 수 있다.
```

---

# 30. Non Goals

v1.0에서 Research Engine이 하지 않는 것:

```text
대본 작성
최종 Claim 확정
Visual Prompt 작성
Provider 직접 호출
Quality Score 최종 계산
Template 직접 수정
YouTube Analytics 직접 수집
완전 자동 사실 검증 보장
```

v1.0에서는 Knowledge와 Story가 사용할 수 있는 근거 기반 Research Output을 안정적으로 만드는 것이 우선이다.

---

# 31. Critical Research Rules

반드시 지켜야 할 규칙:

```text
1. Research Engine은 근거 없는 주장을 만들지 않는다.

2. 중요한 Fact는 Source와 연결한다.

3. Fact와 Speculation을 구분한다.

4. 불확실한 내용은 불확실하다고 표시한다.

5. LOW Source는 단독 근거로 사용하지 않는다.

6. UNKNOWN Source는 Claim 근거로 사용하지 않는다.

7. Risk Note 없이 위험한 Claim을 넘기지 않는다.

8. Research Engine은 대본을 작성하지 않는다.

9. Research Engine은 Provider를 직접 호출하지 않는다.

10. Research Output은 Knowledge Engine이 사용할 수 있어야 한다.

11. Research Validation 실패 시 KNOWLEDGE Stage로 넘어가지 않는다.

12. 중요한 판단은 Self Review와 Handoff에 기록한다.
```

---

# 32. Final Principle

Research Engine은 ADOS 콘텐츠 품질의 첫 번째 방어선이다.

좋은 Research는 좋은 Knowledge를 만들고,

좋은 Knowledge는 좋은 Story를 만들고,

좋은 Story는 좋은 Timeline과 Production을 만든다.

Research Engine의 목적은 자료를 많이 모으는 것이 아니다.

Research Engine의 목적은 정확하고, 쓸 수 있고, 위험이 표시된 재료를 만들어서 고품질 영상 제작의 기반을 만드는 것이다.
