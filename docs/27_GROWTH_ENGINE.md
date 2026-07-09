# 27_GROWTH_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Growth Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Growth Engine을 정의한다.

Growth Engine은 Project와 Channel이 성장할 가능성을 높이기 위해 Topic, Hook, Title, Thumbnail Direction, Retention Flow, Search / Recommendation Fit, Revenue Potential, Subscriber Conversion 가능성을 분석하는 엔진이다.

Growth Engine은 단순 조회수 욕심을 위한 엔진이 아니다.

Growth Engine은 다음 목표를 가진다.

```text
좋은 Topic을 더 잘 선택한다.
좋은 Story가 더 잘 클릭되게 만든다.
좋은 영상이 더 오래 시청되게 만든다.
Channel Brand를 해치지 않으면서 성장 가능성을 높인다.
Quality를 낮추지 않고 CTR / Retention / Subscriber Conversion을 개선한다.
Publishing Engine이 사용할 Metadata와 Growth Notes를 준비한다.
Analytics와 Learning 결과를 다음 Project 개선으로 연결한다.
```

이 문서는 다음 문서들과 직접 연결된다.

```text
03_ARCHITECTURE.md
07_PROJECT_SPEC.md
10_BRAND_SYSTEM.md
11_PORTFOLIO_ENGINE.md
12_PROJECT_ENGINE.md
13_MEMORY_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
17_RESEARCH_ENGINE.md
18_KNOWLEDGE_ENGINE.md
19_STORY_ENGINE.md
21_VISUAL_ENGINE.md
26_QUALITY_ENGINE.md
28_PUBLISHING_ENGINE.md
29_ANALYTICS_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Growth Engine은 영상 제작물의 성장 가능성을 사전에 평가하고, 개선 방향을 제안하는 엔진이다.

전체 흐름:

```text
Topic
↓
Research / Knowledge / Story
↓
Growth Analysis
↓
Title / Thumbnail / Retention / SEO / Revenue Notes
↓
Quality Check
↓
Publishing Package
↓
Analytics
↓
Learning
↓
Next Growth Improvement
```

Growth Engine의 핵심 질문:

```text
이 Topic은 시청자가 클릭할 만한가?
이 Hook은 첫 30초 이탈을 줄일 수 있는가?
이 Title은 궁금증을 만들지만 과장하지 않는가?
이 Thumbnail 방향은 Brand와 맞는가?
영상 구조는 Retention을 만들 수 있는가?
이 영상은 구독 전환 가능성이 있는가?
이 Topic은 수익성이 있는가?
이 영상은 Channel 장기 성장에 도움이 되는가?
```

---

# 3. Growth Philosophy

## 3.1 Growth Must Not Break Trust

Growth는 신뢰를 깨면 안 된다.

금지:

```text
거짓 클릭bait
과장된 제목
사실과 다른 Thumbnail
공포 조장
근거 없는 수익 자극
Brand와 맞지 않는 자극적 표현
```

허용:

```text
강한 궁금증
명확한 Promise
정직한 긴장감
시청자가 클릭할 이유
Story와 일치하는 Title
내용과 일치하는 Thumbnail
```

## 3.2 Quality Before Growth

Growth Score가 높아도 Quality 기준을 위반하면 사용할 수 없다.

우선순위:

```text
1. Factual Accuracy
2. Brand Consistency
3. Quality Gate
4. Retention Potential
5. CTR Potential
6. Revenue Potential
```

## 3.3 Growth Uses Leading Indicators

Growth Engine은 실제 조회수를 미리 알 수 없다.

대신 다음 선행 지표를 추정한다.

```text
CTR Potential
Retention Potential
Watch Time Potential
Subscriber Conversion Potential
Search Potential
Recommendation Potential
Revenue Potential
Brand Growth Fit
```

## 3.4 Growth Learns from Analytics

Growth Engine은 Analytics 결과를 받아 다음 Project의 Growth 판단을 개선해야 한다.

```text
Prediction
↓
Publishing
↓
Analytics
↓
Learning
↓
Growth Memory
↓
Better Prediction
```

---

# 4. Growth Engine Responsibilities

Growth Engine의 책임:

```text
Topic Growth Fit 분석
Audience Interest 분석
CTR Potential 분석
Retention Potential 분석
Hook Strength 분석
Title Candidate 생성
Title Candidate 점수화
Thumbnail Direction 생성
Thumbnail Risk 분석
SEO Keyword 후보 생성
Description Angle 제안
Subscriber Conversion Point 제안
Revenue Potential 추정
Brand Growth Fit 검사
Growth Report 생성
Publishing Engine에 Metadata 후보 전달
Portfolio Engine에 Channel / Project 우선순위 참고 정보 제공
Learning Engine에 Growth Prediction 데이터 제공
```

Growth Engine이 하지 않는 것:

```text
실제 YouTube Analytics를 직접 수집하지 않는다.
최종 Publishing을 수행하지 않는다.
Quality Gate를 우회하지 않는다.
Brand Rule을 무시하지 않는다.
사실과 다른 Title을 만들지 않는다.
실제 수익을 보장하지 않는다.
Template을 직접 수정하지 않는다.
```

---

# 5. Inputs

Growth Engine의 입력:

```text
project.json
topic.json
channel_snapshot.json
template_snapshot.json

research/research.json
research/trend.json
research/audience_questions.json
research/competitors.json

knowledge/knowledge.json
knowledge/claims.json
knowledge/risk_notes.json

story/hook.json
story/outline.json
story/script_master.json
story/story_review.json

direction/director_notes.md
reports/visual_review.json
reports/quality_report.json

channels/{channel_id}/brand.yaml
channels/{channel_id}/growth.yaml
channels/{channel_id}/memory.yaml

workflow/memory_context_GROWTH.json
```

필수 입력:

```text
project.json
topic.json
channel_snapshot.json
story/hook.json
story/outline.json
story/script_master.json
```

선택 입력:

```text
research/trend.json
research/competitors.json
research/audience_questions.json
knowledge/story_materials.json
reports/quality_report.json
Channel Growth Memory
Analytics Memory
Title Success Memory
Thumbnail Success Memory
Retention Pattern Memory
Revenue Pattern Memory
```

---

# 6. Outputs

Growth Engine의 출력:

```text
reports/growth_prediction.json
reports/growth_report.json
reports/title_candidates.json
reports/thumbnail_direction.json
reports/seo_keywords.json
reports/retention_analysis.json
reports/revenue_potential.json
workflow/stage_results/GROWTH_result.json
workflow/handoffs/GROWTH_to_PUBLISHING.json
```

Publishing Engine이 사용할 수 있는 출력:

```text
package/metadata_candidates.json
package/title_candidates.json
package/thumbnail_brief.json
package/description_brief.json
package/tags_candidates.json
```

v1.0 최소 출력:

```text
reports/growth_prediction.json
reports/growth_report.json
reports/title_candidates.json
reports/thumbnail_direction.json
reports/seo_keywords.json
workflow/handoffs/GROWTH_to_PUBLISHING.json
```

---

# 7. Growth Execution Flow

Growth Engine 실행 흐름:

```text
Load Project Context
↓
Load Topic / Story / Brand
↓
Load Research Trend and Audience Questions
↓
Load Growth Memory
↓
Analyze Topic Growth Fit
↓
Analyze Hook / Retention Potential
↓
Generate Title Candidates
↓
Score Title Candidates
↓
Generate Thumbnail Direction
↓
Check Brand and Factual Risk
↓
Generate SEO Keywords
↓
Estimate Subscriber Conversion Potential
↓
Estimate Revenue Potential
↓
Build Growth Prediction
↓
Build Growth Report
↓
Build Publishing Handoff
```

---

# 8. Growth Metrics

Growth Engine은 다음 지표를 사용한다.

```text
topic_interest
ctr_potential
retention_potential
watch_time_potential
subscriber_conversion_potential
search_potential
recommendation_potential
revenue_potential
brand_growth_fit
quality_growth_alignment
```

각 지표는 0~100 점수로 표현할 수 있다.

---

# 9. Growth Score Formula

기본 Growth Score 구성:

```yaml
growth_score:
  topic_interest: 15
  ctr_potential: 20
  retention_potential: 20
  subscriber_conversion_potential: 10
  search_potential: 10
  recommendation_potential: 10
  revenue_potential: 10
  brand_growth_fit: 5
```

Quality와 Brand 문제가 있는 경우 Growth Score는 제한된다.

제한 규칙:

```text
Brand Fit < 80
→ Growth Score 최대 75

Factual Risk HIGH
→ Growth Score 최대 70

Quality Score < 90
→ Publishing Growth Recommendation 보류

Forbidden Claim Risk 있음
→ Title / Thumbnail 사용 금지
```

---

# 10. growth_prediction.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "GROWTH",

  "growth_prediction": {
    "overall_score": 88,
    "level": "HIGH",

    "metrics": {
      "topic_interest": 86,
      "ctr_potential": 90,
      "retention_potential": 88,
      "watch_time_potential": 84,
      "subscriber_conversion_potential": 80,
      "search_potential": 76,
      "recommendation_potential": 88,
      "revenue_potential": 82,
      "brand_growth_fit": 94
    },

    "summary": "The topic has strong curiosity and visual potential. The main growth opportunity is a cinematic title and thumbnail that preserve factual caution."
  },

  "risks": [
    {
      "risk_type": "SPECULATION_OVERPROMISE",
      "severity": "MEDIUM",
      "description": "The topic can be tempting to overstate. Title and thumbnail must avoid presenting future scenarios as facts.",
      "mitigation": "Use question-based title and simulation-based thumbnail framing."
    }
  ],

  "created_at": "2026-07-10T17:00:00"
}
```

---

# 11. Topic Growth Fit

Topic Growth Fit은 주제가 Channel 성장에 얼마나 적합한지 판단한다.

검사 항목:

```text
Channel Category와 맞는가
Audience가 궁금해할 만한가
강한 Hook을 만들 수 있는가
시각화 가능성이 있는가
시리즈로 확장 가능한가
Search 또는 Recommendation 가능성이 있는가
Brand 장기 정체성에 도움이 되는가
```

Topic Growth Fit 예시:

```json
{
  "topic_growth_fit": {
    "score": 88,
    "level": "HIGH",
    "strengths": [
      "Strong curiosity",
      "High visual potential",
      "Fits future channel identity",
      "Can connect to AI, space, evolution, civilization topics"
    ],
    "weaknesses": [
      "High speculation risk",
      "Search intent may be moderate rather than high"
    ]
  }
}
```

---

# 12. CTR Potential

CTR Potential은 사용자가 클릭할 가능성을 추정한다.

CTR에 영향을 주는 요소:

```text
Title Curiosity
Thumbnail Clarity
Topic Novelty
Emotional Pull
Specificity
Question Strength
Brand Trust
Avoidance of Clickbait
```

좋은 CTR 구조:

```text
궁금증이 명확하다.
주제가 구체적이다.
제목과 Thumbnail이 서로 보완한다.
영상 내용과 약속이 일치한다.
```

나쁜 CTR 구조:

```text
너무 일반적이다.
무슨 영상인지 알 수 없다.
과장되어 신뢰가 떨어진다.
Thumbnail이 내용과 다르다.
```

---

# 13. Retention Potential

Retention Potential은 시청자가 얼마나 오래 볼 가능성이 있는지 추정한다.

검사 항목:

```text
Hook Strength
First 30 Seconds
Open Loop
Question Flow
Section Transition
Visual Variety
Pacing
Midpoint Turn
Ending Payoff
```

Retention Risk 예시:

```json
{
  "retention_analysis": {
    "score": 86,
    "strengths": [
      "Strong cinematic opening",
      "Clear core question",
      "Good philosophical ending"
    ],
    "risks": [
      {
        "section_id": "SEC-003",
        "risk": "Explanation section may become too long.",
        "suggested_fix": "Add a visual contrast or question before this section."
      }
    ]
  }
}
```

---

# 14. retention_analysis.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "retention": {
    "score": 86,
    "level": "HIGH",

    "first_10_seconds": {
      "score": 92,
      "notes": "Cinematic future scenario creates immediate curiosity."
    },

    "first_30_seconds": {
      "score": 90,
      "notes": "Core question is clear and emotionally engaging."
    },

    "middle_retention": {
      "score": 82,
      "risks": [
        "Scientific explanation section may need stronger visual rhythm."
      ]
    },

    "ending_retention": {
      "score": 88,
      "notes": "Philosophical ending can support subscriber conversion."
    }
  },

  "recommended_improvements": [
    "Add a clear turning point before the technical explanation section.",
    "Use visual contrast between Earth humans and future off-world humans."
  ]
}
```

---

# 15. Title Candidate Rules

Growth Engine은 여러 Title 후보를 생성하고 점수화해야 한다.

좋은 Title 조건:

```text
궁금증이 있다.
구체적이다.
영상 내용과 일치한다.
과장하지 않는다.
Brand Tone과 맞는다.
CTR 가능성이 있다.
Factual Risk를 위반하지 않는다.
```

금지 Title:

```text
사실과 다른 제목
확정되지 않은 미래를 확정 표현
지나친 공포 조장
싸구려 충격 표현
Brand와 맞지 않는 표현
```

예시 금지:

```text
100만 년 뒤 인간의 진짜 모습이 밝혀졌다
과학자들이 확정한 미래 인간의 충격적 모습
```

예시 허용:

```text
100만 년 후 인간은 어떤 모습일까?
인간은 100만 년 뒤에도 인간일까?
미래 인간은 우리와 얼마나 달라질 수 있을까?
```

---

# 16. title_candidates.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "title_candidates": [
    {
      "title_id": "TITLE-000001",
      "language": "ko",
      "title": "100만 년 후 인간은 어떤 모습일까?",
      "score": 92,

      "metrics": {
        "curiosity": 94,
        "clarity": 90,
        "brand_fit": 95,
        "factual_safety": 96,
        "ctr_potential": 90
      },

      "risk": {
        "level": "LOW",
        "notes": []
      },

      "recommended": true
    },
    {
      "title_id": "TITLE-000002",
      "language": "ko",
      "title": "인간은 100만 년 뒤에도 인간일까?",
      "score": 89,
      "recommended": false,
      "notes": "Strong philosophical angle, but slightly less clear for search."
    }
  ],

  "forbidden_titles": [
    {
      "title": "과학자들이 확정한 100만 년 뒤 인간의 모습",
      "reason": "Unsupported certainty."
    }
  ]
}
```

---

# 17. Thumbnail Direction

Growth Engine은 Thumbnail 자체를 최종 제작하지 않는다.

Growth Engine은 Thumbnail이 어떤 방향이어야 클릭과 Brand를 동시에 만족하는지 정의한다.

Thumbnail Direction 요소:

```text
main_visual_concept
emotion
contrast
focus_object
text_policy
brand_fit
factual_risk
avoid
```

Thumbnail은 Visual Engine 또는 Publishing Engine에서 최종 제작될 수 있다.

---

# 18. thumbnail_direction.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "thumbnail_direction": {
    "score": 90,

    "main_concept": "A mysterious future human silhouette under alien light, contrasted with a present-day human silhouette.",

    "visual_elements": [
      "future human silhouette",
      "alien sunlight",
      "present human comparison",
      "cinematic dark blue background"
    ],

    "emotion": [
      "curiosity",
      "mystery",
      "awe"
    ],

    "text_policy": {
      "use_text": true,
      "recommended_text": [
        "100만 년 후?",
        "인간일까?"
      ],
      "max_words": 3
    },

    "risk": {
      "level": "MEDIUM",
      "notes": [
        "Do not show a future human as confirmed factual prediction."
      ],
      "required_treatment": "simulation or question framing"
    },

    "avoid": [
      "monster-like human",
      "cheap horror",
      "fake scientific certainty",
      "too much text",
      "generic robot face"
    ]
  }
}
```

---

# 19. SEO Keywords

SEO Keywords는 Publishing Metadata에 사용될 수 있다.

키워드 종류:

```text
primary_keywords
secondary_keywords
long_tail_keywords
related_topics
forbidden_keywords
```

주의:

```text
SEO를 위해 사실과 다른 키워드를 넣지 않는다.
영상 내용과 무관한 인기 키워드를 넣지 않는다.
Brand를 해치는 자극적 키워드를 남발하지 않는다.
```

---

# 20. seo_keywords.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "seo": {
    "primary_keywords": [
      "미래 인간",
      "인간 진화",
      "100만 년 후"
    ],

    "secondary_keywords": [
      "AI와 인간",
      "우주 이주",
      "유전자 공학",
      "문명의 미래"
    ],

    "long_tail_keywords": [
      "100만 년 후 인간은 어떻게 변할까",
      "미래 인간의 모습",
      "인류 진화의 미래"
    ],

    "related_topics": [
      "posthuman",
      "space colonization",
      "human evolution",
      "future civilization"
    ],

    "forbidden_keywords": [
      "확정된 미래 인간",
      "과학자들이 증명한 100만 년 뒤 모습"
    ]
  }
}
```

---

# 21. Description Brief

Growth Engine은 Description 작성 방향을 제안할 수 있다.

Description Brief는 Publishing Engine이 최종 Description을 만들 때 사용한다.

포함 내용:

```text
영상 약속
핵심 질문
주의해야 할 Factual Framing
관련 키워드
다음 영상 연결 가능성
구독 유도 포인트
```

예시:

```json
{
  "description_brief": {
    "opening_summary": "이 영상은 100만 년 뒤 인간이 어떤 모습일 수 있는지, 과학적 사실과 가능한 시나리오를 구분하며 탐험한다.",
    "core_question": "미래 인간은 지금의 우리와 얼마나 달라질 수 있을까?",
    "factual_note": "미래 시나리오는 확정된 예측이 아니라 가능성으로 다룬다.",
    "subscriber_conversion_angle": "미래, AI, 문명, 인간의 변화를 탐구하는 Channel 정체성과 연결한다."
  }
}
```

---

# 22. Subscriber Conversion Potential

Subscriber Conversion은 시청자가 영상을 본 뒤 Channel을 구독할 가능성이다.

검사 항목:

```text
Channel Identity가 명확한가
영상이 다음 영상을 기대하게 만드는가
Ending이 좋은 질문을 남기는가
Series Potential이 있는가
Brand Tone이 일관적인가
```

좋은 구독 전환 구조:

```text
이 Channel이 어떤 주제를 계속 다루는지 명확하다.
영상 끝에서 더 큰 질문이 생긴다.
시청자가 다음 영상도 보고 싶어진다.
```

---

# 23. Revenue Potential

Revenue Potential은 실제 수익 보장이 아니라 상대적 가능성 평가이다.

검사 항목:

```text
Topic Category
Audience Value
Advertiser Friendliness
RPM Potential
Evergreen Potential
Series Potential
Global Language Potential
```

Revenue Potential 점수 예시:

```json
{
  "revenue_potential": {
    "score": 82,
    "level": "HIGH",
    "factors": {
      "evergreen_value": 90,
      "global_interest": 85,
      "advertiser_friendliness": 80,
      "series_potential": 88,
      "rpm_estimate_confidence": "LOW"
    },
    "notes": [
      "Future civilization and AI-related topics may have good global potential.",
      "Actual RPM must be verified after publishing."
    ]
  }
}
```

---

# 24. revenue_potential.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "revenue_potential": {
    "score": 82,
    "level": "HIGH",

    "drivers": [
      "Evergreen topic",
      "Global curiosity",
      "AI and future civilization adjacency",
      "Multi-language potential"
    ],

    "risks": [
      "Actual RPM unknown before publishing",
      "Speculative topic must remain advertiser-friendly"
    ],

    "recommended_action": "Track actual RPM and revenue after publishing through Analytics Engine."
  }
}
```

---

# 25. Brand Growth Fit

Growth Engine은 Title, Thumbnail, SEO가 Brand와 충돌하지 않는지 검사한다.

검사 항목:

```text
Title Tone
Thumbnail Tone
Description Tone
Keyword Tone
Hook Promise
Audience Expectation
Long-term Channel Identity
```

Brand Growth 위반 예시:

```text
자극적인 공포 Thumbnail
사실과 다른 제목
Channel Tone과 맞지 않는 유머
과학적 신뢰를 깨는 표현
```

Growth Engine은 Brand 위반 후보를 추천하지 않는다.

---

# 26. growth_report.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "GROWTH",

  "score": 88,
  "status": "HIGH_POTENTIAL",

  "summary": {
    "growth_strengths": [
      "Strong curiosity topic",
      "Cinematic hook",
      "High visual potential",
      "Good multi-language potential"
    ],

    "growth_risks": [
      "Speculative topic can become misleading if title or thumbnail overpromises.",
      "Middle explanation section may need pacing support."
    ],

    "recommended_strategy": "Use question-based title, cinematic future simulation thumbnail, and careful factual framing."
  },

  "recommended_assets": {
    "title_id": "TITLE-000001",
    "thumbnail_direction_ref": "reports/thumbnail_direction.json",
    "seo_keywords_ref": "reports/seo_keywords.json"
  },

  "publishing_notes": [
    "Do not use certainty-based future claims in title.",
    "Thumbnail should feel like a question, not a confirmed prediction."
  ],

  "created_at": "2026-07-10T17:00:00"
}
```

---

# 27. Publishing Handoff

Growth Engine은 Publishing Engine에 Handoff를 생성해야 한다.

파일:

```text
workflow/handoffs/GROWTH_to_PUBLISHING.json
```

포함 내용:

```text
Recommended Title
Title Candidates
Thumbnail Direction
SEO Keywords
Description Brief
Tags Candidates
Growth Risks
Brand Restrictions
Factual Restrictions
```

예시:

```json
{
  "from_stage": "GROWTH",
  "to_stage": "PUBLISHING",
  "project_id": "20260710-093500-future-million-year-human",

  "recommended_title": {
    "ko": "100만 년 후 인간은 어떤 모습일까?",
    "en": "What Will Humans Look Like in One Million Years?"
  },

  "inputs_for_publishing": [
    "reports/title_candidates.json",
    "reports/thumbnail_direction.json",
    "reports/seo_keywords.json",
    "reports/growth_report.json"
  ],

  "must_follow": [
    "Do not present speculative future scenarios as confirmed facts.",
    "Keep title question-based.",
    "Thumbnail should match the actual story and brand tone."
  ]
}
```

---

# 28. Portfolio Integration

Portfolio Engine은 Growth Engine 결과를 Project 우선순위 판단에 사용할 수 있다.

Portfolio에 제공할 정보:

```text
Project Growth Score
Topic Growth Fit
Revenue Potential
Channel Fit
Subscriber Conversion Potential
Risk Level
Recommended Priority
```

예시:

```json
{
  "portfolio_growth_signal": {
    "project_id": "20260710-093500-future-million-year-human",
    "channel_id": "future",
    "growth_score": 88,
    "priority_signal": "HIGH",
    "reason": "Strong topic-channel fit and high retention potential."
  }
}
```

---

# 29. Quality Integration

Growth Engine은 Quality Engine과 충돌하면 안 된다.

규칙:

```text
Quality Fail이면 Growth 추천을 Publishing에 강제하지 않는다.
Brand 위반 Title은 추천하지 않는다.
Factual Risk가 높은 Thumbnail은 추천하지 않는다.
Speculative Claim을 과장하는 Metadata는 금지한다.
```

Quality Engine은 Growth Output을 검사할 수 있다.

검사 대상:

```text
title_candidates.json
thumbnail_direction.json
seo_keywords.json
growth_report.json
```

---

# 30. Analytics Integration

Analytics Engine은 실제 성과를 수집한다.

Growth Engine은 Analytics 결과를 직접 수집하지 않는다.

흐름:

```text
Growth Prediction
↓
Publishing
↓
Analytics Report
↓
Learning Engine
↓
Growth Memory
↓
Next Growth Prediction
```

비교 대상:

```text
Predicted CTR Potential vs Actual CTR
Predicted Retention Potential vs Actual Retention
Predicted Subscriber Conversion vs Actual Subscriber Change
Predicted Revenue Potential vs Actual Revenue
```

---

# 31. Learning Integration

Learning Engine은 Growth 예측과 실제 결과를 비교한다.

학습 대상:

```text
어떤 Title 구조가 실제 CTR이 높았는가
어떤 Thumbnail 방향이 실제 클릭을 만들었는가
어떤 Hook이 Retention을 만들었는가
어떤 Topic이 Subscriber Conversion을 만들었는가
어떤 Topic이 Revenue Potential과 실제 Revenue가 일치했는가
```

Growth Engine은 Learning 결과를 Memory로 받아 다음 Project에서 사용한다.

---

# 32. Memory Integration

Growth Engine은 작업 전 Memory Context를 사용한다.

사용 가능한 Memory:

```text
Successful Title Memory
Failed Title Memory
Thumbnail CTR Memory
Retention Hook Memory
Subscriber Conversion Memory
Revenue Pattern Memory
Channel Growth Memory
Audience Interest Memory
```

Growth Engine은 작업 후 Memory Candidate를 만들 수 있다.

예시:

```text
질문형 Title이 Future Channel에서 좋은 CTR 가능성을 보임
확정적 미래 표현은 Factual Risk가 높아 추천하지 않음
철학적 Ending이 Subscriber Conversion 가능성을 높임
```

Memory 확정은 Memory Engine 또는 Learning Engine이 담당한다.

---

# 33. Growth Validation Rules

Growth Validator는 다음을 확인해야 한다.

```text
reports/growth_prediction.json 존재
reports/growth_report.json 존재
reports/title_candidates.json 존재
reports/thumbnail_direction.json 존재
reports/seo_keywords.json 존재
project_id 일치
channel_id 일치
recommended title 존재
forbidden title 분리
thumbnail risk 표시
seo keyword 존재
Brand Growth Fit 확인
Factual Risk 확인
Publishing Handoff 존재
```

검증 실패 시 Publishing Stage로 이동할 수 없다.

단, Growth Stage가 선택 사항인 Project에서는 Publishing Engine이 최소 Metadata를 직접 생성할 수 있다.

ADOS 기본 운영에서는 Growth Stage를 권장한다.

---

# 34. Auto Fix Rules

Growth 문제 발생 시 수정 대상은 보통 Metadata와 Direction이다.

수정 대상:

```text
Title Candidate
Thumbnail Direction
SEO Keywords
Description Brief
Retention Improvement Note
Subscriber Conversion Note
```

금지:

```text
Story 의미를 왜곡
Forbidden Claim 사용
Quality Gate 우회
Brand Rule 위반
사실과 다른 제목 사용
Thumbnail로 거짓 약속
```

Auto Fix 예시:

```text
Issue:
Recommended title implies confirmed future prediction.

Fix:
Rewrite title as question-based and update title_candidates.json.
```

---

# 35. Error Types

Growth Engine의 Error Type:

```text
GrowthInputMissingError
TopicGrowthAnalysisError
CTRPredictionError
RetentionAnalysisError
TitleCandidateError
TitleFactualRiskError
ThumbnailDirectionError
ThumbnailBrandMismatchError
SEOKeywordError
RevenuePotentialError
BrandGrowthFitError
GrowthReportError
GrowthValidationError
GrowthHandoffError
```

Error 예시:

```json
{
  "error_type": "TitleFactualRiskError",
  "message": "Recommended title presents a speculative future as confirmed fact.",
  "project_id": "20260710-093500-future-million-year-human",
  "stage": "GROWTH",
  "severity": "HIGH",
  "suggested_fix": "Rewrite the title using question-based framing.",
  "created_at": "2026-07-10T17:00:00"
}
```

---

# 36. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
GrowthEngine
GrowthInputLoader
GrowthInputValidator
TopicGrowthAnalyzer
CTRPotentialAnalyzer
RetentionPotentialAnalyzer
TitleCandidateBuilder
TitleScorer
ThumbnailDirectionBuilder
SEOKeywordBuilder
DescriptionBriefBuilder
SubscriberConversionAnalyzer
RevenuePotentialAnalyzer
BrandGrowthFitChecker
FactualGrowthRiskChecker
GrowthPredictionBuilder
GrowthReportBuilder
GrowthValidator
GrowthHandoffBuilder
GrowthMemoryCandidateBuilder
GrowthErrorReporter
```

---

# 37. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/27_GROWTH_ENGINE.md
→ engines/growth/
```

예시 구조:

```text
engines/
└── growth/
    ├── growth_engine.py
    ├── growth_input_loader.py
    ├── growth_input_validator.py
    ├── topic_growth_analyzer.py
    ├── ctr_potential_analyzer.py
    ├── retention_potential_analyzer.py
    ├── title_candidate_builder.py
    ├── title_scorer.py
    ├── thumbnail_direction_builder.py
    ├── seo_keyword_builder.py
    ├── description_brief_builder.py
    ├── subscriber_conversion_analyzer.py
    ├── revenue_potential_analyzer.py
    ├── brand_growth_fit_checker.py
    ├── factual_growth_risk_checker.py
    ├── growth_prediction_builder.py
    ├── growth_report_builder.py
    ├── growth_validator.py
    ├── growth_handoff_builder.py
    ├── growth_memory_candidate_builder.py
    └── growth_error_reporter.py
```

---

# 38. Main Public Operations

Growth Engine은 최소 다음 작업을 제공해야 한다.

```text
run_growth(project_id)
load_growth_inputs(project_id)
validate_growth_inputs(project_id)
analyze_topic_growth(project_id)
analyze_ctr_potential(project_id)
analyze_retention_potential(project_id)
build_title_candidates(project_id)
score_title_candidates(project_id)
build_thumbnail_direction(project_id)
build_seo_keywords(project_id)
build_description_brief(project_id)
analyze_subscriber_conversion(project_id)
analyze_revenue_potential(project_id)
check_brand_growth_fit(project_id)
check_factual_growth_risk(project_id)
build_growth_prediction(project_id)
build_growth_report(project_id)
validate_growth_outputs(project_id)
build_handoff_to_publishing(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
Brand Rule 준수
Factual Risk 준수
Quality Gate 우선
과장 금지
Publishing Engine이 사용할 수 있는 구조 생성
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 39. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Project / Topic / Story 로드
Growth 입력 검증
Topic Growth Fit 분석
CTR Potential 기본 분석
Retention Potential 기본 분석
Title Candidate 생성
Title Candidate 점수화
Thumbnail Direction 생성
SEO Keyword 생성
Revenue Potential 기본 추정
Growth Report 생성
Publishing Handoff 생성
Growth Validation 수행
```

v1.0에서 하지 않아도 되는 것:

```text
실제 YouTube Analytics 직접 수집
정교한 ML 기반 조회수 예측
자동 A/B 테스트 실행
자동 광고 수익 예측 보장
실시간 Trend API 연동
자동 Thumbnail 이미지 생성
Publishing 직접 수행
```

v1.0에서는 Quality와 Brand를 지키면서 Publishing에 필요한 Growth 판단과 Metadata 후보를 만드는 것이 우선이다.

---

# 40. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Project Topic과 Story를 로드할 수 있다.
Growth 입력을 검증할 수 있다.
Topic Growth Fit을 분석할 수 있다.
CTR Potential을 추정할 수 있다.
Retention Potential을 추정할 수 있다.
Title Candidate를 생성할 수 있다.
Title Candidate를 점수화할 수 있다.
Forbidden Title을 분리할 수 있다.
Thumbnail Direction을 생성할 수 있다.
SEO Keywords를 생성할 수 있다.
Revenue Potential을 기본 추정할 수 있다.
Brand Growth Fit을 검사할 수 있다.
Factual Growth Risk를 검사할 수 있다.
growth_prediction.json을 생성할 수 있다.
growth_report.json을 생성할 수 있다.
Publishing Engine으로 Handoff를 만들 수 있다.
Growth Validation 실패 시 Publishing Stage 진행을 막을 수 있다.
```

---

# 41. Non Goals

v1.0에서 Growth Engine이 하지 않는 것:

```text
실제 조회수 보장
실제 CTR 보장
실제 수익 보장
YouTube Analytics 직접 수집
Publishing 직접 수행
Thumbnail 최종 이미지 직접 생성
Quality Gate 우회
Brand Rule 우회
거짓 Clickbait 생성
```

v1.0에서는 성장 가능성을 높이는 구조적 판단과 Publishing Metadata 후보 생성을 안정적으로 수행하는 것이 핵심이다.

---

# 42. Critical Growth Rules

반드시 지켜야 할 규칙:

```text
1. Growth Engine은 Quality보다 우선하지 않는다.

2. Growth Engine은 Brand보다 우선하지 않는다.

3. Growth Engine은 거짓 Clickbait을 만들지 않는다.

4. Title은 영상 내용과 일치해야 한다.

5. Thumbnail Direction은 영상 내용과 일치해야 한다.

6. Speculative Claim을 확정 사실처럼 표현하지 않는다.

7. Forbidden Title은 추천하지 않는다.

8. SEO Keyword는 영상 내용과 관련 있어야 한다.

9. Growth Score는 실제 성과 보장이 아니다.

10. Revenue Potential은 추정일 뿐이다.

11. Publishing Engine은 Growth Output을 사용할 수 있어야 한다.

12. Analytics 결과는 Learning을 통해 Growth Memory로 돌아와야 한다.

13. Growth Validation 실패 시 Publishing Stage로 넘어가지 않는다.

14. Growth Engine은 Publishing을 직접 수행하지 않는다.

15. 중요한 Growth 판단은 Report와 Handoff에 기록한다.
```

---

# 43. Final Principle

Growth Engine은 좋은 영상을 더 잘 발견되게 만드는 엔진이다.

좋은 Growth는 속임수가 아니다.

좋은 Growth는 Topic의 힘을 찾고,

Hook의 힘을 살리고,

Title과 Thumbnail의 약속을 명확히 하고,

Retention을 높이고,

Channel의 장기 신뢰를 지킨다.

Growth Engine의 목적은 클릭을 억지로 만드는 것이 아니다.

Growth Engine의 목적은 좋은 콘텐츠가 더 잘 클릭되고, 더 오래 시청되고, 더 많은 구독과 수익으로 이어질 수 있게 만드는 것이다.
