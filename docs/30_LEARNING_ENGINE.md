# 30_LEARNING_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Learning Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Learning Engine을 정의한다.

Learning Engine은 Project의 제작 과정과 게시 후 성과를 종합하여 다음 Project, Channel, Template, AI Employee가 더 나은 판단을 하도록 학습 결과를 만드는 엔진이다.

Learning Engine은 단순 회고 문서를 만드는 엔진이 아니다.

Learning Engine은 다음을 판단한다.

```text
무엇이 잘 작동했는가?
무엇이 실패했는가?
Growth 예측은 실제와 얼마나 맞았는가?
Quality Score와 실제 성과는 어떤 관계가 있었는가?
어떤 Hook / Title / Thumbnail / Story / Visual / Voice 패턴을 반복할 가치가 있는가?
어떤 실패 패턴을 피해야 하는가?
어떤 Memory를 업데이트해야 하는가?
어떤 Template 개선 후보가 있는가?
어떤 AI Employee의 판단 기준을 개선해야 하는가?
```

Learning Engine의 결과는 다음으로 연결된다.

```text
Memory Engine
Template System
Channel Engine
Growth Engine
Quality Engine
AI Evolution Engine
Portfolio Engine
```

이 문서는 다음 문서들과 직접 연결된다.

```text
06_AI_THINKING_FRAMEWORK.md
07_PROJECT_SPEC.md
08_TEMPLATE_SYSTEM.md
11_PORTFOLIO_ENGINE.md
12_PROJECT_ENGINE.md
13_MEMORY_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
26_QUALITY_ENGINE.md
27_GROWTH_ENGINE.md
28_PUBLISHING_ENGINE.md
29_ANALYTICS_ENGINE.md
31_AI_EVOLUTION_ENGINE.md
```

---

# 2. Core Definition

Learning Engine은 Project 결과를 다음 실행에 사용할 수 있는 학습 구조로 변환하는 엔진이다.

전체 흐름:

```text
Project Execution
↓
Quality Report
↓
Growth Prediction
↓
Publishing Record
↓
Analytics Report
↓
Learning Engine
↓
Learning Report
↓
Memory Candidates
↓
Template Improvement Candidates
↓
AI Evolution Feedback
```

Learning Engine의 핵심 목표는 다음이다.

```text
실패와 성공을 구조화한다.
반복 가능한 패턴을 찾는다.
단순한 느낌이 아니라 근거 기반 학습을 만든다.
과도한 일반화를 막는다.
Memory 업데이트 후보를 만든다.
Template 개선 후보를 만든다.
AI Employee 개선 후보를 만든다.
다음 Project에 반영할 Actionable Recommendation을 만든다.
```

---

# 3. Learning Philosophy

## 3.1 Learning Must Be Evidence-Based

Learning Engine은 근거 없이 결론을 내리지 않는다.

나쁜 학습:

```text
이런 주제는 안 된다.
이 제목은 무조건 잘 된다.
영상이 별로였다.
앞으로 더 자극적으로 가자.
```

좋은 학습:

```text
24h 기준 CTR은 Growth 예측과 유사했지만,
Retention은 예상보다 낮았다.

가능한 원인:
중반 설명 구간의 Visual Rhythm이 약했을 가능성이 있다.

증거:
analytics/retention_report.json
reports/growth_prediction.json
reports/analytics_report.json

권장:
다음 Future Channel 영상에서는 중반부 기술 설명 전
강한 Visual Contrast 또는 Question Reset을 추가한다.
```

## 3.2 Do Not Overgeneralize

한 영상의 결과만으로 Template 전체를 바꾸면 안 된다.

학습 범위는 증거의 강도에 따라 결정한다.

```text
한 Project의 약한 신호
→ Project Learning 또는 Candidate Memory

반복되는 Channel 패턴
→ Channel Memory Candidate

여러 Channel / 여러 Project에서 반복
→ Template Improvement Candidate

강한 반복 실패
→ AI Evolution Candidate
```

## 3.3 Learning Must Be Actionable

Learning은 다음 행동으로 이어져야 한다.

좋은 Learning은 다음 질문에 답해야 한다.

```text
다음 Project에서 무엇을 반복할 것인가?
무엇을 피할 것인가?
어떤 Stage를 개선할 것인가?
어떤 Prompt 또는 Rule을 바꿀 것인가?
어떤 Memory Candidate를 만들 것인가?
어떤 Template 개선 후보가 있는가?
```

## 3.4 Learning Does Not Directly Mutate Core Systems

Learning Engine은 Memory나 Template을 직접 확정 변경하지 않는다.

Learning Engine은 후보를 만든다.

확정은 다음 엔진이 담당한다.

```text
Memory 확정
→ Memory Engine

Template 개선 확정
→ Template System / Template Evolution Manager

AI Employee 개선 확정
→ AI Evolution Engine

Portfolio 우선순위 반영
→ Portfolio Engine
```

---

# 4. Learning Engine Responsibilities

Learning Engine의 책임:

```text
Project 결과 로드
Quality Report 로드
Growth Prediction 로드
Analytics Report 로드
Publishing Record 로드
Stage별 Report 로드
예측과 실제 차이 분석
성공 패턴 추출
실패 패턴 추출
Stage별 개선점 추출
Channel Learning 생성
Template Improvement Candidate 생성
Memory Update Candidate 생성
AI Employee Feedback 생성
Next Project Recommendation 생성
Learning Report 생성
AI Evolution Engine Handoff 생성
Memory Engine Handoff 생성
```

Learning Engine이 하지 않는 것:

```text
Memory를 직접 확정하지 않는다.
Template을 직접 수정하지 않는다.
AI Employee Prompt를 직접 수정하지 않는다.
Project 파일을 임의 수정하지 않는다.
Analytics 데이터를 직접 수집하지 않는다.
Publishing을 직접 수행하지 않는다.
Quality Score를 다시 계산하지 않는다.
성과 원인을 단정하지 않는다.
```

---

# 5. Inputs

Learning Engine의 입력:

```text
project.json
topic.json
channel_snapshot.json
template_snapshot.json

reports/quality_report.json
reports/quality_issues.json
reports/auto_fix_plan.json

reports/growth_prediction.json
reports/growth_report.json
reports/title_candidates.json
reports/thumbnail_direction.json
reports/seo_keywords.json

package/upload_package.json
package/published_record.json
package/metadata_{lang}.json

analytics/raw_metrics.json
analytics/performance_summary.json
analytics/prediction_comparison.json
analytics/retention_report.json
analytics/traffic_source_report.json
analytics/revenue_report.json
reports/analytics_report.json
workflow/handoffs/ANALYTICS_to_LEARNING.json

reports/story_review.json
reports/visual_review.json
reports/motion_review.json
reports/voice_review.json
reports/subtitle_review.json
reports/editing_review.json

workflow/memory_context_LEARNING.json
```

필수 입력:

```text
project.json
reports/quality_report.json
reports/growth_prediction.json
reports/analytics_report.json
analytics/prediction_comparison.json
channel_snapshot.json
```

Analytics가 아직 충분하지 않은 경우 Learning Engine은 부분 학습을 생성할 수 있다.

```text
24h Learning
72h Learning
7d Learning
28d Learning
Final Learning
```

---

# 6. Outputs

Learning Engine의 출력:

```text
learning/learning_report.json
learning/lessons_learned.json
learning/success_patterns.json
learning/failure_patterns.json
learning/prediction_accuracy_report.json
learning/next_project_recommendations.json
learning/memory_update_candidates.json
learning/template_improvement_candidates.json
learning/channel_improvement_candidates.json
learning/ai_employee_feedback.json
reports/learning_summary.md
workflow/stage_results/LEARNING_result.json
workflow/handoffs/LEARNING_to_MEMORY.json
workflow/handoffs/LEARNING_to_AI_EVOLUTION.json
workflow/handoffs/LEARNING_to_PORTFOLIO.json
```

v1.0 최소 출력:

```text
learning/learning_report.json
learning/lessons_learned.json
learning/memory_update_candidates.json
learning/next_project_recommendations.json
workflow/handoffs/LEARNING_to_MEMORY.json
workflow/handoffs/LEARNING_to_AI_EVOLUTION.json
```

---

# 7. Learning Execution Flow

Learning Engine 실행 흐름:

```text
Load Project Context
↓
Load Quality Report
↓
Load Growth Prediction
↓
Load Analytics Report
↓
Load Prediction Comparison
↓
Load Stage Reports
↓
Validate Learning Inputs
↓
Compare Expected vs Actual
↓
Extract Success Signals
↓
Extract Failure Signals
↓
Classify Evidence Strength
↓
Build Lessons Learned
↓
Build Memory Update Candidates
↓
Build Template Improvement Candidates
↓
Build AI Employee Feedback
↓
Build Next Project Recommendations
↓
Write Learning Report
↓
Handoff to Memory / AI Evolution / Portfolio
```

---

# 8. Learning Scope

Learning은 범위를 명확히 가져야 한다.

사용 가능한 Scope:

```text
PROJECT
CHANNEL
TEMPLATE
COMPANY
PROVIDER
AI_EMPLOYEE
STAGE
```

Scope 기준:

```text
PROJECT
한 Project 안에서만 의미 있는 학습

CHANNEL
특정 Channel에서 반복 가능성이 있는 학습

TEMPLATE
Template 구조 개선 후보가 될 수 있는 학습

COMPANY
여러 Channel에 적용될 수 있는 운영 학습

PROVIDER
Midjourney, Typecast 등 Provider 사용 패턴 학습

AI_EMPLOYEE
특정 AI Employee의 판단 기준 개선 학습

STAGE
Research, Story, Visual 등 특정 Stage 개선 학습
```

---

# 9. Evidence Strength

Learning Engine은 학습의 증거 강도를 표시해야 한다.

```text
LOW
MEDIUM
HIGH
LOCKED_CANDIDATE
```

## LOW

데이터가 부족하거나 하나의 약한 신호만 있음.

## MEDIUM

여러 근거가 있지만 반복 검증은 부족함.

## HIGH

여러 Project 또는 강한 데이터로 뒷받침됨.

## LOCKED_CANDIDATE

반복 검증 후 Template / Memory에 강하게 반영할 후보.

v1.0에서는 대부분의 Learning은 LOW 또는 MEDIUM으로 시작한다.

---

# 10. Learning Types

Learning Type은 다음을 사용한다.

```text
success_pattern
failure_pattern
prediction_gap
quality_issue_pattern
growth_pattern
retention_pattern
title_pattern
thumbnail_pattern
story_pattern
visual_pattern
motion_pattern
voice_pattern
subtitle_pattern
editing_pattern
provider_pattern
channel_strategy
template_candidate
ai_employee_feedback
```

---

# 11. learning_report.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "LEARNING",

  "learning_status": {
    "status": "COMPLETED",
    "checkpoint": "24h",
    "data_confidence": "MEDIUM",
    "scope": "PROJECT"
  },

  "summary": {
    "overall_learning": "The project showed promising CTR and subscriber conversion, but retention was lower than predicted in the middle section.",
    "what_worked": [
      "Question-based title likely supported CTR.",
      "Cinematic opening created strong curiosity.",
      "Topic fit the Future channel identity."
    ],
    "what_did_not_work": [
      "Middle explanation section may have reduced retention.",
      "Visual rhythm may have weakened after the hook."
    ],
    "main_recommendation": "For the next Future channel project, preserve question-based titles and cinematic hooks, but add a stronger midpoint visual reveal before technical explanations."
  },

  "evidence_refs": [
    "reports/growth_prediction.json",
    "reports/analytics_report.json",
    "analytics/prediction_comparison.json",
    "analytics/retention_report.json",
    "reports/quality_report.json"
  ],

  "created_at": "2026-07-11T21:00:00"
}
```

---

# 12. Lessons Learned

`learning/lessons_learned.json`은 학습 항목을 구조화한다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "lessons": [
    {
      "lesson_id": "LESSON-000001",
      "type": "title_pattern",
      "scope": "CHANNEL",
      "confidence": "MEDIUM",

      "summary": "Question-based titles may perform well for speculative future topics.",
      "evidence": [
        {
          "source": "analytics/prediction_comparison.json",
          "detail": "CTR prediction was near actual performance."
        },
        {
          "source": "reports/title_candidates.json",
          "detail": "Recommended title used question-based framing."
        }
      ],

      "recommendation": "Use question-based titles for future speculative topics unless search intent requires a clearer explanatory title.",

      "status": "MEMORY_CANDIDATE"
    }
  ]
}
```

---

# 13. Success Pattern Extraction

Success Pattern은 다음 조건에서 추출한다.

```text
Growth 예측과 실제 성과가 일치
Quality Score가 높고 실제 성과도 좋음
CTR이 Channel Baseline보다 좋음
Retention이 예상보다 좋음
Subscriber Conversion이 좋음
특정 Stage 결과가 높은 평가와 실제 성과에 기여한 가능성
```

Success Pattern 예시:

```json
{
  "pattern_id": "SUCCESS-000001",
  "type": "hook_pattern",
  "scope": "CHANNEL",
  "confidence": "MEDIUM",
  "summary": "Cinematic speculative opening can increase curiosity for Future channel topics.",
  "evidence_refs": [
    "story/hook.json",
    "reports/story_review.json",
    "reports/analytics_report.json"
  ],
  "repeat_recommendation": true
}
```

---

# 14. Failure Pattern Extraction

Failure Pattern은 다음 조건에서 추출한다.

```text
Growth 예측보다 실제 성과가 낮음
Quality Issue가 반복됨
Retention Drop이 특정 구간에서 발생
Visual / Voice / Subtitle 문제가 실제 성과와 연결될 가능성
Auto Fix가 반복됨
Provider 결과 품질 문제가 반복됨
```

Failure Pattern 예시:

```json
{
  "pattern_id": "FAILURE-000001",
  "type": "retention_pattern",
  "scope": "CHANNEL",
  "confidence": "LOW",
  "summary": "Long technical explanation sections may weaken retention if not supported by a visual reset.",
  "evidence_refs": [
    "analytics/retention_report.json",
    "story/outline.json",
    "edit/final_timeline.json"
  ],
  "avoid_recommendation": "Avoid long explanation blocks without a question reset or visual contrast."
}
```

---

# 15. Prediction Accuracy Report

Learning Engine은 Growth 예측의 정확도를 평가한다.

파일:

```text
learning/prediction_accuracy_report.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",

  "prediction_accuracy": {
    "checkpoint": "24h",
    "overall": "PARTIAL_MATCH",

    "metrics": {
      "ctr": {
        "predicted": 90,
        "actual": 5.8,
        "accuracy": "NEAR_EXPECTATION"
      },
      "retention": {
        "predicted": 88,
        "actual_average_percentage_viewed": 42.5,
        "accuracy": "BELOW_EXPECTATION"
      },
      "subscriber_conversion": {
        "predicted": 80,
        "actual_subscribers_gained": 18,
        "accuracy": "PROMISING"
      },
      "revenue": {
        "predicted": 82,
        "actual_rpm": 2.74,
        "accuracy": "UNKNOWN"
      }
    },

    "learning_notes": [
      "Growth Engine may have overestimated retention for explanation-heavy middle sections.",
      "CTR prediction was directionally useful."
    ]
  }
}
```

---

# 16. Memory Update Candidates

Learning Engine은 Memory Engine에 넘길 후보를 생성한다.

파일:

```text
learning/memory_update_candidates.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "memory_candidates": [
    {
      "candidate_id": "MEM-CAND-000001",
      "target_scope": "CHANNEL",
      "target_memory": "channels/future/memory.yaml",

      "memory_type": "success_pattern",
      "category": "title",

      "summary": "Question-based titles may work well for speculative future topics.",
      "details": {
        "pattern": "question_based_title",
        "example": "100만 년 후 인간은 어떤 모습일까?",
        "recommended_usage": "Use for speculative topics where certainty would create factual risk."
      },

      "evidence": [
        "reports/title_candidates.json",
        "analytics/prediction_comparison.json",
        "reports/analytics_report.json"
      ],

      "confidence": "MEDIUM",
      "status": "CANDIDATE",
      "requires_human_review": false
    }
  ]
}
```

규칙:

```text
Memory Candidate는 증거를 가져야 한다.
증거 없는 Memory Candidate는 만들지 않는다.
한 Project 결과만으로 HIGH confidence를 주지 않는다.
Template Memory로 승격하려면 반복 증거가 필요하다.
```

---

# 17. Template Improvement Candidates

Learning Engine은 Template 개선 후보를 만들 수 있다.

파일:

```text
learning/template_improvement_candidates.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "template_id": "future_documentary_template",

  "template_improvement_candidates": [
    {
      "candidate_id": "TPL-CAND-000001",
      "target_template_file": "templates/future_documentary_template/story.yaml",
      "type": "story_structure_improvement",

      "summary": "Add a required midpoint visual reset before long explanation sections.",
      "reason": "Retention appeared weaker in the middle explanation section.",

      "evidence": [
        "analytics/retention_report.json",
        "story/outline.json",
        "reports/analytics_report.json"
      ],

      "confidence": "LOW",
      "recommended_action": "Do not apply automatically. Track across more projects.",
      "auto_apply_allowed": false
    }
  ]
}
```

Template 개선 후보는 자동 적용하지 않는다.

Template 수정은 반드시 Template Evolution 절차를 따른다.

---

# 18. Channel Improvement Candidates

Channel 단위 개선 후보 파일:

```text
learning/channel_improvement_candidates.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "channel_improvement_candidates": [
    {
      "candidate_id": "CH-CAND-000001",
      "category": "retention_strategy",
      "summary": "Future channel videos may need stronger midpoint visual reveals when explaining scientific concepts.",
      "evidence": [
        "analytics/retention_report.json",
        "reports/visual_review.json"
      ],
      "confidence": "LOW",
      "recommended_next_test": "Apply this change to the next 2 Future channel projects and compare retention."
    }
  ]
}
```

---

# 19. AI Employee Feedback

Learning Engine은 AI Employee별 개선 피드백을 만들 수 있다.

파일:

```text
learning/ai_employee_feedback.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",

  "employee_feedback": [
    {
      "employee_or_department": "Story Department",
      "related_stage": "STORY",
      "feedback_type": "improvement",

      "summary": "Story structure was strong in the hook but may need stronger midpoint retention design.",
      "evidence": [
        "reports/story_review.json",
        "analytics/retention_report.json"
      ],

      "suggested_rule_update": "When a section is explanation-heavy, add a question reset or contrast before it.",
      "confidence": "LOW",
      "send_to_ai_evolution": true
    },
    {
      "employee_or_department": "Growth Department",
      "related_stage": "GROWTH",
      "feedback_type": "prediction_gap",

      "summary": "Growth Engine predicted high retention, but actual retention was lower.",
      "evidence": [
        "reports/growth_prediction.json",
        "analytics/prediction_comparison.json"
      ],

      "suggested_rule_update": "Apply penalty to retention prediction when middle section has long explanation blocks without visual reset.",
      "confidence": "MEDIUM",
      "send_to_ai_evolution": true
    }
  ]
}
```

---

# 20. Next Project Recommendations

Learning Engine은 다음 Project에서 바로 사용할 수 있는 추천을 만들어야 한다.

파일:

```text
learning/next_project_recommendations.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "recommendations": [
    {
      "recommendation_id": "NEXT-000001",
      "priority": "HIGH",
      "target_stage": "STORY",
      "summary": "Add a midpoint question reset before long explanation sections.",
      "reason": "Retention may have dropped during the explanation-heavy middle section.",
      "apply_to_next_project": true
    },
    {
      "recommendation_id": "NEXT-000002",
      "priority": "MEDIUM",
      "target_stage": "GROWTH",
      "summary": "Continue testing question-based titles for speculative future topics.",
      "reason": "CTR performance was close to Growth prediction.",
      "apply_to_next_project": true
    },
    {
      "recommendation_id": "NEXT-000003",
      "priority": "MEDIUM",
      "target_stage": "VISUAL",
      "summary": "Use stronger visual contrast when shifting from cinematic hook to scientific explanation.",
      "reason": "Visual rhythm may support retention in the middle section.",
      "apply_to_next_project": true
    }
  ]
}
```

---

# 21. Learning Summary Markdown

사람이 읽기 쉬운 요약 파일:

```text
reports/learning_summary.md
```

권장 형식:

```markdown
# Learning Summary

Project ID: 20260710-093500-future-million-year-human  
Channel: future  
Checkpoint: 24h  

---

## What Worked

- Question-based title showed promising CTR.
- Cinematic future hook fit the channel brand.
- Topic had strong subscriber conversion potential.

---

## What Did Not Work

- Retention may have weakened during the middle explanation section.
- Visual rhythm may need stronger reset points.

---

## Recommendations

1. Keep question-based title structure for speculative future topics.
2. Add midpoint visual reveal before technical explanation sections.
3. Track this pattern across the next 2 projects before changing the template.

---

## Memory Candidates

See:
learning/memory_update_candidates.json
```

---

# 22. Learning Review

Learning Engine은 자신의 결과를 검토해야 한다.

파일:

```text
learning/learning_review.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "stage": "LEARNING",

  "score": 92,
  "status": "PASS_WITH_NOTES",

  "checks": {
    "analytics_loaded": true,
    "quality_loaded": true,
    "growth_prediction_loaded": true,
    "prediction_comparison_created": true,
    "success_patterns_created": true,
    "failure_patterns_created": true,
    "memory_candidates_created": true,
    "template_candidates_created": true,
    "ai_employee_feedback_created": true,
    "overgeneralization_avoided": true,
    "evidence_refs_present": true
  },

  "issues": [
    {
      "severity": "LOW",
      "issue_type": "LOW_DATA_CONFIDENCE",
      "description": "Learning is based on 24h data only. Confirm at 7d and 28d checkpoints."
    }
  ]
}
```

---

# 23. Learning Scoring

Learning Score 기준:

```yaml
learning_score:
  input_completeness: 15
  prediction_comparison_quality: 15
  success_pattern_quality: 15
  failure_pattern_quality: 15
  evidence_quality: 15
  actionability: 15
  overgeneralization_control: 10
```

점수 기준:

```text
95~100
Pass

90~94
Pass with notes

80~89
Revision recommended

70~79
Learning incomplete

70 미만
Learning fail
```

---

# 24. Overgeneralization Control

Learning Engine은 과도한 일반화를 막아야 한다.

금지:

```text
한 영상의 낮은 Retention만 보고 Template 변경 확정
24h 데이터만 보고 Topic 실패 확정
한 번 성공한 Title을 모든 Topic에 강제
하나의 Provider 실패로 Provider 전체 불가 판정
```

허용:

```text
후보로 기록
추가 검증 필요 표시
다음 2~3개 Project에서 테스트 제안
Confidence LOW 또는 MEDIUM으로 유지
```

Overgeneralization Risk가 있으면 Learning Review에 기록한다.

---

# 25. Learning Validation Rules

Learning Validator는 다음을 확인해야 한다.

```text
learning/learning_report.json 존재
learning/lessons_learned.json 존재
learning/memory_update_candidates.json 존재
learning/next_project_recommendations.json 존재
reports/learning_summary.md 존재
project_id 일치
channel_id 일치
evidence_refs 존재
confidence 존재
scope 존재
recommendation 존재
Memory Candidate에 evidence 존재
Template Candidate에 auto_apply_allowed 존재
AI Evolution Handoff 존재
Overgeneralization Control 통과
```

검증 실패 시 AI_EVOLUTION 또는 COMPLETE Stage로 이동할 수 없다.

---

# 26. Handoff to Memory Engine

Learning Engine은 Memory Engine에 Memory Candidate를 전달한다.

파일:

```text
workflow/handoffs/LEARNING_to_MEMORY.json
```

예시:

```json
{
  "from_stage": "LEARNING",
  "to_stage": "MEMORY",
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "memory_candidate_refs": [
    "learning/memory_update_candidates.json"
  ],

  "instructions": [
    "Validate evidence before applying memory updates.",
    "Do not promote project-level learning to template memory without repeated evidence.",
    "Keep confidence MEDIUM unless additional projects confirm the pattern."
  ]
}
```

---

# 27. Handoff to AI Evolution Engine

Learning Engine은 AI Evolution Engine에 AI Employee 개선 후보를 전달한다.

파일:

```text
workflow/handoffs/LEARNING_to_AI_EVOLUTION.json
```

예시:

```json
{
  "from_stage": "LEARNING",
  "to_stage": "AI_EVOLUTION",
  "project_id": "20260710-093500-future-million-year-human",

  "ai_employee_feedback_ref": "learning/ai_employee_feedback.json",
  "template_improvement_candidates_ref": "learning/template_improvement_candidates.json",

  "evolution_focus": [
    "Improve Growth Engine retention prediction.",
    "Improve Story Engine midpoint retention design.",
    "Improve Visual Engine support for explanation sections."
  ],

  "constraints": [
    "Do not auto-modify employee rules without review.",
    "Do not apply template changes from a single project unless marked as experimental."
  ]
}
```

---

# 28. Handoff to Portfolio Engine

Learning Engine은 Portfolio Engine에 Channel / Topic 우선순위 Signal을 전달할 수 있다.

파일:

```text
workflow/handoffs/LEARNING_to_PORTFOLIO.json
```

예시:

```json
{
  "from_stage": "LEARNING",
  "to_stage": "PORTFOLIO",
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "portfolio_signal": {
    "topic_cluster": "future_human_evolution",
    "priority_signal": "CONTINUE_WITH_IMPROVEMENT",
    "reason": "CTR and subscriber conversion were promising, but retention needs improvement.",
    "recommended_next_action": "Produce another related topic with stronger midpoint retention design."
  }
}
```

---

# 29. Re-Learning by Checkpoint

Analytics Checkpoint가 업데이트되면 Learning도 다시 실행될 수 있다.

```text
24h Learning
↓
72h Learning
↓
7d Learning
↓
28d Learning
↓
Final Learning
```

Re-Learning 규칙:

```text
기존 Learning을 덮어쓰기 전에 snapshot을 남긴다.
새 데이터가 기존 결론을 강화하는지 약화하는지 표시한다.
Confidence를 업데이트한다.
Memory Candidate 상태를 업데이트할 수 있다.
```

예시 파일:

```text
learning/history/learning_report_24h.json
learning/history/learning_report_72h.json
learning/history/learning_report_7d.json
learning/history/learning_report_28d.json
```

---

# 30. Memory Integration

Learning Engine은 작업 전 Memory Context를 사용한다.

사용 가능한 Memory:

```text
Channel Learning Memory
Template Learning Memory
Growth Prediction Memory
Quality Failure Memory
Analytics Pattern Memory
Provider Failure Memory
AI Employee Feedback Memory
```

Learning Engine은 작업 후 Memory Candidate를 생성한다.

Memory Candidate는 반드시 다음을 가져야 한다.

```text
summary
scope
type
evidence
confidence
status
recommended_usage
```

Memory 확정은 Memory Engine이 담당한다.

---

# 31. Template Evolution Integration

Learning Engine은 Template 개선 후보를 만들지만 Template을 직접 수정하지 않는다.

Template 개선이 가능한 경우:

```text
같은 문제나 성공이 반복됨
Channel 수준을 넘어 Template 구조에 관련됨
Stage Rule 개선이 명확함
Quality / Analytics 근거가 있음
```

Template 개선이 금지되는 경우:

```text
데이터가 부족함
한 Project만의 특수 상황
Brand나 Topic에만 해당
원인 추정이 약함
```

Template Evolution은 31_AI_EVOLUTION_ENGINE 또는 Template Evolution Manager가 처리한다.

---

# 32. AI Evolution Integration

AI Evolution Engine은 Learning 결과를 사용해 다음을 개선한다.

```text
AI Employee Rule
Department Thinking Profile
Stage Review Criteria
Prompt Template
Failure Detector
Quality Checker
Growth Predictor
```

Learning Engine은 다음을 제공한다.

```text
AI Employee Feedback
Prediction Gap
Repeated Failure Pattern
Repeated Success Pattern
Suggested Rule Update
Evidence
Confidence
```

---

# 33. Error Types

Learning Engine의 Error Type:

```text
LearningInputMissingError
AnalyticsReportMissingError
GrowthPredictionMissingError
QualityReportMissingError
PredictionComparisonError
LessonExtractionError
SuccessPatternExtractionError
FailurePatternExtractionError
MemoryCandidateCreationError
TemplateCandidateCreationError
AIEmployeeFeedbackError
OvergeneralizationRiskError
LearningReportError
LearningValidationError
LearningHandoffError
```

Error 예시:

```json
{
  "error_type": "OvergeneralizationRiskError",
  "message": "Template improvement candidate is based on only one low-confidence project signal.",
  "project_id": "20260710-093500-future-million-year-human",
  "stage": "LEARNING",
  "severity": "MEDIUM",
  "suggested_fix": "Downgrade confidence to LOW and mark auto_apply_allowed=false.",
  "created_at": "2026-07-11T21:00:00"
}
```

---

# 34. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
LearningEngine
LearningInputLoader
LearningInputValidator
PredictionComparisonLoader
LearningScopeResolver
EvidenceStrengthClassifier
LessonExtractor
SuccessPatternExtractor
FailurePatternExtractor
PredictionAccuracyAnalyzer
MemoryUpdateCandidateBuilder
TemplateImprovementCandidateBuilder
ChannelImprovementCandidateBuilder
AIEmployeeFeedbackBuilder
NextProjectRecommendationBuilder
LearningReportBuilder
LearningSummaryBuilder
LearningReviewBuilder
LearningValidator
MemoryHandoffBuilder
AIEvolutionHandoffBuilder
PortfolioLearningSignalBuilder
LearningHistoryManager
OvergeneralizationChecker
LearningErrorReporter
```

---

# 35. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/30_LEARNING_ENGINE.md
→ engines/learning/
```

예시 구조:

```text
engines/
└── learning/
    ├── learning_engine.py
    ├── learning_input_loader.py
    ├── learning_input_validator.py
    ├── prediction_comparison_loader.py
    ├── learning_scope_resolver.py
    ├── evidence_strength_classifier.py
    ├── lesson_extractor.py
    ├── success_pattern_extractor.py
    ├── failure_pattern_extractor.py
    ├── prediction_accuracy_analyzer.py
    ├── memory_update_candidate_builder.py
    ├── template_improvement_candidate_builder.py
    ├── channel_improvement_candidate_builder.py
    ├── ai_employee_feedback_builder.py
    ├── next_project_recommendation_builder.py
    ├── learning_report_builder.py
    ├── learning_summary_builder.py
    ├── learning_review_builder.py
    ├── learning_validator.py
    ├── memory_handoff_builder.py
    ├── ai_evolution_handoff_builder.py
    ├── portfolio_learning_signal_builder.py
    ├── learning_history_manager.py
    ├── overgeneralization_checker.py
    └── learning_error_reporter.py
```

---

# 36. Main Public Operations

Learning Engine은 최소 다음 작업을 제공해야 한다.

```text
run_learning(project_id)
load_learning_inputs(project_id)
validate_learning_inputs(project_id)
resolve_learning_scope(project_id)
classify_evidence_strength(project_id)
extract_lessons(project_id)
extract_success_patterns(project_id)
extract_failure_patterns(project_id)
analyze_prediction_accuracy(project_id)
build_memory_update_candidates(project_id)
build_template_improvement_candidates(project_id)
build_channel_improvement_candidates(project_id)
build_ai_employee_feedback(project_id)
build_next_project_recommendations(project_id)
build_learning_report(project_id)
build_learning_summary(project_id)
build_learning_review(project_id)
validate_learning_outputs(project_id)
build_handoff_to_memory(project_id)
build_handoff_to_ai_evolution(project_id)
build_handoff_to_portfolio(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
Evidence 기반 판단
Confidence 표시
Scope 표시
Overgeneralization 방지
Memory 직접 확정 금지
Template 직접 수정 금지
AI Rule 직접 수정 금지
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 37. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Quality Report 로드
Growth Prediction 로드
Analytics Report 로드
Prediction Comparison 로드
Learning 입력 검증
성공 / 실패 요약 생성
Prediction Accuracy 기본 분석
Lessons Learned 생성
Memory Update Candidate 생성
Next Project Recommendation 생성
Learning Report 생성
Learning Summary Markdown 생성
Memory Engine Handoff 생성
AI Evolution Engine Handoff 생성
Learning Validation 수행
```

v1.0에서 하지 않아도 되는 것:

```text
자동 Template 수정
자동 AI Employee Rule 수정
고급 통계 모델링
ML 기반 성과 원인 분석
실시간 학습 대시보드
다수 Channel 자동 비교 분석
Memory 자동 확정
```

v1.0에서는 학습 후보와 다음 실행 개선안을 안정적으로 구조화하는 것이 우선이다.

---

# 38. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Quality / Growth / Analytics 결과를 로드할 수 있다.
Learning 입력을 검증할 수 있다.
Growth 예측과 실제 성과 차이를 분석할 수 있다.
성공 패턴 후보를 추출할 수 있다.
실패 패턴 후보를 추출할 수 있다.
Evidence Strength를 표시할 수 있다.
Learning Scope를 표시할 수 있다.
Lessons Learned를 생성할 수 있다.
Memory Update Candidate를 생성할 수 있다.
Template Improvement Candidate를 생성할 수 있다.
AI Employee Feedback을 생성할 수 있다.
Next Project Recommendation을 생성할 수 있다.
learning_report.json을 생성할 수 있다.
learning_summary.md를 생성할 수 있다.
Memory Engine으로 Handoff를 만들 수 있다.
AI Evolution Engine으로 Handoff를 만들 수 있다.
Learning Validation 실패 시 AI_EVOLUTION 또는 COMPLETE Stage 진행을 막을 수 있다.
```

---

# 39. Non Goals

v1.0에서 Learning Engine이 하지 않는 것:

```text
Memory 직접 확정
Template 직접 수정
AI Employee 직접 수정
성과 원인 단정
자동 수익 최적화
자동 제목 변경
자동 Thumbnail 변경
자동 Project 재실행
Analytics 직접 수집
Quality Score 재계산
```

v1.0에서는 실제 성과와 제작 결과를 근거로 다음 실행에 사용할 수 있는 학습 후보를 만드는 것이 핵심이다.

---

# 40. Critical Learning Rules

반드시 지켜야 할 규칙:

```text
1. Learning Engine은 Analytics 없이 강한 결론을 내리지 않는다.

2. Learning Engine은 Evidence 없이 Memory Candidate를 만들지 않는다.

3. Learning Engine은 한 Project 결과만으로 Template을 확정 변경하지 않는다.

4. Learning Engine은 Confidence를 반드시 표시한다.

5. Learning Engine은 Scope를 반드시 표시한다.

6. Learning Engine은 Overgeneralization을 방지해야 한다.

7. Learning Engine은 Memory를 직접 확정하지 않는다.

8. Learning Engine은 Template을 직접 수정하지 않는다.

9. Learning Engine은 AI Employee Rule을 직접 수정하지 않는다.

10. Success Pattern과 Failure Pattern을 구분한다.

11. Growth Prediction과 Actual Result를 비교한다.

12. Quality Issue와 실제 성과의 관계를 추적한다.

13. Next Project Recommendation은 Actionable해야 한다.

14. Learning Validation 실패 시 다음 Stage로 넘어가지 않는다.

15. 중요한 Learning 판단은 Report와 Handoff에 기록한다.
```

---

# 41. Final Principle

Learning Engine은 ADOS가 같은 실수를 반복하지 않게 만드는 엔진이다.

좋은 Learning은 단순한 회고가 아니다.

좋은 Learning은 실제 결과를 보고,

예측과 현실의 차이를 확인하고,

성공과 실패의 패턴을 조심스럽게 분리하고,

다음 Project가 더 나아지도록 구체적인 개선안을 만든다.

Learning Engine의 목적은 과거를 평가하는 것이 아니다.

Learning Engine의 목적은 다음 영상을 더 잘 만들고, Channel을 더 강하게 만들고, Template을 더 똑똑하게 만들고, AI Employee가 점점 더 좋은 판단을 하게 만드는 것이다.
