# 31_AI_EVOLUTION_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: AI Evolution Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 AI Evolution Engine을 정의한다.

AI Evolution Engine은 Learning Engine이 생성한 학습 결과, Memory Candidate, Template Improvement Candidate, AI Employee Feedback을 바탕으로 ADOS의 AI Employee와 Engine Rule을 더 나은 방향으로 개선하기 위한 후보를 관리하는 엔진이다.

AI Evolution Engine은 단순히 AI를 “자동으로 똑똑하게 만드는” 엔진이 아니다.

AI Evolution Engine은 다음을 관리한다.

```text
AI Employee 개선 후보
Department Thinking Profile 개선 후보
Engine Rule 개선 후보
Prompt Template 개선 후보
Quality Checker 개선 후보
Growth Prediction 기준 개선 후보
Template Evolution 요청
Memory 반영 요청
Versioning
Approval
Rollback
Evolution Report
```

AI Evolution Engine의 핵심 목적은 다음이다.

```text
Learning 결과를 실제 시스템 개선 후보로 바꾼다.
AI Employee의 판단 기준을 점진적으로 개선한다.
반복 실패를 줄인다.
반복 성공 패턴을 강화한다.
무분별한 자동 변경을 막는다.
Versioning과 Rollback을 가능하게 한다.
ADOS가 프로젝트를 반복할수록 더 좋은 판단을 하게 만든다.
```

이 문서는 다음 문서들과 직접 연결된다.

```text
04_AI_ORGANIZATION.md
05_INTER_AI_COMMUNICATION.md
06_AI_THINKING_FRAMEWORK.md
08_TEMPLATE_SYSTEM.md
13_MEMORY_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
26_QUALITY_ENGINE.md
27_GROWTH_ENGINE.md
29_ANALYTICS_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

AI Evolution Engine은 ADOS의 AI Employees와 Engine Rules를 통제된 방식으로 개선하는 엔진이다.

전체 흐름:

```text
Learning Report
↓
AI Employee Feedback
↓
Evolution Candidate
↓
Risk Check
↓
Approval
↓
Versioned Rule Update Candidate
↓
Test / Simulation
↓
Apply or Reject
↓
Rollback Available
```

AI Evolution Engine은 다음을 직접 변경하지 않는다.

```text
실제 모델 자체
외부 AI 모델 가중치
무검증 Production Rule
Template Lock Field
Project 완료 기록
Published 영상
```

AI Evolution Engine은 “개선 후보”를 만들고, 검증하고, 승인된 변경만 적용 가능하게 한다.

---

# 3. Evolution Philosophy

## 3.1 Controlled Evolution

ADOS는 스스로 무분별하게 변하면 안 된다.

모든 변화는 다음 조건을 가져야 한다.

```text
근거
범위
위험도
승인 상태
버전
Rollback 방법
검증 결과
```

## 3.2 Evidence Before Change

AI Employee Rule을 변경하려면 근거가 있어야 한다.

좋지 않은 변경:

```text
이번 영상 Retention이 낮았으니 Story Engine을 전부 바꾼다.
제목 하나가 잘 됐으니 모든 제목을 질문형으로 강제한다.
Midjourney 결과가 한 번 실패했으니 Provider 전략을 바꾼다.
```

좋은 변경:

```text
최근 3개 Future Channel 영상에서 중반 설명 구간 Retention이 반복적으로 낮았다.
Learning Reports와 Analytics Reports에서 같은 문제가 반복된다.
Story Department의 midpoint retention rule 개선 후보를 만든다.
자동 적용하지 않고 다음 2개 Project에서 실험한다.
```

## 3.3 Human Approval for High-Risk Evolution

다음 변경은 Human 또는 COO 승인 없이는 적용할 수 없다.

```text
Template 구조 변경
AI Employee 핵심 역할 변경
Quality Threshold 변경
Brand Rule 변경
Publishing Policy 변경
Auto Publish 관련 변경
Provider 교체
Full Automation 정책 변경
```

## 3.4 Evolution Is Versioned

모든 Evolution은 버전을 가져야 한다.

```text
Before Version
After Version
Change Summary
Reason
Evidence
Applied At
Rollback Target
```

버전 없는 변경은 허용하지 않는다.

---

# 4. AI Evolution Engine Responsibilities

AI Evolution Engine의 책임:

```text
Learning Handoff 로드
AI Employee Feedback 로드
Template Improvement Candidate 로드
Memory Candidate 로드
Evolution Candidate 생성
Candidate Risk 분류
Candidate Scope 분류
Candidate Approval 상태 관리
Rule Update Proposal 생성
Prompt Template Update Proposal 생성
Department Thinking Profile Update Proposal 생성
Quality Checker Update Proposal 생성
Growth Prediction Rule Update Proposal 생성
Template Evolution Request 생성
Simulation / Test Plan 생성
Rollback Plan 생성
Evolution Report 생성
Memory Engine Handoff 생성
Template System Handoff 생성
Portfolio / COO Summary 생성
```

AI Evolution Engine이 하지 않는 것:

```text
외부 AI 모델을 직접 훈련하지 않는다.
검증 없이 Rule을 자동 변경하지 않는다.
Template Lock Field를 무시하지 않는다.
Memory를 직접 확정하지 않는다.
Quality Gate를 우회하지 않는다.
Publishing을 직접 수행하지 않는다.
Analytics를 직접 수집하지 않는다.
Project 결과를 임의 수정하지 않는다.
```

---

# 5. Inputs

AI Evolution Engine의 입력:

```text
project.json
channel_snapshot.json
template_snapshot.json

learning/learning_report.json
learning/lessons_learned.json
learning/memory_update_candidates.json
learning/template_improvement_candidates.json
learning/channel_improvement_candidates.json
learning/ai_employee_feedback.json
learning/next_project_recommendations.json

workflow/handoffs/LEARNING_to_AI_EVOLUTION.json
workflow/handoffs/LEARNING_to_MEMORY.json

reports/quality_report.json
reports/analytics_report.json
reports/growth_prediction.json

docs/04_AI_ORGANIZATION.md
docs/06_AI_THINKING_FRAMEWORK.md
docs/08_TEMPLATE_SYSTEM.md
docs/13_MEMORY_ENGINE.md

workflow/memory_context_AI_EVOLUTION.json
```

필수 입력:

```text
learning/learning_report.json
learning/ai_employee_feedback.json
learning/memory_update_candidates.json
learning/next_project_recommendations.json
project.json
channel_snapshot.json
```

선택 입력:

```text
learning/template_improvement_candidates.json
learning/channel_improvement_candidates.json
Learning History
Quality Failure History
Analytics Pattern Memory
AI Employee Performance Memory
Department Review History
```

---

# 6. Outputs

AI Evolution Engine의 출력:

```text
ai_evolution/evolution_report.json
ai_evolution/evolution_candidates.json
ai_evolution/employee_update_candidates.json
ai_evolution/department_rule_update_candidates.json
ai_evolution/prompt_update_candidates.json
ai_evolution/quality_rule_update_candidates.json
ai_evolution/growth_rule_update_candidates.json
ai_evolution/template_evolution_requests.json
ai_evolution/memory_application_requests.json
ai_evolution/evolution_risk_report.json
ai_evolution/evolution_approval_queue.json
ai_evolution/evolution_test_plan.json
ai_evolution/rollback_plan.json
ai_evolution/version_manifest.json
reports/ai_evolution_summary.md
workflow/stage_results/AI_EVOLUTION_result.json
workflow/handoffs/AI_EVOLUTION_to_MEMORY.json
workflow/handoffs/AI_EVOLUTION_to_TEMPLATE.json
workflow/handoffs/AI_EVOLUTION_to_COMPLETE.json
```

v1.0 최소 출력:

```text
ai_evolution/evolution_report.json
ai_evolution/evolution_candidates.json
ai_evolution/employee_update_candidates.json
ai_evolution/evolution_risk_report.json
ai_evolution/evolution_approval_queue.json
ai_evolution/rollback_plan.json
workflow/handoffs/AI_EVOLUTION_to_COMPLETE.json
```

---

# 7. AI Evolution Execution Flow

AI Evolution Engine 실행 흐름:

```text
Load Project Context
↓
Load Learning Outputs
↓
Load AI Employee Feedback
↓
Load Memory Candidates
↓
Load Template Improvement Candidates
↓
Validate Evolution Inputs
↓
Classify Candidate Scope
↓
Classify Candidate Risk
↓
Build Evolution Candidates
↓
Build Employee Update Candidates
↓
Build Rule Update Candidates
↓
Build Prompt Update Candidates
↓
Build Template Evolution Requests
↓
Build Memory Application Requests
↓
Build Test Plan
↓
Build Rollback Plan
↓
Build Approval Queue
↓
Write Evolution Report
↓
Handoff to Memory / Template / Complete
```

---

# 8. Evolution Scopes

Evolution Scope는 변경 영향 범위를 의미한다.

사용 가능한 Scope:

```text
PROJECT
CHANNEL
TEMPLATE
COMPANY
AI_EMPLOYEE
DEPARTMENT
ENGINE
PROVIDER
QUALITY_POLICY
GROWTH_POLICY
PUBLISHING_POLICY
```

## PROJECT

특정 Project에만 적용되는 회고성 개선.

## CHANNEL

특정 Channel에 반복 적용 가능한 개선.

## TEMPLATE

Template 구조나 규칙 개선 후보.

## COMPANY

CHUNG COMPANY 전체 운영 방식 개선 후보.

## AI_EMPLOYEE

개별 AI Employee의 판단 기준 개선.

## DEPARTMENT

부서 단위 Role / Review Rule 개선.

## ENGINE

특정 Engine의 로직 개선 후보.

## PROVIDER

Midjourney, Typecast 등 Provider 사용 전략 개선.

## QUALITY_POLICY

Quality Threshold, Hard Fail, Review 기준 개선.

## GROWTH_POLICY

Title, Thumbnail, Retention, Revenue 판단 기준 개선.

## PUBLISHING_POLICY

Human Review, Auto Publish, Metadata 정책 개선.

---

# 9. Evolution Risk Levels

Evolution Candidate는 Risk Level을 가져야 한다.

```text
LOW
MEDIUM
HIGH
CRITICAL
```

## LOW

Project 또는 Channel 수준의 작은 Rule 개선.

예시:

```text
Future Channel에서 중반부 설명 전 question reset 권장
```

## MEDIUM

특정 Department나 Engine의 판단 기준 변경.

예시:

```text
Growth Engine의 Retention Prediction에 explanation-heavy penalty 추가
```

## HIGH

Template, Quality, Brand, Automation 관련 변경.

예시:

```text
Template story.yaml 구조 변경
Quality Score Threshold 변경
```

## CRITICAL

Publishing, Auto Publish, Template Lock, Company-wide 정책 변경.

예시:

```text
auto_publish_enabled 활성화
Hard Fail 기준 완화
Brand Rule 삭제
```

---

# 10. Approval Policy

Risk Level별 승인 정책:

```yaml
approval_policy:
  LOW:
    required_approval: false
    auto_apply_allowed: true
    requires_test: false

  MEDIUM:
    required_approval: true
    approver: "COO AI Employee or User"
    auto_apply_allowed: false
    requires_test: true

  HIGH:
    required_approval: true
    approver: "User"
    auto_apply_allowed: false
    requires_test: true
    requires_rollback_plan: true

  CRITICAL:
    required_approval: true
    approver: "User"
    auto_apply_allowed: false
    requires_test: true
    requires_rollback_plan: true
    requires_manual_review: true
```

v1.0 기본값:

```text
LOW도 자동 적용하지 않고 Candidate로 유지한다.
사람이 확인한 후 적용하는 구조를 우선한다.
```

---

# 11. Evolution Candidate Types

Evolution Candidate 유형:

```text
employee_rule_update
department_thinking_update
engine_rule_update
prompt_template_update
quality_checker_update
growth_prediction_update
brand_guardrail_update
template_improvement_request
memory_application_request
provider_strategy_update
workflow_policy_update
automation_policy_update
```

---

# 12. evolution_candidates.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "AI_EVOLUTION",

  "candidates": [
    {
      "candidate_id": "EVO-CAND-000001",
      "type": "growth_prediction_update",
      "scope": "ENGINE",
      "target": "GrowthEngine.RetentionPotentialAnalyzer",

      "summary": "Apply a penalty to retention prediction when the middle section contains long explanation blocks without a visual reset.",

      "reason": "Growth Engine predicted high retention, but Analytics showed lower retention in the middle section.",

      "evidence": [
        "learning/ai_employee_feedback.json",
        "analytics/prediction_comparison.json",
        "analytics/retention_report.json",
        "reports/growth_prediction.json"
      ],

      "risk_level": "MEDIUM",
      "confidence": "MEDIUM",

      "recommended_action": "Create rule update candidate and test on next two Future Channel projects.",

      "approval": {
        "required": true,
        "status": "PENDING",
        "approver": "COO AI Employee or User"
      },

      "auto_apply_allowed": false,
      "created_at": "2026-07-11T22:00:00"
    }
  ]
}
```

---

# 13. Employee Update Candidates

AI Employee 개선 후보는 특정 AI Employee 또는 Department에 적용된다.

파일:

```text
ai_evolution/employee_update_candidates.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",

  "employee_updates": [
    {
      "update_id": "EMP-UPD-000001",
      "employee_or_department": "Story Department",
      "related_stage": "STORY",

      "update_type": "thinking_rule_update",

      "current_issue": "Story hook was strong, but middle retention design may need stronger reset points.",

      "proposed_rule": "When a section contains technical explanation longer than 90 seconds, add a question reset, contrast, or visual reveal before the explanation continues.",

      "expected_benefit": "Improve middle retention and reduce drop-off during explanation-heavy sections.",

      "evidence": [
        "learning/ai_employee_feedback.json",
        "analytics/retention_report.json",
        "story/outline.json"
      ],

      "confidence": "LOW",
      "risk_level": "MEDIUM",

      "test_plan_ref": "ai_evolution/evolution_test_plan.json",
      "approval_status": "PENDING"
    }
  ]
}
```

---

# 14. Department Rule Update Candidates

Department Rule은 부서 단위 운영 기준이다.

파일:

```text
ai_evolution/department_rule_update_candidates.json
```

예시:

```json
{
  "department_rule_updates": [
    {
      "update_id": "DEPT-RULE-000001",
      "department": "Growth Department",
      "rule_area": "retention_prediction",

      "proposed_rule": "If the outline has more than two consecutive explanation sections without contrast, lower retention_potential by 5 to 10 points.",

      "reason": "Analytics showed lower retention than predicted when middle explanation sections were long.",

      "evidence": [
        "analytics/prediction_comparison.json",
        "learning/prediction_accuracy_report.json"
      ],

      "risk_level": "MEDIUM",
      "confidence": "MEDIUM",
      "auto_apply_allowed": false
    }
  ]
}
```

---

# 15. Prompt Update Candidates

Prompt Template 개선 후보는 AI Employee 또는 Engine이 사용하는 Prompt 규칙을 개선한다.

파일:

```text
ai_evolution/prompt_update_candidates.json
```

Schema:

```json
{
  "prompt_update_candidates": [
    {
      "update_id": "PROMPT-UPD-000001",
      "target_prompt": "prompts/story/story_engine_system_prompt.md",
      "related_engine": "StoryEngine",

      "current_prompt_issue": "Prompt does not strongly require midpoint retention reset for explanation-heavy sections.",

      "proposed_prompt_addition": "Before writing long explanation sections, insert a question reset, contrast, or visual reveal to maintain retention.",

      "expected_effect": "Improve retention structure in future scripts.",

      "evidence": [
        "learning/failure_patterns.json",
        "analytics/retention_report.json"
      ],

      "risk_level": "MEDIUM",
      "confidence": "LOW",
      "requires_human_review": true,
      "auto_apply_allowed": false
    }
  ]
}
```

---

# 16. Quality Rule Update Candidates

Quality Rule 개선 후보는 Quality Engine 기준을 조정한다.

파일:

```text
ai_evolution/quality_rule_update_candidates.json
```

예시:

```json
{
  "quality_rule_updates": [
    {
      "update_id": "QUAL-RULE-000001",
      "target_checker": "StoryQualityChecker",
      "rule_area": "middle_retention",

      "proposed_rule": "Flag explanation-heavy middle sections without question reset as MEDIUM retention risk.",

      "reason": "Retention issue appeared after the hook in a long explanation section.",

      "evidence": [
        "reports/analytics_report.json",
        "learning/failure_patterns.json"
      ],

      "risk_level": "MEDIUM",
      "confidence": "LOW",
      "auto_apply_allowed": false
    }
  ]
}
```

---

# 17. Growth Rule Update Candidates

Growth Rule 개선 후보는 Growth Engine의 예측 기준을 조정한다.

파일:

```text
ai_evolution/growth_rule_update_candidates.json
```

예시:

```json
{
  "growth_rule_updates": [
    {
      "update_id": "GROWTH-RULE-000001",
      "target_component": "RetentionPotentialAnalyzer",

      "proposed_rule": "Reduce retention potential when script has more than 120 seconds of explanation without open loop or visual reset.",

      "expected_effect": "Reduce overestimation of retention for explanation-heavy videos.",

      "evidence": [
        "analytics/prediction_comparison.json",
        "learning/prediction_accuracy_report.json"
      ],

      "risk_level": "MEDIUM",
      "confidence": "MEDIUM",
      "test_required": true,
      "auto_apply_allowed": false
    }
  ]
}
```

---

# 18. Template Evolution Requests

Template 개선 요청은 Template System으로 넘기는 후보이다.

파일:

```text
ai_evolution/template_evolution_requests.json
```

Schema:

```json
{
  "template_evolution_requests": [
    {
      "request_id": "TPL-EVO-000001",
      "template_id": "future_documentary_template",
      "target_file": "templates/future_documentary_template/story.yaml",

      "request_type": "story_structure_rule_candidate",

      "summary": "Add optional midpoint visual reset requirement for explanation-heavy Future Channel videos.",

      "reason": "Learning suggests middle retention may weaken without a visual or question reset.",

      "evidence": [
        "learning/template_improvement_candidates.json",
        "analytics/retention_report.json",
        "reports/analytics_report.json"
      ],

      "confidence": "LOW",
      "risk_level": "HIGH",

      "auto_apply_allowed": false,
      "requires_human_approval": true,

      "recommended_next_step": "Test in the next 2 Future Channel projects before applying to template."
    }
  ]
}
```

규칙:

```text
Template Evolution Request는 자동 적용하지 않는다.
Template Lock Field를 건드리면 안 된다.
반복 증거가 부족하면 confidence LOW로 유지한다.
```

---

# 19. Memory Application Requests

Memory Application Request는 Memory Engine으로 넘길 실제 반영 요청이다.

파일:

```text
ai_evolution/memory_application_requests.json
```

Schema:

```json
{
  "memory_application_requests": [
    {
      "request_id": "MEM-APP-000001",
      "source_candidate_id": "MEM-CAND-000001",
      "target_scope": "CHANNEL",
      "target_memory": "channels/future/memory.yaml",

      "summary": "Store question-based title pattern as a Future Channel candidate memory.",

      "evidence": [
        "learning/memory_update_candidates.json",
        "reports/analytics_report.json"
      ],

      "confidence": "MEDIUM",
      "status": "READY_FOR_MEMORY_ENGINE_REVIEW",

      "instruction": "Apply as CANDIDATE memory, not LOCKED memory."
    }
  ]
}
```

---

# 20. Evolution Risk Report

파일:

```text
ai_evolution/evolution_risk_report.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",

  "risk_summary": {
    "highest_risk": "HIGH",
    "critical_count": 0,
    "high_count": 1,
    "medium_count": 3,
    "low_count": 2
  },

  "risks": [
    {
      "candidate_id": "TPL-EVO-000001",
      "risk_level": "HIGH",
      "risk_type": "TEMPLATE_CHANGE_RISK",
      "description": "Template change based on limited evidence may overfit to one project.",
      "mitigation": "Do not apply automatically. Test across additional projects."
    }
  ],

  "overall_recommendation": "Do not auto-apply high-risk changes. Keep them as candidates pending more evidence."
}
```

---

# 21. Evolution Approval Queue

파일:

```text
ai_evolution/evolution_approval_queue.json
```

Schema:

```json
{
  "approval_queue": [
    {
      "approval_id": "APPROVAL-000001",
      "candidate_id": "EVO-CAND-000001",
      "candidate_type": "growth_prediction_update",

      "approval_required": true,
      "approver": "COO AI Employee or User",
      "status": "PENDING",

      "decision_options": [
        "approve_for_test",
        "approve_for_apply",
        "reject",
        "defer",
        "request_more_evidence"
      ],

      "recommended_decision": "approve_for_test",

      "reason": "Candidate has medium confidence but should be tested before applying globally."
    }
  ]
}
```

---

# 22. Evolution Test Plan

AI Evolution은 적용 전 테스트 계획을 만들 수 있다.

파일:

```text
ai_evolution/evolution_test_plan.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",

  "tests": [
    {
      "test_id": "EVO-TEST-000001",
      "candidate_id": "EVO-CAND-000001",
      "test_type": "next_project_observation",

      "test_scope": "Future Channel next 2 projects",

      "hypothesis": "Adding midpoint question reset before long explanation sections will improve retention.",

      "success_metrics": [
        "average_percentage_viewed",
        "middle_retention_drop",
        "watch_time_hours"
      ],

      "minimum_data_required": [
        "2 projects",
        "7d analytics checkpoint"
      ],

      "apply_mode": "experimental_rule",
      "rollback_required": true
    }
  ]
}
```

v1.0에서는 대부분 실제 자동 A/B 테스트가 아니라 다음 Project 관찰형 테스트로 시작한다.

---

# 23. Rollback Plan

모든 적용 가능한 Evolution은 Rollback Plan을 가져야 한다.

파일:

```text
ai_evolution/rollback_plan.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",

  "rollback_items": [
    {
      "candidate_id": "EVO-CAND-000001",
      "target": "GrowthEngine.RetentionPotentialAnalyzer",

      "before_version": "1.0.0",
      "after_version": "1.0.1-candidate",

      "rollback_method": "Restore previous rule version from version_manifest.json.",

      "rollback_trigger": [
        "Next 2 projects show no retention improvement.",
        "Quality score decreases due to over-penalizing explanation sections."
      ],

      "rollback_available": true
    }
  ]
}
```

Rollback Plan이 없는 HIGH 또는 CRITICAL 변경은 승인될 수 없다.

---

# 24. Version Manifest

AI Evolution 변경은 Version Manifest에 기록한다.

파일:

```text
ai_evolution/version_manifest.json
```

Schema:

```json
{
  "version_manifest": [
    {
      "version_id": "EVO-VERSION-000001",
      "candidate_id": "EVO-CAND-000001",

      "target": "GrowthEngine.RetentionPotentialAnalyzer",
      "before_version": "1.0.0",
      "proposed_version": "1.0.1-candidate",

      "change_summary": "Add explanation-heavy section penalty to retention prediction.",

      "status": "CANDIDATE",

      "evidence": [
        "learning/ai_employee_feedback.json",
        "analytics/prediction_comparison.json"
      ],

      "approval_status": "PENDING",
      "applied_at": null,
      "rollback_ref": "ai_evolution/rollback_plan.json"
    }
  ]
}
```

---

# 25. Evolution Report

AI Evolution Report는 Stage 결과의 중심 파일이다.

파일:

```text
ai_evolution/evolution_report.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "AI_EVOLUTION",

  "status": "COMPLETED_WITH_CANDIDATES",

  "summary": {
    "total_candidates": 6,
    "auto_applied": 0,
    "pending_approval": 4,
    "rejected": 0,
    "deferred": 2,

    "main_evolution_opportunities": [
      "Improve Growth Engine retention prediction.",
      "Improve Story Department midpoint retention design.",
      "Store question-based title pattern as Channel Memory candidate."
    ],

    "main_risks": [
      "Template changes should not be applied from a single project.",
      "Retention conclusion needs more projects to confirm."
    ],

    "recommended_next_action": "Approve low-risk memory candidates and test medium-risk retention rules in next Future Channel projects."
  },

  "handoffs": {
    "memory": "workflow/handoffs/AI_EVOLUTION_to_MEMORY.json",
    "template": "workflow/handoffs/AI_EVOLUTION_to_TEMPLATE.json",
    "complete": "workflow/handoffs/AI_EVOLUTION_to_COMPLETE.json"
  },

  "created_at": "2026-07-11T22:00:00"
}
```

---

# 26. AI Evolution Summary Markdown

사람이 읽기 좋은 요약 파일:

```text
reports/ai_evolution_summary.md
```

권장 형식:

```markdown
# AI Evolution Summary

Project ID: 20260710-093500-future-million-year-human  
Channel: future  

---

## Main Evolution Candidates

1. Growth Engine retention prediction rule update
2. Story Department midpoint retention rule update
3. Future Channel question-based title memory candidate

---

## Do Not Auto Apply

- Template story.yaml change
- Quality threshold changes
- Auto publishing policies

---

## Recommended Next Step

Test midpoint retention reset in the next 2 Future Channel projects.
```

---

# 27. Handoff to Memory Engine

AI Evolution Engine은 Memory Application Requests를 Memory Engine에 전달한다.

파일:

```text
workflow/handoffs/AI_EVOLUTION_to_MEMORY.json
```

Schema:

```json
{
  "from_stage": "AI_EVOLUTION",
  "to_stage": "MEMORY",
  "project_id": "20260710-093500-future-million-year-human",

  "memory_application_requests_ref": "ai_evolution/memory_application_requests.json",
  "memory_candidates_ref": "learning/memory_update_candidates.json",

  "instructions": [
    "Apply only approved or low-risk candidate memories.",
    "Do not promote single-project learning to LOCKED memory.",
    "Keep uncertain patterns as CANDIDATE."
  ]
}
```

---

# 28. Handoff to Template System

Template Evolution Requests는 Template System으로 전달된다.

파일:

```text
workflow/handoffs/AI_EVOLUTION_to_TEMPLATE.json
```

Schema:

```json
{
  "from_stage": "AI_EVOLUTION",
  "to_stage": "TEMPLATE_SYSTEM",
  "project_id": "20260710-093500-future-million-year-human",

  "template_evolution_requests_ref": "ai_evolution/template_evolution_requests.json",

  "instructions": [
    "Do not apply template changes automatically.",
    "Require repeated evidence before template-level update.",
    "Respect Template Lock Rules.",
    "Create new template version if approved."
  ]
}
```

---

# 29. Handoff to Complete

AI Evolution 이후 Project는 COMPLETE 상태로 이동할 수 있다.

파일:

```text
workflow/handoffs/AI_EVOLUTION_to_COMPLETE.json
```

Schema:

```json
{
  "from_stage": "AI_EVOLUTION",
  "to_stage": "COMPLETE",
  "project_id": "20260710-093500-future-million-year-human",

  "completion_ready": true,

  "required_final_outputs": [
    "learning/learning_report.json",
    "ai_evolution/evolution_report.json",
    "ai_evolution/evolution_candidates.json",
    "workflow/handoffs/AI_EVOLUTION_to_MEMORY.json"
  ],

  "notes": [
    "Project learning and evolution candidates have been generated.",
    "Project can be marked COMPLETE after required handoffs are recorded."
  ]
}
```

---

# 30. Evolution Validation Rules

AI Evolution Validator는 다음을 확인해야 한다.

```text
ai_evolution/evolution_report.json 존재
ai_evolution/evolution_candidates.json 존재
ai_evolution/employee_update_candidates.json 존재
ai_evolution/evolution_risk_report.json 존재
ai_evolution/evolution_approval_queue.json 존재
ai_evolution/rollback_plan.json 존재
project_id 일치
channel_id 일치
candidate_id 중복 없음
각 Candidate에 type 존재
각 Candidate에 scope 존재
각 Candidate에 evidence 존재
각 Candidate에 risk_level 존재
각 Candidate에 confidence 존재
HIGH 이상 Candidate에 approval_required=true
HIGH 이상 Candidate에 rollback_plan 존재
Template Evolution Request는 auto_apply_allowed=false
Memory Application Request는 Memory Engine Handoff에 포함
Complete Handoff 존재
```

검증 실패 시 COMPLETE Stage로 이동할 수 없다.

---

# 31. Auto Apply Policy

v1.0 기본 정책:

```text
auto_apply_evolution: false
```

즉, Evolution Candidate는 생성되지만 자동 적용하지 않는다.

예외적으로 나중에 다음 조건을 만족하면 LOW Risk 변경만 자동 적용을 고려할 수 있다.

```text
반복 증거 존재
Rollback 가능
Quality에 영향 낮음
Brand에 영향 없음
Template Lock과 무관
Human Policy에서 허용
```

v1.0에서는 다음을 자동 적용하지 않는다.

```text
Template 변경
Quality 기준 변경
Brand 기준 변경
Publishing 정책 변경
AI Employee 핵심 역할 변경
Provider 전략 변경
Auto Publish 정책 변경
```

---

# 32. Integration with Memory Engine

AI Evolution Engine은 Memory Engine에 다음을 전달한다.

```text
Memory Application Request
Evidence
Confidence
Scope
Recommended Status
```

Memory Engine은 다음을 결정한다.

```text
적용
보류
거절
Confidence 조정
Scope 조정
중복 병합
```

AI Evolution Engine은 Memory를 직접 확정하지 않는다.

---

# 33. Integration with Template System

AI Evolution Engine은 Template System에 개선 요청을 전달한다.

Template System은 다음을 검토한다.

```text
Template Lock 위반 여부
Version 증가 필요 여부
Backward Compatibility
Channel 영향 범위
Human Approval 여부
```

AI Evolution Engine은 Template을 직접 수정하지 않는다.

---

# 34. Integration with AI Organization

AI Evolution Engine은 AI Employee와 Department에 대한 Feedback을 생성한다.

적용 대상 예시:

```text
COO AI Employee
Project Manager Employee
Research Department
Story Department
Visual Department
Growth Department
Quality Department
Learning Department
```

Feedback은 다음으로 구성된다.

```text
무엇을 개선할지
왜 개선해야 하는지
어떤 증거가 있는지
어떤 위험이 있는지
언제 테스트할지
```

AI Employee의 핵심 역할과 권한은 Human Approval 없이 변경하지 않는다.

---

# 35. Integration with Workflow Orchestrator

Workflow Orchestrator는 AI Evolution 결과에 따라 Project를 COMPLETE로 전환한다.

전환 조건:

```text
Learning Report 존재
Evolution Report 존재
Required Handoffs 존재
Evolution Validation 통과
Blocking Approval 없음
```

Approval이 필요한 Candidate가 있어도 Project Completion은 가능하다.

단, 다음은 Blocking이다.

```text
Evolution Report 생성 실패
Memory Handoff 생성 실패
Complete Handoff 생성 실패
Validation 실패
```

---

# 36. Evolution Error Types

AI Evolution Engine의 Error Type:

```text
AIEvolutionInputMissingError
LearningHandoffMissingError
AIEmployeeFeedbackMissingError
EvolutionCandidateCreationError
EvolutionRiskClassificationError
ApprovalQueueError
RollbackPlanMissingError
VersionManifestError
TemplateEvolutionRequestError
MemoryApplicationRequestError
EmployeeUpdateCandidateError
PromptUpdateCandidateError
QualityRuleUpdateCandidateError
GrowthRuleUpdateCandidateError
EvolutionReportError
EvolutionValidationError
EvolutionHandoffError
```

Error 예시:

```json
{
  "error_type": "RollbackPlanMissingError",
  "message": "High-risk template evolution request has no rollback plan.",
  "project_id": "20260710-093500-future-million-year-human",
  "stage": "AI_EVOLUTION",
  "severity": "HIGH",
  "suggested_fix": "Create rollback plan before adding candidate to approval queue.",
  "created_at": "2026-07-11T22:00:00"
}
```

---

# 37. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
AIEvolutionEngine
AIEvolutionInputLoader
AIEvolutionInputValidator
LearningFeedbackLoader
EvolutionCandidateBuilder
EvolutionScopeClassifier
EvolutionRiskClassifier
EmployeeUpdateCandidateBuilder
DepartmentRuleUpdateCandidateBuilder
PromptUpdateCandidateBuilder
QualityRuleUpdateCandidateBuilder
GrowthRuleUpdateCandidateBuilder
TemplateEvolutionRequestBuilder
MemoryApplicationRequestBuilder
EvolutionRiskReportBuilder
EvolutionApprovalQueueBuilder
EvolutionTestPlanBuilder
RollbackPlanBuilder
VersionManifestBuilder
EvolutionReportBuilder
AIEvolutionSummaryBuilder
AIEvolutionValidator
MemoryEvolutionHandoffBuilder
TemplateEvolutionHandoffBuilder
CompleteHandoffBuilder
AIEvolutionErrorReporter
```

---

# 38. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/31_AI_EVOLUTION_ENGINE.md
→ engines/ai_evolution/
```

예시 구조:

```text
engines/
└── ai_evolution/
    ├── ai_evolution_engine.py
    ├── ai_evolution_input_loader.py
    ├── ai_evolution_input_validator.py
    ├── learning_feedback_loader.py
    ├── evolution_candidate_builder.py
    ├── evolution_scope_classifier.py
    ├── evolution_risk_classifier.py
    ├── employee_update_candidate_builder.py
    ├── department_rule_update_candidate_builder.py
    ├── prompt_update_candidate_builder.py
    ├── quality_rule_update_candidate_builder.py
    ├── growth_rule_update_candidate_builder.py
    ├── template_evolution_request_builder.py
    ├── memory_application_request_builder.py
    ├── evolution_risk_report_builder.py
    ├── evolution_approval_queue_builder.py
    ├── evolution_test_plan_builder.py
    ├── rollback_plan_builder.py
    ├── version_manifest_builder.py
    ├── evolution_report_builder.py
    ├── ai_evolution_summary_builder.py
    ├── ai_evolution_validator.py
    ├── memory_evolution_handoff_builder.py
    ├── template_evolution_handoff_builder.py
    ├── complete_handoff_builder.py
    └── ai_evolution_error_reporter.py
```

---

# 39. Main Public Operations

AI Evolution Engine은 최소 다음 작업을 제공해야 한다.

```text
run_ai_evolution(project_id)
load_ai_evolution_inputs(project_id)
validate_ai_evolution_inputs(project_id)
load_learning_feedback(project_id)
build_evolution_candidates(project_id)
classify_evolution_scope(project_id)
classify_evolution_risk(project_id)
build_employee_update_candidates(project_id)
build_department_rule_update_candidates(project_id)
build_prompt_update_candidates(project_id)
build_quality_rule_update_candidates(project_id)
build_growth_rule_update_candidates(project_id)
build_template_evolution_requests(project_id)
build_memory_application_requests(project_id)
build_evolution_risk_report(project_id)
build_approval_queue(project_id)
build_evolution_test_plan(project_id)
build_rollback_plan(project_id)
build_version_manifest(project_id)
build_evolution_report(project_id)
build_ai_evolution_summary(project_id)
validate_ai_evolution_outputs(project_id)
build_handoff_to_memory(project_id)
build_handoff_to_template(project_id)
build_handoff_to_complete(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
Evidence 확인
Scope 표시
Risk Level 표시
Confidence 표시
Approval 필요 여부 표시
Rollback 가능성 표시
자동 적용 금지
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 40. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Learning Output 로드
AI Employee Feedback 로드
Evolution 입력 검증
Evolution Candidate 생성
Employee Update Candidate 생성
Risk Level 분류
Approval Queue 생성
Rollback Plan 생성
Version Manifest 생성
Evolution Report 생성
AI Evolution Summary 생성
Memory Engine Handoff 생성
Complete Handoff 생성
AI Evolution Validation 수행
```

v1.0에서 하지 않아도 되는 것:

```text
외부 AI 모델 직접 학습
AI Employee Rule 자동 적용
Template 자동 수정
Quality 기준 자동 변경
Brand 기준 자동 변경
Publishing 정책 자동 변경
Auto Publish 활성화
고급 실험 플랫폼
자동 A/B 테스트 실행
```

v1.0에서는 Learning 결과를 안전한 개선 후보로 구조화하고, 다음 적용을 위한 승인 / 테스트 / 롤백 구조를 만드는 것이 우선이다.

---

# 41. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Learning 결과를 로드할 수 있다.
AI Employee Feedback을 로드할 수 있다.
Evolution 입력을 검증할 수 있다.
Evolution Candidate를 생성할 수 있다.
Evolution Scope를 분류할 수 있다.
Evolution Risk를 분류할 수 있다.
AI Employee Update Candidate를 생성할 수 있다.
Department Rule Update Candidate를 생성할 수 있다.
Prompt Update Candidate를 생성할 수 있다.
Template Evolution Request를 생성할 수 있다.
Memory Application Request를 생성할 수 있다.
Approval Queue를 생성할 수 있다.
Rollback Plan을 생성할 수 있다.
Version Manifest를 생성할 수 있다.
Evolution Report를 생성할 수 있다.
AI Evolution Summary를 생성할 수 있다.
Memory Engine으로 Handoff를 만들 수 있다.
Template System으로 Handoff를 만들 수 있다.
Complete Stage로 Handoff를 만들 수 있다.
AI Evolution Validation 실패 시 COMPLETE Stage 진행을 막을 수 있다.
```

---

# 42. Non Goals

v1.0에서 AI Evolution Engine이 하지 않는 것:

```text
외부 AI 모델 가중치 학습
무검증 자동 자기수정
Template 직접 수정
Memory 직접 확정
AI Employee 핵심 역할 직접 변경
Quality Gate 우회
Brand Rule 우회
Publishing Policy 변경
Auto Publish 활성화
성과 원인 단정
```

v1.0에서는 안전한 Evolution Candidate와 승인 가능한 개선 구조를 만드는 것이 핵심이다.

---

# 43. Critical AI Evolution Rules

반드시 지켜야 할 규칙:

```text
1. AI Evolution Engine은 Learning 결과 없이 실행하지 않는다.

2. Evidence 없는 Evolution Candidate를 만들지 않는다.

3. 모든 Candidate는 Scope를 가져야 한다.

4. 모든 Candidate는 Risk Level을 가져야 한다.

5. 모든 Candidate는 Confidence를 가져야 한다.

6. HIGH 이상 변경은 Approval이 필요하다.

7. HIGH 이상 변경은 Rollback Plan이 필요하다.

8. Template 변경은 자동 적용하지 않는다.

9. Memory는 직접 확정하지 않는다.

10. AI Employee 핵심 역할은 자동 변경하지 않는다.

11. Quality 기준은 자동 변경하지 않는다.

12. Brand 기준은 자동 변경하지 않는다.

13. Auto Publish 정책은 자동 변경하지 않는다.

14. Version Manifest 없이 변경하지 않는다.

15. Evolution Validation 실패 시 COMPLETE Stage로 넘어가지 않는다.
```

---

# 44. Final Principle

AI Evolution Engine은 ADOS가 시간이 지날수록 더 좋은 회사처럼 일하게 만드는 엔진이다.

좋은 AI Evolution은 무작정 자동화하지 않는다.

좋은 AI Evolution은 Learning을 근거로 삼고,

성공과 실패를 구분하고,

작은 개선 후보를 만들고,

위험한 변경을 막고,

승인과 버전을 남기고,

필요하면 되돌릴 수 있게 만든다.

AI Evolution Engine의 목적은 AI가 마음대로 변하게 하는 것이 아니다.

AI Evolution Engine의 목적은 CHUNG COMPANY의 AI Employees가 반복 작업을 통해 더 정확하고, 더 신중하고, 더 높은 품질의 판단을 하도록 안전하게 진화시키는 것이다.
