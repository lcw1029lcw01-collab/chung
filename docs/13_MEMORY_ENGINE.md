# 13_MEMORY_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Memory Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Memory Engine을 정의한다.

Memory Engine은 CHUNG COMPANY가 Project를 반복하면서 얻은 성공 패턴, 실패 패턴, Channel별 특징, Template별 학습, Provider 실패, 품질 문제, 성장 데이터, 운영 기록을 저장하고 필요한 시점에 불러오는 엔진이다.

ADOS는 매번 처음부터 생각하는 시스템이 아니다.

ADOS는 기억하고, 비교하고, 반복 실패를 줄이고, 성공 패턴을 재사용하는 시스템이다.

Memory Engine은 다음을 담당한다.

```text
Company Memory 관리
Template Memory 관리
Channel Memory 관리
Project Memory 관리
Provider Memory 관리
Quality Memory 관리
Growth Memory 관리
Success Pattern 저장
Failure Pattern 저장
작업 전 Memory Context 제공
Project 완료 후 Learning 결과 반영
Memory Update Candidate 검토
중복 Memory 방지
낡은 Memory 관리
잘못된 Memory 기록 방지
```

이 문서는 다음 문서들과 직접 연결된다.

```text
03_ARCHITECTURE.md
04_AI_ORGANIZATION.md
05_INTER_AI_COMMUNICATION.md
06_AI_THINKING_FRAMEWORK.md
07_PROJECT_SPEC.md
08_TEMPLATE_SYSTEM.md
09_CHANNEL_ENGINE.md
11_PORTFOLIO_ENGINE.md
12_PROJECT_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
26_QUALITY_ENGINE.md
27_GROWTH_ENGINE.md
29_ANALYTICS_ENGINE.md
30_LEARNING_ENGINE.md
31_AI_EVOLUTION_ENGINE.md
```

---

# 2. Core Definition

Memory는 ADOS가 과거 작업에서 얻은 구조화된 지식이다.

Memory는 단순 로그가 아니다.

로그는 사건 기록이다.

Memory는 다음 작업에 실제로 사용되는 학습된 운영 지식이다.

```text
Logs
↓
Reports
↓
Learning
↓
Memory
↓
Next Project Context
```

Memory는 다음 질문에 답해야 한다.

```text
이 Channel에서 잘 먹힌 Hook은 무엇인가?
이 Channel에서 실패한 Topic은 무엇인가?
이 Template에서 반복되는 품질 문제는 무엇인가?
Midjourney에서 자주 실패한 Prompt 패턴은 무엇인가?
Typecast에서 좋은 Voice 설정은 무엇인가?
CTR이 높았던 제목 패턴은 무엇인가?
Retention이 떨어진 구간의 공통점은 무엇인가?
반복적으로 발생하는 Project 병목은 무엇인가?
```

---

# 3. Memory Philosophy

## 3.1 Memory Before Work

AI Employee와 Engine은 작업 전에 관련 Memory를 불러와야 한다.

예시:

```text
Story Engine
→ 성공한 Hook / 실패한 Hook Memory 참고

Visual Engine
→ 성공한 Visual Style / Provider Failure Memory 참고

Voice Engine
→ 좋은 Voice Speed / 실패한 Voice Tone Memory 참고

Quality Engine
→ 반복 Hard Fail / 반복 Brand Violation Memory 참고
```

## 3.2 Learning After Work

Project가 끝나면 Learning 결과가 Memory로 이어져야 한다.

Learning 없는 반복 제작은 금지한다.

## 3.3 Do Not Overgeneralize

한 번의 성공이나 실패를 바로 절대 규칙으로 저장하면 안 된다.

Memory는 Confidence와 Evidence를 가져야 한다.

## 3.4 Memory Must Be Actionable

Memory는 다음 작업에 쓸 수 있어야 한다.

나쁜 Memory:

```text
이 영상은 좋았다.
```

좋은 Memory:

```text
future Channel에서는 첫 30초에 미래 시뮬레이션 장면으로 시작한 Hook이 Story Quality와 Retention Potential을 높였다.
```

## 3.5 Memory Must Be Scoped

모든 Memory는 적용 범위를 가져야 한다.

```text
Company Level
Template Level
Channel Level
Project Level
Provider Level
Quality Level
Growth Level
```

---

# 4. Memory Engine Responsibilities

Memory Engine의 책임은 다음과 같다.

```text
Memory 파일 생성
Memory 파일 로드
Memory Schema 검증
작업 전 Memory Context 생성
Memory Update Candidate 수신
Memory Update Candidate 검증
Memory 중복 감지
Memory Confidence 관리
Memory Evidence 연결
Memory Scope 관리
Memory 검색
Memory 요약
Memory 오래됨 감지
Memory Report 생성
Learning Engine과 연동
Template Evolution에 필요한 Memory 제공
```

Memory Engine이 하지 않는 것:

```text
Project 성과를 직접 분석하지 않는다.
Quality Score를 직접 계산하지 않는다.
Template을 직접 수정하지 않는다.
Channel 전략을 직접 변경하지 않는다.
Provider를 직접 호출하지 않는다.
```

분석은 Analytics Engine과 Learning Engine이 담당한다.

Memory Engine은 저장, 검색, 검증, 제공을 담당한다.

---

# 5. Memory Types

ADOS는 다음 Memory Type을 사용한다.

```text
Company Memory
Template Memory
Channel Memory
Project Memory
Provider Memory
Quality Memory
Growth Memory
Success Memory
Failure Memory
Decision Memory
```

## 5.1 Company Memory

회사 전체 운영에서 반복되는 패턴.

예시:

```text
전체 Project 병목
전체 품질 문제
전체 운영 원칙
성공 Channel 패턴
실패 Channel 패턴
```

## 5.2 Template Memory

특정 Template에서 반복되는 성공/실패 패턴.

예시:

```text
future Template에서 잘 작동한 Hook 구조
history Template에서 실패한 Visual 스타일
science Template에서 필요한 Fact Check 규칙
```

## 5.3 Channel Memory

특정 Channel의 운영 기억.

예시:

```text
future Channel에서 성공한 제목 패턴
future Channel에서 실패한 Thumbnail 스타일
future Channel에서 좋은 Voice 톤
```

## 5.4 Project Memory

특정 Project에서 발생한 주요 결정, 실패, 결과.

예시:

```text
Project별 품질 이슈
Project별 Auto Fix 기록
Project별 성과 요약
Project별 Learning 후보
```

## 5.5 Provider Memory

Provider 사용 중 쌓인 성공/실패 정보.

예시:

```text
Midjourney에서 실패한 Prompt 패턴
Midjourney Video에서 잘 먹힌 Motion Prompt
Typecast에서 좋은 Voice 설정
```

## 5.6 Quality Memory

품질 검사에서 반복되는 문제와 개선 패턴.

예시:

```text
반복 Hard Fail
반복 Brand Violation
반복 Subtitle Sync 문제
반복 Timeline Integrity 문제
```

## 5.7 Growth Memory

성과와 성장 관련 기억.

예시:

```text
CTR 높은 제목 패턴
Retention이 좋은 Hook 구조
Subscriber Conversion이 좋은 Ending
Revenue Potential이 높은 Topic 유형
```

---

# 6. Memory Directory Structure

v1.0 기본 구조:

```text
memory/
├── company/
│   ├── company_memory.yaml
│   ├── company_events.jsonl
│   ├── success_patterns.json
│   ├── failure_patterns.json
│   └── portfolio_memory.json
│
├── templates/
│   └── {template_id}/
│       ├── template_memory.yaml
│       ├── success_patterns.json
│       ├── failure_patterns.json
│       └── improvement_candidates.json
│
├── channels/
│   └── {channel_id}/
│       ├── channel_memory.yaml
│       ├── success_patterns.json
│       ├── failure_patterns.json
│       ├── growth_memory.json
│       ├── quality_memory.json
│       └── provider_memory.json
│
├── projects/
│   └── {project_id}/
│       ├── project_memory.yaml
│       ├── learning_summary.json
│       └── memory_updates.json
│
└── providers/
    ├── midjourney_memory.json
    ├── midjourney_video_memory.json
    └── typecast_memory.json
```

Channel 폴더에도 `memory.yaml`이 존재한다.

```text
channels/{channel_id}/memory.yaml
```

Project 폴더에도 Learning Report가 존재한다.

```text
projects/{channel_id}/{year}/{month}/{project_id}/reports/learning_report.json
```

Memory Engine은 두 위치를 연결해서 사용한다.

---

# 7. Memory Scope Rules

Memory는 반드시 Scope를 가진다.

```text
GLOBAL
TEMPLATE
CHANNEL
PROJECT
PROVIDER
QUALITY
GROWTH
```

Scope 규칙:

```text
Company Memory는 모든 Channel에 참고 가능하다.
Template Memory는 해당 Template 기반 Channel에 참고 가능하다.
Channel Memory는 해당 Channel Project에 우선 적용한다.
Project Memory는 해당 Project 분석과 재현에 사용한다.
Provider Memory는 해당 Provider를 사용하는 모든 Engine에 참고 가능하다.
Quality Memory는 Quality Engine과 Auto Fix에 사용한다.
Growth Memory는 Topic, Title, Thumbnail, SEO 판단에 사용한다.
```

---

# 8. Memory Entry Schema

Memory Entry는 다음 구조를 따른다.

```json
{
  "memory_id": "MEM-000001",
  "scope": "CHANNEL",
  "type": "success_pattern",
  "category": "hook",
  "channel_id": "future",
  "template_id": "future",
  "project_ids": [
    "20260710-093500-future-million-year-human"
  ],

  "summary": "Future scenario hooks work well for the future channel.",
  "details": "Opening with a cinematic future simulation created stronger curiosity and better story quality score.",

  "evidence": [
    {
      "file": "reports/quality_report.json",
      "metric": "story_score",
      "value": 96
    },
    {
      "file": "reports/analytics_report.json",
      "metric": "retention_first_30_seconds",
      "value": null
    }
  ],

  "confidence": "MEDIUM",
  "status": "ACTIVE",

  "usage": {
    "use_for": [
      "story_hook",
      "direction_opening_scene"
    ],
    "do_not_use_for": []
  },

  "created_at": "2026-07-10T10:00:00",
  "updated_at": "2026-07-10T10:00:00",
  "created_by": "learning_engine"
}
```

---

# 9. Confidence Levels

Memory는 Confidence를 가진다.

```text
LOW
근거가 약함. 참고만 가능.

MEDIUM
합리적 근거가 있음. 작업에 참고 가능.

HIGH
여러 Project와 Report에서 반복 확인됨. 강하게 참고 가능.

LOCKED
검증된 핵심 규칙. 임의 변경 금지.
```

규칙:

```text
LOW Memory는 자동 규칙으로 사용하지 않는다.
MEDIUM Memory는 작업 참고 자료로 사용한다.
HIGH Memory는 Engine 판단에 강하게 반영한다.
LOCKED Memory는 승인 없이 변경하지 않는다.
```

---

# 10. Memory Status

Memory Entry는 다음 상태를 가진다.

```text
ACTIVE
CANDIDATE
NEEDS_REVIEW
DEPRECATED
REJECTED
LOCKED
```

## ACTIVE

사용 가능한 Memory.

## CANDIDATE

Learning Engine이 제안했지만 아직 확정되지 않은 Memory.

## NEEDS_REVIEW

사람 또는 Manager 검토가 필요한 Memory.

## DEPRECATED

과거에는 유효했지만 현재는 권장되지 않는 Memory.

## REJECTED

검토 후 사용하지 않기로 한 Memory.

## LOCKED

핵심 규칙으로 고정된 Memory.

---

# 11. Memory Update Candidate

Learning Engine이나 Quality Engine은 Memory Update Candidate를 생성할 수 있다.

Memory Engine은 Candidate를 바로 확정하지 않고 검증한다.

Schema:

```json
{
  "candidate_id": "MUC-000001",
  "source": "learning_engine",
  "target_scope": "CHANNEL",
  "target_id": "future",
  "type": "success_pattern",
  "category": "hook",

  "summary": "Future simulation hooks should be preferred for opening scenes.",
  "evidence": [
    "reports/quality_report.json",
    "reports/learning_report.json"
  ],

  "confidence": "MEDIUM",
  "recommended_status": "ACTIVE",

  "risk": {
    "overgeneralization": true,
    "notes": [
      "Only one Project has evidence. Should remain MEDIUM confidence."
    ]
  },

  "created_at": "2026-07-10T10:00:00"
}
```

---

# 12. Memory Update Rules

Memory Update는 다음 규칙을 따른다.

```text
Evidence 없는 Memory는 저장하지 않는다.
불확실한 Memory는 LOW 또는 CANDIDATE로 저장한다.
한 Project 결과만으로 HIGH Confidence를 주지 않는다.
Template 수준 Memory는 여러 Project 근거가 필요하다.
Company 수준 Memory는 여러 Channel 근거가 필요하다.
LOCKED Memory 변경은 승인 필요.
중복 Memory는 병합하거나 업데이트한다.
Rejected Memory는 기본 Context에 포함하지 않는다.
```

---

# 13. Memory Load Rules

작업 전 Memory Load 기준:

```text
Project 생성 전:
Company Memory
Template Memory
Channel Memory
Growth Memory
Quality Memory

Story Stage:
Channel Hook Memory
Story Success Pattern
Story Failure Pattern
Factuality Risk Memory

Visual Stage:
Visual Success Pattern
Brand Violation Memory
Provider Memory
Midjourney Failure Pattern

Motion Stage:
Motion Success Pattern
Midjourney Video Failure Pattern

Voice Stage:
Voice Success Pattern
Typecast Provider Memory

Quality Stage:
Quality Failure Pattern
Brand Violation Pattern
Timeline Failure Pattern

Growth Stage:
CTR Pattern
Retention Pattern
Revenue Potential Pattern

Learning Stage:
Project Reports
Analytics Reports
Quality Reports
Previous Memory
```

---

# 14. Memory Context Package

Engine은 원본 Memory 전체를 매번 직접 읽기보다 Memory Context Package를 받아야 한다.

Schema:

```json
{
  "context_id": "MEMCTX-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "STORY",

  "loaded_memory": {
    "company": [],
    "template": [],
    "channel": [
      {
        "memory_id": "MEM-000001",
        "type": "success_pattern",
        "category": "hook",
        "summary": "Future scenario hooks work well.",
        "confidence": "MEDIUM"
      }
    ],
    "provider": [],
    "quality": [],
    "growth": []
  },

  "recommended_use": [
    "Consider using a future simulation opening hook."
  ],

  "warnings": [
    "Do not overstate future predictions as facts."
  ]
}
```

---

# 15. Memory Retrieval Rules

Memory 검색은 다음 기준을 따른다.

```text
Scope 일치
Channel 일치
Template 일치
Stage 일치
Category 일치
Confidence 우선
최근성
Evidence 품질
Status ACTIVE 또는 LOCKED
```

검색 우선순위:

```text
1. Project-specific Memory
2. Channel Memory
3. Template Memory
4. Provider Memory
5. Quality / Growth Memory
6. Company Memory
```

단, LOCKED Company Rule은 항상 우선할 수 있다.

---

# 16. Memory Deduplication

중복 Memory는 저장하지 않는다.

중복 판단 기준:

```text
같은 scope
같은 category
비슷한 summary
같은 적용 대상
같은 evidence
```

중복 발견 시 처리:

```text
기존 Memory의 evidence 추가
confidence 업데이트 가능
updated_at 갱신
새 Memory는 생성하지 않음
```

---

# 17. Memory Aging

Memory는 오래되면 재검토될 수 있다.

Aging 기준:

```text
오래된 Provider 실패 패턴
성과가 더 이상 맞지 않는 Growth Pattern
Channel Brand 변경 전 Memory
Template Major Version 변경 전 Memory
반복 검증에서 더 이상 유효하지 않은 Memory
```

Aging 처리:

```text
ACTIVE → NEEDS_REVIEW
ACTIVE → DEPRECATED
HIGH → MEDIUM
MEDIUM → LOW
```

LOCKED Memory는 승인 없이 Aging 처리하지 않는다.

---

# 18. Memory Validation Rules

Memory Validator는 다음을 확인해야 한다.

```text
memory_id 존재
scope 유효
type 존재
category 존재
summary 존재
confidence 유효
status 유효
evidence 존재
created_at 존재
target scope와 target id 일치
LOCKED Memory 변경 권한 확인
```

검증 실패 시 Memory Update를 거부한다.

---

# 19. Memory and Project Engine

Project Engine은 Project Context 생성 시 Memory Engine을 호출한다.

Project 생성 시:

```text
Channel Memory 로드
Template Memory 로드
Company Memory 요약 로드
Project Context에 포함
```

Project 완료 시:

```text
Learning Report 생성 확인
Memory Update Candidate 확인
Project Completion 조건에 Memory Update 상태 반영
```

Project Engine은 Memory를 직접 수정하지 않는다.

---

# 20. Memory and Workflow Orchestrator

Workflow Orchestrator는 Stage 실행 전 Memory Context를 요청한다.

흐름:

```text
Stage Start
↓
Workflow Orchestrator requests Memory Context
↓
Memory Engine builds Stage Memory Context
↓
Stage Engine receives Memory Context
↓
Stage Engine executes work
```

Stage 실패 시:

```text
Error Report
↓
Quality or Learning analysis
↓
Memory Update Candidate if repeated
```

---

# 21. Memory and Quality Engine

Quality Engine은 반복 품질 문제를 Memory로 남길 수 있다.

예시:

```text
Brand Mismatch 반복
Subtitle Sync Failure 반복
Timeline Scene ID 오류 반복
Hook Weakness 반복
Visual Prompt 품질 실패 반복
```

Quality Engine은 Memory Update Candidate를 생성하고, Memory Engine은 이를 검증한다.

---

# 22. Memory and Growth Engine

Growth Engine은 성과 좋은 패턴을 Memory로 남길 수 있다.

예시:

```text
CTR 높은 Title Pattern
Retention 좋은 Hook Pattern
Subscriber Conversion 좋은 Ending Pattern
Revenue Potential 높은 Topic Pattern
```

Growth Memory는 Topic 추천, Title 작성, Thumbnail 방향에 사용된다.

---

# 23. Memory and Analytics Engine

Analytics Engine은 성과 데이터를 제공한다.

Memory Engine은 Analytics 데이터를 직접 분석하지 않는다.

Analytics Engine → Learning Engine → Memory Engine 흐름이 기본이다.

```text
Analytics Report
↓
Learning Report
↓
Memory Update Candidate
↓
Memory Engine Validation
↓
Memory Update
```

---

# 24. Memory and Learning Engine

Learning Engine은 Memory Update Candidate의 주요 생성자이다.

Learning Engine이 생성할 수 있는 Candidate:

```text
Success Pattern
Failure Pattern
Template Improvement Candidate
Channel Strategy Candidate
Provider Improvement Candidate
Quality Rule Improvement Candidate
Growth Pattern Candidate
```

Memory Engine은 다음을 검증한다.

```text
근거가 충분한가
Scope가 적절한가
Confidence가 과도하지 않은가
중복이 아닌가
Template 변경으로 가야 할 내용인가
Channel Memory로 충분한 내용인가
```

---

# 25. Memory and Template Evolution

Memory가 충분히 쌓이면 Template Improvement Proposal로 이어질 수 있다.

조건 예시:

```text
같은 Template 기반 여러 Project에서 같은 성공 패턴 반복
같은 Template 기반 여러 Channel에서 같은 실패 패턴 반복
Quality Fail이 Template 규칙 문제로 반복
Growth 성과가 특정 Template 구조와 연관됨
```

Memory Engine은 Template Evolution을 직접 수행하지 않는다.

Template Evolution Engine 또는 Template Manager가 최종 판단한다.

---

# 26. Memory Reports

Memory Engine은 다음 Report를 생성할 수 있다.

```text
memory/company/memory_report.json
memory/channels/{channel_id}/memory_report.json
memory/templates/{template_id}/memory_report.json
memory/providers/provider_memory_report.json
```

Report 예시:

```json
{
  "scope": "CHANNEL",
  "channel_id": "future",
  "total_memory_entries": 12,
  "active_entries": 8,
  "candidate_entries": 3,
  "deprecated_entries": 1,
  "high_confidence_entries": 2,
  "common_success_patterns": [
    "future simulation hook"
  ],
  "common_failure_patterns": [
    "overly generic AI visuals"
  ],
  "recommended_actions": [
    "Use future simulation opening when topic fits.",
    "Avoid generic robot imagery."
  ],
  "updated_at": "2026-07-10T10:00:00"
}
```

---

# 27. Memory Logs

Memory Engine은 다음 로그를 남긴다.

```text
memory/company/company_events.jsonl
logs/memory.log
logs/memory_events.jsonl
```

로그 대상:

```text
Memory 파일 생성
Memory 로드
Memory Context 생성
Memory Update Candidate 수신
Memory Update 승인
Memory Update 거부
Memory 중복 병합
Memory Confidence 변경
Memory Status 변경
Memory Report 생성
Memory Error 발생
```

Event 예시:

```json
{
  "event_type": "MEMORY_UPDATED",
  "memory_id": "MEM-000001",
  "scope": "CHANNEL",
  "target_id": "future",
  "type": "success_pattern",
  "confidence": "MEDIUM",
  "created_at": "2026-07-10T10:00:00"
}
```

---

# 28. Error Types

Memory Engine의 Error Type은 다음과 같다.

```text
MemoryFileNotFoundError
InvalidMemorySchemaError
MemoryValidationError
MemoryScopeError
MemoryEvidenceMissingError
MemoryDuplicateError
MemoryUpdateRejectedError
MemoryConfidenceError
MemoryStatusError
MemoryLockViolationError
MemoryContextBuildError
MemoryReportError
```

Error 예시:

```json
{
  "error_type": "MemoryEvidenceMissingError",
  "message": "Memory update candidate has no evidence.",
  "candidate_id": "MUC-000001",
  "scope": "CHANNEL",
  "target_id": "future",
  "severity": "MEDIUM",
  "suggested_fix": "Attach quality_report.json or learning_report.json as evidence.",
  "created_at": "2026-07-10T10:00:00"
}
```

---

# 29. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
MemoryEngine
MemoryLoader
MemoryValidator
MemoryWriter
MemoryContextBuilder
MemoryRetriever
MemoryUpdateCandidateValidator
MemoryDeduplicator
MemoryConfidenceManager
MemoryStatusManager
MemoryAgingManager
MemoryReportBuilder
MemoryLogger
MemoryEvidenceLinker
MemoryScopeResolver
```

---

# 30. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/13_MEMORY_ENGINE.md
→ engines/memory/
```

예시 구조:

```text
engines/
└── memory/
    ├── memory_engine.py
    ├── memory_loader.py
    ├── memory_validator.py
    ├── memory_writer.py
    ├── memory_context_builder.py
    ├── memory_retriever.py
    ├── memory_update_candidate_validator.py
    ├── memory_deduplicator.py
    ├── memory_confidence_manager.py
    ├── memory_status_manager.py
    ├── memory_aging_manager.py
    ├── memory_report_builder.py
    ├── memory_logger.py
    ├── memory_evidence_linker.py
    └── memory_scope_resolver.py
```

---

# 31. Main Public Operations

Memory Engine은 최소 다음 작업을 제공해야 한다.

```text
load_memory(scope, target_id)
validate_memory(memory_entry)
build_memory_context(project_id, stage)
search_memory(query, scope, target_id)
create_memory_update_candidate(candidate)
apply_memory_update(candidate_id)
reject_memory_update(candidate_id, reason)
deduplicate_memory(scope, target_id)
update_confidence(memory_id, confidence)
update_status(memory_id, status)
build_memory_report(scope, target_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
Scope 검증
Evidence 검증
중복 검사
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 32. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Memory 폴더 구조 생성
Company Memory 로드/저장
Channel Memory 로드/저장
Template Memory 로드/저장
Provider Memory 로드/저장
Memory Entry Schema 검증
Stage별 Memory Context 생성
Memory Update Candidate 저장
Evidence 없는 Candidate 거부
중복 Memory 기본 감지
Memory Report 기본 생성
Memory Event Log 기록
```

v1.0에서 하지 않아도 되는 것:

```text
복잡한 Vector Database
고급 Semantic Search
자동 Template 변경 적용
완전 자동 Memory Confidence 학습
외부 대시보드
실시간 Memory 시각화 UI
```

v1.0에서는 파일 기반 Memory 구조로 시작한다.

---

# 33. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Memory 폴더 구조를 생성할 수 있다.
Company Memory를 로드하고 저장할 수 있다.
Channel Memory를 로드하고 저장할 수 있다.
Template Memory를 로드하고 저장할 수 있다.
Provider Memory를 로드하고 저장할 수 있다.
Memory Entry를 검증할 수 있다.
Memory Update Candidate를 저장할 수 있다.
Evidence 없는 Memory Update를 거부할 수 있다.
중복 Memory를 감지할 수 있다.
Stage별 Memory Context Package를 생성할 수 있다.
Project Engine에 Memory Context를 제공할 수 있다.
Workflow Orchestrator에 Memory Context를 제공할 수 있다.
Learning Report 기반 Memory Update를 처리할 수 있다.
Memory Report를 생성할 수 있다.
Memory 관련 Error를 구조화해서 기록할 수 있다.
```

---

# 34. Non Goals

v1.0에서 Memory Engine이 하지 않는 것:

```text
고급 벡터 검색 시스템 구축
외부 사용자용 Memory 관리 UI
자동 Template Major Version 변경
자동 Channel 전략 변경
CEO 승인 없는 핵심 규칙 변경
복잡한 실시간 학습 시스템
Provider API 직접 호출
```

v1.0에서는 내부 ADOS 운영에 필요한 파일 기반 Memory 관리와 Context 제공 구조를 먼저 완성한다.

---

# 35. Critical Memory Rules

반드시 지켜야 할 규칙:

```text
1. Memory는 단순 로그가 아니다.

2. Memory는 다음 작업에 사용될 수 있어야 한다.

3. 작업 전 관련 Memory를 로드한다.

4. Project 완료 후 Learning 결과를 Memory 후보로 남긴다.

5. Evidence 없는 Memory는 저장하지 않는다.

6. 한 번의 결과를 과도하게 일반화하지 않는다.

7. 모든 Memory는 Scope를 가져야 한다.

8. 모든 Memory는 Confidence를 가져야 한다.

9. 중복 Memory는 병합하거나 업데이트한다.

10. Rejected Memory는 기본 Context에 포함하지 않는다.

11. LOCKED Memory는 승인 없이 변경하지 않는다.

12. Memory Engine은 Template을 직접 수정하지 않는다.

13. Memory Engine은 Provider를 직접 호출하지 않는다.

14. Memory 변경은 로그로 남긴다.
```

---

# 36. Final Principle

Memory Engine은 ADOS가 반복할수록 강해지게 만드는 시스템이다.

기억이 없으면 ADOS는 매번 처음부터 다시 시작한다.

기억이 있으면 ADOS는 실패를 반복하지 않고, 성공을 재사용하고, Channel을 성장시키고, Template을 진화시킬 수 있다.

좋은 Memory는 좋은 Project를 만들고,

좋은 Project는 좋은 Data를 만들고,

좋은 Data는 좋은 Learning을 만들고,

좋은 Learning은 더 좋은 Memory를 만든다.

Memory Engine의 목적은 과거를 저장하는 것이 아니라, 다음 Project를 더 좋게 만드는 것이다.
