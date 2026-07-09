# 11_PORTFOLIO_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Portfolio Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Portfolio Engine을 정의한다.

Portfolio Engine은 CHUNG COMPANY가 여러 Channel과 여러 Project를 동시에 운영할 수 있도록 관리하는 엔진이다.

Channel Engine이 하나의 Channel을 만들고 관리한다면, Portfolio Engine은 여러 Channel의 운영 상태, 우선순위, 진행 중 Project, 업로드 일정, 병목, 성과, 리소스 배분을 관리한다.

이 문서는 다음을 정의한다.

```text
Portfolio란 무엇인가
Portfolio Engine의 책임은 무엇인가
여러 Channel을 어떻게 관리하는가
여러 Project를 어떻게 추적하는가
Project 우선순위는 어떻게 판단하는가
업로드 일정은 어떻게 관리하는가
병목은 어떻게 감지하는가
Portfolio Report는 어떻게 생성하는가
Claude Code가 어떤 구조로 구현해야 하는가
```

이 문서는 다음 문서들과 직접 연결된다.

```text
03_ARCHITECTURE.md
04_AI_ORGANIZATION.md
07_PROJECT_SPEC.md
08_TEMPLATE_SYSTEM.md
09_CHANNEL_ENGINE.md
12_PROJECT_ENGINE.md
13_MEMORY_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
27_GROWTH_ENGINE.md
29_ANALYTICS_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Portfolio는 CHUNG COMPANY가 운영하는 Channel과 Project의 전체 묶음이다.

전체 구조:

```text
Company
↓
Portfolio
↓
Channels
↓
Projects
↓
Videos
↓
Analytics
↓
Learning
```

Portfolio Engine은 다음 질문에 답해야 한다.

```text
현재 어떤 Channel들이 운영 중인가?
각 Channel의 상태는 어떤가?
현재 어떤 Project들이 진행 중인가?
어떤 Project가 가장 우선인가?
어떤 Channel에 다음 Project를 만들어야 하는가?
어떤 Project가 병목 상태인가?
업로드 일정은 지켜지고 있는가?
어떤 Channel이 성과가 좋은가?
어떤 Channel을 일시 중지해야 하는가?
어떤 Channel에 리소스를 더 줘야 하는가?
```

---

# 3. Portfolio Philosophy

## 3.1 Portfolio Is Company-Level Control

Portfolio는 영상 하나를 보는 구조가 아니다.

Portfolio는 회사 전체 운영을 보는 구조이다.

```text
Project = 영상 1개
Channel = 사업 단위 1개
Portfolio = 여러 사업 단위 전체 운영
```

## 3.2 Portfolio Balances Quality, Growth, and Consistency

Portfolio Engine은 단순히 많은 영상을 만들기 위한 엔진이 아니다.

다음 균형을 관리해야 한다.

```text
Quality
Growth
Upload Consistency
Resource Usage
Learning Value
Revenue Potential
Brand Stability
```

## 3.3 Portfolio Does Not Produce Content

Portfolio Engine은 대본, 이미지, 음성, 자막을 만들지 않는다.

Portfolio Engine은 무엇을 먼저 만들고, 어떤 Channel을 우선하고, 어떤 Project가 막혔는지 판단한다.

---

# 4. Portfolio Engine Responsibilities

Portfolio Engine의 책임은 다음과 같다.

```text
Channel 등록
Channel 상태 추적
Project 등록
Project 상태 추적
Project 우선순위 계산
Upload Schedule 관리
Channel별 작업량 관리
진행 중 Project 병목 감지
성과 좋은 Channel 식별
성과 낮은 Channel 식별
Channel별 제작 균형 관리
Portfolio Report 생성
COO에게 운영 요약 제공
```

Portfolio Engine이 하지 않는 것:

```text
Channel을 직접 생성하지 않는다.
Project를 직접 생성하지 않는다.
영상 제작 Stage를 직접 실행하지 않는다.
Quality Score를 직접 계산하지 않는다.
Analytics 데이터를 직접 수집하지 않는다.
Template을 직접 수정하지 않는다.
Provider를 직접 호출하지 않는다.
```

---

# 5. Portfolio Data Location

v1.0에서는 단순한 파일 기반 구조를 사용한다.

Portfolio 중심 파일:

```text
memory/company_portfolio.json
```

Portfolio Report 파일:

```text
reports/portfolio_report.json
reports/upload_schedule.json
reports/bottleneck_report.json
reports/channel_priority_report.json
reports/project_priority_report.json
```

Portfolio 로그:

```text
logs/portfolio.log
logs/portfolio_events.jsonl
```

v1.0에서 별도 `portfolio/` 폴더를 만들 수도 있지만, 기본 기준은 `memory/company_portfolio.json`이다.

---

# 6. company_portfolio.json Schema

```json
{
  "portfolio": {
    "id": "chung_company_portfolio",
    "owner": "CHUNG COMPANY",
    "system": "ADOS",
    "version": "1.0.0",
    "status": "ACTIVE",
    "created_at": "2026-07-10T09:00:00",
    "updated_at": "2026-07-10T09:00:00"
  },

  "operating_goals": {
    "north_star_metric": "monthly_net_revenue",
    "supporting_metrics": [
      "quality_score",
      "watch_time",
      "retention",
      "ctr",
      "subscriber_conversion",
      "upload_consistency",
      "rpm"
    ]
  },

  "channels": [],

  "active_projects": [],

  "upload_schedule": [],

  "priority_policy": {
    "quality_first": true,
    "growth_aware": true,
    "avoid_overloading_single_channel": true,
    "prefer_learning_value": true
  },

  "operating_limits": {
    "max_active_projects_total": 5,
    "max_active_projects_per_channel": 2,
    "minimum_quality_score_for_ready": 95
  },

  "reports": {
    "portfolio_report": "reports/portfolio_report.json",
    "upload_schedule": "reports/upload_schedule.json",
    "bottleneck_report": "reports/bottleneck_report.json",
    "channel_priority_report": "reports/channel_priority_report.json",
    "project_priority_report": "reports/project_priority_report.json"
  }
}
```

---

# 7. Channel Portfolio Entry Schema

Portfolio에 등록되는 Channel 정보는 다음 구조를 따른다.

```json
{
  "channel_id": "future",
  "channel_name": "Beyond Humanity",
  "status": "ACTIVE",
  "priority": "HIGH",

  "template": {
    "template_id": "future",
    "template_version": "1.0.0"
  },

  "production": {
    "active_project_count": 1,
    "completed_project_count": 0,
    "published_project_count": 0,
    "last_project_id": null,
    "last_published_at": null
  },

  "quality": {
    "average_quality_score": null,
    "last_quality_score": null,
    "hard_fail_count": 0
  },

  "growth": {
    "growth_status": "NO_DATA",
    "ctr_average": null,
    "retention_average": null,
    "revenue_estimate": null
  },

  "risk": {
    "status": "NORMAL",
    "open_critical_errors": 0,
    "open_escalations": 0
  },

  "recommendation": {
    "create_next_project": true,
    "reason": "New active channel with no published project yet."
  }
}
```

---

# 8. Project Portfolio Entry Schema

Portfolio에 등록되는 Project 정보는 다음 구조를 따른다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "project_name": "100만 년 후 인간은 어떤 모습일까?",

  "status": "STORY",
  "current_stage": "STORY",
  "owner_department": "Story Department",

  "priority": {
    "score": 88,
    "level": "HIGH",
    "reason": "High strategic fit and strong growth potential."
  },

  "schedule": {
    "created_at": "2026-07-10T09:35:00",
    "target_ready_at": null,
    "target_publish_at": null,
    "is_delayed": false
  },

  "quality": {
    "current_score": null,
    "quality_status": "NOT_REVIEWED",
    "hard_fail": false
  },

  "risk": {
    "open_critical_messages": 0,
    "open_escalations": 0,
    "bottleneck": false,
    "bottleneck_reason": null
  }
}
```

---

# 9. Portfolio Status

Portfolio는 다음 상태를 가진다.

```text
ACTIVE
PAUSED
MAINTENANCE
ERROR
ARCHIVED
```

## ACTIVE

정상 운영 상태.

## PAUSED

전체 Project 생성 또는 진행이 일시 중지된 상태.

## MAINTENANCE

구조 정리, Template 수정, 대규모 업데이트 중인 상태.

## ERROR

Portfolio 파일 또는 핵심 상태 검증 실패.

## ARCHIVED

보관 상태.

---

# 10. Channel Registration Flow

Channel이 생성되면 Portfolio에 등록되어야 한다.

흐름:

```text
Channel Created
↓
Channel Engine sends registration request
↓
Portfolio Engine validates channel entry
↓
Channel added to company_portfolio.json
↓
Portfolio Report updated
↓
Portfolio Event logged
```

등록 조건:

```text
Channel Status가 ACTIVE
channel_id가 중복되지 않음
template_snapshot.json 존재
channel.yaml 유효
필수 Channel Reports 존재
```

---

# 11. Project Registration Flow

Project가 생성되면 Portfolio에 등록되어야 한다.

흐름:

```text
Project Created
↓
Project Engine sends registration request
↓
Portfolio Engine validates project entry
↓
Project added to active_projects
↓
Project priority calculated
↓
Upload Schedule updated if needed
↓
Portfolio Event logged
```

등록 조건:

```text
Project ID 유효
Channel이 Portfolio에 등록되어 있음
Project Status가 INITIALIZED 이상
project.json 존재
channel_snapshot.json 존재
template_snapshot.json 존재
```

---

# 12. Priority Calculation

Portfolio Engine은 Project 우선순위를 계산할 수 있어야 한다.

기본 Priority Score:

```yaml
priority_score:
  strategic_fit: 20
  growth_potential: 20
  channel_need: 15
  upload_urgency: 15
  quality_readiness: 10
  resource_efficiency: 10
  learning_value: 10
```

점수 기준:

```text
90~100
CRITICAL Priority

80~89
HIGH Priority

60~79
MEDIUM Priority

40~59
LOW Priority

40 미만
HOLD
```

Priority는 고정값이 아니다.

Project 상태, 품질, 일정, 병목, 성장 가능성에 따라 변경될 수 있다.

---

# 13. Channel Priority Rules

Channel 우선순위 판단 기준:

```text
최근 업로드 공백
성장 가능성
최근 품질 점수
Learning 가치
수익 가능성
Template 검증 상태
Brand 안정성
진행 중 Project 수
Open Critical Error 수
```

Channel에 Project를 더 만들어도 되는 조건:

```text
Channel Status가 ACTIVE
Open Critical Error 없음
진행 중 Project 수가 제한 이하
최근 품질 문제가 심각하지 않음
Template 또는 Brand 검증 문제가 없음
```

Channel에 Project 생성을 중단해야 하는 조건:

```text
Channel Status가 PAUSED 또는 ERROR
Open Critical Error 존재
Brand 불안정
반복 Quality Fail
Template 개선 필요
진행 중 Project 과다
```

---

# 14. Upload Schedule Management

Portfolio Engine은 업로드 일정을 관리한다.

업로드 일정 파일:

```text
reports/upload_schedule.json
```

예시:

```json
{
  "schedule": [
    {
      "project_id": "20260710-093500-future-million-year-human",
      "channel_id": "future",
      "target_publish_at": "2026-07-15T18:00:00",
      "status": "PLANNED",
      "publish_mode": "human_review"
    }
  ]
}
```

업로드 상태:

```text
PLANNED
READY
PUBLISHED
MISSED
CANCELLED
```

v1.0에서는 실제 자동 업로드보다 일정 관리와 Package 준비 추적이 우선이다.

---

# 15. Bottleneck Detection

Portfolio Engine은 병목을 감지해야 한다.

병목 조건:

```text
Project가 같은 Stage에 오래 머무름
Quality에서 반복 실패
Auto Fix가 3회 이상 반복
Open Critical Message 존재
Open Escalation 존재
필수 Output 누락
Provider 실패 반복
Upload Schedule 지연
Channel별 Project 과다
```

Bottleneck Report 예시:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "bottleneck": true,
  "stage": "VISUAL",
  "severity": "HIGH",
  "reason": "Visual prompt regeneration failed 3 times.",
  "recommended_action": "Escalate to Project Manager and Visual Department Lead."
}
```

---

# 16. Resource Balance Rules

Portfolio Engine은 특정 Channel이나 Stage에 작업이 과도하게 몰리지 않도록 관리한다.

기본 규칙:

```text
하나의 Channel에 진행 중 Project가 과도하게 몰리지 않게 한다.
Quality 문제가 많은 Channel은 새 Project를 줄인다.
성과가 좋은 Channel에는 우선순위를 줄 수 있다.
하지만 품질이 불안정하면 무리하게 확장하지 않는다.
새 Channel은 초기 테스트 Project 수를 제한한다.
```

v1.0 기본 제한:

```yaml
operating_limits:
  max_active_projects_total: 5
  max_active_projects_per_channel: 2
  max_auto_fix_projects_total: 2
  max_quality_blocked_projects_total: 2
```

---

# 17. Portfolio Reports

Portfolio Engine은 다음 Report를 생성한다.

```text
reports/portfolio_report.json
reports/channel_priority_report.json
reports/project_priority_report.json
reports/bottleneck_report.json
reports/upload_schedule.json
```

## 17.1 portfolio_report.json

```json
{
  "portfolio_id": "chung_company_portfolio",
  "status": "ACTIVE",
  "total_channels": 1,
  "active_channels": 1,
  "total_projects": 1,
  "active_projects": 1,
  "ready_projects": 0,
  "published_projects": 0,
  "open_bottlenecks": 0,
  "open_critical_errors": 0,
  "summary": "Portfolio is active with one channel and one active project.",
  "updated_at": "2026-07-10T10:00:00"
}
```

## 17.2 channel_priority_report.json

```json
{
  "channels": [
    {
      "channel_id": "future",
      "priority": "HIGH",
      "recommendation": "Create next test project after first upload package is ready.",
      "reason": "New channel requires initial performance data."
    }
  ]
}
```

## 17.3 project_priority_report.json

```json
{
  "projects": [
    {
      "project_id": "20260710-093500-future-million-year-human",
      "priority_score": 88,
      "priority_level": "HIGH",
      "next_action": "Continue current workflow."
    }
  ]
}
```

---

# 18. Portfolio and COO

Portfolio Engine은 COO AI Employee에게 운영 요약을 제공한다.

COO에게 제공하는 정보:

```text
전체 Channel 상태
전체 Project 상태
우선순위 높은 Project
지연된 Project
Open Critical Error
Open Escalation
업로드 일정 위험
성과 좋은 Channel
성과 낮은 Channel
리소스 병목
추천 조치
```

COO는 Portfolio Report를 바탕으로 다음을 결정한다.

```text
Project 우선순위 변경
Channel 일시 중지
Full Regeneration 승인 여부
Template 개선 검토
운영 전략 변경
CEO Escalation 필요 여부
```

---

# 19. Portfolio and Growth Engine

Portfolio Engine은 Growth Engine의 결과를 사용한다.

Growth Engine에서 받는 정보:

```text
Topic Score
Channel Growth Status
CTR Prediction
Retention Prediction
Revenue Potential
Subscriber Conversion Potential
```

Portfolio Engine은 Growth Score만 보고 결정하지 않는다.

다음 기준과 함께 판단한다.

```text
Quality
Brand Stability
Resource Availability
Upload Schedule
Learning Value
Channel Strategy
```

---

# 20. Portfolio and Analytics Engine

Analytics Engine은 Published Project의 성과를 분석한다.

Portfolio Engine은 Analytics 결과를 받아 다음에 활용한다.

```text
Channel 우선순위 조정
Project 유형 우선순위 조정
Upload Schedule 조정
성과 낮은 Channel 감지
성과 좋은 Channel 확장 판단
```

Portfolio Engine은 Analytics 데이터를 직접 수집하지 않는다.

---

# 21. Portfolio and Learning Engine

Learning Engine은 Project 결과를 학습한다.

Portfolio Engine은 Learning 결과를 다음에 활용한다.

```text
반복 실패 Channel 감지
성공 Pattern이 많은 Channel 감지
Template 개선 필요 Channel 감지
Project 우선순위 조정
신규 Channel 확장 판단
```

---

# 22. Portfolio Logs

Portfolio Engine은 다음 로그를 남긴다.

```text
logs/portfolio.log
logs/portfolio_events.jsonl
```

로그 대상:

```text
Channel 등록
Project 등록
Project 상태 업데이트
Channel 상태 업데이트
Priority 변경
Upload Schedule 변경
Bottleneck 감지
Portfolio Report 생성
COO Report 생성
Error 발생
```

Event 예시:

```json
{
  "event_type": "PROJECT_PRIORITY_UPDATED",
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "old_priority": "MEDIUM",
  "new_priority": "HIGH",
  "reason": "Upload schedule urgency increased.",
  "created_at": "2026-07-10T10:00:00"
}
```

---

# 23. Error Types

Portfolio Engine의 Error Type은 다음과 같다.

```text
PortfolioFileNotFoundError
InvalidPortfolioSchemaError
ChannelNotRegisteredError
ProjectNotRegisteredError
DuplicateChannelEntryError
DuplicateProjectEntryError
InvalidPriorityScoreError
UploadScheduleError
BottleneckDetectionError
PortfolioReportError
PortfolioStateError
```

Error 예시:

```json
{
  "error_type": "ChannelNotRegisteredError",
  "message": "Project belongs to a channel that is not registered in portfolio.",
  "channel_id": "future",
  "project_id": "20260710-093500-future-million-year-human",
  "severity": "HIGH",
  "suggested_fix": "Register channel before registering project.",
  "created_at": "2026-07-10T10:00:00"
}
```

---

# 24. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
PortfolioEngine
PortfolioLoader
PortfolioValidator
PortfolioStateManager
ChannelPortfolioRegistry
ProjectPortfolioRegistry
PriorityCalculator
UploadScheduleManager
BottleneckDetector
ResourceBalanceChecker
PortfolioReportBuilder
PortfolioLogger
COOReportBuilder
```

---

# 25. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/11_PORTFOLIO_ENGINE.md
→ engines/portfolio/
```

예시 구조:

```text
engines/
└── portfolio/
    ├── portfolio_engine.py
    ├── portfolio_loader.py
    ├── portfolio_validator.py
    ├── portfolio_state_manager.py
    ├── channel_portfolio_registry.py
    ├── project_portfolio_registry.py
    ├── priority_calculator.py
    ├── upload_schedule_manager.py
    ├── bottleneck_detector.py
    ├── resource_balance_checker.py
    ├── portfolio_report_builder.py
    ├── coo_report_builder.py
    └── portfolio_logger.py
```

---

# 26. Main Public Operations

Portfolio Engine은 최소 다음 작업을 제공해야 한다.

```text
load_portfolio()
validate_portfolio()
register_channel(channel_id)
update_channel_status(channel_id, status)
register_project(project_id)
update_project_status(project_id, status)
calculate_channel_priority(channel_id)
calculate_project_priority(project_id)
update_upload_schedule(project_id, schedule)
detect_bottlenecks()
build_portfolio_report()
build_coo_report()
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
중복 등록 방지
상태 검증
파일 존재 확인
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 27. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
memory/company_portfolio.json 생성 또는 로드
Channel 등록
Project 등록
Channel 상태 추적
Project 상태 추적
Project Priority 기본 계산
Upload Schedule 파일 생성
Bottleneck 기본 감지
Portfolio Report 생성
COO Report 생성용 Summary 생성
Portfolio Event Log 기록
```

v1.0에서 하지 않아도 되는 것:

```text
복잡한 자동 리소스 최적화
실시간 운영 대시보드
다중 사용자 운영 권한 관리
자동 예산 배분
정교한 수익 예측 모델
자동 Channel 폐쇄 결정
```

---

# 28. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Portfolio 파일을 생성하거나 로드할 수 있다.
Channel을 Portfolio에 등록할 수 있다.
Project를 Portfolio에 등록할 수 있다.
Channel 상태를 추적할 수 있다.
Project 상태를 추적할 수 있다.
Project 우선순위를 계산할 수 있다.
업로드 일정을 저장할 수 있다.
진행 중 Project 병목을 감지할 수 있다.
Portfolio Report를 생성할 수 있다.
COO에게 전달할 운영 Summary를 생성할 수 있다.
중복 Channel 등록을 막을 수 있다.
중복 Project 등록을 막을 수 있다.
Portfolio 관련 Error를 구조화해서 기록할 수 있다.
```

---

# 29. Non Goals

v1.0에서 Portfolio Engine이 하지 않는 것:

```text
외부 사용자용 Portfolio Dashboard
YouTube Analytics API 직접 수집
자동 수익 정산
광고 예산 자동 집행
복잡한 인력 관리 시스템
Channel 자동 폐쇄
CEO 승인 없는 전략 변경
```

v1.0에서는 내부 ADOS 운영에 필요한 전체 Channel / Project 추적과 우선순위 관리 구조를 먼저 완성한다.

---

# 30. Critical Portfolio Rules

반드시 지켜야 할 규칙:

```text
1. Portfolio는 Company 전체 운영을 관리한다.

2. Portfolio Engine은 콘텐츠를 직접 제작하지 않는다.

3. Channel 생성 후 Portfolio에 등록해야 한다.

4. Project 생성 후 Portfolio에 등록해야 한다.

5. 중복 Channel 등록을 허용하지 않는다.

6. 중복 Project 등록을 허용하지 않는다.

7. ACTIVE가 아닌 Channel에 새 Project를 무리하게 배정하지 않는다.

8. Open Critical Error가 있는 Channel은 우선순위를 낮추거나 중단한다.

9. Quality 문제가 반복되는 Project는 병목으로 감지한다.

10. Growth Score만 보고 우선순위를 결정하지 않는다.

11. Brand와 Quality를 훼손하는 확장은 금지한다.

12. Portfolio Report는 COO 판단에 사용될 수 있어야 한다.

13. 모든 중요한 Portfolio 변경은 로그로 남긴다.
```

---

# 31. Final Principle

Portfolio Engine은 CHUNG COMPANY의 운영 시야를 넓히는 시스템이다.

Project 하나만 보면 영상 제작자가 된다.

Channel 하나만 보면 채널 운영자가 된다.

Portfolio 전체를 보면 회사 운영자가 된다.

CHUNG COMPANY는 하나의 영상이 아니라 여러 Channel과 Project를 운영하는 AI 콘텐츠 회사이다.

Portfolio Engine의 목적은 좋은 Project를 많이 만드는 것이 아니라, 좋은 Channel을 지속적으로 성장시키는 운영 판단을 가능하게 만드는 것이다.
