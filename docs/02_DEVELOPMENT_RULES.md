# 02_DEVELOPMENT_RULES.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Development Rules  

---

# 1. Purpose

이 문서는 CHUNG COMPANY / ADOS 프로젝트를 개발할 때 반드시 지켜야 하는 규칙을 정의한다.

Claude Code와 모든 AI 개발 도구는 이 문서를 기준으로 코드를 작성해야 한다.

이 문서의 목적은 다음과 같다.

- 개발 방향 고정
- 파일/폴더 구조 일관성 유지
- 문서와 코드의 불일치 방지
- 무분별한 기능 추가 방지
- Provider 종속 방지
- 품질 기준 유지
- 확장 가능한 구조 유지

---

# 2. Highest Priority Rule

모든 개발은 다음 문서를 우선순위대로 따른다.

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
상세 설계 문서
↓
실제 코드
```

코드가 문서와 충돌하면 문서를 우선한다.

하위 문서가 MASTER_PLAN과 충돌하면 MASTER_PLAN을 우선한다.

---

# 3. Development Philosophy

ADOS는 단순 자동화 스크립트가 아니다.

ADOS는 AI Employee들이 Template 기반으로 Channel을 만들고, Project를 실행하며, 품질 검사와 학습을 반복하는 AI 콘텐츠 회사 운영체제이다.

따라서 모든 개발은 다음 질문을 기준으로 판단한다.

```text
이 기능은 CHUNG COMPANY 운영에 필요한가?

이 기능은 Template, Channel, Project, Timeline, Quality, Learning 흐름과 연결되는가?

이 기능은 여러 채널 운영으로 확장 가능한가?

이 기능은 나중에 Provider가 바뀌어도 유지 가능한가?
```

---

# 4. Core Development Principles

## 4.1 Docs Before Code

중요 기능은 문서를 먼저 작성한 뒤 구현한다.

문서 없이 큰 구조를 만들지 않는다.

## 4.2 Schema First

데이터 구조를 먼저 정의한 뒤 엔진을 만든다.

## 4.3 Template First

Channel은 Template에서 생성되어야 한다.

Template 없이 Channel을 직접 만들지 않는다.

## 4.4 Channel First

Project는 반드시 Channel 아래에서 생성된다.

Channel 없는 Project는 만들지 않는다.

## 4.5 Timeline First

영상 제작의 중심은 final video가 아니라 Timeline이다.

모든 Asset은 Timeline을 기준으로 연결되어야 한다.

## 4.6 Provider Independent

엔진은 Midjourney, Typecast 같은 Provider를 직접 호출하지 않는다.

반드시 Interface와 Adapter를 사용한다.

## 4.7 Partial Regeneration First

문제가 발생하면 전체 재생성보다 부분 수정이 우선이다.

## 4.8 Quality Gate Mandatory

품질 기준을 통과하지 못하면 다음 단계로 이동할 수 없다.

## 4.9 Memory Before Work

AI Employee와 Engine은 작업 전 Memory를 확인해야 한다.

## 4.10 Learning After Work

Project 완료 후 Learning 결과는 Memory와 Template 개선으로 연결되어야 한다.

---

# 5. Repository Structure

기본 저장소 구조는 다음을 따른다.

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

# 6. Folder Responsibilities

## docs

설계 문서를 저장한다.

## templates

채널 생성용 Template을 저장한다.

## channels

실제 운영 채널 설정을 저장한다.

## projects

영상 제작 Project를 저장한다.

## engines

핵심 실행 엔진을 저장한다.

## providers

외부 AI 서비스 Adapter를 저장한다.

## employees

AI Employee 구현을 저장한다.

## workflows

Workflow Orchestrator와 실행 흐름을 저장한다.

## memory

Company, Template, Channel, Project Memory를 저장한다.

## config

전역 설정을 저장한다.

## prompts

AI 프롬프트 템플릿을 저장한다.

## scripts

보조 실행 스크립트를 저장한다.

## tests

테스트 코드를 저장한다.

## outputs

생성 결과물을 저장한다.

---

# 7. Naming Rules

## 7.1 Markdown Documents

문서 파일명은 대문자와 언더스코어를 사용한다.

예시:

```text
09_CHANNEL_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
```

## 7.2 Python Files

Python 파일명은 snake_case를 사용한다.

예시:

```text
channel_engine.py
workflow_orchestrator.py
template_validator.py
```

## 7.3 Python Classes

Python 클래스명은 PascalCase를 사용한다.

예시:

```text
ChannelEngine
WorkflowOrchestrator
TemplateValidator
ProjectFactory
```

## 7.4 JSON/YAML Keys

JSON/YAML key는 snake_case를 사용한다.

예시:

```yaml
channel_id: future
template_id: future
quality_score: 95
```

---

# 8. Code Style Rules

코드는 다음 원칙을 따른다.

- 작고 명확한 함수
- 명확한 타입
- 명확한 에러
- 명확한 입력과 출력
- 과도한 추상화 금지
- 문서와 일치하는 이름 사용
- 숨겨진 동작 금지
- 추측 기반 구현 금지

---

# 9. File Safety Rules

Claude Code는 다음을 지켜야 한다.

```text
기존 사용자 파일을 임의로 삭제하지 않는다.
기존 문서를 임의로 덮어쓰지 않는다.
요청받은 파일만 수정한다.
요청받지 않은 폴더 구조를 대규모로 바꾸지 않는다.
큰 구조 변경 전에는 관련 문서를 먼저 수정한다.
```

---

# 10. State Management Rules

Project 상태 변경은 반드시 검증 후 수행한다.

잘못된 상태 전환은 허용하지 않는다.

예시:

```text
NEW → INITIALIZED
INITIALIZED → RESEARCH
RESEARCH → KNOWLEDGE
KNOWLEDGE → STORY
```

허용되지 않는 예시:

```text
NEW → VISUAL
STORY → PACKAGE
VOICE → COMPLETE
```

---

# 11. Logging Rules

중요한 작업은 반드시 로그로 남긴다.

로그 대상:

- Project 생성
- 상태 변경
- AI Employee 요청
- AI Employee 응답
- 품질 검사
- Auto Fix
- 재시도
- 실패
- 승인
- Template 변경
- Channel 변경
- Provider 오류

---

# 12. Error Handling Rules

에러는 조용히 무시하지 않는다.

모든 에러는 다음 정보를 포함해야 한다.

```text
error_type
message
location
project_id
stage
cause
suggested_fix
created_at
```

---

# 13. Provider Rules

Provider는 Adapter를 통해서만 호출한다.

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

# 14. Quality Rules

품질 기준은 다음과 같다.

```text
95~100: 통과
90~94: 사람 확인 권장
80~89: 자동 수정
70~79: 부분 재생성
70 미만: 실패
```

품질 점수 95점 미만 Project는 자동 통과할 수 없다.

---

# 15. Test Rules

핵심 시스템은 테스트가 필요하다.

우선 테스트 대상:

```text
Template Loader
Template Validator
Channel Factory
Project Factory
Project State Manager
Timeline Validator
Provider Adapter
Quality Gate
Workflow Orchestrator
```

---

# 16. Git Rules

중요 문서나 핵심 코드 변경 후에는 커밋 단위를 작게 유지한다.

권장 커밋 메시지 예시:

```text
docs: update development rules
docs: add architecture specification
feat: add template validator
test: add project state tests
fix: prevent invalid project transition
```

커밋은 기능 단위로 나눈다.

여러 개의 큰 변경을 하나의 커밋에 몰아넣지 않는다.

---

# 17. Document Update Rules

다음 변경이 있으면 관련 문서도 함께 수정해야 한다.

```text
폴더 구조 변경
엔진 이름 변경
데이터 Schema 변경
Project 상태 변경
Template 구조 변경
Channel 구조 변경
Provider 전략 변경
Quality 기준 변경
AI Employee 책임 변경
Workflow 순서 변경
```

문서를 업데이트하지 않고 코드만 바꾸는 것은 금지한다.

---

# 18. Non Goals for v1.0

v1.0에서는 다음을 구현하지 않는다.

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

v1.0은 내부 운영 가능한 ADOS 기반을 먼저 만든다.

---

# 19. v1.0 Development Priority

v1.0 개발 우선순위는 다음과 같다.

```text
1. 문서 구조 확정
2. Template 구조 확정
3. Channel 생성 구조 확정
4. Project 생성 구조 확정
5. Timeline 구조 확정
6. Provider Interface 구조 확정
7. Quality Gate 구조 확정
8. Workflow Orchestrator 구조 확정
9. 1개 Template 기반 1개 Channel 생성
10. 1개 Project 생성과 Package 구조 완성
```

---

# 20. Final Principle

좋은 코드는 많은 기능을 가진 코드가 아니다.

좋은 코드는 회사의 운영 구조를 정확히 반영하는 코드이다.

ADOS의 코드는 CHUNG COMPANY의 운영 방식과 일치해야 한다.
