# 00_AI_CONTEXT.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: AI Context Guide  

---

# 1. Purpose

이 문서는 Claude Code와 모든 AI 개발 도구가 CHUNG COMPANY / ADOS 프로젝트를 올바르게 이해하기 위한 AI Context 문서이다.

이 문서는 구현 명세서가 아니다.

이 문서는 AI가 프로젝트의 목적, 철학, 구조, 우선순위, 금지사항을 이해하기 위한 기준 문서이다.

Claude Code는 코드를 작성하기 전에 반드시 이 문서를 기준으로 프로젝트를 이해해야 한다.

---

# 2. Project Identity

이 프로젝트는 단순한 유튜브 자동화 프로그램이 아니다.

이 프로젝트는 AI Employee들이 여러 유튜브 채널을 기획, 제작, 운영, 성장시키는 AI 콘텐츠 회사 운영체제이다.

회사 이름:

```text
CHUNG COMPANY
```

시스템 이름:

```text
ADOS
```

ADOS 의미:

```text
AI Digital Operating System
```

핵심 정의:

```text
CHUNG COMPANY는 AI 콘텐츠 제작 회사이다.

ADOS는 CHUNG COMPANY를 운영하는 AI Digital Operating System이다.
```

---

# 3. What ADOS Is

ADOS는 다음을 수행한다.

- Template 생성
- Channel 생성
- Brand 설정
- Topic 추천
- Project 생성
- Research
- Knowledge 정리
- Story 제작
- Direction 설계
- Timeline 생성
- Visual Prompt 생성
- Motion Prompt 생성
- Voice Script 생성
- Subtitle 생성
- Editing Plan 생성
- Quality Review
- Auto Fix
- Publishing Package 생성
- Analytics
- Learning
- Template Evolution

ADOS는 영상 하나를 만드는 도구가 아니다.

ADOS는 여러 채널을 운영하는 시스템이다.

---

# 4. What ADOS Is Not

ADOS는 다음이 아니다.

```text
단순 유튜브 자동 업로드 봇
단순 대본 생성기
단순 이미지 프롬프트 생성기
단순 영상 편집 자동화 스크립트
단순 ChatGPT 프롬프트 모음
외부 사용자용 SaaS
웹 대시보드 우선 프로젝트
```

v1.0에서는 내부 운영 시스템을 먼저 만든다.

---

# 5. Highest Priority Document

모든 판단의 최상위 기준은 다음 문서이다.

```text
docs/MASTER_PLAN.md
```

문서 우선순위는 다음과 같다.

```text
MASTER_PLAN.md
↓
00_AI_CONTEXT.md
↓
01_COMPANY.md
↓
02_DEVELOPMENT_RULES.md
↓
03_ARCHITECTURE.md
↓
04번 이후 상세 설계 문서
↓
실제 코드
```

하위 문서나 코드가 MASTER_PLAN과 충돌하면 MASTER_PLAN을 우선한다.

---

# 6. Core Philosophy

ADOS의 핵심 철학은 다음과 같다.

```text
Template First
Channel First
Timeline First
Quality First
Memory Before Work
Learning After Work
Provider Independent
Partial Regeneration First
Human Review Initially
```

---

# 7. Main Operating Flow

ADOS의 핵심 흐름은 다음과 같다.

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
Production Engines
↓
Quality
↓
Publishing
↓
Analytics
↓
Learning
↓
Template Improvement
```

모든 기능은 이 흐름 안에서 설계되어야 한다.

---

# 8. Core Asset

CHUNG COMPANY의 핵심 자산은 코드가 아니다.

핵심 자산은 Template이다.

Template은 채널을 만들고, 채널은 영상을 만들고, 영상은 데이터를 만들고, 데이터는 Template을 성장시킨다.

```text
Template
↓
Channel
↓
Video
↓
Data
↓
Learning
↓
Template Evolution
```

---

# 9. User Role

사용자는 CEO이다.

사용자는 다음을 결정한다.

- 어떤 채널을 만들 것인가
- 어떤 Template을 승인할 것인가
- 어떤 큰 사업 방향으로 갈 것인가
- 초기 결과물을 승인할 것인가
- 완전 자동화로 전환할 것인가

사용자는 반복 제작 실무를 하지 않는다.

AI Employee가 반복 업무를 수행한다.

---

# 10. AI Employee Concept

이 프로젝트에서는 AI Agent라는 개념보다 AI Employee라는 개념을 사용한다.

Agent는 명령을 수행한다.

Employee는 책임을 가진다.

모든 AI Employee는 다음을 가져야 한다.

- Role
- Responsibility
- Input
- Output
- KPI
- Failure Conditions
- Reports To
- Approval Authority
- Communication Rules
- Thinking Rules

---

# 11. AI Organization Summary

기본 조직 구조는 다음과 같다.

```text
CEO / USER
↓
COO AI Employee
↓
Portfolio Manager Employee
↓
Template Manager Employee
↓
Channel Manager Employee
↓
Project Manager Employee
↓
Department Employees
↓
Specialist Employees
```

주요 부서:

```text
Research Department
Knowledge Department
Story Department
Direction Department
Timeline Department
Visual Department
Motion Department
Voice Department
Subtitle Department
Editing Department
Quality Department
Growth Department
Publishing Department
Analytics Department
Learning Department
Memory Department
```

---

# 12. Communication Principle

AI Employee는 혼자 일하지 않는다.

AI Employee는 서로 요청하고, 검토하고, 반박하고, 수정 요청하고, 승인한다.

모든 중요한 대화는 기록되어야 한다.

기본 흐름:

```text
Task Request
↓
Task Accepted
↓
Work
↓
Self Review
↓
Task Result
↓
Peer Review
↓
Quality Review
↓
Approval
↓
Handoff
```

---

# 13. Thinking Principle

AI Employee는 작업 전에 Context를 불러와야 한다.

기본 사고 흐름:

```text
Context Load
↓
Goal Understanding
↓
Constraint Check
↓
Evidence Check
↓
Option Building
↓
Decision
↓
Execution
↓
Self Review
↓
Handoff
↓
Learning
```

긴 내부 추론을 저장하지 않는다.

대신 Decision Record를 저장한다.

저장 대상:

- 결정 요약
- 사용한 근거
- 선택한 이유
- 고려한 선택지
- 위험 요소
- 다음 행동

---

# 14. Quality Principle

품질 기준은 다음과 같다.

```text
95~100: 통과
90~94: 사람 확인 권장
80~89: 자동 수정
70~79: 부분 재생성
70 미만: 실패
```

품질 점수 95점 미만 Project는 자동 통과할 수 없다.

초기 운영 단계에서는 Human Review가 필요하다.

---

# 15. Auto Fix Principle

문제가 발생하면 전체를 다시 만들지 않는다.

부분 수정이 우선이다.

예시:

```text
Scene 7 이미지 문제
→ Scene 7 이미지만 재생성

영어 음성 문제
→ 영어 음성만 재생성

Hook 문제
→ Hook과 초반 Story만 수정

Timeline 싱크 문제
→ Timeline과 Subtitle만 수정
```

전체 재생성은 최후의 방법이다.

---

# 16. Provider Strategy

ADOS는 Provider Independent 구조를 따른다.

현재 기본 Provider:

```text
Visual Provider: Midjourney
Motion Provider: Midjourney Video
Voice Provider: Typecast
Subtitle Provider: Internal
Editing Provider: Internal
```

엔진은 Provider를 직접 호출하지 않는다.

엔진은 Provider Interface를 호출하고, 실제 Provider는 Adapter가 처리한다.

예시:

```text
Visual Engine
↓
Visual Provider Interface
↓
Midjourney Adapter
```

---

# 17. Language Strategy

하나의 Project는 여러 언어 버전을 만들 수 있다.

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

기본 지원 언어:

```text
ko
en
```

---

# 18. Important Data Units

## Template

채널을 만들기 위한 DNA.

## Channel

실제로 운영되는 유튜브 채널 단위.

## Portfolio

여러 Channel과 여러 Project를 동시에 관리하는 운영 단위.

## Project

영상 1개를 제작하기 위한 작업 단위.

## Timeline

영상 제작의 핵심 설계도.

## Asset

이미지, 영상, 음성, 자막, 썸네일 등 제작 재료.

## Memory

회사, 채널, 프로젝트가 학습한 기록.

---

# 19. Current Document Roadmap

문서 구조는 다음을 따른다.

```text
README.md
MASTER_PLAN.md

docs/00_AI_CONTEXT.md
docs/01_COMPANY.md
docs/02_DEVELOPMENT_RULES.md
docs/03_ARCHITECTURE.md

docs/04_AI_ORGANIZATION.md
docs/05_INTER_AI_COMMUNICATION.md
docs/06_AI_THINKING_FRAMEWORK.md

docs/07_PROJECT_SPEC.md
docs/08_TEMPLATE_SYSTEM.md

docs/09_CHANNEL_ENGINE.md
docs/10_BRAND_SYSTEM.md
docs/11_PORTFOLIO_ENGINE.md
docs/12_PROJECT_ENGINE.md

docs/13_MEMORY_ENGINE.md
docs/14_PROVIDER_ENGINE.md
docs/15_WORKFLOW_ORCHESTRATOR.md
docs/16_TIMELINE_ENGINE.md

docs/17_RESEARCH_ENGINE.md
docs/18_KNOWLEDGE_ENGINE.md
docs/19_STORY_ENGINE.md
docs/20_DIRECTION_ENGINE.md
docs/21_VISUAL_ENGINE.md
docs/22_MOTION_ENGINE.md
docs/23_VOICE_ENGINE.md
docs/24_SUBTITLE_ENGINE.md
docs/25_EDITING_ENGINE.md

docs/26_QUALITY_ENGINE.md
docs/27_GROWTH_ENGINE.md
docs/28_PUBLISHING_ENGINE.md
docs/29_ANALYTICS_ENGINE.md
docs/30_LEARNING_ENGINE.md

docs/31_AI_EVOLUTION_ENGINE.md
```

---

# 20. Expected Repository Direction

기본 저장소 구조는 다음과 같다.

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

# 21. Claude Code Working Rules

Claude Code는 다음 규칙을 따라야 한다.

## 21.1 Do Not Change Architecture Without Reason

이미 정의된 문서 구조와 시스템 흐름을 임의로 바꾸지 않는다.

구조 변경이 필요하면 먼저 관련 문서를 수정해야 한다.

## 21.2 Do Not Delete Existing User Work

사용자가 만든 파일을 임의로 삭제하지 않는다.

## 21.3 Follow Existing Naming

파일명, 폴더명, 클래스명은 문서에 정의된 이름을 따른다.

## 21.4 Write Small and Clear Code

처음부터 과도하게 복잡한 코드를 만들지 않는다.

문서 구조에 맞게 작고 명확하게 구현한다.

## 21.5 Prefer Interface and Adapter

외부 Provider는 직접 호출하지 않는다.

반드시 Interface와 Adapter 구조를 사용한다.

## 21.6 Validate Before Moving Forward

상태 전환, 파일 생성, 품질 통과는 검증 후 진행한다.

## 21.7 Log Important Decisions

중요한 작업, 실패, 수정, 승인, 상태 변경은 로그로 남긴다.

---

# 22. Naming Rules

문서 파일명은 대문자와 언더스코어를 사용한다.

예시:

```text
09_CHANNEL_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
```

Python 코드에서는 snake_case를 사용한다.

예시:

```text
channel_engine.py
workflow_orchestrator.py
```

Python 클래스는 PascalCase를 사용한다.

예시:

```text
ChannelEngine
WorkflowOrchestrator
ProjectFactory
TemplateValidator
```

---

# 23. Implementation Attitude

Claude Code는 이 프로젝트를 단순 자동화로 축소하면 안 된다.

모든 구현은 다음 질문을 기준으로 판단한다.

```text
이 기능은 CHUNG COMPANY라는 AI 콘텐츠 회사 운영에 필요한가?

이 기능은 Template, Channel, Project, Timeline, Quality, Learning 흐름과 연결되는가?

이 기능은 나중에 여러 채널 운영으로 확장 가능한가?
```

---

# 24. Non Goals for v1.0

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
```

v1.0의 목표는 내부 운영 가능한 ADOS 기반을 만드는 것이다.

---

# 25. Current v1.0 Goal

초기 목표는 다음과 같다.

```text
1개 Template 생성
↓
1개 Channel 생성
↓
1개 Project 생성
↓
한국어/영어 제작 구조 생성
↓
Timeline 생성
↓
Midjourney Prompt 생성
↓
Typecast Voice Script 생성
↓
Subtitle 생성
↓
Quality Report 생성
↓
Upload Package 생성
↓
Learning Report 생성
```

---

# 26. Critical Reminder

이 프로젝트에서 가장 중요한 문장은 다음이다.

```text
CHUNG COMPANY는 영상을 만드는 회사가 아니다.

CHUNG COMPANY는 AI Employee들이 채널을 만들고, 운영하고, 성장시키는 AI 콘텐츠 회사이다.

ADOS는 그 회사를 운영하는 AI Digital Operating System이다.
```

모든 코드와 문서는 이 정의를 벗어나면 안 된다.
