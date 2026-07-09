# MASTER_PLAN.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Priority: Constitution  

---

# 1. Purpose

이 문서는 CHUNG COMPANY와 ADOS의 최상위 설계 문서이다.

이 문서는 프로젝트의 헌법이다.

모든 문서, 코드, 엔진, AI Employee, Template, Channel, Project는 이 문서를 기준으로 설계되고 구현되어야 한다.

이 문서보다 하위 문서나 코드가 우선할 수 없다.

우선순위는 다음과 같다.

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

---

# 2. Company Definition

CHUNG COMPANY는 AI가 운영하는 유튜브 콘텐츠 제작 회사이다.

CHUNG COMPANY는 단순한 영상 자동화 도구를 만드는 회사가 아니다.

CHUNG COMPANY는 여러 AI Employee가 협업하여 여러 유튜브 채널을 기획, 제작, 운영, 성장시키는 AI 콘텐츠 회사이다.

---

# 3. System Definition

ADOS는 AI Digital Operating System의 약자이다.

ADOS는 CHUNG COMPANY를 운영하기 위한 AI 기반 디지털 운영체제이다.

ADOS는 다음 작업을 수행한다.

- 채널 생성
- 채널 설정
- 브랜드 설계
- 주제 추천
- 리서치
- 지식 정리
- 대본 작성
- 장면 연출
- Timeline 설계
- 이미지 프롬프트 생성
- 영상 프롬프트 생성
- 음성 생성 준비
- 자막 생성
- 편집 패키지 구성
- 품질 검사
- 자동 수정
- 업로드 패키지 생성
- 성과 분석
- 학습
- Template 개선

ADOS는 영상 하나를 만드는 프로그램이 아니다.

ADOS는 채널을 운영하는 시스템이다.

---

# 4. Final Goal

CHUNG COMPANY의 최종 사업 목표는 수익이다.

하지만 수익은 직접 조작할 수 있는 값이 아니다.

수익은 다음 요소들의 결과이다.

```text
좋은 주제
↓
높은 클릭률
↓
높은 시청 지속 시간
↓
높은 추천 노출
↓
구독자 증가
↓
조회수 증가
↓
수익 증가
```

따라서 ADOS는 수익을 직접 만드는 것이 아니라, 수익을 만드는 선행 지표를 개선한다.

---

# 5. North Star Metric

최상위 사업 지표:

```text
Monthly Net Revenue
```

핵심 선행 지표:

```text
CTR
Watch Time
Retention Rate
Subscriber Conversion
Upload Consistency
Quality Score
Revenue Potential
Production Cost
```

ADOS는 모든 Project에서 다음 질문에 답해야 한다.

```text
이 영상은 채널 성장에 도움이 되는가?

시청자가 끝까지 볼 이유가 있는가?

클릭하고 싶은 제목과 썸네일이 있는가?

구독자가 늘 가능성이 있는가?

수익 가능성이 있는가?

품질 점수 95점 이상인가?
```

---

# 6. Core Philosophy

## 6.1 Not Video Automation

ADOS는 유튜브 영상 자동 생성기가 아니다.

ADOS는 AI 콘텐츠 회사 운영체제이다.

나쁜 정의:

```text
AI로 유튜브 영상을 자동으로 만든다.
```

올바른 정의:

```text
AI Employee들이 Template 기반으로 Channel을 만들고,
Project를 실행하며,
영상을 제작하고,
품질을 검사하고,
성과를 학습하여,
채널을 성장시키는 운영체제이다.
```

---

## 6.2 Channel First

시스템의 시작은 영상이 아니다.

시스템의 시작은 Channel이다.

그리고 Channel은 Template에서 생성된다.

```text
Template
↓
Channel
↓
Project
↓
Timeline
↓
Assets
↓
Video
↓
Learning
```

---

## 6.3 Template is Core Asset

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
Template Improvement
```

---

## 6.4 AI Employee, Not AI Agent

CHUNG COMPANY는 AI Agent를 만들지 않는다.

CHUNG COMPANY는 AI Employee를 만든다.

Agent는 명령을 수행한다.

Employee는 책임을 가진다.

모든 AI Employee는 다음을 가져야 한다.

- 역할
- 책임
- 입력
- 출력
- KPI
- 실패 조건
- 보고 대상
- 승인 권한
- 협업 규칙
- 사고 기준

---

## 6.5 Quality Before Automation

자동화보다 품질이 먼저다.

초기에는 사람이 최종 검토한다.

품질이 안정되면 자동화 수준을 높인다.

완전 자동화 조건:

```text
연속 Project 품질 점수 95점 이상
Critical Error 0개
Package 누락 0개
사용자 수정 개입 감소
채널 톤 안정화
```

---

## 6.6 Timeline First

최종 영상 파일보다 중요한 것은 Timeline이다.

Timeline은 영상의 설계도이다.

Timeline은 다음을 연결한다.

- Scene
- Narration
- Image
- Motion
- Subtitle
- Audio
- Transition
- Quality Check

ADOS의 제작 중심은 `final_video.mp4`가 아니라 `timeline.json`이다.

---

## 6.7 Provider Independent

ADOS는 특정 AI 서비스에 종속되지 않는다.

현재 기본 Provider는 다음과 같다.

```text
Visual Provider: Midjourney
Motion Provider: Midjourney Video
Voice Provider: Typecast
Subtitle Provider: Internal
Editing Provider: Internal
```

하지만 엔진 구조는 Provider가 변경되어도 유지되어야 한다.

---

## 6.8 One Project, Multiple Languages

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

언어별로 달라지는 것:

```text
Voice
Subtitle
Title
Description
Tags
SEO
Pinned Comment
```

한국어와 영어 버전은 같은 영상을 기반으로 하지만, 언어 레이어는 분리한다.

---

# 7. User Role

사용자는 CEO이다.

사용자가 결정하는 것:

- 어떤 채널을 만들 것인가
- 어떤 Template을 승인할 것인가
- 어떤 큰 사업 방향으로 갈 것인가
- 초기 결과물을 승인할 것인가
- 완전 자동화로 전환할 것인가

사용자가 반복적으로 하지 않는 것:

- 매번 대본 작성
- 매번 프롬프트 작성
- 매번 이미지 검토
- 매번 음성 생성
- 매번 자막 제작
- 매번 SEO 작성
- 매번 품질 검사
- 매번 수정 지시

최종 목표:

```text
사용자는 무엇을 만들지 결정한다.
AI는 어떻게 만들지 수행한다.
```

---

# 8. AI Role

AI Employee들은 CHUNG COMPANY의 직원이다.

AI Employee들은 다음을 수행한다.

- 분석
- 기획
- 제작
- 검토
- 수정
- 보고
- 학습

AI Employee는 혼자 일하지 않는다.

AI Employee는 서로 요청하고, 검토하고, 반박하고, 수정 요청하고, 승인한다.

---

# 9. System Flow

ADOS의 전체 흐름은 다음과 같다.

```text
Company
↓
Template System
↓
Channel Engine
↓
Brand System
↓
Portfolio Engine
↓
Project Engine
↓
Memory Engine
↓
Provider Engine
↓
Workflow Orchestrator
↓
Timeline Engine
↓
Production Engines
↓
Quality Engine
↓
Growth Engine
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

# 10. Core Operating Flow

실제 영상 제작 흐름은 다음과 같다.

```text
Template 선택
↓
Channel 생성
↓
Brand 설정
↓
Topic 입력 또는 AI 추천
↓
Project 생성
↓
Research
↓
Knowledge
↓
Story
↓
Direction
↓
Timeline
↓
Visual
↓
Motion
↓
Voice
↓
Subtitle
↓
Editing
↓
Quality Review
↓
Auto Fix
↓
Package
↓
Ready
↓
Publish
↓
Analytics
↓
Learning
↓
Template Improvement
```

---

# 11. Core Units

## 11.1 Company

CHUNG COMPANY 전체를 의미한다.

관리 대상:

- 전체 목표
- 전체 수익
- 전체 채널
- 전체 Template
- 전체 AI Employee
- 전체 Portfolio

---

## 11.2 Template

채널을 만들기 위한 DNA이다.

포함 요소:

- Brand
- Story Rules
- Visual Rules
- Voice Rules
- Subtitle Rules
- Quality Rules
- Growth Rules
- Employee Rules
- Communication Rules
- Thinking Rules
- Memory Rules

---

## 11.3 Channel

실제로 운영되는 유튜브 채널 단위이다.

Channel은 Template에서 생성된다.

Channel은 고유한 브랜드, 메모리, 성장 전략, 프로젝트 목록을 가진다.

---

## 11.4 Portfolio

여러 Channel과 여러 Project를 동시에 관리하는 운영 단위이다.

Portfolio는 다음을 관리한다.

- 채널별 프로젝트 수
- 업로드 일정
- 우선순위
- 제작 리소스
- 병목
- 성과 비교

---

## 11.5 Project

영상 1개를 제작하기 위한 작업 단위이다.

Project는 다음을 포함한다.

- Topic
- Research
- Knowledge
- Story
- Direction
- Timeline
- Assets
- Language Files
- Quality Reports
- Package
- Learning Report

---

## 11.6 Timeline

영상 제작의 핵심 설계도이다.

Timeline은 모든 Scene과 Asset을 연결한다.

---

## 11.7 Asset

Project에서 생성되는 모든 제작 재료이다.

예시:

- 이미지
- Motion 영상
- 음성
- 자막
- 썸네일
- 편집 파일
- 최종 영상

---

## 11.8 Memory

CHUNG COMPANY가 학습한 기록이다.

Memory 종류:

```text
Company Memory
Template Memory
Channel Memory
Project Memory
Success Memory
Failure Memory
Provider Memory
Quality Memory
Growth Memory
```

---

# 12. Quality Policy

품질 기준은 다음과 같다.

```text
95~100: 통과
90~94: 사람 확인 권장
80~89: 자동 수정
70~79: 부분 재생성
70 미만: 실패
```

Hard Fail 조건:

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

품질 점수 95점 미만 Project는 자동 통과할 수 없다.

---

# 13. Auto Fix Policy

문제가 발생하면 전체를 다시 만들지 않는다.

항상 부분 수정이 우선이다.

```text
Issue Detection
↓
Root Cause Analysis
↓
Targeted Fix
↓
Partial Regeneration
↓
Recheck
↓
Pass or Escalate
```

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

전체 재생성은 COO 승인 없이는 수행하지 않는다.

---

# 14. Automation Modes

## 14.1 Human Review Mode

초기 기본 모드이다.

AI가 제작하고 사용자가 최종 확인한다.

## 14.2 Assisted Auto Mode

AI가 제작, 검사, 수정까지 수행한다.

사용자는 최종 업로드 전만 확인한다.

## 14.3 Full Auto Mode

AI가 제작, 검사, 수정, 패키징, 업로드 준비까지 자동 수행한다.

Full Auto 전환 조건은 품질 안정성이 확인된 이후에만 가능하다.

---

# 15. Provider Strategy

ADOS는 Provider Adapter 구조를 사용한다.

각 엔진은 Provider를 직접 호출하지 않는다.

엔진은 Provider Interface를 호출한다.

```text
Visual Engine
↓
Visual Provider Interface
↓
Midjourney Adapter
```

```text
Voice Engine
↓
Voice Provider Interface
↓
Typecast Adapter
```

이 구조를 사용하는 이유:

- Provider 교체 가능
- 실패 처리 가능
- 비용 추적 가능
- 품질 비교 가능
- 확장 가능

---

# 16. AI Organization

CHUNG COMPANY의 AI 조직은 다음과 같다.

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

핵심 부서:

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

# 17. Communication Policy

AI Employee는 Communication Bus를 통해 협업한다.

모든 요청, 응답, 검토, 승인, 반려, 회의, Escalation은 로그로 남긴다.

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

중요한 결과물은 Handoff Package를 생성해야 한다.

---

# 18. Thinking Policy

AI Employee는 긴 내부 추론을 저장하지 않는다.

대신 Decision Record를 저장한다.

저장 대상:

- 결정 요약
- 사용한 근거
- 선택한 이유
- 고려한 선택지
- 위험 요소
- 다음 행동

사고 흐름:

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

---

# 19. Memory Policy

Memory는 작업 전에 불러오고, 작업 후 업데이트한다.

기본 원칙:

```text
Memory Before Work
Learning After Work
```

Memory는 다음 단계에서 사용된다.

- Topic 추천
- Story 구조 개선
- Visual 스타일 개선
- Voice 설정 개선
- Quality 검사 기준 개선
- Growth 전략 개선
- Template Evolution

---

# 20. Template Evolution

Template은 고정된 파일이 아니다.

Template은 성장한다.

흐름:

```text
Project Published
↓
Performance Data Collected
↓
Analytics
↓
Learning
↓
Pattern Detected
↓
Template Improvement Proposal
↓
Approval
↓
New Template Version
```

예시:

```text
future v1.0.0
↓
future v1.1.0
↓
future v2.0.0
```

Template 변경은 반드시 버전 관리되어야 한다.

---

# 21. Document Roadmap

최종 문서 구조는 다음과 같다.

```text
README.md
MASTER_PLAN.md

docs/
├── 00_AI_CONTEXT.md
├── 01_COMPANY.md
├── 02_DEVELOPMENT_RULES.md
├── 03_ARCHITECTURE.md
├── 04_AI_ORGANIZATION.md
├── 05_INTER_AI_COMMUNICATION.md
├── 06_AI_THINKING_FRAMEWORK.md
├── 07_PROJECT_SPEC.md
├── 08_TEMPLATE_SYSTEM.md
├── 09_CHANNEL_ENGINE.md
├── 10_BRAND_SYSTEM.md
├── 11_PORTFOLIO_ENGINE.md
├── 12_PROJECT_ENGINE.md
├── 13_MEMORY_ENGINE.md
├── 14_PROVIDER_ENGINE.md
├── 15_WORKFLOW_ORCHESTRATOR.md
├── 16_TIMELINE_ENGINE.md
├── 17_RESEARCH_ENGINE.md
├── 18_KNOWLEDGE_ENGINE.md
├── 19_STORY_ENGINE.md
├── 20_DIRECTION_ENGINE.md
├── 21_VISUAL_ENGINE.md
├── 22_MOTION_ENGINE.md
├── 23_VOICE_ENGINE.md
├── 24_SUBTITLE_ENGINE.md
├── 25_EDITING_ENGINE.md
├── 26_QUALITY_ENGINE.md
├── 27_GROWTH_ENGINE.md
├── 28_PUBLISHING_ENGINE.md
├── 29_ANALYTICS_ENGINE.md
├── 30_LEARNING_ENGINE.md
└── 31_AI_EVOLUTION_ENGINE.md
```

---

# 22. Layered Architecture

## 22.1 Foundation Layer

프로젝트의 철학과 기준을 정의한다.

```text
MASTER_PLAN
00_AI_CONTEXT
01_COMPANY
02_DEVELOPMENT_RULES
03_ARCHITECTURE
```

## 22.2 Organization Layer

AI Employee의 조직, 협업, 사고 기준을 정의한다.

```text
04_AI_ORGANIZATION
05_INTER_AI_COMMUNICATION
06_AI_THINKING_FRAMEWORK
```

## 22.3 Core Data Layer

Project와 Template의 구조를 정의한다.

```text
07_PROJECT_SPEC
08_TEMPLATE_SYSTEM
```

## 22.4 Business Layer

채널과 포트폴리오 운영을 정의한다.

```text
09_CHANNEL_ENGINE
10_BRAND_SYSTEM
11_PORTFOLIO_ENGINE
12_PROJECT_ENGINE
```

## 22.5 Core System Layer

메모리, Provider, Workflow, Timeline을 정의한다.

```text
13_MEMORY_ENGINE
14_PROVIDER_ENGINE
15_WORKFLOW_ORCHESTRATOR
16_TIMELINE_ENGINE
```

## 22.6 Production Layer

실제 콘텐츠 제작 엔진을 정의한다.

```text
17_RESEARCH_ENGINE
18_KNOWLEDGE_ENGINE
19_STORY_ENGINE
20_DIRECTION_ENGINE
21_VISUAL_ENGINE
22_MOTION_ENGINE
23_VOICE_ENGINE
24_SUBTITLE_ENGINE
25_EDITING_ENGINE
```

## 22.7 Control and Growth Layer

품질, 성장, 출판, 분석, 학습을 정의한다.

```text
26_QUALITY_ENGINE
27_GROWTH_ENGINE
28_PUBLISHING_ENGINE
29_ANALYTICS_ENGINE
30_LEARNING_ENGINE
```

## 22.8 Advanced Layer

AI가 Template과 운영 방식을 진화시키는 구조를 정의한다.

```text
31_AI_EVOLUTION_ENGINE
```

---

# 23. Development Principles

개발은 다음 원칙을 따른다.

## 23.1 Docs Before Code

중요 기능은 문서를 먼저 작성한 후 구현한다.

## 23.2 Schema First

데이터 구조를 먼저 정의한 후 엔진을 구현한다.

## 23.3 Timeline First

영상 제작 관련 기능은 Timeline 기준으로 구현한다.

## 23.4 Template First

Channel은 Template에서 생성되어야 한다.

## 23.5 Provider Independent

엔진은 특정 Provider에 직접 종속되지 않는다.

## 23.6 Partial Regeneration First

실패 시 전체 재생성보다 부분 수정이 우선이다.

## 23.7 Log Everything

중요한 작업, 결정, 실패, 수정은 모두 기록한다.

## 23.8 Quality Gate Mandatory

품질 기준을 통과하지 못하면 다음 단계로 진행할 수 없다.

## 23.9 Human Review Initially

초기에는 사람 검토를 유지한다.

## 23.10 No Hidden Magic

Claude Code가 이해할 수 없는 암묵적 규칙을 만들지 않는다.

모든 규칙은 문서와 코드에 명시한다.

---

# 24. Repository Direction

기본 폴더 방향은 다음과 같다.

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

각 폴더의 목적:

```text
docs
설계 문서

templates
채널 생성용 Template

channels
실제 운영 채널 설정

projects
영상 제작 Project

engines
핵심 실행 엔진

providers
외부 AI 서비스 Adapter

employees
AI Employee 구현

workflows
제작 흐름 Orchestrator

memory
회사/채널/프로젝트 Memory

config
전역 설정

prompts
AI 프롬프트 템플릿

scripts
보조 실행 스크립트

tests
테스트 코드

outputs
생성 결과물
```

---

# 25. Versioning Policy

모든 핵심 문서는 Version을 가진다.

버전 형식:

```text
Major.Minor.Patch
```

예시:

```text
1.0.0
1.1.0
1.1.1
2.0.0
```

변경 기준:

```text
Patch
오타 수정, 작은 설명 보강

Minor
기능 추가, 구조 일부 개선

Major
철학, 아키텍처, 데이터 구조의 큰 변경
```

---

# 26. Change Policy

다음 변경은 반드시 MASTER_PLAN 또는 ARCHITECTURE에 반영해야 한다.

- 시스템 흐름 변경
- 문서 번호 변경
- 핵심 엔진 추가
- Template 구조 변경
- Project 구조 변경
- 품질 기준 변경
- 자동화 정책 변경
- Provider 전략 변경
- AI Employee 조직 변경

하위 문서만 수정하고 MASTER_PLAN을 갱신하지 않는 것은 금지한다.

---

# 27. Non Goals

v1.0에서 하지 않는 것:

- 외부 사용자용 SaaS
- 결제 시스템
- 웹 대시보드
- 다중 사용자 권한 관리
- 외부 Template Marketplace
- 자동 광고 영업
- 댓글 자동 대응
- 커뮤니티 자동 운영
- 완전 무검토 자동 업로드

v1.0은 내부 운영 시스템을 먼저 완성한다.

---

# 28. v1 Success Criteria

v1.0 성공 기준은 다음과 같다.

```text
1개 Template 생성 가능

1개 Channel 생성 가능

1개 Project 생성 가능

한국어/영어 버전 구조 생성 가능

Timeline 생성 가능

Midjourney 프롬프트 생성 가능

Typecast용 음성 스크립트 생성 가능

자막 파일 생성 가능

Quality Report 생성 가능

Auto Fix 요청 생성 가능

Upload Package 생성 가능

Learning Report 생성 가능
```

초기 목표:

```text
1개 채널
↓
1개 고품질 영상 Project
↓
한국어/영어 패키지
↓
품질 점수 95 이상
↓
사용자 최종 검토 가능
```

---

# 29. Long Term Vision

CHUNG COMPANY의 장기 목표는 다음과 같다.

```text
여러 Template 보유

여러 Channel 운영

여러 Project 동시 진행

AI Employee 협업 자동화

Template별 성과 학습

채널별 성장 전략 자동 개선

AI가 새로운 Template 제안

AI가 새로운 채널 기회 탐색

AI가 콘텐츠 회사를 운영
```

최종 형태:

```text
사용자
↓
큰 방향 결정
↓
ADOS
↓
Template 생성
↓
Channel 운영
↓
Project 제작
↓
성과 학습
↓
수익 성장
```

---

# 30. Critical Rules

다음 규칙은 반드시 지켜야 한다.

```text
1. ADOS는 단순 영상 자동화 도구가 아니다.

2. Template은 핵심 자산이다.

3. Channel은 Template에서 생성된다.

4. Project는 Channel 아래에서 생성된다.

5. Timeline은 영상 제작의 중심이다.

6. AI Employee는 책임과 KPI를 가진다.

7. 모든 중요한 작업은 로그로 남긴다.

8. 품질 점수 95 미만은 자동 통과할 수 없다.

9. 초기에는 Human Review가 필요하다.

10. Provider는 교체 가능해야 한다.

11. Memory는 작업 전에 불러오고 작업 후 갱신한다.

12. Learning은 Template 개선으로 이어져야 한다.

13. 전체 재생성보다 부분 수정이 우선이다.

14. 수익은 최종 목표지만 품질과 브랜드를 깨뜨리면 안 된다.

15. 모든 구현은 이 MASTER_PLAN을 기준으로 한다.
```

---

# 31. Final Principle

CHUNG COMPANY는 영상을 만드는 회사가 아니다.

CHUNG COMPANY는 AI Employee들이 채널을 만들고, 운영하고, 성장시키는 AI 콘텐츠 회사이다.

ADOS는 그 회사를 운영하는 AI Digital Operating System이다.

사용자는 무엇을 만들지 결정한다.

AI는 어떻게 만들지 수행한다.

Template은 채널을 만들고,

Channel은 Project를 만들고,

Project는 영상을 만들고,

영상은 데이터를 만들고,

데이터는 Learning을 만들고,

Learning은 Template을 성장시킨다.

이 순환 구조가 CHUNG COMPANY의 핵심 경쟁력이다.
