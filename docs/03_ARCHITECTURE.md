# 03_ARCHITECTURE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: System Architecture  

---

# 1. Purpose

이 문서는 CHUNG COMPANY / ADOS의 전체 시스템 아키텍처를 정의한다.

이 문서는 단순한 기술 구조 문서가 아니다.

이 문서는 CHUNG COMPANY라는 AI 콘텐츠 회사가 어떻게 작동해야 하는지, 그리고 ADOS가 그 회사를 어떤 구조로 운영해야 하는지를 정의하는 최상위 설계도이다.

이 문서는 다음 문서들의 기준이 된다.

```text
04_AI_ORGANIZATION.md
05_INTER_AI_COMMUNICATION.md
06_AI_THINKING_FRAMEWORK.md
07_PROJECT_SPEC.md
08_TEMPLATE_SYSTEM.md
09_CHANNEL_ENGINE.md
10_BRAND_SYSTEM.md
11_PORTFOLIO_ENGINE.md
12_PROJECT_ENGINE.md
13_MEMORY_ENGINE.md
14_PROVIDER_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
16_TIMELINE_ENGINE.md
17~31 Production / Control / Growth / Evolution 문서
```

---

# 2. Architecture Identity

ADOS는 단순한 유튜브 자동화 프로그램이 아니다.

ADOS는 AI Employee들이 Template 기반으로 Channel을 만들고, Project를 실행하며, 품질 검사와 학습을 반복하여 채널을 성장시키는 AI Digital Operating System이다.

핵심 정의:

```text
CHUNG COMPANY
=
AI 콘텐츠 제작 회사

ADOS
=
CHUNG COMPANY를 운영하는 AI Digital Operating System

Template
=
Channel을 생성하는 DNA

Channel
=
실제 운영되는 사업 단위

Project
=
영상 1개를 제작하는 작업 단위

Timeline
=
영상 제작의 핵심 설계도

Learning
=
다음 Project와 Template을 개선하는 성장 루프
```

---

# 3. Highest Architecture Rule

ADOS의 모든 구조는 다음 흐름을 깨면 안 된다.

```text
Template
↓
Channel
↓
Portfolio
↓
Project
↓
Workflow
↓
Timeline
↓
Production
↓
Quality
↓
Publishing
↓
Analytics
↓
Learning
↓
Template Evolution
```

이 흐름을 벗어난 구현은 잘못된 구현이다.

---

# 4. What This Architecture Is Not

ADOS 아키텍처는 다음이 아니다.

```text
단순 Script Runner
단순 Prompt Generator
단순 YouTube Upload Bot
단순 Video Automation Pipeline
단순 ChatGPT Wrapper
단순 폴더 생성기
단순 SaaS Backend
단순 영상 편집 도구
```

ADOS는 다음이다.

```text
Template 기반으로 Channel을 만들고,
Channel 아래에서 Project를 운영하며,
AI Employee들이 Workflow를 따라 협업하고,
Quality Gate를 통과한 콘텐츠만 Package로 만들고,
성과를 Learning하여 Template과 Channel을 성장시키는
AI 콘텐츠 회사 운영체제
```

---

# 5. Core Architecture Principles

## 5.1 Template First

Channel은 Template에서 생성된다.

Template 없이 Channel을 만들면 안 된다.

## 5.2 Channel First

Project는 반드시 Channel 아래에서 생성된다.

Channel 없는 Project는 만들면 안 된다.

## 5.3 Portfolio Aware

CHUNG COMPANY는 여러 Channel과 여러 Project를 동시에 운영할 수 있어야 한다.

따라서 Project 하나만 보는 구조는 부족하다.

## 5.4 Workflow Controlled

각 Engine은 독립적으로 마음대로 실행되지 않는다.

Workflow Orchestrator가 실행 순서, 상태, 실패, 재시도, 품질 게이트를 관리한다.

## 5.5 Timeline First

영상 제작의 중심은 최종 mp4 파일이 아니다.

중심은 Timeline이다.

Timeline은 Scene, Visual, Motion, Voice, Subtitle, Editing, Quality를 연결한다.

## 5.6 Memory Before Work

AI Employee와 Engine은 작업 전에 Memory를 불러와야 한다.

## 5.7 Learning After Work

Project 완료 후 결과는 Memory와 Template 개선으로 연결되어야 한다.

## 5.8 Provider Independent

Midjourney, Typecast 같은 외부 도구는 직접 호출하지 않는다.

반드시 Provider Interface와 Adapter를 통해 연결한다.

## 5.9 Quality Gate Mandatory

품질 점수 95점 미만 Project는 자동 통과할 수 없다.

## 5.10 Partial Regeneration First

실패 시 전체 재생성보다 부분 수정이 우선이다.

## 5.11 Human Review Initially

초기 운영 단계에서는 사람이 최종 확인한다.

## 5.12 Logs Are Required

중요한 작업, 결정, 실패, 수정, 승인, 상태 변경은 반드시 로그로 남긴다.

---

# 6. High Level System Model

ADOS의 최상위 구조는 다음과 같다.

```text
User / CEO
↓
COO AI Employee
↓
Portfolio Manager
↓
Template System
↓
Channel Engine
↓
Project Engine
↓
Workflow Orchestrator
↓
Core Engines
↓
Quality Engine
↓
Publishing Engine
↓
Analytics Engine
↓
Learning Engine
↓
AI Evolution Engine
```

---

# 7. Layered Architecture

ADOS는 다음 8개 Layer로 구성된다.

```text
1. Foundation Layer
2. Organization Layer
3. Core Data Layer
4. Business Layer
5. Core System Layer
6. Production Layer
7. Control / Growth Layer
8. Advanced Layer
```

각 Layer는 아래 Layer의 규칙을 따르고, 위 Layer에 기능을 제공한다.

---

# 8. Foundation Layer

Foundation Layer는 프로젝트의 철학과 기준을 정의한다.

문서:

```text
MASTER_PLAN.md
00_AI_CONTEXT.md
01_COMPANY.md
02_DEVELOPMENT_RULES.md
03_ARCHITECTURE.md
```

책임:

```text
프로젝트 정체성 정의
회사 목표 정의
개발 원칙 정의
금지사항 정의
문서 우선순위 정의
전체 시스템 흐름 정의
```

이 Layer는 실제 기능을 실행하지 않는다.

이 Layer는 모든 기능이 지켜야 할 기준을 제공한다.

---

# 9. Organization Layer

Organization Layer는 AI Employee 조직과 협업 방식을 정의한다.

문서:

```text
04_AI_ORGANIZATION.md
05_INTER_AI_COMMUNICATION.md
06_AI_THINKING_FRAMEWORK.md
```

핵심 구성:

```text
AI Employee
Department
Communication Bus
Message
Handoff Package
Decision Record
Self Review
Meeting
Escalation
Approval Authority
```

책임:

```text
누가 일하는가
누가 책임지는가
누가 승인하는가
어떻게 요청하는가
어떻게 검토하는가
어떻게 반려하는가
어떻게 수정 요청하는가
어떻게 기록하는가
```

---

# 10. Core Data Layer

Core Data Layer는 ADOS의 핵심 데이터 단위를 정의한다.

문서:

```text
07_PROJECT_SPEC.md
08_TEMPLATE_SYSTEM.md
```

핵심 데이터:

```text
Template
Channel
Project
Timeline
Asset
Memory
Quality Report
Learning Report
Decision Record
Handoff Package
```

책임:

```text
데이터 구조 정의
파일 구조 정의
상태 정의
필수 파일 정의
Snapshot 정의
검증 기준 정의
```

---

# 11. Business Layer

Business Layer는 실제 사업 운영 단위를 관리한다.

문서:

```text
09_CHANNEL_ENGINE.md
10_BRAND_SYSTEM.md
11_PORTFOLIO_ENGINE.md
12_PROJECT_ENGINE.md
```

책임:

```text
Channel 생성
Brand 적용
여러 Channel 관리
여러 Project 관리
Project 생성
운영 우선순위 결정
업로드 일정 관리
채널별 성장 상태 관리
```

Business Layer는 "영상 제작"보다 상위에 있다.

영상 제작 전에 먼저 채널과 운영 구조가 있어야 한다.

---

# 12. Core System Layer

Core System Layer는 모든 제작 엔진이 의존하는 기반 시스템이다.

문서:

```text
13_MEMORY_ENGINE.md
14_PROVIDER_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
16_TIMELINE_ENGINE.md
```

책임:

```text
Memory 로드/저장
Provider Interface 관리
Provider Adapter 관리
Workflow 실행
Stage 상태 관리
실패 재시도 관리
Timeline 생성
Timeline 검증
Scene과 Asset 매핑
```

Core System Layer가 안정적이지 않으면 Production Layer는 흔들린다.

---

# 13. Production Layer

Production Layer는 실제 콘텐츠 제작을 담당한다.

문서:

```text
17_RESEARCH_ENGINE.md
18_KNOWLEDGE_ENGINE.md
19_STORY_ENGINE.md
20_DIRECTION_ENGINE.md
21_VISUAL_ENGINE.md
22_MOTION_ENGINE.md
23_VOICE_ENGINE.md
24_SUBTITLE_ENGINE.md
25_EDITING_ENGINE.md
```

책임:

```text
Research 수행
Knowledge 정리
Story 작성
Direction 설계
Timeline 기반 Visual Prompt 생성
Motion Prompt 생성
Voice Script 생성
Subtitle 생성
Editing Plan 생성
Final Timeline 구성
```

Production Layer의 모든 결과물은 Project 폴더에 저장된다.

---

# 14. Control / Growth Layer

Control / Growth Layer는 품질, 성장, 출판, 분석, 학습을 담당한다.

문서:

```text
26_QUALITY_ENGINE.md
27_GROWTH_ENGINE.md
28_PUBLISHING_ENGINE.md
29_ANALYTICS_ENGINE.md
30_LEARNING_ENGINE.md
```

책임:

```text
Quality Score 계산
Hard Fail 감지
Auto Fix 판단
Growth 예측
SEO Package 생성
Publishing Package 생성
성과 데이터 분석
Learning Report 생성
Memory 업데이트
Template 개선 제안
```

---

# 15. Advanced Layer

Advanced Layer는 ADOS의 장기 진화를 담당한다.

문서:

```text
31_AI_EVOLUTION_ENGINE.md
```

책임:

```text
Template Evolution
AI Employee 개선
새로운 Template 제안
새로운 Channel 기회 탐색
운영 전략 개선
반복 실패 구조 개선
```

Advanced Layer는 v1.0의 핵심 구현 대상은 아니다.

하지만 v1.0 구조는 Advanced Layer가 나중에 붙을 수 있도록 설계되어야 한다.

---

# 16. Dependency Direction

ADOS의 의존성 방향은 아래를 따른다.

```text
Foundation
↓
Organization
↓
Core Data
↓
Business
↓
Core System
↓
Production
↓
Control / Growth
↓
Advanced
```

하위 Layer는 상위 Layer의 구체 구현에 직접 의존하지 않는다.

예시:

```text
Quality Engine은 MASTER_PLAN의 품질 원칙을 따른다.
하지만 MASTER_PLAN 파일을 실행 로직처럼 직접 조작하지 않는다.
```

---

# 17. Runtime Flow: Channel Creation

Channel 생성 흐름은 다음과 같다.

```text
User selects Template
↓
Template System loads Base Template
↓
Template System loads Category Template
↓
Template System loads Channel Template
↓
Template Resolver merges configuration
↓
Template Validator validates resolved Template
↓
Channel Engine creates Channel folder
↓
Brand System applies brand configuration
↓
Channel Memory initialized
↓
Channel Reports initialized
↓
Channel Status becomes ACTIVE
```

결과:

```text
channels/{channel_id}/
```

---

# 18. Runtime Flow: Project Creation

Project 생성 흐름은 다음과 같다.

```text
User enters Topic or requests AI Topic Recommendation
↓
Channel Engine provides Channel Context
↓
Project Engine creates Project
↓
Project Engine saves Channel Snapshot
↓
Project Engine saves Template Snapshot
↓
Project folders are created
↓
Project Status becomes INITIALIZED
↓
Workflow Orchestrator starts RESEARCH
```

결과:

```text
projects/{channel_id}/{year}/{month}/{project_id}/
```

---

# 19. Runtime Flow: Production

Project 제작 흐름은 다음과 같다.

```text
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
```

각 Stage는 다음을 수행한다.

```text
Input 확인
Memory 로드
작업 수행
Self Review
Output 저장
Handoff Package 생성
Quality 또는 Peer Review
다음 Stage로 전달
```

---

# 20. Runtime Flow: Quality and Auto Fix

Quality 흐름은 다음과 같다.

```text
Quality Engine receives Project Outputs
↓
Quality Engine checks required files
↓
Quality Engine checks Timeline integrity
↓
Quality Engine checks Brand consistency
↓
Quality Engine checks Story / Visual / Voice / Subtitle quality
↓
Quality Engine calculates score
↓
Decision
```

점수 기준:

```text
95~100
Pass

90~94
Human Review Recommended

80~89
Auto Fix

70~79
Partial Regeneration

Below 70
Fail / Escalation
```

Auto Fix 흐름:

```text
Issue Detection
↓
Root Cause Analysis
↓
Targeted Fix Request
↓
Partial Regeneration
↓
Recheck
↓
Pass or Escalate
```

전체 재생성은 COO 승인 없이는 수행하지 않는다.

---

# 21. Runtime Flow: Publishing

Publishing 흐름은 다음과 같다.

```text
Quality Passed
↓
Publishing Engine checks Package requirements
↓
Language-specific metadata generated
↓
Thumbnail checked
↓
Subtitle files checked
↓
Upload Package generated
↓
Project Status becomes READY
```

v1.0에서는 자동 업로드보다 Upload Package 생성이 우선이다.

---

# 22. Runtime Flow: Analytics and Learning

성과 분석과 학습 흐름은 다음과 같다.

```text
Project Published
↓
Analytics Data collected
↓
Analytics Engine creates analytics_report.json
↓
Learning Engine analyzes success and failure
↓
Learning Report generated
↓
Memory updated
↓
Template Improvement Proposal created if needed
```

Learning은 단순 기록이 아니다.

Learning은 다음 제작 품질을 높이는 데 사용되어야 한다.

---

# 23. Core Domain Objects

## 23.1 Template

Channel을 만들기 위한 DNA.

저장 위치:

```text
templates/
```

주요 파일:

```text
template.yaml
brand.yaml
story.yaml
visual.yaml
voice.yaml
subtitle.yaml
quality.yaml
growth.yaml
employees.yaml
provider.yaml
memory.yaml
communication.yaml
thinking.yaml
```

---

## 23.2 Channel

실제로 운영되는 유튜브 채널 단위.

저장 위치:

```text
channels/{channel_id}/
```

주요 파일:

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
memory.yaml
communication.yaml
thinking.yaml
```

---

## 23.3 Portfolio

여러 Channel과 Project를 동시에 관리하는 운영 단위.

저장 위치:

```text
portfolio/
```

또는 v1.0에서는 다음 파일로 시작할 수 있다.

```text
memory/company_portfolio.json
```

관리 대상:

```text
채널 목록
프로젝트 목록
업로드 일정
진행 상태
우선순위
병목
성과 요약
```

---

## 23.4 Project

영상 1개를 제작하는 작업 단위.

저장 위치:

```text
projects/{channel_id}/{year}/{month}/{project_id}/
```

주요 파일:

```text
project.json
topic.json
channel_snapshot.json
template_snapshot.json
timeline/timeline.json
reports/quality_report.json
reports/learning_report.json
package/upload_package.json
```

---

## 23.5 Timeline

영상 제작의 핵심 설계도.

저장 위치:

```text
projects/{channel_id}/{year}/{month}/{project_id}/timeline/timeline.json
```

Timeline은 다음을 연결한다.

```text
Scene
Image
Motion
Voice
Subtitle
Timing
Transition
Quality Check
```

---

## 23.6 Asset

Project에서 생성되는 제작 재료.

저장 위치:

```text
projects/{channel_id}/{year}/{month}/{project_id}/assets/
```

종류:

```text
images
motion
audio
subtitles
thumbnails
temp
```

---

## 23.7 Memory

학습된 정보.

저장 위치:

```text
memory/
channels/{channel_id}/memory.yaml
templates/.../memory.yaml
projects/.../reports/learning_report.json
```

종류:

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
```

---

# 24. Command and Data Separation

ADOS는 명령과 데이터를 구분한다.

Command는 작업 요청이다.

Data는 저장된 결과이다.

예시:

```text
CreateChannelCommand
→ channels/{channel_id}/ 생성

CreateProjectCommand
→ projects/{project_id}/ 생성

RunStageCommand
→ 특정 Stage 실행

QualityReviewCommand
→ reports/quality_report.json 생성
```

Command는 실행 후 반드시 결과 파일 또는 로그를 남긴다.

---

# 25. Event and Log Architecture

중요한 사건은 Event로 기록한다.

Event 종류:

```text
CHANNEL_CREATED
PROJECT_CREATED
STAGE_STARTED
STAGE_COMPLETED
STAGE_FAILED
QUALITY_PASSED
QUALITY_FAILED
AUTO_FIX_REQUESTED
AUTO_FIX_COMPLETED
PACKAGE_CREATED
PROJECT_PUBLISHED
LEARNING_COMPLETED
TEMPLATE_IMPROVEMENT_PROPOSED
```

로그 위치:

```text
projects/{channel_id}/{year}/{month}/{project_id}/logs/
channels/{channel_id}/logs/
memory/company_events.jsonl
```

로그는 나중에 Learning과 Debugging에 사용된다.

---

# 26. Snapshot Architecture

Project는 중요한 시점마다 Snapshot을 만든다.

Snapshot 시점:

```text
INITIALIZED
STORY_COMPLETE
TIMELINE_COMPLETE
VISUAL_COMPLETE
VOICE_COMPLETE
QUALITY_COMPLETE
PACKAGE_COMPLETE
```

Snapshot 목적:

```text
재현성 확보
실패 복구
변경 비교
Learning 분석
```

저장 위치:

```text
projects/{channel_id}/{year}/{month}/{project_id}/snapshots/
```

---

# 27. State Architecture

ADOS는 상태를 명확히 관리해야 한다.

## 27.1 Channel Status

```text
DRAFT
INITIALIZING
ACTIVE
PAUSED
ARCHIVED
ERROR
```

## 27.2 Project Status

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

## 27.3 Message Status

```text
OPEN
ACCEPTED
IN_PROGRESS
BLOCKED
COMPLETED
REJECTED
ESCALATED
CLOSED
```

상태 전환은 반드시 검증되어야 한다.

---

# 28. Workflow Orchestration Architecture

Workflow Orchestrator는 ADOS의 실행 관리자이다.

책임:

```text
Project 상태 확인
다음 Stage 결정
Stage 실행 요청
필수 Input 확인
필수 Output 확인
Quality Gate 확인
실패 감지
Retry 결정
Auto Fix 요청
Escalation 요청
상태 전환 기록
```

Workflow Orchestrator가 없으면 Engine들은 따로 노는 구조가 된다.

따라서 모든 Stage 실행은 Workflow Orchestrator를 통해 이루어져야 한다.

---

# 29. Engine Architecture

모든 Engine은 공통 구조를 따른다.

```text
Input
↓
Context Load
↓
Validation
↓
Execution
↓
Self Review
↓
Output Write
↓
Handoff
↓
Log
```

Engine 공통 인터페이스 방향:

```python
class Engine:
    def load_context(self, request):
        pass

    def validate_input(self, context):
        pass

    def run(self, context):
        pass

    def self_review(self, result):
        pass

    def write_output(self, result):
        pass

    def handoff(self, result):
        pass
```

실제 구현에서 반드시 위 형태를 그대로 강제할 필요는 없지만, 개념 구조는 지켜야 한다.

---

# 30. Provider Architecture

Provider는 Interface와 Adapter로 분리한다.

구조:

```text
Engine
↓
Provider Interface
↓
Provider Adapter
↓
External Provider
```

예시:

```text
Visual Engine
↓
VisualProviderInterface
↓
MidjourneyAdapter
```

```text
Motion Engine
↓
MotionProviderInterface
↓
MidjourneyVideoAdapter
```

```text
Voice Engine
↓
VoiceProviderInterface
↓
TypecastAdapter
```

금지:

```text
Visual Engine에서 Midjourney 직접 호출
Voice Engine에서 Typecast 직접 호출
```

허용:

```text
Visual Engine → VisualProviderInterface → MidjourneyAdapter
Voice Engine → VoiceProviderInterface → TypecastAdapter
```

---

# 31. Memory Architecture

Memory는 작업 전후에 사용된다.

```text
Before Work:
Memory Load

After Work:
Memory Update
```

Memory 종류:

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
```

Memory 사용 예:

```text
Story Engine
→ 이전에 성공한 Hook 패턴 참고

Visual Engine
→ 성공한 이미지 스타일 참고

Voice Engine
→ 언어별 좋은 속도 참고

Growth Engine
→ CTR 높은 제목 패턴 참고

Quality Engine
→ 반복 실패 패턴 참고
```

---

# 32. Quality Architecture

Quality Engine은 모든 핵심 결과물을 검사한다.

검사 대상:

```text
Topic
Research
Knowledge
Story
Direction
Timeline
Visual
Motion
Voice
Subtitle
Editing
Package
Brand Consistency
Factuality
```

품질 기준:

```text
95~100: 통과
90~94: 사람 확인 권장
80~89: 자동 수정
70~79: 부분 재생성
70 미만: 실패
```

Hard Fail:

```text
명확한 Hook 없음
사실 오류
Timeline 깨짐
필수 파일 없음
음성 생성 실패
자막 싱크 불량
이미지 스타일 불일치
저작권 위험 요소
채널 브랜드 불일치
```

---

# 33. Auto Fix Architecture

Auto Fix는 문제 위치를 좁혀서 수정한다.

기본 원칙:

```text
전체 재생성 금지
부분 수정 우선
원인 분석 필수
재검사 필수
3회 반복 시 Escalation
```

예시:

```text
Scene 7 이미지 문제
→ Scene 7 Prompt 수정
→ Scene 7 Image 재생성
→ Visual Review
→ Quality Recheck
```

---

# 34. Brand Architecture

Brand는 Channel 정체성을 유지한다.

Brand는 다음 단계에 적용된다.

```text
Topic Selection
Story Writing
Direction Planning
Visual Prompt Generation
Voice Style
Subtitle Style
Thumbnail Style
SEO Metadata
Quality Review
```

Brand 위반은 Quality Engine에서 감지되어야 한다.

---

# 35. Language Architecture

하나의 Project는 여러 언어를 지원할 수 있다.

공유되는 것:

```text
Story Structure
Scene Plan
Timeline
Images
Motion Clips
Thumbnail Base
```

언어별로 분리되는 것:

```text
Voice
Subtitle
Title
Description
Tags
SEO
Pinned Comment
```

기본 언어:

```text
ko
en
```

언어별 결과는 다음 위치에 저장한다.

```text
projects/{project_id}/languages/ko/
projects/{project_id}/languages/en/
```

---

# 36. Security and Secrets Architecture

Provider API Key나 로그인 정보는 코드에 직접 저장하지 않는다.

금지:

```text
API Key를 Python 파일에 직접 작성
API Key를 Markdown 문서에 직접 작성
API Key를 Git에 커밋
```

허용 방향:

```text
.env
local config
environment variables
secret manager
```

v1.0에서는 최소한 `.env` 기반 구조를 사용한다.

---

# 37. Configuration Architecture

설정은 다음 범위로 나뉜다.

```text
Global Config
Template Config
Channel Config
Project Config
Provider Config
Runtime Config
```

우선순위:

```text
Global Default
↓
Template Config
↓
Channel Config
↓
Project Override
↓
Runtime Option
```

단, Locked Field는 Override할 수 없다.

---

# 38. Validation Architecture

ADOS는 모든 중요한 단계에서 Validation을 수행한다.

검증 대상:

```text
Template Validation
Channel Validation
Project Validation
Timeline Validation
Provider Request Validation
Quality Validation
Package Validation
```

검증 실패 시 다음 단계로 진행하지 않는다.

---

# 39. Error Architecture

모든 Error는 구조화되어야 한다.

기본 Error 구조:

```json
{
  "error_type": "",
  "message": "",
  "location": "",
  "project_id": "",
  "channel_id": "",
  "stage": "",
  "cause": "",
  "suggested_fix": "",
  "severity": "LOW | MEDIUM | HIGH | CRITICAL",
  "created_at": ""
}
```

CRITICAL Error는 Escalation된다.

---

# 40. Testing Architecture

v1.0에서 우선 테스트해야 하는 대상:

```text
Template Loader
Template Resolver
Template Validator
Channel Factory
Channel Validator
Project Factory
Project State Manager
Workflow Orchestrator
Timeline Validator
Provider Interface
Quality Gate
Memory Loader
```

테스트 원칙:

```text
문서에 정의된 구조와 코드가 일치하는지 검증한다.
상태 전환이 올바른지 검증한다.
필수 파일 누락을 감지하는지 검증한다.
Provider 직접 호출을 방지하는지 검증한다.
Quality Gate가 작동하는지 검증한다.
```

---

# 41. Repository Architecture

기본 저장소 구조:

```text
ados/
├── README.md
├── docs/
├── templates/
├── channels/
├── projects/
├── engines/
├── providers/
├── employees/
├── workflows/
├── memory/
├── config/
├── prompts/
├── scripts/
├── tests/
└── outputs/
```

---

# 42. Code Module Direction

구현 방향:

```text
engines/
  template/
  channel/
  brand/
  portfolio/
  project/
  memory/
  provider/
  timeline/
  research/
  knowledge/
  story/
  direction/
  visual/
  motion/
  voice/
  subtitle/
  editing/
  quality/
  growth/
  publishing/
  analytics/
  learning/
  evolution/

providers/
  interfaces/
  adapters/

employees/
  base/
  departments/

workflows/
  orchestrator/
  stages/

memory/
  company/
  templates/
  channels/
  projects/
```

---

# 43. Implementation Boundary

각 Engine은 자신의 책임만 수행한다.

예시:

```text
Story Engine
→ Story 생성
→ Visual 생성 금지
→ Voice 생성 금지

Visual Engine
→ Visual Prompt와 이미지 자산 처리
→ 대본 수정 금지

Quality Engine
→ 문제 감지와 수정 요청
→ 직접 모든 파일을 임의 수정하지 않음

Workflow Orchestrator
→ 실행 순서와 상태 관리
→ 실제 Story 작성 금지
```

책임이 섞이면 시스템은 유지보수하기 어려워진다.

---

# 44. Document to Code Mapping

문서와 코드 매핑은 다음 방향을 따른다.

```text
08_TEMPLATE_SYSTEM.md
→ engines/template/

09_CHANNEL_ENGINE.md
→ engines/channel/

10_BRAND_SYSTEM.md
→ engines/brand/

11_PORTFOLIO_ENGINE.md
→ engines/portfolio/

12_PROJECT_ENGINE.md
→ engines/project/

13_MEMORY_ENGINE.md
→ engines/memory/

14_PROVIDER_ENGINE.md
→ engines/provider/

15_WORKFLOW_ORCHESTRATOR.md
→ workflows/orchestrator/

16_TIMELINE_ENGINE.md
→ engines/timeline/
```

Production Layer:

```text
17_RESEARCH_ENGINE.md
→ engines/research/

18_KNOWLEDGE_ENGINE.md
→ engines/knowledge/

19_STORY_ENGINE.md
→ engines/story/

20_DIRECTION_ENGINE.md
→ engines/direction/

21_VISUAL_ENGINE.md
→ engines/visual/

22_MOTION_ENGINE.md
→ engines/motion/

23_VOICE_ENGINE.md
→ engines/voice/

24_SUBTITLE_ENGINE.md
→ engines/subtitle/

25_EDITING_ENGINE.md
→ engines/editing/
```

Control Layer:

```text
26_QUALITY_ENGINE.md
→ engines/quality/

27_GROWTH_ENGINE.md
→ engines/growth/

28_PUBLISHING_ENGINE.md
→ engines/publishing/

29_ANALYTICS_ENGINE.md
→ engines/analytics/

30_LEARNING_ENGINE.md
→ engines/learning/

31_AI_EVOLUTION_ENGINE.md
→ engines/evolution/
```

---

# 45. v1.0 Minimal Architecture

v1.0에서 반드시 완성해야 하는 최소 구조:

```text
Template 로드
Template 검증
Channel 생성
Project 생성
Project 상태 관리
Timeline 생성
Provider Interface 정의
Quality Gate 정의
Upload Package 구조 생성
Learning Report 생성
```

v1.0에서 실제 외부 Provider 자동 호출은 필수는 아니다.

먼저 구조와 파일 흐름을 완성한다.

---

# 46. v1.0 Non Goals

v1.0에서 하지 않는 것:

```text
외부 사용자용 SaaS
결제 시스템
웹 대시보드
다중 사용자 권한 관리
외부 Template Marketplace
댓글 자동 대응
커뮤니티 자동 운영
완전 무검토 자동 업로드
고급 클라우드 렌더링
```

---

# 47. Architecture Acceptance Criteria

이 Architecture가 구현되면 시스템은 다음을 만족해야 한다.

```text
Template에서 Channel을 생성할 수 있다.
Channel에서 Project를 생성할 수 있다.
Project는 명확한 상태를 가진다.
Workflow Orchestrator가 Stage를 실행할 수 있다.
각 Engine은 자신의 책임만 수행한다.
Timeline이 모든 Asset의 기준이 된다.
Provider는 Interface와 Adapter로 분리된다.
Quality Gate가 다음 단계 진행을 통제한다.
Memory는 작업 전후에 사용된다.
Learning은 Template 개선으로 연결된다.
모든 중요한 작업은 로그로 남는다.
```

---

# 48. Critical Architecture Rules

반드시 지켜야 할 규칙:

```text
1. ADOS는 단순 영상 자동화 도구가 아니다.

2. Template 없이 Channel을 생성하지 않는다.

3. Channel 없이 Project를 생성하지 않는다.

4. Project 없이 Production Engine을 실행하지 않는다.

5. Workflow Orchestrator 없이 Stage를 무단 실행하지 않는다.

6. Timeline 없이 Visual, Motion, Voice, Subtitle을 최종 연결하지 않는다.

7. Provider를 Engine에서 직접 호출하지 않는다.

8. Quality Gate를 우회하지 않는다.

9. 전체 재생성보다 부분 수정이 우선이다.

10. Learning 없는 반복 제작은 금지한다.

11. Template 변경은 버전 관리한다.

12. 중요한 결정은 Decision Record로 남긴다.

13. 중요한 오류는 Error Log로 남긴다.

14. MASTER_PLAN과 충돌하는 구현은 허용하지 않는다.
```

---

# 49. Final Principle

ADOS의 아키텍처는 영상 제작 프로그램의 구조가 아니다.

ADOS의 아키텍처는 AI 콘텐츠 회사를 운영하는 구조이다.

Template은 Channel을 만들고,

Channel은 Project를 만들고,

Project는 Timeline을 만들고,

Timeline은 Asset을 만들고,

Asset은 Video를 만들고,

Video는 Data를 만들고,

Data는 Learning을 만들고,

Learning은 Template을 성장시킨다.

이 순환 구조가 CHUNG COMPANY의 핵심 경쟁력이다.
