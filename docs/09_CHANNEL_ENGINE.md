# 09_CHANNEL_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Channel Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Channel Engine을 정의한다.

Channel Engine은 Template에서 실제 운영 가능한 Channel을 생성하고 초기화하는 엔진이다.

Channel은 단순한 폴더가 아니다.

Channel은 CHUNG COMPANY가 실제로 운영하는 유튜브 사업 단위이다.

Channel Engine은 다음을 담당한다.

```text
Template 기반 Channel 생성
Channel 폴더 구조 생성
Channel 설정 파일 생성
Template Snapshot 저장
Brand / Story / Visual / Voice / Quality / Growth 설정 적용
Channel Memory 초기화
Channel Reports 초기화
Channel Logs 초기화
Project 생성 가능 상태 검증
Channel 상태 관리
```

이 문서는 다음 문서들과 직접 연결된다.

```text
03_ARCHITECTURE.md
07_PROJECT_SPEC.md
08_TEMPLATE_SYSTEM.md
10_BRAND_SYSTEM.md
11_PORTFOLIO_ENGINE.md
12_PROJECT_ENGINE.md
13_MEMORY_ENGINE.md
26_QUALITY_ENGINE.md
27_GROWTH_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Channel은 Template에서 생성되는 실제 운영 단위이다.

전체 흐름:

```text
Template
↓
Channel
↓
Project
↓
Video
↓
Analytics
↓
Learning
↓
Template Improvement
```

Channel은 다음을 가진다.

```text
Channel Identity
Brand Rules
Story Rules
Visual Rules
Motion Rules
Voice Rules
Subtitle Rules
Quality Rules
Growth Rules
Provider Rules
AI Employee Settings
Communication Rules
Thinking Rules
Publishing Rules
Learning Rules
Memory
Reports
Logs
Projects
```

---

# 3. Channel Engine Philosophy

## 3.1 Channel Is a Business Unit

Channel은 단순 설정 파일이 아니다.

Channel은 다음을 가진 사업 단위이다.

```text
Target Audience
Brand Identity
Content Strategy
Production Rules
Quality Standard
Growth Strategy
Revenue Potential
Memory
Learning Loop
```

## 3.2 Channel Must Come From Template

Channel은 반드시 Template에서 생성되어야 한다.

금지:

```text
Template 없이 Channel 직접 생성
Channel 설정을 임의로 수동 조합
Project 생성 후 Channel 설정 붙이기
```

허용:

```text
Template 검증
Resolved Template 생성
Channel Folder 생성
Channel Config 저장
Channel Memory 초기화
Project 생성 준비
```

## 3.3 Channel Must Be Reproducible

Channel 생성 시점의 Template Snapshot을 저장해야 한다.

이유:

```text
어떤 Template에서 Channel이 만들어졌는지 추적
Template 변경 후에도 Channel 생성 원인 확인
Quality 문제 원인 분석
Learning과 Template Evolution 연결
```

---

# 4. Channel Engine Responsibilities

Channel Engine의 책임은 다음과 같다.

```text
Create Channel Request 검증
Template 존재 확인
Template Resolver 호출
Template Validator 결과 확인
Template Score 확인
Channel ID 생성 또는 검증
Channel Folder 생성
Channel 설정 파일 생성
Resolved Template 파일 복사
Template Snapshot 생성
Channel Memory 초기화
Channel Reports 초기화
Channel Logs 초기화
Channel 상태 관리
Channel 검증
Project 생성 가능 여부 제공
```

Channel Engine이 하지 않는 것:

```text
Template 내용을 직접 설계하지 않는다.
Brand 전략을 직접 작성하지 않는다.
Project를 직접 제작하지 않는다.
영상 Asset을 생성하지 않는다.
Quality Score를 직접 계산하지 않는다.
Analytics를 직접 분석하지 않는다.
```

---

# 5. Channel Creation Input

Channel 생성 요청은 다음 구조를 따른다.

```yaml
create_channel:
  channel_id: future
  channel_name: Beyond Humanity
  template_id: future
  template_version: 1.0.0

  languages:
    default: ko
    supported:
      - ko
      - en

  publish_mode: human_review

  owner: CHUNG COMPANY

  automation:
    allow_full_auto_after_trust: true
    minimum_quality_score_for_auto: 95

  project_policy:
    allow_ai_topic_recommendation: true
    default_project_languages:
      - ko
      - en
```

필수 입력:

```text
channel_id
channel_name
template_id
languages.default
languages.supported
publish_mode
owner
```

---

# 6. Channel ID Rules

Channel ID는 다음 규칙을 따른다.

```text
소문자 사용
공백 금지
특수문자 금지
영문, 숫자, underscore 사용
너무 긴 이름 금지
의미가 명확해야 함
```

좋은 예:

```text
future
psychology
civilization
history_reimagined
fitness_body
ai_business
```

나쁜 예:

```text
My Channel
미래채널
future!!!
channel_001_random
new test channel
```

---

# 7. Channel Creation Flow

Channel 생성 흐름은 다음과 같다.

```text
Create Channel Request
↓
Input Validation
↓
Template Existence Check
↓
Template Loader
↓
Template Resolver
↓
Template Lock Check
↓
Template Validator
↓
Template Score Check
↓
Channel Path Build
↓
Channel Folder Creation
↓
channel.yaml Creation
↓
Resolved Template Files Copy
↓
Template Snapshot Creation
↓
Channel Memory Initialization
↓
Reports Initialization
↓
Logs Initialization
↓
Channel Validation
↓
Channel Status ACTIVE
```

---

# 8. Channel Directory Structure

Channel은 다음 위치에 생성된다.

```text
channels/{channel_id}/
```

기본 구조:

```text
channels/
└── {channel_id}/
    ├── channel.yaml
    ├── template_snapshot.json
    │
    ├── brand.yaml
    ├── story.yaml
    ├── visual.yaml
    ├── motion.yaml
    ├── voice.yaml
    ├── subtitle.yaml
    ├── quality.yaml
    ├── growth.yaml
    ├── employees.yaml
    ├── provider.yaml
    ├── memory.yaml
    ├── communication.yaml
    ├── thinking.yaml
    ├── publishing.yaml
    ├── learning.yaml
    │
    ├── projects/
    │
    ├── reports/
    │   ├── channel_status.json
    │   ├── growth_report.json
    │   ├── quality_summary.json
    │   ├── project_summary.json
    │   └── memory_update_report.json
    │
    └── logs/
        ├── channel.log
        ├── error_log.jsonl
        ├── decision_records.jsonl
        └── events.jsonl
```

v1.0 최소 구조:

```text
channel.yaml
template_snapshot.json
brand.yaml
story.yaml
visual.yaml
voice.yaml
quality.yaml
growth.yaml
employees.yaml
provider.yaml
memory.yaml
communication.yaml
thinking.yaml
projects/
reports/
logs/
```

---

# 9. channel.yaml Schema

`channel.yaml`은 Channel의 중심 설정 파일이다.

```yaml
channel:
  id: future
  name: Beyond Humanity
  status: active
  owner: CHUNG COMPANY
  created_at: 2026-07-10T09:00:00
  updated_at: 2026-07-10T09:00:00
  version: 1.0.0

template:
  id: future
  version: 1.0.0
  snapshot_file: template_snapshot.json
  inherited:
    - base
    - documentary
    - future

languages:
  default: ko
  supported:
    - ko
    - en

automation:
  mode: human_review
  allow_full_auto_after_trust: true
  minimum_quality_score_for_auto: 95
  require_human_review_before_publish: true

project_policy:
  allow_project_creation: true
  allow_ai_topic_recommendation: true
  default_project_languages:
    - ko
    - en
  require_template_snapshot: true
  require_channel_snapshot: true

quality:
  pass_score: 95
  hard_fail_blocks_publish: true
  require_quality_report: true

memory:
  enabled: true
  file: memory.yaml
  load_before_project: true
  update_after_learning: true

reports:
  channel_status: reports/channel_status.json
  growth_report: reports/growth_report.json
  quality_summary: reports/quality_summary.json
  project_summary: reports/project_summary.json

logs:
  channel_log: logs/channel.log
  error_log: logs/error_log.jsonl
  event_log: logs/events.jsonl
  decision_records: logs/decision_records.jsonl
```

---

# 10. Channel Status

Channel은 다음 상태를 가진다.

```text
DRAFT
INITIALIZING
ACTIVE
PAUSED
ARCHIVED
ERROR
```

## 10.1 DRAFT

Channel 생성 요청은 있으나 아직 운영 가능하지 않은 상태.

## 10.2 INITIALIZING

Template에서 Channel 파일을 생성하고 있는 상태.

## 10.3 ACTIVE

Project 생성과 운영이 가능한 상태.

## 10.4 PAUSED

일시적으로 Project 생성이 중단된 상태.

## 10.5 ARCHIVED

보관 상태. 신규 Project를 만들지 않는다.

## 10.6 ERROR

검증 실패 또는 복구가 필요한 상태.

---

# 11. Allowed Status Transitions

허용되는 상태 전환:

```text
DRAFT → INITIALIZING
INITIALIZING → ACTIVE
INITIALIZING → ERROR
ACTIVE → PAUSED
PAUSED → ACTIVE
ACTIVE → ARCHIVED
PAUSED → ARCHIVED
ERROR → INITIALIZING
ERROR → ARCHIVED
```

금지되는 상태 전환:

```text
DRAFT → ACTIVE
ARCHIVED → ACTIVE
ERROR → ACTIVE
```

`ERROR → ACTIVE`는 반드시 재검증 후 `INITIALIZING → ACTIVE` 흐름을 거쳐야 한다.

---

# 12. Resolved Template Files

Channel 생성 시 Template System에서 Resolved Template을 받아와 Channel 폴더에 저장한다.

Resolved Template에서 복사되는 파일:

```text
brand.yaml
story.yaml
visual.yaml
motion.yaml
voice.yaml
subtitle.yaml
quality.yaml
growth.yaml
employees.yaml
provider.yaml
memory.yaml
communication.yaml
thinking.yaml
publishing.yaml
learning.yaml
```

규칙:

```text
Channel 폴더의 설정 파일은 생성 시점의 Resolved Template 기준이다.
Channel 운영 중 수정이 필요한 경우 Channel Manager의 승인 기록이 필요하다.
Template 원본을 직접 수정하지 않는다.
```

---

# 13. Template Snapshot

Channel 생성 시 반드시 Template Snapshot을 저장한다.

파일:

```text
channels/{channel_id}/template_snapshot.json
```

Snapshot에는 다음 정보가 포함되어야 한다.

```json
{
  "template_id": "future",
  "template_version": "1.0.0",
  "resolved_at": "2026-07-10T09:00:00",
  "inherits": [
    "base",
    "documentary",
    "future"
  ],
  "resolved_files": [
    "brand.yaml",
    "story.yaml",
    "visual.yaml",
    "voice.yaml",
    "quality.yaml",
    "growth.yaml"
  ],
  "template_score": 96,
  "locked_fields": [
    "brand.identity.core",
    "quality.pass_score"
  ]
}
```

---

# 14. Channel Memory Initialization

Channel 생성 시 `memory.yaml`을 초기화한다.

초기 Memory 구조:

```yaml
memory:
  channel_id: future
  enabled: true
  created_at: 2026-07-10T09:00:00
  updated_at: 2026-07-10T09:00:00

successful_patterns:
  topics: []
  hooks: []
  titles: []
  thumbnails: []
  visual_styles: []
  voice_settings: []

failed_patterns:
  topics: []
  hooks: []
  titles: []
  visual_styles: []
  provider_failures: []
  quality_failures: []

project_history: []

learning_notes: []
```

Channel Memory는 Project 생성 전 Context로 사용된다.

Project 완료 후 Learning 결과가 Channel Memory에 반영된다.

---

# 15. Channel Reports Initialization

Channel 생성 시 기본 Report 파일을 만든다.

## 15.1 channel_status.json

```json
{
  "channel_id": "future",
  "status": "ACTIVE",
  "created_at": "2026-07-10T09:00:00",
  "project_count": 0,
  "published_count": 0,
  "average_quality_score": null,
  "last_project_id": null,
  "last_updated": "2026-07-10T09:00:00"
}
```

## 15.2 project_summary.json

```json
{
  "channel_id": "future",
  "projects": [],
  "active_projects": [],
  "paused_projects": [],
  "completed_projects": []
}
```

## 15.3 quality_summary.json

```json
{
  "channel_id": "future",
  "average_quality_score": null,
  "quality_pass_count": 0,
  "quality_fail_count": 0,
  "hard_fail_count": 0,
  "common_quality_issues": []
}
```

## 15.4 growth_report.json

```json
{
  "channel_id": "future",
  "north_star_metric": "monthly_net_revenue",
  "status": "NO_DATA",
  "summary": {},
  "last_updated": "2026-07-10T09:00:00"
}
```

---

# 16. Channel Validation Rules

Channel Validator는 다음을 확인해야 한다.

필수 파일:

```text
channel.yaml
template_snapshot.json
brand.yaml
story.yaml
visual.yaml
voice.yaml
quality.yaml
growth.yaml
employees.yaml
provider.yaml
memory.yaml
communication.yaml
thinking.yaml
```

권장 파일:

```text
motion.yaml
subtitle.yaml
publishing.yaml
learning.yaml
```

필수 조건:

```text
channel.id 존재
channel.name 존재
channel.status 유효
template.id 존재
template.version 존재
languages.default 존재
languages.supported 존재
quality.pass_score 존재
memory.enabled 존재
provider 설정 존재
brand 정체성 존재
growth 기준 존재
projects/ 폴더 존재
reports/ 폴더 존재
logs/ 폴더 존재
```

검증 실패 시 Channel 상태는 `ERROR`가 된다.

---

# 17. Project Creation Readiness

Channel은 Project 생성 전에 준비 상태를 제공해야 한다.

Project 생성 가능 조건:

```text
Channel Status가 ACTIVE
channel.yaml 유효
template_snapshot.json 존재
brand.yaml 존재
story.yaml 존재
visual.yaml 존재
voice.yaml 존재
quality.yaml 존재
growth.yaml 존재
memory.yaml 존재
projects/ 폴더 존재
Open Critical Channel Error 없음
```

Project 생성 시 Channel Engine은 Project Engine에 다음 Context를 제공한다.

```text
Channel Config
Channel Snapshot
Template Snapshot
Brand Rules
Story Rules
Visual Rules
Voice Rules
Quality Rules
Growth Rules
Provider Rules
Employee Rules
Communication Rules
Thinking Rules
Memory Context
```

---

# 18. Channel Snapshot for Project

Project 생성 시 Channel Snapshot을 만들어 Project 폴더에 저장해야 한다.

파일:

```text
projects/{channel_id}/{year}/{month}/{project_id}/channel_snapshot.json
```

Snapshot 목적:

```text
Project 생성 당시 Channel 설정 보존
Channel 설정 변경 후에도 Project 재현 가능
Quality 문제 원인 추적
Learning 분석 가능
```

Channel Snapshot에는 최소 다음 정보가 포함된다.

```json
{
  "channel_id": "future",
  "channel_name": "Beyond Humanity",
  "channel_version": "1.0.0",
  "snapshot_at": "2026-07-10T09:35:00",
  "template_id": "future",
  "template_version": "1.0.0",
  "languages": {
    "default": "ko",
    "supported": ["ko", "en"]
  },
  "quality": {
    "pass_score": 95
  },
  "files_included": [
    "brand.yaml",
    "story.yaml",
    "visual.yaml",
    "voice.yaml",
    "quality.yaml",
    "growth.yaml"
  ]
}
```

---

# 19. Channel and Brand System

Channel Engine은 Brand System과 연결된다.

Channel 생성 시:

```text
brand.yaml 생성
Brand Validation 요청
Brand Context 준비
```

Project 생성 시:

```text
Brand Context를 Project Engine에 전달
Brand Rules를 Quality Engine에서 사용할 수 있게 제공
```

Channel Engine은 Brand를 직접 판단하지 않는다.

Brand 판단은 Brand System이 수행한다.

---

# 20. Channel and Memory Engine

Channel Engine은 Memory Engine과 연결된다.

Channel 생성 시:

```text
Channel Memory 초기화
```

Project 생성 전:

```text
Channel Memory 로드
Project Context에 포함
```

Project 완료 후:

```text
Learning Engine 또는 Memory Engine이 Channel Memory 업데이트
Channel Engine은 업데이트 결과를 Channel Report에 반영
```

---

# 21. Channel and Portfolio Engine

Channel Engine은 Portfolio Engine과 연결된다.

Channel 생성 후:

```text
Portfolio에 Channel 등록
```

Channel 상태 변경 시:

```text
Portfolio에 상태 변경 보고
```

Channel Reports는 Portfolio Engine에서 다음 판단에 사용된다.

```text
어떤 Channel에 Project를 더 만들 것인가
어떤 Channel을 일시 중지할 것인가
어떤 Channel이 성장 중인가
어떤 Channel이 Template 개선이 필요한가
```

---

# 22. Channel and Quality Engine

Channel은 Quality 기준을 제공한다.

Quality Engine은 다음 파일을 참고한다.

```text
channels/{channel_id}/quality.yaml
channels/{channel_id}/brand.yaml
channels/{channel_id}/story.yaml
channels/{channel_id}/visual.yaml
```

Channel Engine은 Quality Score를 직접 계산하지 않는다.

하지만 Channel의 Quality Summary는 관리한다.

---

# 23. Channel and Growth Engine

Channel은 Growth 기준을 제공한다.

Growth Engine은 다음 파일을 참고한다.

```text
channels/{channel_id}/growth.yaml
channels/{channel_id}/memory.yaml
channels/{channel_id}/reports/growth_report.json
```

Channel Engine은 Growth Report를 직접 분석하지 않는다.

하지만 Growth Report 파일을 보관하고 상태를 추적한다.

---

# 24. Channel Logs

Channel Engine은 다음 로그를 남긴다.

```text
logs/channel.log
logs/events.jsonl
logs/error_log.jsonl
logs/decision_records.jsonl
```

로그 대상:

```text
Channel 생성 요청
Channel 생성 완료
Channel 검증 실패
Channel 상태 변경
Template Snapshot 생성
Memory 초기화
Report 초기화
Project 생성 준비 요청
Channel Snapshot 생성
Channel Error 발생
```

Event 예시:

```json
{
  "event_type": "CHANNEL_CREATED",
  "channel_id": "future",
  "template_id": "future",
  "template_version": "1.0.0",
  "created_at": "2026-07-10T09:00:00"
}
```

---

# 25. Error Types

Channel Engine의 Error Type은 다음과 같다.

```text
ChannelAlreadyExistsError
InvalidChannelIdError
InvalidChannelRequestError
TemplateNotFoundError
TemplateValidationError
TemplateScoreTooLowError
ChannelFolderCreationError
MissingChannelFileError
InvalidChannelConfigError
ChannelValidationError
ChannelStatusTransitionError
ChannelSnapshotError
ChannelMemoryInitializationError
ChannelReportInitializationError
```

Error는 다음 구조로 기록한다.

```json
{
  "error_type": "MissingChannelFileError",
  "message": "brand.yaml is missing.",
  "channel_id": "future",
  "location": "channels/future/brand.yaml",
  "severity": "HIGH",
  "suggested_fix": "Recreate channel from resolved template or restore missing file.",
  "created_at": "2026-07-10T09:10:00"
}
```

---

# 26. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
ChannelEngine
ChannelFactory
ChannelValidator
ChannelStateManager
ChannelPathBuilder
ChannelConfigLoader
ChannelSnapshotBuilder
ChannelMemoryInitializer
ChannelReportInitializer
ChannelReportBuilder
ChannelLogger
ChannelProjectContextBuilder
ChannelPortfolioReporter
```

---

# 27. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/09_CHANNEL_ENGINE.md
→ engines/channel/
```

예시 구조:

```text
engines/
└── channel/
    ├── channel_engine.py
    ├── channel_factory.py
    ├── channel_validator.py
    ├── channel_state_manager.py
    ├── channel_path_builder.py
    ├── channel_config_loader.py
    ├── channel_snapshot_builder.py
    ├── channel_memory_initializer.py
    ├── channel_report_initializer.py
    ├── channel_report_builder.py
    ├── channel_logger.py
    └── channel_project_context_builder.py
```

다른 Engine과의 연결:

```text
engines/template/
engines/brand/
engines/memory/
engines/project/
engines/portfolio/
```

---

# 28. Main Public Operations

Channel Engine은 최소 다음 작업을 제공해야 한다.

```text
create_channel(request)
validate_channel(channel_id)
load_channel(channel_id)
get_channel_status(channel_id)
change_channel_status(channel_id, status)
build_project_context(channel_id)
create_channel_snapshot(channel_id, project_id)
update_channel_report(channel_id, report_type)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
파일 존재 확인
상태 확인
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 29. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Channel 생성 요청 검증
Template Resolver 결과 입력 받기
Channel 폴더 생성
channel.yaml 생성
Resolved Template 파일 복사
template_snapshot.json 생성
memory.yaml 초기화
reports/ 기본 파일 생성
logs/ 기본 파일 생성
Channel Validation 수행
ACTIVE 상태 전환
Project 생성용 Channel Context 생성
```

v1.0에서 하지 않아도 되는 것:

```text
복잡한 웹 UI
실제 YouTube API 연동
실시간 Channel Dashboard
고급 자동 성장 전략 실행
다중 사용자 권한 관리
```

---

# 30. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Template에서 Channel을 생성할 수 있다.
Channel ID를 검증할 수 있다.
Channel Folder를 생성할 수 있다.
channel.yaml을 생성할 수 있다.
Resolved Template 파일을 Channel에 저장할 수 있다.
Template Snapshot을 생성할 수 있다.
Channel Memory를 초기화할 수 있다.
Channel Reports를 초기화할 수 있다.
Channel Logs를 초기화할 수 있다.
Channel 필수 파일을 검증할 수 있다.
Channel Status를 관리할 수 있다.
잘못된 Status 전환을 막을 수 있다.
Project 생성 가능 여부를 판단할 수 있다.
Project Engine에 Channel Context를 제공할 수 있다.
Project 생성 시 Channel Snapshot을 만들 수 있다.
```

---

# 31. Non Goals

v1.0에서 Channel Engine이 하지 않는 것:

```text
외부 사용자용 채널 관리 UI
YouTube 채널 API 직접 생성
YouTube 자동 업로드
실시간 성과 대시보드
복잡한 권한 관리
외부 SaaS용 Channel Tenant 관리
Template Marketplace 연동
```

v1.0에서는 내부 ADOS 운영에 필요한 Channel 생성과 검증 구조를 먼저 완성한다.

---

# 32. Critical Channel Rules

반드시 지켜야 할 규칙:

```text
1. Channel은 Template 없이 생성하지 않는다.

2. Template Validation 실패 시 Channel을 생성하지 않는다.

3. Template Score 80 미만이면 Channel 생성 금지.

4. Channel 생성 시 Template Snapshot을 저장한다.

5. Channel 생성 시 Memory를 초기화한다.

6. Channel 생성 시 Reports와 Logs를 초기화한다.

7. ACTIVE 상태가 아니면 Project를 생성하지 않는다.

8. Project 생성 시 Channel Snapshot을 저장한다.

9. Channel 설정 변경은 로그로 남긴다.

10. Channel Engine은 Project 제작을 직접 수행하지 않는다.

11. Channel Engine은 Quality Score를 직접 계산하지 않는다.

12. Channel Engine은 Provider를 직접 호출하지 않는다.

13. Channel은 CHUNG COMPANY의 사업 단위로 취급한다.
```

---

# 33. Final Principle

Channel은 단순 폴더가 아니다.

Channel은 CHUNG COMPANY가 실제로 운영하는 사업 단위이다.

좋은 Channel은 좋은 Template에서 생성된다.

좋은 Channel은 일관된 Brand를 가진다.

좋은 Channel은 좋은 Project를 반복한다.

좋은 Project는 데이터를 만든다.

좋은 데이터는 Learning을 만든다.

좋은 Learning은 Template과 Channel을 성장시킨다.

Channel Engine의 목적은 단순히 파일을 만드는 것이 아니라, 성장 가능한 Channel 운영 단위를 만드는 것이다.
