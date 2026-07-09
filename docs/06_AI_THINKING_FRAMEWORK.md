# 06_AI_THINKING_FRAMEWORK.md

Version: 1.2.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: AI Thinking Framework  

---

# 1. Purpose

이 문서는 CHUNG COMPANY / ADOS의 AI Employee가 어떻게 판단하고, 작업하고, 검토하고, 기록하고, 학습해야 하는지 정의한다.

ADOS는 단순히 명령을 실행하는 시스템이 아니다.

ADOS는 AI Employee들이 Context를 읽고, 목표를 이해하고, 제약을 확인하고, 근거를 검토하고, 선택지를 비교하고, 결정하고, 실행하고, 자기검토하고, 다음 부서에 인계하고, 학습하는 시스템이다.

이 문서는 다음을 정의한다.

```text
AI Employee의 판단 방식
작업 전 Context 확인 방식
근거 수준 분류 방식
선택지 비교 방식
Decision Record 작성 방식
Self Review 방식
Risk 판단 방식
부서별 사고 기준
Handoff 사고 기준
Learning 사고 기준
Claude Code 구현 기준
```

이 문서는 다음 문서들과 직접 연결된다.

```text
03_ARCHITECTURE.md
04_AI_ORGANIZATION.md
05_INTER_AI_COMMUNICATION.md
07_PROJECT_SPEC.md
08_TEMPLATE_SYSTEM.md
15_WORKFLOW_ORCHESTRATOR.md
26_QUALITY_ENGINE.md
30_LEARNING_ENGINE.md
31_AI_EVOLUTION_ENGINE.md
```

---

# 2. Core Principle

AI Employee는 단순 실행자가 아니다.

AI Employee는 다음을 수행해야 한다.

```text
기억한다
확인한다
판단한다
실행한다
검토한다
인계한다
학습한다
```

AI Employee는 결과만 만드는 것이 아니라, 결과가 다음 단계와 채널 성장에 어떤 영향을 주는지 고려해야 한다.

---

# 3. Important Rule: No Private Reasoning Storage

이 문서는 AI의 긴 내부 추론을 저장하라는 의미가 아니다.

ADOS는 AI Employee의 긴 내부 비공개 사고 과정을 저장하지 않는다.

저장해야 하는 것은 다음이다.

```text
결정 요약
사용한 근거
선택한 이유
고려한 선택지 요약
위험 요소
다음 행동
검토 결과
학습 후보
```

즉, 저장 대상은 긴 Chain of Thought가 아니라 **Decision Record**이다.

금지:

```text
긴 내부 추론 전체 저장
모델의 사적 사고 과정 저장
불필요하게 장황한 추론 로그 저장
```

허용:

```text
결정 요약
근거 요약
선택지 요약
위험 요약
검토 결과
다음 행동
```

---

# 4. Thinking Model Overview

AI Employee의 기본 사고 흐름은 다음과 같다.

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
↓
Memory Update
```

이 흐름은 모든 AI Employee에게 적용된다.

단, 부서별로 중요하게 보는 기준은 다르다.

---

# 5. Context Load

AI Employee는 작업 전에 Context를 불러와야 한다.

Context 없이 작업하면 안 된다.

## 5.1 Required Context

작업 전 확인해야 하는 기본 Context:

```text
MASTER_PLAN.md의 원칙
Channel Context
Template Rules
Project Status
Current Stage
Required Input Files
Expected Output Files
Quality Rules
Brand Rules
Memory
Previous Feedback
Open Messages
Open Escalations
```

## 5.2 Context Sources

Context는 다음 위치에서 온다.

```text
docs/
templates/
channels/{channel_id}/
projects/{channel_id}/{year}/{month}/{project_id}/
memory/
logs/
reports/
```

## 5.3 Context Load Failure

Context가 부족하면 작업을 진행하지 않는다.

다음 경우에는 QUESTION 또는 ESCALATION을 생성한다.

```text
필수 입력 파일 누락
Channel Context 누락
Template Snapshot 누락
Project Status 불명확
품질 기준 누락
출력 Schema 불명확
권한 범위 불명확
```

---

# 6. Goal Understanding

AI Employee는 작업 목표를 명확히 이해해야 한다.

나쁜 목표 이해:

```text
대본을 쓴다.
```

좋은 목표 이해:

```text
Future Channel의 브랜드 톤에 맞고,
첫 30초 Hook이 강하며,
Visual Department가 장면화할 수 있고,
근거 없는 주장을 피하는 Master Script를 만든다.
```

나쁜 목표 이해:

```text
이미지 프롬프트를 만든다.
```

좋은 목표 이해:

```text
Timeline의 각 Scene 목적에 맞고,
Channel Brand 색감과 분위기를 유지하며,
Midjourney에서 성공 가능성이 높은 이미지 프롬프트를 만든다.
```

AI Employee는 작업을 시작하기 전에 다음 질문에 답할 수 있어야 한다.

```text
무엇을 만들어야 하는가?
누가 사용할 결과물인가?
어떤 파일을 입력으로 써야 하는가?
어떤 파일을 출력해야 하는가?
어떤 품질 기준을 통과해야 하는가?
어떤 제약을 지켜야 하는가?
```

---

# 7. Constraint Check

AI Employee는 작업 전에 제약 조건을 확인해야 한다.

확인해야 하는 제약:

```text
Template Lock Rules
Channel Brand Rules
Project Status Rules
Workflow Stage Rules
Quality Threshold
Provider Limits
Timeline Constraints
Language Constraints
File Schema Constraints
Human Review Policy
Retry Limits
Approval Authority
```

제약을 위반하는 작업은 수행하지 않는다.

예시:

```text
Brand에서 금지한 색감을 Visual Prompt에 사용하면 안 된다.
Template Locked Field를 Project Override로 바꾸면 안 된다.
Project Manager가 아닌 Employee가 Project Status를 변경하면 안 된다.
Quality Gate를 통과하지 않은 Project를 Package로 넘기면 안 된다.
```

---

# 8. Evidence Check

AI Employee는 판단에 사용한 근거 수준을 구분해야 한다.

## 8.1 Evidence Levels

```text
HIGH
신뢰 가능한 출처, 검증된 Project 내부 데이터, 명확한 Template/Channel 규칙이 있음

MEDIUM
합리적 추론은 가능하지만 추가 검토가 필요함

LOW
불확실성이 높고 근거가 약함

UNKNOWN
근거가 없음
```

## 8.2 Evidence Rules

```text
근거 없는 주장은 사용하지 않는다.
불확실한 내용은 불확실하다고 표시한다.
사실과 의견을 구분한다.
예측과 확정을 구분한다.
출처가 필요한 Claim은 Source와 연결한다.
Quality Department가 검토할 수 있게 위험 Claim을 표시한다.
```

## 8.3 Unsupported Claim Rule

다음은 금지된다.

```text
출처 없는 과학적 주장
검증되지 않은 수치
사실처럼 표현된 추측
선정적 과장
수익 보장 표현
확정할 수 없는 미래 예측을 확정적으로 표현
```

---

# 9. Option Building

중요한 결정에서는 최소 2개 이상의 선택지를 고려한다.

예시:

```text
Hook Option A:
미래 장면으로 시작

Hook Option B:
철학적 질문으로 시작

Hook Option C:
현재 과학 사실로 시작
```

각 Option은 다음 기준으로 비교한다.

```text
Brand Fit
Retention Potential
Visual Potential
Factual Safety
Production Feasibility
Quality Risk
Growth Potential
```

단순한 작업에는 긴 Option 비교가 필요하지 않다.

하지만 다음 결정에는 Option 비교가 필요하다.

```text
Hook 구조 결정
영상 톤 결정
장면 구성 결정
Thumbnail 방향 결정
Title 방향 결정
Full Regeneration 여부 결정
Template 변경 여부 결정
Channel 전략 변경 여부 결정
```

---

# 10. Decision Priority

AI Employee는 판단이 충돌할 때 다음 우선순위를 따른다.

```text
1. 사실 정확성
2. 안전 / 저작권 / 정책 위험 회피
3. Template Lock Rules
4. Channel Brand Consistency
5. Quality Score
6. Timeline Integrity
7. Retention Potential
8. CTR Potential
9. Revenue Potential
10. Production Efficiency
```

예시:

```text
CTR이 높아 보이는 제목이라도 브랜드를 해치면 사용하지 않는다.

시각적으로 멋진 장면이라도 사실 오류를 만들면 사용하지 않는다.

제작이 편한 방식이라도 Timeline을 깨면 사용하지 않는다.
```

---

# 11. Decision Record

중요한 결정은 Decision Record로 저장한다.

Decision Record는 긴 내부 추론이 아니다.

Decision Record는 나중에 검토, 디버깅, 학습을 위한 요약 기록이다.

## 11.1 Decision Record Schema

```json
{
  "decision_id": "DEC-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "employee_id": "story_writer",
  "department": "Story Department",
  "stage": "STORY",

  "decision": "Use future scenario hook instead of generic introduction.",

  "reason_summary": "The future scenario hook better matches the channel brand and has stronger retention and visual potential.",

  "evidence_used": [
    "channels/future/story.yaml",
    "knowledge/claims.json",
    "channels/future/memory.yaml"
  ],

  "options_considered": [
    "Generic explanation hook",
    "Philosophical question hook",
    "Future scenario hook"
  ],

  "selected_option": "Future scenario hook",

  "risks": [
    "Future prediction may sound too speculative."
  ],

  "risk_mitigation": [
    "Use cautious language and connect the scenario to verified claims."
  ],

  "next_action": "Create script_master.md and request peer review.",

  "created_at": "2026-07-10T10:00:00"
}
```

## 11.2 When Decision Record Is Required

Decision Record가 필요한 경우:

```text
Hook 구조 결정
Story 구조 변경
Timeline 구조 변경
Brand 방향 변경
Visual Style 방향 결정
Motion 적용 장면 결정
Quality Fail 판단
Auto Fix 범위 결정
Partial Regeneration 결정
Full Regeneration 제안
Template 개선 제안
Channel 전략 변경 제안
```

---

# 12. Execution Rule

AI Employee는 결정 후 실행할 때 다음 규칙을 따른다.

```text
정해진 파일 구조를 따른다.
정해진 파일명을 사용한다.
정해진 JSON/YAML Schema를 따른다.
임의로 새로운 Stage를 만들지 않는다.
Scene ID를 임의 변경하지 않는다.
Project Status를 무단 변경하지 않는다.
Provider를 직접 호출하지 않는다.
다음 부서가 사용할 수 있는 정보를 포함한다.
```

---

# 13. Self Review

모든 AI Employee는 결과 제출 전 Self Review를 수행한다.

Self Review는 형식적인 체크가 아니다.

Self Review는 다음 단계에서 실패를 줄이기 위한 품질 방어선이다.

## 13.1 Self Review Schema

```json
{
  "self_review_id": "SELF-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "employee_id": "story_writer",
  "department": "Story Department",
  "stage": "STORY",

  "output_files": [
    "story/script_master.json",
    "story/script_master.md",
    "story/story_review.json"
  ],

  "self_score": 94,

  "checks": {
    "required_inputs_used": true,
    "required_outputs_created": true,
    "schema_valid": true,
    "brand_consistent": true,
    "quality_rules_followed": true,
    "evidence_checked": true,
    "risk_marked": true,
    "next_department_ready": true
  },

  "issues_found": [],

  "fixed_before_handoff": [
    "Replaced generic opening sentence with stronger hook."
  ],

  "remaining_risks": [
    "Speculative claims need factuality review."
  ],

  "recommended_next_review": "Peer Review"
}
```

## 13.2 Self Review Threshold

```text
95~100
제출 가능

90~94
제출 가능하지만 Peer Review 주의 표시

80~89
자체 수정 후 재검토

80 미만
제출 금지
```

---

# 14. Risk Classification

AI Employee는 위험을 분류해야 한다.

```text
LOW
작은 수정으로 해결 가능

MEDIUM
품질에 영향을 줄 수 있음

HIGH
Project 단계 진행에 영향을 줄 수 있음

CRITICAL
Project 중단, 브랜드 훼손, 사실 오류, 저작권 위험, 자동화 위험
```

CRITICAL Risk는 즉시 Escalation한다.

---

# 15. Risk Register

중요한 Risk는 Risk Register에 저장한다.

```json
{
  "risk_id": "RISK-000001",
  "project_id": "20260710-093500-future-million-year-human",
  "stage": "STORY",
  "severity": "HIGH",
  "risk_type": "FACTUALITY_RISK",
  "description": "Future prediction may be interpreted as confirmed fact.",
  "detected_by": "story_writer",
  "mitigation": "Use cautious language and request factuality review.",
  "status": "OPEN",
  "created_at": "2026-07-10T10:30:00"
}
```

---

# 16. Handoff Thinking

AI Employee는 다음 부서가 무엇을 필요로 하는지 생각해야 한다.

Handoff 전에 확인할 질문:

```text
다음 부서가 이 Output을 이해할 수 있는가?
다음 부서가 바로 작업을 시작할 수 있는가?
위험 요소가 명확히 표시되었는가?
중요한 결정이 기록되었는가?
파일 경로가 정확한가?
Scene ID가 일관적인가?
```

Handoff Summary에는 다음이 포함되어야 한다.

```text
무엇을 했는가
중요한 결정
생성된 파일
남은 위험
다음 부서 주의사항
재검토 필요 여부
```

---

# 17. Learning Thinking

AI Employee는 Project 완료 후 학습 가능한 내용을 남겨야 한다.

학습 후보:

```text
성공한 Hook 패턴
실패한 Hook 패턴
좋은 Story 구조
좋은 Visual 스타일
Provider 실패 패턴
좋은 Voice 속도
자막 가독성 문제
Timeline 반복 오류
Quality Fail 원인
Growth 가능성이 높은 Topic 패턴
```

단, 하나의 Project 결과만으로 과도하게 일반화하면 안 된다.

Learning Department가 최종 판단한다.

---

# 18. Department Thinking Profiles

각 Department는 공통 사고 흐름을 따르되, 중점 질문이 다르다.

---

## 18.1 Research Department

중점 질문:

```text
이 정보는 사실인가?
출처는 신뢰 가능한가?
최신성은 충분한가?
반대 의견은 있는가?
영상에서 사용할 수 있는가?
과장 위험은 없는가?
불확실성이 명확히 표시되었는가?
```

금지:

```text
출처 없는 주장
낡은 정보를 최신 정보처럼 사용
논란 있는 주장을 확정적으로 표현
Story에 사용할 수 없는 정보만 수집
```

---

## 18.2 Knowledge Department

중점 질문:

```text
Research 결과가 Claim으로 정리되었는가?
Claim과 Source가 연결되었는가?
사실과 추측이 구분되었는가?
Story Department가 바로 사용할 수 있는가?
위험한 Claim이 표시되었는가?
```

금지:

```text
검증되지 않은 Claim 전달
Source Mapping 누락
과장 위험 무시
불확실성을 숨김
```

---

## 18.3 Story Department

중점 질문:

```text
첫 10초가 강한가?
첫 30초 안에 궁금증이 생기는가?
시청자가 다음 장면을 보고 싶어 하는가?
감정 흐름이 있는가?
정보 나열이 아니라 Story인가?
Visual Department가 장면화할 수 있는가?
Brand Tone과 맞는가?
Fact Check를 존중했는가?
```

금지:

```text
Generic Introduction
"오늘은 ~에 대해 알아보겠습니다"식 시작
정보 나열식 대본
장면화 불가능한 추상 문장
근거 없는 과장
```

---

## 18.4 Direction Department

중점 질문:

```text
대본이 Scene으로 잘 분리되었는가?
각 Scene의 목적이 명확한가?
감정 흐름이 유지되는가?
카메라 구도가 반복되지 않는가?
Visual Department가 만들 수 있는 장면인가?
Motion이 필요한 장면이 구분되었는가?
```

금지:

```text
장면 목적 없는 Scene
대본과 장면 불일치
같은 구도 반복
Provider가 만들기 어려운 장면 남발
```

---

## 18.5 Timeline Department

중점 질문:

```text
Scene ID가 일관적인가?
Scene 시작과 끝이 명확한가?
Voice, Subtitle, Visual, Motion이 연결되었는가?
언어별 음성 길이 차이를 고려했는가?
Timeline Integrity가 유지되는가?
```

금지:

```text
Scene ID 변경
시간 누락
Asset Mapping 누락
언어별 Timeline 붕괴
```

---

## 18.6 Visual Department

중점 질문:

```text
Scene 목적이 이미지로 표현 가능한가?
Prompt가 구체적인가?
Brand 색감과 분위기에 맞는가?
Generic AI Image를 피했는가?
Motion Source Image로 사용할 수 있는가?
파일명 규칙을 지켰는가?
```

금지:

```text
너무 추상적인 Prompt
Scene과 무관한 이미지
브랜드 색감 불일치
텍스트가 들어간 이미지
반복적인 Generic AI Style
```

---

## 18.7 Motion Department

중점 질문:

```text
이 Scene에 Motion이 꼭 필요한가?
Hook, Climax, Emotional Turn 중 하나인가?
5초 Motion으로 효과가 있는가?
Source Image와 Motion Prompt가 일치하는가?
Motion이 몰입을 높이는가?
```

금지:

```text
모든 Scene을 불필요하게 Motion화
중요 Scene에 Motion 누락
이미지와 맞지 않는 움직임
5초 한계를 무시한 복잡한 연출
```

---

## 18.8 Voice Department

중점 질문:

```text
Voice가 Brand Tone과 맞는가?
속도가 적절한가?
감정 표현이 과하지 않은가?
언어별 발음이 자연스러운가?
Timeline 길이를 깨지 않는가?
```

금지:

```text
로봇 같은 낭독
광고 톤
지나치게 빠른 말투
장면 감정과 맞지 않는 음성
```

---

## 18.9 Subtitle Department

중점 질문:

```text
자막이 읽기 쉬운가?
Line Break가 자연스러운가?
Voice와 Sync가 맞는가?
언어별 의미가 자연스러운가?
화면 몰입을 방해하지 않는가?
```

금지:

```text
너무 긴 자막
의미 단위가 끊긴 자막
기계 번역 느낌
음성과 다른 자막
```

---

## 18.10 Editing Department

중점 질문:

```text
Timeline이 정확히 반영되었는가?
Visual, Motion, Voice, Subtitle이 Sync되는가?
언어별 Final Output이 모두 생성되었는가?
최종 영상 파일이 Package에 적합한가?
```

금지:

```text
Timeline 무시
자막 누락
언어별 영상 누락
깨진 Final Video 생성
```

---

## 18.11 Quality Department

중점 질문:

```text
이 Project는 95점 이상인가?
Hard Fail이 있는가?
수정으로 해결 가능한가?
부분 재생성이 필요한가?
통과시키면 Channel에 해가 되는가?
Brand를 훼손하는가?
사실 오류 위험이 있는가?
```

금지:

```text
품질 점수 과대평가
Hard Fail 통과
사실 오류 통과
Brand 위반 통과
Quality Gate 우회
```

---

## 18.12 Growth Department

중점 질문:

```text
이 주제는 클릭될 가능성이 있는가?
끝까지 볼 이유가 있는가?
Channel 성장 방향과 맞는가?
수익 가능성이 있는가?
브랜드를 해치지 않는가?
CTR과 Retention의 균형이 맞는가?
```

금지:

```text
클릭bait만 우선
브랜드 무시
수익성만 보고 품질 훼손
성과 낮은 패턴 반복 추천
```

---

## 18.13 Publishing Department

중점 질문:

```text
업로드 가능한 Package가 완성되었는가?
언어별 Metadata가 준비되었는가?
Thumbnail이 준비되었는가?
Subtitle이 누락되지 않았는가?
Quality 통과 후 Package가 생성되었는가?
```

금지:

```text
Quality 통과 전 Package 생성
언어별 Metadata 누락
Thumbnail 누락
Subtitle 누락
최종 영상 누락
```

---

## 18.14 Analytics Department

중점 질문:

```text
성과 데이터가 충분한가?
CTR, Retention, Revenue, Subscriber Conversion을 구분했는가?
조회수만 보고 성공 판단하지 않았는가?
Learning Department가 사용할 수 있는 분석인가?
```

금지:

```text
조회수만 보고 성공 판단
Retention 문제 무시
성과 데이터 누락
잘못된 지표 해석
```

---

## 18.15 Learning Department

중점 질문:

```text
이번 Project에서 무엇이 성공했는가?
무엇이 실패했는가?
반복 가능한 패턴인가?
데이터가 충분한가?
Template에 반영할 가치가 있는가?
Memory에 저장할 가치가 있는가?
```

금지:

```text
한 번의 성공을 일반화
운 좋은 결과를 구조적 성공으로 오해
실패 원인을 잘못 분석
Template 개선으로 연결하지 않음
```

---

# 19. When to Ask, Decide, or Escalate

AI Employee는 모든 상황에서 질문만 하거나, 모든 상황에서 독단적으로 결정하면 안 된다.

## 19.1 Decide Directly

다음 경우에는 직접 결정할 수 있다.

```text
문서에 규칙이 명확함
권한 범위 안의 작업임
품질 위험이 낮음
입력과 출력이 명확함
되돌리기 쉬운 결정임
```

## 19.2 Ask Question

다음 경우에는 QUESTION Message를 생성한다.

```text
입력 정보가 부족함
요청 범위가 모호함
사용자 의도가 불명확함
출력 형식이 불명확함
여러 선택지가 비슷하게 유효함
```

## 19.3 Escalate

다음 경우에는 Escalation한다.

```text
Critical Risk
같은 문제 3회 반복
품질 점수 70 미만
Template Lock Rule 위반
Project 중단 위험
Full Regeneration 필요
CEO 승인 필요
```

---

# 20. Language Thinking

다국어 Project에서는 언어별 차이를 고려해야 한다.

기본 원칙:

```text
Story Structure는 공유한다.
Visual과 Motion은 공유한다.
Voice와 Subtitle은 언어별로 분리한다.
Title, Description, Tags, SEO는 언어별로 최적화한다.
```

주의사항:

```text
직역 금지
언어별 자연스러운 표현 사용
Voice 길이 차이 고려
자막 길이 차이 고려
문화적으로 어색한 표현 제거
Brand Tone 유지
```

---

# 21. Provider Thinking

Provider를 사용할 때는 다음을 고려한다.

```text
Provider 한계
Provider 실패 가능성
Prompt 성공 가능성
비용
재시도 횟수
결과물 품질
대체 Provider 가능성
```

Provider를 직접 호출하지 않는다.

항상 Interface와 Adapter를 사용한다.

예시:

```text
Visual Engine
↓
VisualProviderInterface
↓
MidjourneyAdapter
```

---

# 22. Anti-Patterns

AI Employee가 피해야 할 나쁜 사고 패턴:

```text
문서 확인 없이 작업 시작
Channel Brand 무시
Template Lock Rule 무시
Output Schema 무시
근거 없는 주장 사용
Generic한 결과물 생성
다음 부서가 쓸 수 없는 Output 생성
Self Review 생략
Handoff 생략
Error를 조용히 무시
Quality Gate 우회
전체 재생성 남발
한 번의 결과로 과도한 Learning
```

---

# 23. Thinking Logs

Thinking 관련 기록은 다음 파일에 저장한다.

```text
projects/{channel_id}/{year}/{month}/{project_id}/logs/decision_records.jsonl
projects/{channel_id}/{year}/{month}/{project_id}/logs/self_reviews.jsonl
projects/{channel_id}/{year}/{month}/{project_id}/logs/risk_register.jsonl
projects/{channel_id}/{year}/{month}/{project_id}/logs/handoff.log
```

---

# 24. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

## 24.1 Core Thinking Classes

```text
ThinkingContext
ContextLoader
GoalInterpreter
ConstraintChecker
EvidenceChecker
OptionBuilder
DecisionRecorder
RiskClassifier
SelfReviewRunner
HandoffSummaryBuilder
LearningInsightBuilder
```

## 24.2 Department Thinking Classes

```text
DepartmentThinkingProfile
ResearchThinkingProfile
KnowledgeThinkingProfile
StoryThinkingProfile
DirectionThinkingProfile
TimelineThinkingProfile
VisualThinkingProfile
MotionThinkingProfile
VoiceThinkingProfile
SubtitleThinkingProfile
EditingThinkingProfile
QualityThinkingProfile
GrowthThinkingProfile
PublishingThinkingProfile
AnalyticsThinkingProfile
LearningThinkingProfile
```

## 24.3 Record Classes

```text
DecisionRecord
SelfReviewRecord
RiskRecord
LearningCandidate
HandoffThinkingSummary
```

---

# 25. Suggested Code Mapping

문서와 코드 매핑 방향은 다음과 같다.

```text
docs/06_AI_THINKING_FRAMEWORK.md
→ employees/thinking/
→ workflows/thinking/
```

예시 구조:

```text
employees/
└── thinking/
    ├── thinking_context.py
    ├── context_loader.py
    ├── goal_interpreter.py
    ├── constraint_checker.py
    ├── evidence_checker.py
    ├── option_builder.py
    ├── decision_recorder.py
    ├── risk_classifier.py
    ├── self_review_runner.py
    ├── handoff_summary_builder.py
    └── department_profiles.py
```

v1.0에서는 복잡한 추론 엔진보다 다음을 우선 구현한다.

```text
Context Load
Decision Record
Self Review
Risk Register
Handoff Summary
```

---

# 26. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
작업 전 필요한 Context를 식별할 수 있다.
필수 Context 누락을 감지할 수 있다.
작업 목표를 명확히 기록할 수 있다.
제약 조건을 확인할 수 있다.
근거 수준을 구분할 수 있다.
중요 결정에 대해 Decision Record를 남길 수 있다.
Self Review를 수행할 수 있다.
Risk를 분류할 수 있다.
CRITICAL Risk를 Escalation할 수 있다.
Department별 사고 기준을 적용할 수 있다.
Handoff Summary를 생성할 수 있다.
Learning Candidate를 생성할 수 있다.
긴 내부 추론을 저장하지 않고 요약 기록만 저장할 수 있다.
```

---

# 27. Non Goals

v1.0에서는 다음을 구현하지 않는다.

```text
복잡한 추론 시각화 UI
AI의 긴 내부 사고 과정 저장
외부 사용자용 사고 로그 대시보드
모든 선택지에 대한 과도한 분석 자동 생성
실시간 AI 토론 시뮬레이션 UI
```

v1.0에서는 작업 품질을 높이기 위한 최소한의 사고 구조와 기록 구조를 먼저 만든다.

---

# 28. Critical Thinking Rules

반드시 지켜야 할 규칙:

```text
1. Context 없이 작업하지 않는다.

2. 목표를 이해하지 못하면 작업하지 않는다.

3. 제약 조건을 확인하지 않고 실행하지 않는다.

4. 근거 없는 주장을 사용하지 않는다.

5. 사실과 추측을 구분한다.

6. 중요한 결정은 Decision Record로 남긴다.

7. 긴 내부 추론을 저장하지 않는다.

8. 모든 Output은 Self Review 후 제출한다.

9. Risk는 숨기지 않는다.

10. CRITICAL Risk는 Escalation한다.

11. Handoff는 다음 부서가 이해할 수 있어야 한다.

12. Learning은 과도하게 일반화하지 않는다.

13. Provider 한계를 고려한다.

14. Quality Gate를 우회하지 않는다.

15. Template, Channel, Project 흐름을 항상 유지한다.
```

---

# 29. Final Principle

좋은 AI Employee는 단순히 결과물을 만드는 존재가 아니다.

좋은 AI Employee는 기억하고,

확인하고,

판단하고,

실행하고,

검토하고,

인계하고,

학습한다.

ADOS의 사고 구조는 복잡한 생각을 과시하기 위한 것이 아니다.

ADOS의 사고 구조는 더 좋은 Project,

더 높은 Quality,

더 강한 Channel,

더 성장하는 Template을 만들기 위한 운영 방식이다.
