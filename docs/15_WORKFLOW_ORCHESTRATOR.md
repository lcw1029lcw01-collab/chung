# 15_WORKFLOW_ORCHESTRATOR.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Workflow Orchestrator Specification  

---

# 1. Purpose

이 문서는 ADOS의 Workflow Orchestrator를 정의한다.

Workflow Orchestrator는 Project가 어떤 순서로 실행되고, 어떤 Stage가 언제 시작되고, 어떤 조건에서 다음 Stage로 넘어가며, 실패 시 어떻게 Retry / Auto Fix / Escalation할지 결정하는 실행 관리자이다.

ADOS는 각 Engine이 마음대로 실행되는 구조가 아니다.

Project는 반드시 Workflow Orchestrator의 통제를 받아 순서대로 진행되어야 한다.

Workflow Orchestrator는 다음을 담당한다.

```text
Project 실행 순서 관리
Stage 시작 조건 확인
Stage별 Input 검증
Stage별 Output 검증
Stage Owner 확인
Task Request 생성
Memory Context 요청
Thinking / Communication 기록 연결
Stage 실행 요청
Stage 결과 수신
State Transition 요청
Quality Gate 확인
Auto Fix 흐름 관리
Retry Count 관리
Escalation Trigger 감지
Workflow Logs 기록
Project 진행 상태 보고
```

이 문서는 다음 문서들과 직접 연결된다.

```text
03_ARCHITECTURE.md
04_AI_ORGANIZATION.md
05_INTER_AI_COMMUNICATION.md
06_AI_THINKING_FRAMEWORK.md
07_PROJECT_SPEC.md
12_PROJECT_ENGINE.md
13_MEMORY_ENGINE.md
14_PROVIDER_ENGINE.md
16_TIMELINE_ENGINE.md
17_RESEARCH_ENGINE.md
18_KNOWLEDGE_ENGINE.md
19_STORY_ENGINE.md
20_DIRECTION_ENGINE.md
21_VISUAL_ENGINE.md
22_MOTION_ENGINE.md
23_VOICE_ENGINE.md
24_SUBTITLE_ENGINE.md
25_EDITING_ENGINE.md
26_QUALITY_ENGINE.md
28_PUBLISHING_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Workflow Orchestrator는 Project의 실행 흐름을 관리하는 중앙 관리자이다.

전체 흐름:

```text
Project Engine
↓
Workflow Orchestrator
↓
Stage Runner
↓
Department / Engine
↓
Stage Result
↓
Validation
↓
State Transition
```

Workflow Orchestrator는 직접 콘텐츠를 만들지 않는다.

Workflow Orchestrator는 다음을 결정한다.

```text
지금 어떤 Stage를 실행해야 하는가?
이 Stage를 실행할 준비가 되었는가?
필수 입력 파일이 존재하는가?
어떤 Department가 Owner인가?
어떤 Engine을 호출해야 하는가?
Stage 결과가 유효한가?
다음 Stage로 넘어가도 되는가?
품질 문제가 있으면 어떻게 수정할 것인가?
언제 Escalation해야 하는가?
```

---

# 3. Workflow Philosophy

## 3.1 Orchestrator Controls Flow

모든 Stage 실행은 Workflow Orchestrator를 통해 이루어진다.

금지:

```text
Story Engine이 임의로 실행됨
Visual Engine이 Timeline 없이 실행됨
Voice Engine이 Script 없이 실행됨
Quality Gate 없이 Package 생성
```

허용:

```text
Workflow Orchestrator가 Stage 조건 확인
↓
Stage 실행 요청
↓
Output 검증
↓
다음 Stage 결정
```

## 3.2 Engines Do Work, Orchestrator Controls Order

Engine은 작업을 수행한다.

Orchestrator는 순서와 조건을 통제한다.

```text
Story Engine
→ Story 작성

Workflow Orchestrator
→ Story Stage를 실행할지, 완료되었는지, 다음 Stage로 넘어갈지 판단
```

## 3.3 Partial Fix Before Full Regeneration

실패 시 전체 Project를 다시 만들지 않는다.

Workflow Orchestrator는 문제 위치를 좁히고 부분 수정 흐름을 만든다.

## 3.4 State Must Be Explicit

Project의 현재 상태와 Workflow의 진행 상태는 파일로 기록되어야 한다.

---

# 4. Workflow Orchestrator Responsibilities

Workflow Orchestrator의 책임은 다음과 같다.

```text
Workflow 시작
Workflow 중지
Workflow 재개
현재 Stage 확인
다음 Stage 결정
Stage 실행 조건 검증
Stage별 Required Input 검증
Stage별 Expected Output 검증
Stage Owner 확인
Task Request 생성
Handoff 확인
Review 확인
Approval 확인
Open Critical Message 확인
Open Escalation 확인
Retry Count 확인
Auto Fix 흐름 생성
Escalation 생성
Project Engine에 State Change 요청
Portfolio에 진행 상태 보고
Workflow Report 생성
```

Workflow Orchestrator가 하지 않는 것:

```text
Project를 직접 생성하지 않는다.
Story를 직접 작성하지 않는다.
이미지 Prompt를 직접 작성하지 않는다.
Provider를 직접 호출하지 않는다.
Quality Score를 직접 계산하지 않는다.
Template을 직접 수정하지 않는다.
Memory를 직접 확정하지 않는다.
Final Publish를 직접 수행하지 않는다.
```

---

# 5. Workflow Stages

기본 Stage 순서:

```text
INITIALIZED
↓
RESEARCH
↓
KNOWLEDGE
↓
STORY
↓
DIRECTION
↓
TIMELINE
↓
VISUAL
↓
MOTION
↓
VOICE
↓
SUBTITLE
↓
EDITING
↓
QUALITY
↓
PACKAGE
↓
READY
↓
PUBLISHED
↓
ANALYTICS
↓
LEARNING
↓
COMPLETE
```

조건부 Stage:

```text
AUTO_FIX
ESCALATION
HUMAN_REVIEW
```

---

# 6. Stage Registry

Workflow Orchestrator는 Stage Registry를 가져야 한다.

Stage Registry는 각 Stage의 Owner, Required Inputs, Expected Outputs, Engine, Next Stage를 정의한다.

예시:

```yaml
stages:
  RESEARCH:
    owner_department: Research Department
    engine: ResearchEngine
    required_inputs:
      - topic.json
      - channel_snapshot.json
      - template_snapshot.json
    expected_outputs:
      - research/research.json
      - research/sources.json
      - research/facts.json
    next_stage: KNOWLEDGE

  STORY:
    owner_department: Story Department
    engine: StoryEngine
    required_inputs:
      - knowledge/knowledge.json
      - knowledge/claims.json
      - knowledge/fact_check.json
      - channel_snapshot.json
    expected_outputs:
      - story/outline.json
      - story/hook.json
      - story/script_master.json
      - story/script_master.md
      - story/story_review.json
    next_stage: DIRECTION

  QUALITY:
    owner_department: Quality Department
    engine: QualityEngine
    required_inputs:
      - project.json
      - timeline/timeline.json
      - channel_snapshot.json
    expected_outputs:
      - reports/quality_report.json
    next_stage: PACKAGE
    conditional_next:
      auto_fix: AUTO_FIX
      fail: ESCALATION
```

---

# 7. Workflow Run Modes

Workflow는 다음 실행 모드를 가진다.

```text
manual
semi_auto
auto_until_quality
auto_until_package
full_auto
```

## 7.1 manual

사용자가 각 Stage 실행을 승인한다.

## 7.2 semi_auto

일부 Stage는 자동으로 실행하고, 핵심 Stage는 사용자 확인을 받는다.

## 7.3 auto_until_quality

QUALITY 전까지 자동 실행하고 Quality 단계에서 멈춘다.

## 7.4 auto_until_package

Package 생성까지 자동 실행하지만 Publish는 하지 않는다.

## 7.5 full_auto

Publish까지 자동화한다.

v1.0에서는 `full_auto`를 기본 사용하지 않는다.

기본값:

```text
auto_until_package
또는
human_review
```

---

# 8. Workflow Request Schema

Workflow 실행 요청은 다음 구조를 따른다.

```json
{
  "workflow_request_id": "WF-REQ-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "mode": "auto_until_package",

  "start_stage": "RESEARCH",
  "stop_stage": "PACKAGE",

  "options": {
    "require_human_review_before_publish": true,
    "allow_auto_fix": true,
    "allow_partial_regeneration": true,
    "allow_full_regeneration": false,
    "max_retry_per_issue": 3,
    "max_total_retry_per_project": 10
  },

  "created_by": "project_manager",
  "created_at": "2026-07-10T09:40:00"
}
```

---

# 9. Workflow State File

Workflow 상태는 Project 폴더 안에 저장한다.

파일:

```text
workflow/workflow_state.json
```

v1.0에서 Project 생성 시 `workflow/` 폴더를 만들 수 있다.

Schema:

```json
{
  "workflow_id": "WF-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "status": "RUNNING",
  "mode": "auto_until_package",

  "current_stage": "STORY",
  "previous_stage": "KNOWLEDGE",
  "next_stage": "DIRECTION",

  "stage_history": [
    {
      "stage": "RESEARCH",
      "status": "COMPLETED",
      "started_at": "2026-07-10T09:45:00",
      "completed_at": "2026-07-10T10:10:00"
    }
  ],

  "retry": {
    "total_retry_count": 0,
    "issues": []
  },

  "blocking": {
    "blocked": false,
    "reason": null,
    "open_critical_messages": 0,
    "open_escalations": 0
  },

  "updated_at": "2026-07-10T10:30:00"
}
```

---

# 10. Workflow Status

Workflow는 다음 상태를 가진다.

```text
CREATED
READY
RUNNING
PAUSED
BLOCKED
AUTO_FIX
WAITING_FOR_HUMAN_REVIEW
FAILED
COMPLETED
CANCELLED
```

## CREATED

Workflow 요청이 생성된 상태.

## READY

실행 준비가 완료된 상태.

## RUNNING

Stage가 진행 중인 상태.

## PAUSED

사용자 또는 COO 판단으로 일시 중지된 상태.

## BLOCKED

필수 파일 누락, Open Critical Message, Escalation 등으로 진행 불가.

## AUTO_FIX

Quality 문제 해결을 위한 자동 수정 흐름이 진행 중.

## WAITING_FOR_HUMAN_REVIEW

사람 검토 대기 상태.

## FAILED

복구 불가능하거나 승인 필요한 실패 상태.

## COMPLETED

목표 Stage까지 완료된 상태.

## CANCELLED

사용자 또는 COO가 취소한 상태.

---

# 11. Stage Execution Flow

Stage 실행 흐름:

```text
Check Current Project Status
↓
Resolve Stage Definition
↓
Check Stage Owner
↓
Check Required Inputs
↓
Check Open Messages
↓
Load Memory Context
↓
Build Stage Context
↓
Create TASK_REQUEST
↓
Run Stage Engine
↓
Receive TASK_RESULT
↓
Validate Expected Outputs
↓
Run Self Review / Peer Review if required
↓
Create Handoff Package
↓
Request Approval
↓
Project State Transition
↓
Update Workflow State
↓
Log Event
```

---

# 12. Stage Context Schema

Stage Engine에 전달되는 Context는 다음 구조를 따른다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "STORY",

  "paths": {
    "project_root": "projects/future/2026/07/20260710-093500-future-million-year-human",
    "required_inputs": [
      "knowledge/knowledge.json",
      "knowledge/claims.json",
      "knowledge/fact_check.json"
    ],
    "expected_outputs": [
      "story/script_master.json",
      "story/script_master.md"
    ]
  },

  "context": {
    "project": "project.json",
    "topic": "topic.json",
    "channel_snapshot": "channel_snapshot.json",
    "template_snapshot": "template_snapshot.json",
    "memory_context": "workflow/memory_context_STORY.json"
  },

  "rules": {
    "quality_pass_score": 95,
    "require_self_review": true,
    "require_handoff": true,
    "allow_partial_regeneration": true
  }
}
```

---

# 13. Stage Result Schema

Stage 실행 결과는 다음 구조를 따른다.

```json
{
  "stage": "STORY",
  "project_id": "20260710-093500-future-million-year-human",
  "status": "COMPLETED",

  "outputs": [
    "story/outline.json",
    "story/hook.json",
    "story/script_master.json",
    "story/script_master.md",
    "story/story_review.json"
  ],

  "self_review": {
    "completed": true,
    "score": 94,
    "file": "logs/self_reviews.jsonl"
  },

  "handoff": {
    "created": true,
    "to_stage": "DIRECTION",
    "file": "workflow/handoffs/STORY_to_DIRECTION.json"
  },

  "issues": [],
  "requires_review": true,
  "created_at": "2026-07-10T11:00:00"
}
```

---

# 14. Required Input Validation

Stage 실행 전 Required Input을 검증한다.

검증 항목:

```text
파일 존재 여부
파일이 비어 있지 않은지
기본 Schema가 맞는지
현재 Stage에서 사용할 수 있는 상태인지
Locked File 위반이 없는지
```

Input 누락 시:

```text
Workflow Status → BLOCKED
ERROR_REPORT 생성
Project Manager에게 Message 생성
Stage 실행 중단
```

---

# 15. Expected Output Validation

Stage 완료 후 Expected Output을 검증한다.

검증 항목:

```text
필수 파일 생성 여부
파일이 비어 있지 않은지
Schema 유효성
Scene ID 일관성
Language 파일 존재 여부
Asset Registry 연결 여부
Self Review 존재 여부
Handoff 존재 여부
```

Output 검증 실패 시:

```text
REVISION_REQUEST 생성
Retry Count 증가
필요 시 AUTO_FIX 또는 ESCALATION
```

---

# 16. State Transition Control

Workflow Orchestrator는 Project Engine에 상태 변경을 요청한다.

Orchestrator가 직접 `project.json`을 임의 수정하지 않는다.

흐름:

```text
Stage Output Validated
↓
Approval Completed
↓
Workflow Orchestrator requests State Change
↓
Project Engine validates transition
↓
Project Engine updates project.json
↓
Workflow Orchestrator updates workflow_state.json
```

금지:

```text
Workflow Orchestrator가 project.json 상태를 직접 무단 수정
Stage Engine이 Project Status 직접 변경
Quality Engine이 READY 상태 직접 변경
```

---

# 17. Communication Integration

Workflow Orchestrator는 Communication Bus와 연결된다.

Stage 시작 시:

```text
TASK_REQUEST 생성
```

Stage 완료 시:

```text
TASK_RESULT 확인
```

Stage 간 이동 시:

```text
HANDOFF_REQUEST 또는 HANDOFF_RESULT 확인
```

문제 발생 시:

```text
ERROR_REPORT
REVISION_REQUEST
ESCALATION
```

상태 변경 전 확인:

```text
Open Critical Message 없음
Open Escalation 없음
Required Approval 완료
Required Revision 완료
```

---

# 18. Memory Integration

Workflow Orchestrator는 Stage 실행 전 Memory Engine에 Memory Context를 요청한다.

흐름:

```text
Stage Start
↓
Request Memory Context
↓
Memory Engine builds Memory Context Package
↓
Save to workflow/memory_context_{stage}.json
↓
Stage Engine receives context
```

Memory Context는 Stage 결과 품질을 높이기 위해 사용된다.

Workflow Orchestrator는 Memory를 직접 수정하지 않는다.

---

# 19. Thinking Integration

Workflow Orchestrator는 Thinking Framework와 연결된다.

필수 확인:

```text
중요 Stage 결과에 Self Review가 있는가
중요 결정에 Decision Record가 있는가
Risk Register에 Critical Risk가 있는가
Handoff Summary가 있는가
```

Workflow Orchestrator는 긴 내부 추론을 저장하지 않는다.

저장 대상은 구조화된 기록이다.

```text
Decision Record
Self Review
Risk Register
Handoff Summary
```

---

# 20. Organization Integration

Workflow Orchestrator는 Stage별 Owner를 `04_AI_ORGANIZATION.md` 기준으로 확인한다.

Stage Owner 예시:

```text
RESEARCH → Research Department
KNOWLEDGE → Knowledge Department
STORY → Story Department
DIRECTION → Direction Department
TIMELINE → Timeline Department
VISUAL → Visual Department
MOTION → Motion Department
VOICE → Voice Department
SUBTITLE → Subtitle Department
EDITING → Editing Department
QUALITY → Quality Department
PACKAGE → Publishing Department
ANALYTICS → Analytics Department
LEARNING → Learning Department
```

Stage Owner가 불명확하면 실행하지 않는다.

---

# 21. Quality Gate Integration

QUALITY Stage 결과는 Workflow 흐름을 바꿀 수 있다.

Quality Score 처리:

```text
95~100
QUALITY → PACKAGE

90~94
WAITING_FOR_HUMAN_REVIEW 또는 PACKAGE

80~89
QUALITY → AUTO_FIX

70~79
Partial Regeneration Required

70 미만
ESCALATION
```

Hard Fail 발생 시:

```text
Workflow Status → BLOCKED
Project Manager에게 ESCALATION
Quality Report 기록
Auto Fix 또는 Partial Regeneration 판단
```

---

# 22. Auto Fix Flow

Auto Fix 흐름:

```text
Quality Issue Detected
↓
Issue Scope Identify
↓
Root Cause Analysis
↓
Target Stage Determine
↓
REVISION_REQUEST 생성
↓
Failed Department 또는 Target Engine 실행
↓
Output Recheck
↓
QUALITY 재진입
```

Auto Fix 대상 예시:

```text
Story Hook 약함
→ STORY 일부 수정

Scene 7 이미지 Brand 불일치
→ VISUAL의 SC007 Prompt 수정

영어 Voice 길이 초과
→ VOICE의 en narration 수정

Subtitle Sync 문제
→ SUBTITLE 재생성
```

원칙:

```text
전체 재생성 금지
부분 수정 우선
같은 Issue 최대 3회 Retry
Retry 실패 시 Escalation
```

---

# 23. Retry Policy

Retry 설정:

```yaml
retry_policy:
  max_retry_per_issue: 3
  max_total_retry_per_project: 10
  prefer_partial_regeneration: true
  full_regeneration_requires_coo_approval: true
```

Retry Count는 `workflow_state.json`에 기록한다.

Retry 기록 예시:

```json
{
  "issue_id": "ISSUE-000001",
  "stage": "VISUAL",
  "scene_id": "SC007",
  "retry_count": 2,
  "reason": "Brand mismatch in generated image.",
  "last_action": "Regenerated SC007 image prompt.",
  "status": "RETRYING"
}
```

---

# 24. Escalation Rules

Escalation이 필요한 경우:

```text
같은 Issue 3회 실패
Project 전체 품질 점수 70 미만
Critical Risk 발생
Open Critical Message 장기 미해결
Template Lock Rule 위반
필수 파일 반복 누락
Provider 실패 반복
Full Regeneration 필요
CEO 승인 필요
```

Escalation 순서:

```text
Department Lead
↓
Project Manager
↓
Channel Manager
↓
Portfolio Manager
↓
COO
↓
CEO / USER
```

Workflow Orchestrator는 Escalation Message를 생성하고 Workflow를 BLOCKED 또는 PAUSED로 전환할 수 있다.

---

# 25. Human Review Rules

v1.0에서는 Human Review를 지원해야 한다.

Human Review가 필요한 경우:

```text
Quality Score 90~94
Full Auto Publish 전환 전
Brand 핵심 변경
Template Major Version 변경
Full Regeneration
Critical Risk
사용자가 명시한 검토 지점
```

Human Review 상태:

```text
WAITING_FOR_HUMAN_REVIEW
```

Human Review 결과:

```text
APPROVED
REVISION_REQUIRED
REJECTED
ESCALATE
```

---

# 26. Pause and Resume

Workflow는 중단과 재개를 지원해야 한다.

Pause 사유:

```text
Human Review 대기
Provider Manual Action 대기
Critical Issue 발생
사용자 요청
COO 판단
```

Resume 조건:

```text
필수 파일 생성 완료
Manual Provider Result 등록
Human Review 승인
Open Critical Message 해결
Escalation 처리 완료
```

---

# 27. Workflow Directory Structure

Project 안의 Workflow 폴더 구조:

```text
workflow/
├── workflow_state.json
├── stage_registry_snapshot.json
├── memory_context_RESEARCH.json
├── memory_context_STORY.json
├── handoffs/
│   ├── RESEARCH_to_KNOWLEDGE.json
│   ├── STORY_to_DIRECTION.json
│   └── TIMELINE_to_VISUAL.json
├── stage_results/
│   ├── RESEARCH_result.json
│   ├── STORY_result.json
│   └── QUALITY_result.json
└── auto_fix/
    ├── auto_fix_plan.json
    └── auto_fix_history.jsonl
```

v1.0에서 최소 생성:

```text
workflow/workflow_state.json
workflow/stage_results/
workflow/handoffs/
workflow/auto_fix/
```

---

# 28. Workflow Reports

Workflow Orchestrator는 다음 Report를 생성할 수 있다.

```text
reports/workflow_report.json
reports/stage_status_report.json
reports/auto_fix_report.json
```

`workflow_report.json` 예시:

```json
{
  "workflow_id": "WF-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "status": "RUNNING",
  "current_stage": "STORY",
  "completed_stages": [
    "RESEARCH",
    "KNOWLEDGE"
  ],
  "blocked": false,
  "retry_total": 0,
  "open_escalations": 0,
  "next_action": "Run Story Stage",
  "updated_at": "2026-07-10T11:00:00"
}
```

---

# 29. Workflow Logs

Workflow Orchestrator는 다음 로그를 남긴다.

```text
logs/workflow.log
logs/workflow_events.jsonl
logs/error_log.jsonl
logs/communication.jsonl
```

로그 대상:

```text
Workflow 생성
Workflow 시작
Stage 시작
Stage 완료
Stage 실패
Input Validation 실패
Output Validation 실패
State Transition 요청
Auto Fix 시작
Auto Fix 완료
Retry 발생
Escalation 발생
Human Review 대기
Workflow 완료
Workflow 중단
```

Event 예시:

```json
{
  "event_type": "STAGE_COMPLETED",
  "workflow_id": "WF-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "stage": "STORY",
  "next_stage": "DIRECTION",
  "created_at": "2026-07-10T11:00:00"
}
```

---

# 30. Error Types

Workflow Orchestrator의 Error Type은 다음과 같다.

```text
WorkflowRequestValidationError
WorkflowStateNotFoundError
InvalidWorkflowStatusError
StageDefinitionNotFoundError
StageOwnerNotFoundError
StageInputMissingError
StageOutputMissingError
StageExecutionError
InvalidStageTransitionError
OpenCriticalMessageError
OpenEscalationError
ApprovalMissingError
HandoffMissingError
SelfReviewMissingError
QualityGateBlockedError
AutoFixFailedError
RetryLimitExceededError
EscalationRequiredError
HumanReviewRequiredError
```

Error 예시:

```json
{
  "error_type": "StageInputMissingError",
  "message": "Required input knowledge/claims.json is missing.",
  "project_id": "20260710-093500-future-million-year-human",
  "stage": "STORY",
  "severity": "HIGH",
  "suggested_fix": "Complete KNOWLEDGE stage and generate required output before STORY.",
  "created_at": "2026-07-10T11:00:00"
}
```

---

# 31. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
WorkflowOrchestrator
WorkflowRequestValidator
WorkflowStateManager
StageRegistry
StageResolver
StageRunner
StageInputValidator
StageOutputValidator
StageContextBuilder
StageResultHandler
WorkflowTransitionManager
WorkflowPauseManager
WorkflowResumeManager
WorkflowReportBuilder
WorkflowLogger
```

Auto Fix / Retry / Escalation 관련:

```text
AutoFixPlanner
AutoFixRunner
RetryManager
EscalationTrigger
HumanReviewGate
BlockingConditionChecker
```

---

# 32. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/15_WORKFLOW_ORCHESTRATOR.md
→ workflows/orchestrator/
→ workflows/stages/
```

예시 구조:

```text
workflows/
├── orchestrator/
│   ├── workflow_orchestrator.py
│   ├── workflow_request_validator.py
│   ├── workflow_state_manager.py
│   ├── stage_registry.py
│   ├── stage_resolver.py
│   ├── stage_runner.py
│   ├── stage_input_validator.py
│   ├── stage_output_validator.py
│   ├── stage_context_builder.py
│   ├── stage_result_handler.py
│   ├── workflow_transition_manager.py
│   ├── workflow_report_builder.py
│   └── workflow_logger.py
│
└── stages/
    ├── research_stage.py
    ├── knowledge_stage.py
    ├── story_stage.py
    ├── direction_stage.py
    ├── timeline_stage.py
    ├── visual_stage.py
    ├── motion_stage.py
    ├── voice_stage.py
    ├── subtitle_stage.py
    ├── editing_stage.py
    ├── quality_stage.py
    ├── package_stage.py
    ├── analytics_stage.py
    └── learning_stage.py
```

---

# 33. Main Public Operations

Workflow Orchestrator는 최소 다음 작업을 제공해야 한다.

```text
create_workflow(project_id, request)
start_workflow(project_id)
pause_workflow(project_id, reason)
resume_workflow(project_id)
cancel_workflow(project_id, reason)
get_current_stage(project_id)
get_next_stage(project_id)
run_current_stage(project_id)
run_stage(project_id, stage)
validate_stage_inputs(project_id, stage)
validate_stage_outputs(project_id, stage)
handle_stage_result(project_id, result)
request_state_transition(project_id, next_status)
handle_quality_result(project_id)
start_auto_fix(project_id, quality_issue)
escalate(project_id, reason)
build_workflow_report(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
Project 상태 확인
Stage 정의 확인
필수 파일 확인
Open Critical Message 확인
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 34. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Workflow Request 검증
workflow_state.json 생성
Stage Registry 정의
현재 Stage 확인
다음 Stage 확인
Stage Input 검증
Stage Output 검증
Stage Context 생성
Stage Result 저장
Project Engine에 State Change 요청
Quality Result 기반 흐름 분기
Auto Fix 기본 흐름 생성
Retry Count 관리
Escalation 기본 생성
Workflow Report 생성
Workflow Event Log 기록
```

v1.0에서 하지 않아도 되는 것:

```text
복잡한 병렬 Workflow 실행
실시간 UI 기반 Workflow Monitor
분산 작업 큐
외부 Worker 시스템
완전 자동 Publish
고급 스케줄링 엔진
```

v1.0에서는 단일 Project를 안정적으로 순차 실행할 수 있는 구조가 우선이다.

---

# 35. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Project에 Workflow를 생성할 수 있다.
workflow_state.json을 생성하고 업데이트할 수 있다.
Stage Registry에서 현재 Stage 정의를 찾을 수 있다.
Stage별 Required Input을 검증할 수 있다.
Stage별 Expected Output을 검증할 수 있다.
Stage Context를 생성할 수 있다.
Stage 실행 결과를 저장할 수 있다.
Project Engine에 상태 변경을 요청할 수 있다.
잘못된 Stage 순서를 막을 수 있다.
Open Critical Message가 있으면 진행을 막을 수 있다.
Quality 결과에 따라 PACKAGE 또는 AUTO_FIX 또는 ESCALATION으로 분기할 수 있다.
Retry Count를 관리할 수 있다.
Human Review 대기 상태를 처리할 수 있다.
Workflow Report를 생성할 수 있다.
Workflow 관련 Error를 구조화해서 기록할 수 있다.
```

---

# 36. Non Goals

v1.0에서 Workflow Orchestrator가 하지 않는 것:

```text
콘텐츠 직접 제작
Provider 직접 호출
Quality Score 직접 계산
Analytics 직접 수집
Template 직접 수정
Memory 직접 확정
Final Publish 직접 수행
복잡한 분산 실행 시스템 구축
```

v1.0에서는 ADOS 내부 Project Workflow를 안정적으로 통제하는 구조를 먼저 완성한다.

---

# 37. Critical Workflow Rules

반드시 지켜야 할 규칙:

```text
1. Stage는 Workflow Orchestrator 없이 임의 실행하지 않는다.

2. Workflow Orchestrator는 콘텐츠를 직접 만들지 않는다.

3. Stage 실행 전 Required Input을 검증한다.

4. Stage 완료 후 Expected Output을 검증한다.

5. Stage Owner가 없으면 실행하지 않는다.

6. Open Critical Message가 있으면 진행하지 않는다.

7. Open Escalation이 있으면 진행하지 않는다.

8. State 변경은 Project Engine을 통해 수행한다.

9. Quality Gate를 우회하지 않는다.

10. Auto Fix는 부분 수정이 우선이다.

11. 같은 Issue Retry는 최대 3회로 제한한다.

12. Full Regeneration은 COO 승인 없이는 수행하지 않는다.

13. Human Review가 필요한 경우 Workflow를 멈춘다.

14. 모든 Stage 시작과 완료는 로그로 남긴다.

15. Workflow Report는 Project Manager와 COO가 이해할 수 있어야 한다.
```

---

# 38. Final Principle

Workflow Orchestrator는 ADOS의 실행 관리자이다.

좋은 Engine이 많아도 실행 순서가 무너지면 좋은 Project가 나오지 않는다.

Workflow Orchestrator는 Project가 올바른 순서로 흐르게 만들고,

필수 입력을 확인하고,

결과물을 검증하고,

품질 문제를 수정 흐름으로 연결하고,

필요할 때 멈추고,

필요할 때 Escalation한다.

Workflow Orchestrator의 목적은 빠르게 실행하는 것이 아니라, 반복 가능한 고품질 제작 흐름을 지키는 것이다.
