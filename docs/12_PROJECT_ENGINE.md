# 12_PROJECT_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Project Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Project Engine을 정의한다.

Project Engine은 Channel 아래에서 영상 1개 단위의 Project를 생성하고, Project 상태, 폴더 구조, 필수 파일, Snapshot, Stage Output, Report, Package 준비 상태를 관리하는 엔진이다.

Project는 단순한 영상 파일이 아니다.

Project는 하나의 영상을 만들기 위한 전체 작업 단위이다.

Project Engine은 다음을 담당한다.

```text
Project 생성 요청 검증
Channel Context 로드
Template Snapshot 저장
Channel Snapshot 저장
Project ID 생성
Project 폴더 구조 생성
project.json 생성
topic.json 생성
Project 상태 관리
Stage별 필수 Output 검증
Workflow Orchestrator에 실행 요청
Quality Gate 결과 반영
Auto Fix 상태 관리
Upload Package 준비 상태 확인
Learning 완료 상태 확인
Portfolio에 Project 등록 및 상태 보고
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
13_MEMORY_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
16_TIMELINE_ENGINE.md
26_QUALITY_ENGINE.md
28_PUBLISHING_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Project Engine은 하나의 Channel 안에서 하나의 영상 제작 Project를 생성하고 관리하는 엔진이다.

전체 흐름:

```text
Channel
↓
Project Engine
↓
Project Folder
↓
Workflow Orchestrator
↓
Production Engines
↓
Quality Engine
↓
Publishing Engine
↓
Analytics Engine
↓
Learning Engine
```

Project Engine은 Project를 직접 제작하지 않는다.

Project Engine은 Project가 올바르게 생성되고, 올바른 순서로 진행되고, 올바른 기준을 통과하는지 관리한다.

---

# 3. Project Engine Philosophy

## 3.1 Project Is a Controlled Work Unit

Project는 자유롭게 파일을 넣는 폴더가 아니다.

Project는 상태, 입력, 출력, 검증, 로그, 품질 기준을 가진 통제된 작업 단위이다.

## 3.2 Channel Context First

Project는 Channel 없이 생성되지 않는다.

Project 생성 전 반드시 Channel Context를 로드해야 한다.

필수 Context:

```text
channel.yaml
template_snapshot.json
brand.yaml
story.yaml
visual.yaml
voice.yaml
quality.yaml
growth.yaml
provider.yaml
memory.yaml
communication.yaml
thinking.yaml
```

## 3.3 Snapshot First

Project 생성 시점의 Channel과 Template 기준을 반드시 저장한다.

필수 Snapshot:

```text
channel_snapshot.json
template_snapshot.json
```

## 3.4 Workflow Controlled

Project Engine은 Stage를 직접 실행하지 않는다.

Stage 실행은 Workflow Orchestrator가 담당한다.

Project Engine은 상태와 파일 구조를 관리하고, Workflow Orchestrator가 실행할 수 있는 준비 상태를 제공한다.

---

# 4. Project Engine Responsibilities

Project Engine의 책임은 다음과 같다.

```text
Create Project Request 검증
Channel 존재 및 ACTIVE 상태 확인
Channel Context 로드
Project ID 생성
Project Path 생성
Project 폴더 구조 생성
project.json 생성
topic.json 생성
channel_snapshot.json 생성
template_snapshot.json 생성
기본 logs/ reports/ snapshots/ 생성
Project 상태 전환 관리
Stage별 필수 Output 검증
Project Lock 관리
Project Snapshot 관리
Project Report 생성
Quality Gate 결과 반영
Package 준비 상태 확인
Learning 완료 상태 확인
Portfolio Engine에 Project 등록 및 업데이트
```

Project Engine이 하지 않는 것:

```text
Research를 직접 수행하지 않는다.
Story를 직접 작성하지 않는다.
Visual Prompt를 직접 작성하지 않는다.
Provider를 직접 호출하지 않는다.
Quality Score를 직접 계산하지 않는다.
Analytics 데이터를 직접 수집하지 않는다.
Template을 직접 수정하지 않는다.
```

---

# 5. Project Creation Input

Project 생성 요청은 다음 구조를 따른다.

```yaml
create_project:
  channel_id: future

  topic:
    source: user
    title: "100만 년 후 인간은 어떤 모습일까?"
    category: future
    keywords:
      - future
      - human evolution
      - AI
      - civilization

  languages:
    master: ko
    target:
      - ko
      - en

  publish_mode: human_review

  automation:
    run_workflow_after_creation: false
    stop_before_publish: true
    allow_partial_regeneration: true
```

필수 입력:

```text
channel_id
topic.source
topic.title 또는 topic.id
languages.master
languages.target
publish_mode
```

---

# 6. Project Creation Flow

Project 생성 흐름은 다음과 같다.

```text
Create Project Request
↓
Request Validation
↓
Channel ACTIVE Check
↓
Channel Context Load
↓
Project ID Build
↓
Project Path Build
↓
Duplicate Project Check
↓
Project Folder Creation
↓
project.json Creation
↓
topic.json Creation
↓
Channel Snapshot Creation
↓
Template Snapshot Creation
↓
Default Folders Creation
↓
Default Logs Creation
↓
Project Validation
↓
Portfolio Registration
↓
Project Status INITIALIZED
```

옵션으로 Workflow 자동 시작이 켜져 있으면:

```text
INITIALIZED
↓
Workflow Orchestrator receives start request
↓
Project Status RESEARCH
```

---

# 7. Project ID Rule

Project ID는 `07_PROJECT_SPEC.md`의 규칙을 따른다.

형식:

```text
YYYYMMDD-HHMMSS-{channel_id}-{topic_slug}
```

예시:

```text
20260710-093500-future-million-year-human
```

Project Engine은 다음을 수행해야 한다.

```text
Topic title에서 slug 생성
한글 Topic을 영어 slug로 변환하거나 안전한 slug로 변환
공백 제거
특수문자 제거
중복 Project ID 방지
동일 ID 존재 시 suffix 추가
```

중복 예시:

```text
20260710-093500-future-million-year-human
20260710-093500-future-million-year-human-02
```

---

# 8. Project Directory Structure

Project Engine은 `07_PROJECT_SPEC.md`의 구조에 맞게 Project 폴더를 생성한다.

기본 위치:

```text
projects/{channel_id}/{year}/{month}/{project_id}/
```

v1.0에서 반드시 생성해야 하는 폴더:

```text
research/
knowledge/
story/
direction/
timeline/
languages/
prompts/
assets/
assets/images/
assets/motion/
assets/audio/
assets/subtitles/
assets/thumbnails/
assets/temp/
edit/
package/
reports/
snapshots/
logs/
```

언어별 폴더:

```text
languages/ko/
languages/en/
```

Target Language는 Project 생성 요청에 따라 달라질 수 있다.

---

# 9. Required Initial Files

Project 생성 시 반드시 생성되는 파일:

```text
project.json
topic.json
channel_snapshot.json
template_snapshot.json
logs/project.log
logs/communication.jsonl
logs/decision_records.jsonl
logs/self_reviews.jsonl
logs/risk_register.jsonl
logs/error_log.jsonl
```

선택적으로 초기화 가능한 파일:

```text
reports/final_report.json
reports/project_status.json
snapshots/INITIALIZED/
```

---

# 10. project.json Management

Project Engine은 `project.json`을 Project의 중심 상태 파일로 관리한다.

Project Engine이 관리하는 주요 필드:

```text
project_id
project_name
status
current_stage
created_at
updated_at
channel
topic
languages
providers
automation
quality
organization
communication
thinking
```

Project Engine은 다음 상황에서 `project.json`을 업데이트한다.

```text
Project 생성
Stage 시작
Stage 완료
Stage 실패
Quality Gate 결과 반영
Auto Fix 시작
Auto Fix 완료
Package 생성
Ready 상태 전환
Published 상태 기록
Analytics 시작
Learning 완료
Complete 상태 전환
```

---

# 11. topic.json Management

`topic.json`은 Project의 주제 정보를 담는다.

Project Engine은 Topic 정보를 다음 기준으로 정리한다.

```text
원본 Topic 보존
Topic slug 생성
Category 저장
Keyword 저장
Risk Note 저장
Growth Note 저장 가능
```

예시:

```json
{
  "topic_id": "million-year-human",
  "source": "USER",
  "title": "100만 년 후 인간은 어떤 모습일까?",
  "slug": "million-year-human",
  "category": "future",
  "keywords": [
    "future",
    "human evolution",
    "AI",
    "civilization"
  ],
  "risk_notes": [
    "Future predictions must be framed as possibilities, not certainties."
  ],
  "growth_notes": []
}
```

---

# 12. Channel Snapshot

Project 생성 시 Channel Snapshot을 저장한다.

파일:

```text
channel_snapshot.json
```

Channel Snapshot에는 Project 생성 당시의 Channel 설정이 포함되어야 한다.

포함 대상:

```text
channel.yaml 요약
brand.yaml
story.yaml
visual.yaml
motion.yaml
voice.yaml
subtitle.yaml
quality.yaml
growth.yaml
provider.yaml
employees.yaml
communication.yaml
thinking.yaml
memory.yaml 요약
```

Snapshot 목적:

```text
Project 재현성
Channel 변경 영향 분리
Quality 문제 원인 분석
Learning 분석
```

---

# 13. Template Snapshot

Project 생성 시 Template Snapshot도 저장한다.

파일:

```text
template_snapshot.json
```

Template Snapshot은 Channel 생성 시 저장된 Template Snapshot을 Project에 복사하거나, 현재 Resolved Template 기준으로 생성할 수 있다.

원칙:

```text
Project 생성 당시 기준을 보존한다.
Project 진행 중 임의 수정하지 않는다.
Template 변경은 Project에 자동 반영하지 않는다.
```

---

# 14. Project State Management

Project Engine은 Project 상태 전환을 관리한다.

기본 상태:

```text
NEW
INITIALIZED
RESEARCH
KNOWLEDGE
STORY
DIRECTION
TIMELINE
VISUAL
MOTION
VOICE
SUBTITLE
EDITING
QUALITY
AUTO_FIX
PACKAGE
READY
PUBLISHED
ANALYTICS
LEARNING
COMPLETE
```

Project Engine은 다음을 검증해야 한다.

```text
현재 상태에서 다음 상태로 이동 가능한가
이전 Stage Output이 존재하는가
Open Critical Message가 없는가
Open Escalation이 없는가
Quality Gate를 우회하지 않는가
Package 전 필수 파일이 존재하는가
Complete 전 Learning Report가 존재하는가
```

---

# 15. Allowed State Transitions

허용되는 기본 전환:

```text
NEW → INITIALIZED
INITIALIZED → RESEARCH
RESEARCH → KNOWLEDGE
KNOWLEDGE → STORY
STORY → DIRECTION
DIRECTION → TIMELINE
TIMELINE → VISUAL
VISUAL → MOTION
MOTION → VOICE
VOICE → SUBTITLE
SUBTITLE → EDITING
EDITING → QUALITY
QUALITY → PACKAGE
PACKAGE → READY
READY → PUBLISHED
PUBLISHED → ANALYTICS
ANALYTICS → LEARNING
LEARNING → COMPLETE
```

조건부 전환:

```text
QUALITY → AUTO_FIX
AUTO_FIX → QUALITY
QUALITY → PACKAGE
```

금지 전환:

```text
NEW → STORY
INITIALIZED → VISUAL
RESEARCH → PACKAGE
QUALITY → COMPLETE
PACKAGE → COMPLETE
```

---

# 16. Stage Output Validation

Project Engine은 Stage 완료 전 필수 Output을 확인한다.

## RESEARCH

```text
research/research.json
research/sources.json
research/facts.json
```

## KNOWLEDGE

```text
knowledge/knowledge.json
knowledge/claims.json
knowledge/fact_check.json
```

## STORY

```text
story/outline.json
story/hook.json
story/script_master.json
story/script_master.md
story/story_review.json
```

## DIRECTION

```text
direction/scene_plan.json
direction/emotion_plan.json
direction/camera_plan.json
direction/director_notes.md
```

## TIMELINE

```text
timeline/timeline.json
timeline/timeline_review.json
timeline/timeline_lock.json
```

## VISUAL

```text
prompts/midjourney_image_prompts.json
prompts/prompt_review.json
assets/images/
```

## MOTION

```text
prompts/midjourney_video_prompts.json
assets/motion/
```

## VOICE

```text
languages/{lang}/narration.txt
languages/{lang}/voice.json
assets/audio/
```

## SUBTITLE

```text
languages/{lang}/subtitle.srt
assets/subtitles/
```

## EDITING

```text
edit/edit_plan.json
edit/render_plan.json
edit/final_timeline.json
```

## QUALITY

```text
reports/quality_report.json
```

## PACKAGE

```text
package/upload_package.json
package/metadata_{lang}.json
package/thumbnail.png
```

## ANALYTICS

```text
reports/analytics_report.json
```

## LEARNING

```text
reports/learning_report.json
```

---

# 17. Project Context Builder

Project Engine은 각 Engine이 사용할 Project Context를 만들 수 있어야 한다.

Project Context에는 다음이 포함된다.

```text
Project Config
Topic
Channel Snapshot
Template Snapshot
Brand Context
Story Rules
Visual Rules
Voice Rules
Quality Rules
Growth Rules
Provider Rules
Communication Rules
Thinking Rules
Memory Context
Current Stage
Required Input Files
Expected Output Files
```

Project Context 예시:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "current_stage": "STORY",
  "topic": {
    "title": "100만 년 후 인간은 어떤 모습일까?"
  },
  "languages": ["ko", "en"],
  "required_inputs": [
    "knowledge/knowledge.json",
    "knowledge/claims.json",
    "knowledge/fact_check.json",
    "channel_snapshot.json"
  ],
  "expected_outputs": [
    "story/script_master.json",
    "story/script_master.md"
  ]
}
```

---

# 18. Workflow Orchestrator Integration

Project Engine은 Workflow Orchestrator와 연결된다.

Project Engine의 역할:

```text
Project 생성
Project 상태 제공
Stage Input/Output 검증
State Transition 수행
Project Context 제공
```

Workflow Orchestrator의 역할:

```text
다음 Stage 결정
Stage 실행 요청
Department 호출
Retry 처리
Auto Fix 흐름 관리
Escalation 요청
```

Project Engine은 Stage를 직접 실행하지 않는다.

---

# 19. Communication Integration

Project Engine은 Communication 시스템과 연결되어야 한다.

Project 생성 시 기본 로그 생성:

```text
logs/communication.jsonl
logs/decision_records.jsonl
logs/self_reviews.jsonl
logs/risk_register.jsonl
logs/error_log.jsonl
```

상태 전환 전 확인:

```text
Open Critical Message 없음
Open Escalation 없음
Required Approval 완료
Required Revision 완료
```

Project Engine은 상태 변경 시 Event를 기록해야 한다.

```json
{
  "event_type": "PROJECT_STATUS_CHANGED",
  "project_id": "20260710-093500-future-million-year-human",
  "old_status": "STORY",
  "new_status": "DIRECTION",
  "changed_by": "project_manager",
  "created_at": "2026-07-10T12:00:00"
}
```

---

# 20. Thinking Integration

Project Engine은 Decision Record, Self Review, Risk Register 위치를 관리한다.

필수 파일:

```text
logs/decision_records.jsonl
logs/self_reviews.jsonl
logs/risk_register.jsonl
```

Project Engine은 다음을 직접 작성하지 않아도 된다.

```text
긴 내부 추론
부서별 상세 판단
Stage별 창작 결정
```

Project Engine은 Thinking 기록이 존재해야 하는 시점에 파일 존재와 기본 형식을 검증한다.

---

# 21. Memory Integration

Project 생성 전 Memory Engine을 통해 Channel Memory를 로드할 수 있어야 한다.

사용 시점:

```text
Project 생성
Project Context 생성
Stage 실행 전
Learning 완료 후
```

Project Engine의 역할:

```text
Memory 위치 제공
Project Context에 Memory Summary 포함
Learning 완료 후 Memory Update 상태 확인
```

Memory 자체 업데이트는 Memory Engine 또는 Learning Engine이 수행한다.

---

# 22. Portfolio Integration

Project 생성 후 Portfolio Engine에 Project를 등록한다.

등록 정보:

```text
project_id
channel_id
project_name
status
current_stage
priority 초기값
created_at
target_languages
```

Project 상태가 변경될 때 Portfolio Engine에 업데이트를 보낼 수 있어야 한다.

예시:

```text
INITIALIZED → RESEARCH
STORY → DIRECTION
QUALITY → AUTO_FIX
PACKAGE → READY
```

Portfolio Engine은 이 정보를 사용해 전체 운영 상태를 판단한다.

---

# 23. Quality Gate Integration

Project Engine은 Quality Engine의 결과를 반영한다.

Quality Report 위치:

```text
reports/quality_report.json
```

Quality 결과에 따른 처리:

```text
95~100
QUALITY → PACKAGE

90~94
Human Review Recommended

80~89
QUALITY → AUTO_FIX

70~79
Partial Regeneration Required

70 미만
Fail / Escalation
```

Project Engine은 Quality Score를 직접 계산하지 않는다.

하지만 Quality Gate를 우회한 상태 전환은 막아야 한다.

---

# 24. Auto Fix Management

Auto Fix 상태는 Project Engine과 Workflow Orchestrator가 함께 관리한다.

Project Engine의 역할:

```text
AUTO_FIX 상태 전환
Auto Fix 대상 파일 기록
Retry Count 추적
Auto Fix Report 존재 확인
Auto Fix 완료 후 QUALITY로 복귀
```

Auto Fix Report 위치:

```text
reports/auto_fix_report.json
```

Retry 제한:

```yaml
retry:
  max_retry_per_issue: 3
  max_total_retry_per_project: 10
```

같은 문제가 3회 이상 반복되면 Escalation한다.

---

# 25. Package Readiness Check

Project Engine은 READY 상태 전환 전 Package를 검증해야 한다.

필수 파일:

```text
package/upload_package.json
package/thumbnail.png
package/metadata_{lang}.json
```

Final Video가 생성된 경우:

```text
package/final_video_{lang}.mp4
```

언어별 필수 연결:

```text
languages/{lang}/subtitle.srt
languages/{lang}/metadata.json 또는 package/metadata_{lang}.json
```

READY 전환 조건:

```text
Quality Pass
Upload Package 존재
Thumbnail 존재
Metadata 존재
Open Critical Message 없음
Open Escalation 없음
publish_mode 확인
```

---

# 26. Published Status

v1.0에서는 실제 YouTube API 업로드보다 수동 업로드 기록을 우선한다.

Published 기록 예시:

```yaml
publish_record:
  project_id: 20260710-093500-future-million-year-human
  channel_id: future
  published_at: 2026-07-15T18:00:00
  platform: youtube
  url: ""
  publish_mode: manual
```

Published 상태 전환 조건:

```text
READY 상태
사용자 또는 Publishing Engine의 Published 기록 존재
upload_package.json 존재
```

---

# 27. Completion Check

Project가 COMPLETE가 되기 위한 조건:

```text
PUBLISHED 상태 기록
reports/analytics_report.json 존재
reports/learning_report.json 존재
Memory Update 완료 또는 Memory Update Candidate 존재
Final Report 존재
Open Critical Message 없음
Open Escalation 없음
```

Project Engine은 Learning 없이 COMPLETE 처리하지 않는다.

---

# 28. Reports

Project Engine이 관리하거나 생성하는 Report:

```text
reports/project_status.json
reports/final_report.json
```

다른 Engine이 생성하지만 Project Engine이 존재를 확인하는 Report:

```text
reports/quality_report.json
reports/auto_fix_report.json
reports/growth_prediction.json
reports/analytics_report.json
reports/learning_report.json
```

`project_status.json` 예시:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "status": "STORY",
  "current_stage": "STORY",
  "channel_id": "future",
  "quality_status": "NOT_REVIEWED",
  "open_critical_messages": 0,
  "open_escalations": 0,
  "updated_at": "2026-07-10T12:00:00"
}
```

---

# 29. Logs

Project Engine은 다음 로그를 관리한다.

```text
logs/project.log
logs/error_log.jsonl
logs/communication.jsonl
logs/decision_records.jsonl
logs/self_reviews.jsonl
logs/risk_register.jsonl
```

로그 대상:

```text
Project 생성
Project 검증
Project 상태 변경
Stage Output 검증
Snapshot 생성
Quality Gate 결과 반영
Auto Fix 시작/완료
Package 검증
Published 기록
Complete 처리
Error 발생
```

---

# 30. Error Types

Project Engine의 Error Type은 다음과 같다.

```text
InvalidProjectRequestError
ProjectAlreadyExistsError
ProjectNotFoundError
InvalidProjectIdError
ChannelNotFoundError
ChannelNotActiveError
MissingChannelContextError
ProjectFolderCreationError
MissingProjectFileError
InvalidProjectSchemaError
InvalidProjectStatusError
InvalidStateTransitionError
MissingStageOutputError
MissingChannelSnapshotError
MissingTemplateSnapshotError
OpenCriticalMessageError
OpenEscalationError
QualityGateError
PackageReadinessError
ProjectCompletionError
```

Error 예시:

```json
{
  "error_type": "InvalidStateTransitionError",
  "message": "Cannot move from STORY to VISUAL.",
  "project_id": "20260710-093500-future-million-year-human",
  "current_status": "STORY",
  "requested_status": "VISUAL",
  "severity": "HIGH",
  "suggested_fix": "Complete DIRECTION and TIMELINE stages first.",
  "created_at": "2026-07-10T12:00:00"
}
```

---

# 31. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
ProjectEngine
ProjectFactory
ProjectValidator
ProjectStateManager
ProjectPathBuilder
ProjectIdBuilder
ProjectConfigLoader
ProjectContextBuilder
ProjectSnapshotManager
ProjectLockManager
ProjectStageOutputValidator
ProjectReportBuilder
ProjectPackageReadinessChecker
ProjectCompletionChecker
ProjectLogger
ProjectPortfolioReporter
```

---

# 32. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/12_PROJECT_ENGINE.md
→ engines/project/
```

예시 구조:

```text
engines/
└── project/
    ├── project_engine.py
    ├── project_factory.py
    ├── project_validator.py
    ├── project_state_manager.py
    ├── project_path_builder.py
    ├── project_id_builder.py
    ├── project_config_loader.py
    ├── project_context_builder.py
    ├── project_snapshot_manager.py
    ├── project_lock_manager.py
    ├── project_stage_output_validator.py
    ├── project_report_builder.py
    ├── project_package_readiness_checker.py
    ├── project_completion_checker.py
    ├── project_logger.py
    └── project_portfolio_reporter.py
```

---

# 33. Main Public Operations

Project Engine은 최소 다음 작업을 제공해야 한다.

```text
create_project(request)
load_project(project_id)
validate_project(project_id)
get_project_status(project_id)
change_project_status(project_id, next_status)
build_project_context(project_id, stage)
validate_stage_outputs(project_id, stage)
create_project_snapshot(project_id, label)
check_quality_gate(project_id)
check_package_readiness(project_id)
record_published(project_id, publish_record)
check_completion(project_id)
build_project_report(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
상태 검증
필수 파일 존재 확인
로그 기록
Error 발생 시 구조화된 Error 기록
Portfolio 업데이트 가능
```

---

# 34. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Project 생성 요청 검증
Channel ACTIVE 확인
Project ID 생성
Project 폴더 구조 생성
project.json 생성
topic.json 생성
channel_snapshot.json 생성
template_snapshot.json 생성
기본 logs/ 생성
기본 reports/ 생성
Project 상태 전환 관리
Stage Output 기본 검증
Project Context 생성
Portfolio 등록
Quality Gate 결과 기반 상태 전환
Package Readiness 확인
```

v1.0에서 하지 않아도 되는 것:

```text
실제 영상 렌더링 직접 수행
YouTube API 자동 업로드
고급 웹 Project Dashboard
다중 사용자 Project 권한 관리
복잡한 실시간 진행률 UI
```

---

# 35. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Channel 아래에서 Project를 생성할 수 있다.
Channel이 ACTIVE가 아니면 Project 생성을 막을 수 있다.
Project ID를 안정적으로 생성할 수 있다.
Project 폴더 구조를 생성할 수 있다.
project.json과 topic.json을 생성할 수 있다.
Channel Snapshot과 Template Snapshot을 저장할 수 있다.
Project 상태를 조회할 수 있다.
Project 상태를 변경할 수 있다.
잘못된 상태 전환을 막을 수 있다.
Stage별 필수 Output을 검증할 수 있다.
Project Context를 생성할 수 있다.
Workflow Orchestrator가 사용할 Context를 제공할 수 있다.
Quality Gate를 우회한 READY 전환을 막을 수 있다.
Package 준비 상태를 확인할 수 있다.
Learning 전 COMPLETE 전환을 막을 수 있다.
Portfolio에 Project 상태를 보고할 수 있다.
```

---

# 36. Non Goals

v1.0에서 Project Engine이 하지 않는 것:

```text
Research 직접 수행
Story 직접 작성
Visual Prompt 직접 작성
음성 직접 생성
영상 직접 렌더링
YouTube 자동 업로드
Analytics 직접 수집
Template 직접 수정
Provider 직접 호출
```

v1.0에서는 내부 ADOS 운영에 필요한 Project 생성, 상태 관리, Context 제공, 검증 구조를 먼저 완성한다.

---

# 37. Critical Project Engine Rules

반드시 지켜야 할 규칙:

```text
1. Project는 Channel 없이 생성하지 않는다.

2. Channel이 ACTIVE가 아니면 Project를 생성하지 않는다.

3. Project 생성 시 Channel Snapshot을 저장한다.

4. Project 생성 시 Template Snapshot을 저장한다.

5. Project Engine은 Stage를 직접 실행하지 않는다.

6. Stage 실행은 Workflow Orchestrator가 담당한다.

7. Project Engine은 상태 전환을 검증해야 한다.

8. Stage별 필수 Output이 없으면 다음 Stage로 이동하지 않는다.

9. Open Critical Message가 있으면 다음 Stage로 이동하지 않는다.

10. Open Escalation이 있으면 다음 Stage로 이동하지 않는다.

11. Quality Gate를 통과하지 못하면 READY가 될 수 없다.

12. Learning Report 없이 COMPLETE가 될 수 없다.

13. Project Engine은 Provider를 직접 호출하지 않는다.

14. 모든 중요한 상태 변경은 로그로 남긴다.
```

---

# 38. Final Principle

Project Engine은 영상을 직접 만드는 엔진이 아니다.

Project Engine은 영상 제작이 올바른 구조 안에서 진행되도록 관리하는 엔진이다.

좋은 Project Engine은 Project를 만들고,

상태를 지키고,

필수 파일을 검증하고,

Workflow가 일할 수 있는 Context를 제공하고,

Quality Gate를 우회하지 못하게 막고,

Learning까지 완료되도록 관리한다.

Project Engine의 목적은 단순한 폴더 생성이 아니라, 고품질 영상 제작이 반복 가능한 운영 단위를 만드는 것이다.
