# 05_INTER_AI_COMMUNICATION.md

Version: 1.2.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Inter-AI Communication Protocol  

---

# 1. Purpose

이 문서는 CHUNG COMPANY / ADOS 내부의 AI Employee들이 서로 어떻게 요청하고, 응답하고, 검토하고, 수정하고, 승인하고, Escalation하는지 정의한다.

ADOS는 단순히 함수가 순서대로 실행되는 시스템이 아니다.

ADOS는 AI Employee들이 각자의 책임을 가지고 협업하는 AI 콘텐츠 회사 운영체제이다.

따라서 모든 AI Employee 간 통신은 명확한 규칙을 가져야 한다.

이 문서는 다음을 정의한다.

```text
AI Employee 간 Message 구조
Task 요청 방식
Review 요청 방식
Revision 요청 방식
Approval 방식
Handoff 방식
Meeting 방식
Escalation 방식
Conflict Resolution 방식
Communication Log 방식
Claude Code 구현 기준
```

이 문서는 다음 문서들과 직접 연결된다.

```text
03_ARCHITECTURE.md
04_AI_ORGANIZATION.md
06_AI_THINKING_FRAMEWORK.md
07_PROJECT_SPEC.md
12_PROJECT_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
26_QUALITY_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Principle

AI Employee는 파일만 넘기지 않는다.

AI Employee는 작업 결과와 함께 다음 정보를 전달해야 한다.

```text
무엇을 했는가
왜 그렇게 했는가
어떤 입력을 사용했는가
어떤 결과물이 생성되었는가
품질 상태는 어떤가
위험 요소는 무엇인가
다음 부서가 주의해야 할 점은 무엇인가
수정이 필요한 부분은 무엇인가
승인이 필요한 부분은 무엇인가
```

좋은 통신은 좋은 품질을 만든다.

나쁜 통신은 다음 단계의 실패를 만든다.

---

# 3. Communication Model

ADOS의 모든 AI Employee 통신은 Message 기반으로 처리한다.

AI Employee끼리 임의로 직접 대화하지 않는다.

모든 통신은 Communication Bus를 통해 전달되고 기록된다.

```text
AI Employee
↓
Message
↓
Communication Bus
↓
Target Employee or Department
↓
Response Message
↓
Log
↓
Memory Candidate
```

Communication Bus는 다음 역할을 가진다.

```text
Message 생성
Message 전달
Message 상태 관리
Message 우선순위 관리
Message Log 저장
Escalation 감지
Open Message 추적
Blocked Message 추적
```

---

# 4. Communication Scope

통신은 다음 범위에서 발생한다.

```text
Employee → Employee
Employee → Department
Department → Department
Department → Project Manager
Project Manager → Channel Manager
Channel Manager → Portfolio Manager
Portfolio Manager → COO
COO → CEO / USER
```

통신 범위는 작업의 중요도와 위험도에 따라 달라진다.

---

# 5. Message Types

ADOS의 표준 Message Type은 다음과 같다.

```text
TASK_REQUEST
TASK_ACCEPTED
TASK_REJECTED
TASK_RESULT

REVIEW_REQUEST
REVIEW_RESULT

REVISION_REQUEST
REVISION_RESULT

APPROVAL_REQUEST
APPROVAL_RESULT

QUESTION
ANSWER

MEETING_REQUEST
MEETING_RESULT

ESCALATION
ESCALATION_RESULT

STATE_CHANGE_REQUEST
STATE_CHANGE_RESULT

MEMORY_UPDATE_REQUEST
MEMORY_UPDATE_RESULT

ERROR_REPORT
WARNING_REPORT

HANDOFF_REQUEST
HANDOFF_RESULT
```

---

# 6. Message Priority

Message Priority는 다음 4단계를 사용한다.

```text
LOW
일반 기록 또는 참고 메시지

MEDIUM
보통 작업 메시지

HIGH
Project 진행, 품질, 일정에 영향을 주는 메시지

CRITICAL
Project 중단, 브랜드 위험, 사실 오류, 저작권 위험, 필수 파일 누락 등 즉시 대응이 필요한 메시지
```

CRITICAL Message는 자동으로 Project Manager에게 전달되어야 한다.

Project 전체에 영향을 줄 경우 COO에게 Escalation된다.

---

# 7. Message Status

Message는 다음 상태를 가진다.

```text
OPEN
ACCEPTED
IN_PROGRESS
BLOCKED
COMPLETED
REJECTED
ESCALATED
CANCELLED
CLOSED
```

상태 의미:

```text
OPEN
생성되었지만 아직 처리되지 않음

ACCEPTED
대상 Employee 또는 Department가 작업을 수락함

IN_PROGRESS
작업 진행 중

BLOCKED
입력 누락, 오류, 승인 대기 등으로 진행 불가

COMPLETED
요청된 작업 완료

REJECTED
요청 거절 또는 결과 반려

ESCALATED
상위 책임자에게 전달됨

CANCELLED
요청이 취소됨

CLOSED
모든 처리가 끝나고 로그가 닫힘
```

---

# 8. Standard Message Schema

모든 Message는 다음 구조를 따른다.

```json
{
  "message_id": "MSG-000001",
  "message_type": "TASK_REQUEST",
  "priority": "HIGH",
  "status": "OPEN",

  "from": {
    "employee_id": "project_manager",
    "department": "Project Management",
    "role": "Project Manager Employee"
  },

  "to": {
    "employee_id": "story_writer",
    "department": "Story Department",
    "role": "Script Writer Employee"
  },

  "context": {
    "company": "CHUNG COMPANY",
    "system": "ADOS",
    "channel_id": "future",
    "template_id": "future",
    "project_id": "20260710-093500-future-million-year-human",
    "stage": "STORY",
    "scene_id": null,
    "language": null
  },

  "request": {
    "title": "Create master script",
    "description": "Create script_master.json and script_master.md based on approved knowledge files.",
    "required_inputs": [
      "knowledge/knowledge.json",
      "knowledge/claims.json",
      "knowledge/fact_check.json",
      "brand.yaml",
      "story.yaml"
    ],
    "expected_outputs": [
      "story/script_master.json",
      "story/script_master.md",
      "story/story_review.json"
    ],
    "constraints": [
      "Follow channel story rules",
      "Do not use unsupported factual claims",
      "Avoid generic introduction",
      "Hook must be strong within first 30 seconds"
    ]
  },

  "quality": {
    "minimum_score": 95,
    "self_review_required": true,
    "peer_review_required": true,
    "quality_review_required": true
  },

  "risk": {
    "risk_level": "MEDIUM",
    "known_risks": [
      "Speculative future claims must be clearly framed"
    ]
  },

  "timestamps": {
    "created_at": "2026-07-10T10:00:00",
    "updated_at": "2026-07-10T10:00:00",
    "due_at": null
  }
}
```

---

# 9. Task Request Protocol

Task Request는 Project Manager 또는 Department Lead가 특정 Employee나 Department에 작업을 요청할 때 사용한다.

Task Request에는 반드시 다음이 포함되어야 한다.

```text
작업 제목
작업 설명
필수 입력 파일
기대 출력 파일
작업 제약 조건
품질 기준
완료 기준
위험 요소
```

Task Request 없이 작업을 수행하지 않는다.

---

# 10. Task Acceptance Protocol

작업을 받은 Employee는 다음 중 하나로 응답해야 한다.

```text
TASK_ACCEPTED
TASK_REJECTED
QUESTION
ESCALATION
```

작업을 수락할 수 있는 경우:

```text
필수 입력 파일이 존재함
작업 범위가 명확함
출력 Schema가 명확함
권한 범위 안의 작업임
```

작업을 거절해야 하는 경우:

```text
입력 파일 누락
요청 범위 불명확
권한 밖의 요청
Template Lock Rule 위반
Channel Brand Rule 위반
품질 기준 충돌
```

---

# 11. Task Result Protocol

작업 완료 후 Employee는 TASK_RESULT를 제출한다.

TASK_RESULT에는 다음이 포함되어야 한다.

```json
{
  "message_type": "TASK_RESULT",
  "status": "COMPLETED",
  "result": {
    "summary": "Master script created.",
    "output_files": [
      "story/script_master.json",
      "story/script_master.md",
      "story/story_review.json"
    ],
    "decisions_made": [
      "Used future scenario hook instead of generic explanation."
    ],
    "known_risks": [
      "Some future predictions are speculative and must be framed carefully."
    ],
    "next_department_notes": [
      "Direction Department should emphasize the opening scene visually."
    ]
  },
  "self_review": {
    "self_score": 94,
    "status": "NEEDS_PEER_REVIEW",
    "issues_found": [],
    "remaining_risks": [
      "Need factuality review for speculative claims."
    ]
  }
}
```

---

# 12. Handoff Protocol

한 Department가 다음 Department로 작업을 넘길 때는 Handoff Package를 생성한다.

Handoff는 단순 파일 전달이 아니다.

Handoff는 다음 부서가 작업을 이어받을 수 있게 만드는 문맥 전달이다.

## 12.1 Handoff Package Schema

```json
{
  "handoff_id": "HANDOFF-000001",
  "project_id": "20260710-093500-future-million-year-human",

  "from": {
    "department": "Story Department",
    "employee_id": "story_writer"
  },

  "to": {
    "department": "Direction Department",
    "employee_id": "scene_planner"
  },

  "stage_completed": "STORY",
  "next_stage": "DIRECTION",

  "outputs": [
    "story/outline.json",
    "story/hook.json",
    "story/script_master.json",
    "story/script_master.md",
    "story/story_review.json"
  ],

  "summary": {
    "what_was_done": "Created master script and hook structure.",
    "important_decisions": [
      "Opening uses a future scenario rather than a direct explanation."
    ],
    "known_risks": [
      "Some claims must remain framed as possible scenarios."
    ],
    "recommended_attention": [
      "Opening scene should be cinematic and mysterious.",
      "Avoid overly literal robot imagery."
    ]
  },

  "quality": {
    "self_score": 94,
    "peer_score": 96,
    "status": "PASS_WITH_NOTES"
  },

  "requires_follow_up": true,
  "follow_up_items": [
    "Factuality Quality Employee should check speculative claims."
  ]
}
```

---

# 13. Review Protocol

ADOS는 3단계 Review 구조를 사용한다.

```text
Self Review
↓
Peer Review
↓
Quality Review
```

## 13.1 Self Review

작업 수행 Employee가 스스로 검토한다.

검토 항목:

```text
필수 파일 생성 여부
Schema 준수 여부
Brand 규칙 준수 여부
Quality 규칙 준수 여부
다음 부서가 사용할 수 있는지
위험 요소 표시 여부
```

## 13.2 Peer Review

동료 Employee 또는 다음 Department가 검토한다.

목적:

```text
작업자가 놓친 문제 감지
다음 단계 사용 가능성 확인
Output 해석 가능성 확인
품질 개선 지점 발견
```

## 13.3 Quality Review

Quality Department가 최종 품질 기준으로 검토한다.

목적:

```text
95점 기준 충족 여부 판단
Hard Fail 감지
Auto Fix 필요 여부 판단
Human Review 필요 여부 판단
```

---

# 14. Review Result Schema

```json
{
  "message_type": "REVIEW_RESULT",
  "review_id": "REV-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "reviewer": {
    "employee_id": "story_reviewer",
    "department": "Story Department"
  },
  "target": {
    "stage": "STORY",
    "files": [
      "story/script_master.json",
      "story/script_master.md"
    ]
  },
  "score": 92,
  "status": "REVISION_REQUIRED",
  "passed": false,
  "issues": [
    {
      "severity": "HIGH",
      "location": "story/script_master.md",
      "description": "Hook is visually strong but factual framing is weak.",
      "suggested_fix": "Add cautious language for speculative claims."
    }
  ],
  "next_action": "REVISION_REQUEST"
}
```

---

# 15. Approval Protocol

Approval은 제한된 권한을 가진 Employee 또는 Department만 수행할 수 있다.

```text
작업 결과 제출:
모든 Employee

Self Review:
작업 수행 Employee

Peer Review:
Reviewer Employee

Quality Approval:
Quality Department

Project State Change Approval:
Project Manager

Channel Strategy Approval:
Channel Manager

Portfolio Priority Approval:
Portfolio Manager

Template Version Approval:
Template Manager

Full Regeneration Approval:
COO

Full Auto Publish Approval:
CEO / USER
```

승인 없이 다음 단계로 넘어가면 안 된다.

---

# 16. Approval Result Schema

```json
{
  "message_type": "APPROVAL_RESULT",
  "approval_id": "APP-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "stage": "STORY",
  "approved_by": {
    "employee_id": "project_manager",
    "role": "Project Manager Employee"
  },
  "approval_status": "APPROVED",
  "conditions": [
    "Direction Department must preserve the opening hook."
  ],
  "next_stage": "DIRECTION",
  "created_at": "2026-07-10T12:00:00"
}
```

---

# 17. Revision Protocol

Revision은 문제가 있는 부분을 수정하기 위한 요청이다.

ADOS는 전체 재생성보다 부분 수정을 우선한다.

Revision Request에는 반드시 다음이 포함되어야 한다.

```text
문제 위치
문제 설명
원인 추정
수정 범위
기대 결과
재시도 제한
검토 기준
```

## 17.1 Revision Request Schema

```json
{
  "message_type": "REVISION_REQUEST",
  "revision_id": "REVREQ-000001",
  "project_id": "20260710-093500-future-million-year-human",

  "target": {
    "stage": "STORY",
    "file": "story/script_master.md",
    "scene_id": "SC001",
    "language": "ko"
  },

  "problem": {
    "severity": "HIGH",
    "description": "Opening hook is too generic.",
    "root_cause": "The script starts with explanation instead of a strong future scenario."
  },

  "required_change": {
    "scope": "PARTIAL",
    "instruction": "Rewrite only the first 30 seconds using a cinematic future scenario.",
    "must_keep": [
      "Main topic",
      "Scientific framing",
      "Channel tone"
    ]
  },

  "retry": {
    "attempt": 1,
    "max_attempts": 3
  }
}
```

---

# 18. Revision Result Schema

```json
{
  "message_type": "REVISION_RESULT",
  "revision_id": "REVREQ-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "status": "COMPLETED",
  "changed_files": [
    "story/script_master.md",
    "story/script_master.json"
  ],
  "summary": "Rewrote the first 30 seconds with a stronger cinematic hook.",
  "remaining_risks": [],
  "requires_recheck": true
}
```

---

# 19. Retry Policy

Retry 정책은 다음과 같다.

```yaml
retry_policy:
  max_retry_per_issue: 3
  max_total_retry_per_project: 10
  prefer_partial_regeneration: true
  full_regeneration_requires_coo_approval: true
```

같은 문제가 3회 이상 반복되면 Escalation한다.

---

# 20. Meeting Protocol

AI Meeting은 여러 Department가 함께 판단해야 하는 경우에 사용한다.

Meeting은 일반 대화가 아니다.

Meeting은 결정이 필요한 문제를 해결하기 위한 구조화된 협의이다.

## 20.1 Meeting Triggers

```text
품질 점수 80 미만
Critical Issue 발생
같은 문제 3회 반복
Story와 Visual 판단 충돌
Growth와 Brand 방향 충돌
Timeline 구조 붕괴
사실 오류 위험
저작권 위험
전체 재생성 여부 판단 필요
Template 변경 여부 판단 필요
```

## 20.2 Meeting Result Schema

```json
{
  "meeting_id": "MEET-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "trigger": "QUALITY_SCORE_BELOW_THRESHOLD",

  "participants": [
    "Project Manager",
    "Story Department",
    "Direction Department",
    "Quality Department"
  ],

  "problem": "Story quality score is below threshold.",
  "root_cause": "Opening hook and visual direction are misaligned.",

  "options_considered": [
    "Rewrite entire script",
    "Rewrite only opening hook",
    "Change visual direction only"
  ],

  "decision": "Rewrite only opening hook and update first three scene directions.",
  "owner": "Story Department",
  "next_action": "REVISION_REQUEST",
  "requires_coo_approval": false,
  "created_at": "2026-07-10T13:00:00"
}
```

---

# 21. Escalation Protocol

Escalation은 일반적인 수정으로 해결할 수 없는 문제를 상위 책임자에게 넘기는 절차이다.

Escalation 순서:

```text
Specialist Employee
↓
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

## 21.1 Escalation Triggers

```text
같은 오류 3회 반복
품질 점수 70 미만
Critical Risk 발생
필수 파일 누락
Locked Field Override 시도
Template 검증 실패
Project 중단 위험
브랜드/수익/품질 충돌
저작권 위험
사실 오류 위험
Full Regeneration 필요
Full Auto Publish 전환 필요
```

## 21.2 Escalation Schema

```json
{
  "message_type": "ESCALATION",
  "escalation_id": "ESC-000001",
  "priority": "CRITICAL",

  "context": {
    "project_id": "20260710-093500-future-million-year-human",
    "channel_id": "future",
    "stage": "QUALITY"
  },

  "from": {
    "employee_id": "final_quality_employee",
    "department": "Quality Department"
  },

  "to": {
    "employee_id": "project_manager",
    "department": "Project Management"
  },

  "problem": {
    "summary": "Quality score is below 70.",
    "severity": "CRITICAL",
    "details": "Story structure and timeline are both failing."
  },

  "attempted_fixes": [
    "Hook revision",
    "Scene direction revision",
    "Timeline adjustment"
  ],

  "recommended_action": "Hold AI Meeting and decide partial or full regeneration."
}
```

---

# 22. Conflict Resolution

Department 간 의견 충돌 시 다음 우선순위를 따른다.

```text
1. 사실 정확성
2. 안전 / 저작권 / 정책 위험 회피
3. Template Lock Rules
4. Channel Brand Rules
5. Quality Rules
6. Timeline Integrity
7. Growth Strategy
8. Production Efficiency
9. Department Preference
```

예시:

```text
Growth Department가 클릭률을 위해 자극적인 제목을 제안했지만,
Brand System이 채널 정체성과 맞지 않는다고 판단하면
Brand Rule이 우선한다.
```

---

# 23. Communication and Project State

Message는 Project 상태 변경과 연결된다.

Project 상태 변경은 반드시 다음 조건을 만족해야 한다.

```text
해당 Stage Output 생성 완료
Self Review 완료
필요 시 Peer Review 완료
Quality Gate 조건 충족
Handoff Package 생성
Open Critical Message 없음
Open Escalation 없음
Project Manager 승인
```

Project Manager만 Project 상태를 변경할 수 있다.

---

# 24. Communication Logs

모든 Communication은 로그로 저장한다.

Project Communication Log:

```text
projects/{channel_id}/{year}/{month}/{project_id}/logs/communication.log
```

Meeting Log:

```text
projects/{channel_id}/{year}/{month}/{project_id}/logs/meeting.log
```

Escalation Log:

```text
projects/{channel_id}/{year}/{month}/{project_id}/logs/escalation.log
```

Error Log:

```text
projects/{channel_id}/{year}/{month}/{project_id}/logs/error.log
```

Decision Record:

```text
projects/{channel_id}/{year}/{month}/{project_id}/logs/decision_records.jsonl
```

---

# 25. Memory Update Communication

중요한 결과는 Memory Update Candidate가 될 수 있다.

Memory Update가 필요한 경우:

```text
반복 실패 발견
성공한 Hook 패턴 발견
좋은 Visual 스타일 발견
Provider 실패 패턴 발견
좋은 Voice 설정 발견
높은 CTR 가능성 있는 제목 패턴 발견
품질 기준 개선 필요 발견
Template 개선 필요 발견
```

Memory Update Request Schema:

```json
{
  "message_type": "MEMORY_UPDATE_REQUEST",
  "project_id": "20260710-093500-future-million-year-human",
  "target_memory": "channel_memory",
  "update_type": "success_pattern",
  "summary": "Future scenario hooks perform better for this channel.",
  "evidence": [
    "story_review.json",
    "quality_report.json"
  ],
  "confidence": "MEDIUM",
  "requires_human_review": false
}
```

---

# 26. Error Reporting Protocol

Error는 조용히 무시하지 않는다.

Error Report는 다음 구조를 따른다.

```json
{
  "message_type": "ERROR_REPORT",
  "error_id": "ERR-000001",
  "severity": "HIGH",
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "VISUAL",
  "location": "prompts/midjourney_image_prompts.json",
  "error_type": "SCHEMA_VALIDATION_ERROR",
  "message": "Required field scene_id is missing.",
  "cause": "Visual prompt generator produced incomplete output.",
  "suggested_fix": "Regenerate only the invalid prompt entry.",
  "requires_escalation": false,
  "created_at": "2026-07-10T14:00:00"
}
```

---

# 27. Open Message Rules

Project는 다음 상태에서 다음 Stage로 넘어갈 수 없다.

```text
Open CRITICAL Message 존재
Open Escalation 존재
Required Review Message 미완료
Approval Request 미완료
Revision Request 미완료
```

단, LOW 또는 MEDIUM 참고 메시지는 Project 진행을 막지 않을 수 있다.

---

# 28. Communication File Format

v1.0에서는 단순하고 추적 가능한 형식을 우선한다.

권장 형식:

```text
.jsonl
```

이유:

```text
Message를 한 줄 단위로 추가 가능
로그 누적이 쉬움
나중에 검색과 분석이 쉬움
Git diff 확인이 쉬움
```

예시 파일:

```text
communication.jsonl
decision_records.jsonl
self_reviews.jsonl
error_log.jsonl
meeting_log.jsonl
```

---

# 29. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

## 29.1 Core Message Classes

```text
Message
MessageType
MessagePriority
MessageStatus
MessageContext
MessagePayload
MessageResult
```

## 29.2 Communication Classes

```text
CommunicationBus
MessageRouter
MessageStore
MessageLogger
MessageValidator
OpenMessageTracker
```

## 29.3 Workflow Communication Classes

```text
TaskRequestManager
HandoffManager
ReviewManager
ApprovalManager
RevisionManager
RetryManager
MeetingManager
EscalationManager
```

## 29.4 Memory and Error Classes

```text
CommunicationMemoryWriter
ErrorReporter
WarningReporter
DecisionRecordLinker
```

---

# 30. Suggested Code Mapping

문서와 코드 매핑 방향은 다음과 같다.

```text
docs/05_INTER_AI_COMMUNICATION.md
→ employees/communication/
→ workflows/communication/
```

예시 구조:

```text
employees/
└── communication/
    ├── message.py
    ├── message_type.py
    ├── message_status.py
    ├── communication_bus.py
    ├── message_router.py
    ├── message_store.py
    ├── handoff_manager.py
    ├── review_manager.py
    ├── approval_manager.py
    ├── revision_manager.py
    ├── meeting_manager.py
    └── escalation_manager.py
```

또는 Workflow 중심 구조:

```text
workflows/
└── communication/
    ├── task_request_manager.py
    ├── handoff_manager.py
    ├── review_manager.py
    ├── approval_manager.py
    ├── retry_manager.py
    └── escalation_manager.py
```

v1.0에서는 복잡한 메시지 서버보다 파일 기반 Message Store로 시작해도 된다.

---

# 31. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Message를 생성할 수 있다.
Message Type을 구분할 수 있다.
Message Priority를 구분할 수 있다.
Message Status를 변경할 수 있다.
Task Request를 생성할 수 있다.
Task Result를 기록할 수 있다.
Handoff Package를 생성할 수 있다.
Review Result를 기록할 수 있다.
Approval Result를 기록할 수 있다.
Revision Request를 생성할 수 있다.
Escalation을 생성할 수 있다.
Open Critical Message를 감지할 수 있다.
Project 상태 변경 전에 Open Message를 확인할 수 있다.
Communication Log를 저장할 수 있다.
Memory Update Candidate를 생성할 수 있다.
```

---

# 32. Non Goals

v1.0에서는 다음을 구현하지 않는다.

```text
실시간 채팅 UI
복잡한 WebSocket 기반 Message Server
외부 사용자용 협업 도구
Slack/Discord 연동
사람 직원용 조직 메신저
복잡한 권한 관리 대시보드
```

v1.0에서는 내부 ADOS Workflow가 사용할 수 있는 구조화된 Message 시스템을 먼저 만든다.

---

# 33. Critical Communication Rules

반드시 지켜야 할 규칙:

```text
1. AI Employee는 임의로 직접 작업하지 않는다.

2. 모든 중요한 작업은 Message로 요청된다.

3. 모든 중요한 결과는 Message로 보고된다.

4. Handoff 없이 다음 Stage로 넘어가지 않는다.

5. Review 없이 품질 통과를 선언하지 않는다.

6. 승인 권한이 없는 Employee는 Approval을 할 수 없다.

7. Project Manager만 Project State를 변경할 수 있다.

8. CRITICAL Message가 열려 있으면 다음 Stage로 진행하지 않는다.

9. 같은 문제 3회 반복 시 Escalation한다.

10. 전체 재생성은 COO 승인 없이는 수행하지 않는다.

11. CEO 승인 없이 Full Auto Publish로 전환하지 않는다.

12. 중요한 판단은 Decision Record와 연결한다.

13. 중요한 실패는 Error Report로 남긴다.

14. Communication Log는 Learning에 사용될 수 있어야 한다.
```

---

# 34. Final Principle

좋은 AI 시스템은 좋은 모델 하나로 만들어지지 않는다.

좋은 AI 시스템은 좋은 협업 구조로 만들어진다.

AI Employee는 혼자 일하지 않는다.

AI Employee는 요청하고, 응답하고, 검토하고, 수정하고, 승인하고, 학습한다.

Communication은 ADOS의 혈관이다.

Communication이 명확해야 Project가 흐르고,

Project가 흐르면 Quality가 올라가고,

Quality가 올라가면 Channel이 성장한다.
