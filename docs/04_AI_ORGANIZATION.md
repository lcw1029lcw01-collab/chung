# 04_AI_ORGANIZATION.md

Version: 1.2.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: AI Organization Architecture  

---

# 1. Purpose

이 문서는 CHUNG COMPANY / ADOS의 AI 조직 구조를 정의한다.

ADOS는 단순 자동화 스크립트가 아니다.

ADOS는 여러 AI Employee가 각자의 책임을 가지고 협업하는 AI 콘텐츠 회사 운영체제이다.

이 문서는 다음을 정의한다.

```text
AI Employee란 무엇인가
AI Employee가 어떤 책임을 가지는가
AI Employee 조직 구조는 어떻게 구성되는가
각 부서의 역할은 무엇인가
각 부서의 입력과 출력은 무엇인가
각 부서의 KPI는 무엇인가
각 부서의 실패 조건은 무엇인가
누가 승인 권한을 가지는가
누가 상태 변경 권한을 가지는가
누가 Escalation을 처리하는가
Claude Code가 어떤 클래스와 모듈로 구현해야 하는가
```

이 문서는 다음 문서들과 직접 연결된다.

```text
03_ARCHITECTURE.md
05_INTER_AI_COMMUNICATION.md
06_AI_THINKING_FRAMEWORK.md
07_PROJECT_SPEC.md
08_TEMPLATE_SYSTEM.md
09_CHANNEL_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
26_QUALITY_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Philosophy

CHUNG COMPANY는 AI Agent를 만들지 않는다.

CHUNG COMPANY는 AI Employee를 만든다.

Agent는 명령을 수행한다.

Employee는 책임을 가진다.

Agent는 작업을 끝내면 멈춘다.

Employee는 결과의 품질과 다음 단계의 영향을 생각한다.

따라서 ADOS의 모든 AI Employee는 다음을 가져야 한다.

```text
Role
Responsibility
Input
Output
KPI
Failure Conditions
Reports To
Approval Authority
Communication Rules
Thinking Rules
Memory Requirements
Quality Requirements
Escalation Rules
```

---

# 3. Company Organization Model

CHUNG COMPANY의 조직 구조는 다음과 같다.

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
Department Lead Employees
↓
Specialist Employees
```

이 구조는 단순한 이름 목록이 아니다.

이 구조는 권한과 책임의 흐름이다.

```text
CEO
→ 최종 사업 방향 결정

COO
→ 전체 운영 결정

Portfolio Manager
→ 여러 채널과 프로젝트의 우선순위 관리

Template Manager
→ Template 검증과 진화 관리

Channel Manager
→ 개별 Channel 운영 관리

Project Manager
→ 개별 Project 실행 관리

Department Lead
→ 각 제작 단계의 결과 책임

Specialist Employee
→ 구체적인 작업 수행
```

---

# 4. Organization Design Rules

AI 조직은 다음 규칙을 따른다.

## 4.1 One Owner Rule

모든 작업에는 반드시 하나의 Owner가 있어야 한다.

Owner가 없는 작업은 실행하지 않는다.

## 4.2 Clear Input Rule

AI Employee는 입력 파일과 입력 Context가 명확하지 않으면 작업하지 않는다.

## 4.3 Clear Output Rule

AI Employee는 반드시 정해진 Output 파일을 생성해야 한다.

## 4.4 No Silent Failure Rule

실패를 조용히 무시하지 않는다.

실패는 Error Log, Communication Message, Escalation 중 하나로 남겨야 한다.

## 4.5 No Unauthorized Approval Rule

모든 AI Employee가 승인 권한을 가지는 것은 아니다.

승인 권한은 제한된다.

## 4.6 Quality Gate Rule

Quality Department 또는 Project Manager가 승인하지 않으면 다음 단계로 넘어갈 수 없다.

## 4.7 Handoff Rule

한 부서가 다음 부서로 넘길 때는 반드시 Handoff Package를 생성해야 한다.

## 4.8 Memory Rule

AI Employee는 작업 전 Memory를 참고하고, 작업 후 학습 가능한 내용을 남겨야 한다.

---

# 5. Role Hierarchy

ADOS의 Role Hierarchy는 다음과 같다.

```text
Level 0: CEO / USER
Level 1: COO AI Employee
Level 2: Portfolio Manager Employee
Level 3: Template Manager Employee
Level 4: Channel Manager Employee
Level 5: Project Manager Employee
Level 6: Department Lead Employee
Level 7: Specialist Employee
Level 8: Reviewer Employee
```

각 Level은 아래 Level의 작업을 조정할 수 있다.

하지만 모든 Level이 모든 파일을 수정할 수 있는 것은 아니다.

---

# 6. CEO / USER

CEO는 사용자이다.

CEO는 CHUNG COMPANY의 최종 의사결정자이다.

## 6.1 Responsibilities

```text
운영할 채널 선택
Template 승인
큰 사업 방향 결정
초기 결과물 최종 검토
완전 자동화 전환 승인
중요한 전략 변경 승인
중요한 브랜드 변경 승인
고위험 자동화 승인
```

## 6.2 CEO Does Not Repeatedly Do

```text
매번 대본 작성
매번 이미지 프롬프트 작성
매번 음성 스크립트 작성
매번 자막 제작
매번 SEO 작성
매번 품질 검사
매번 파일 패키징
매번 반복 수정
```

## 6.3 CEO Decisions

CEO가 결정해야 하는 것:

```text
새 Template을 만들 것인가
새 Channel을 운영할 것인가
특정 Channel을 중단할 것인가
자동화 수준을 높일 것인가
Template Major Version을 승인할 것인가
채널 브랜드 방향을 바꿀 것인가
```

---

# 7. COO AI Employee

COO AI Employee는 ADOS 전체 운영을 총괄한다.

COO는 모든 프로젝트를 직접 제작하지 않는다.

COO는 회사가 올바른 방향으로 작동하는지 관리한다.

## 7.1 Responsibilities

```text
전체 운영 상태 관리
Portfolio 우선순위 결정
부서 간 충돌 해결
큰 실패 상황 처리
Escalation 최종 조정
자동화 수준 관리
품질 기준 유지
수익 목표와 품질 목표 균형 관리
CEO에게 보고
```

## 7.2 Inputs

```text
Company Memory
Portfolio Status
Channel Status Reports
Project Status Reports
Quality Reports
Growth Reports
Analytics Reports
Learning Reports
Error Reports
Escalation Messages
```

## 7.3 Outputs

```text
Operation Decision
Priority Decision
Escalation Decision
Recovery Plan
Automation Level Decision
Weekly Company Report
Strategic Recommendation
```

## 7.4 KPI

```text
전체 Project 성공률
품질 점수 95 이상 Project 비율
Critical Error 감소율
자동 수정 성공률
반복 실패 감소율
채널 성장률
월간 수익 성장률
운영 병목 감소율
```

## 7.5 Failure Conditions

```text
품질 기준 미달 Project를 승인함
반복 실패를 감지하지 못함
부서 간 충돌을 방치함
낮은 성과 Channel을 방치함
Template 개선 필요성을 감지하지 못함
수익만 보고 브랜드 품질을 훼손함
CEO 승인 없이 고위험 자동화를 허용함
```

## 7.6 Authority

COO는 다음 권한을 가진다.

```text
Portfolio 우선순위 변경
Project 일시 중단
전체 재생성 승인
Template 개선 제안 승인 요청
자동화 수준 변경 제안
Department 간 충돌 조정
CEO Escalation
```

COO는 CEO 승인 없이 다음을 할 수 없다.

```text
완전 자동 업로드 전환
Template Major Version 확정
Channel 폐쇄
브랜드 핵심 정체성 변경
외부 SaaS 전환
```

---

# 8. Portfolio Manager Employee

Portfolio Manager는 여러 Channel과 여러 Project를 동시에 관리한다.

CHUNG COMPANY는 영상 하나만 만드는 시스템이 아니므로 Portfolio Manager가 필요하다.

## 8.1 Responsibilities

```text
Channel별 Project 현황 관리
Project 우선순위 관리
업로드 일정 관리
채널별 제작량 균형 관리
진행 중 Project 병목 감지
리소스 배분 제안
성과 기반 우선순위 조정
중단된 Project 감지
```

## 8.2 Inputs

```text
Channel List
Project List
Upload Calendar
Channel Growth Goals
Project Status
Quality Reports
Analytics Reports
Resource Availability
COO Direction
```

## 8.3 Outputs

```text
Portfolio Plan
Project Priority List
Upload Schedule
Bottleneck Report
Channel Workload Report
Resource Allocation Recommendation
```

## 8.4 KPI

```text
업로드 일정 준수율
진행 중 Project 병목 감소율
채널별 제작 균형
우선순위 판단 정확도
방치 Project 감소율
성과 좋은 Channel 집중도
```

## 8.5 Failure Conditions

```text
중요 Project가 방치됨
성과 낮은 Project에 리소스가 과도하게 투입됨
업로드 일정이 무너짐
한 Channel에 작업이 과도하게 몰림
품질 낮은 Project를 빠르게 밀어붙임
```

## 8.6 Owned Files

```text
memory/company_portfolio.json
reports/portfolio_report.json
reports/upload_schedule.json
reports/bottleneck_report.json
```

---

# 9. Template Manager Employee

Template Manager는 Template의 생성, 검증, 버전 관리, 개선 제안을 담당한다.

Template은 CHUNG COMPANY의 핵심 자산이므로 Template Manager의 역할은 매우 중요하다.

## 9.1 Responsibilities

```text
Template 로드
Template 검증
Template 상속 구조 확인
Template Override 검증
Locked Field 보호
Template Score 계산
Template Version 관리
Template Improvement Proposal 생성
Template Evolution 후보 관리
Channel 생성 가능 여부 판단
```

## 9.2 Inputs

```text
Base Template
Category Template
Channel Template
Project Override
Template Memory
Learning Reports
Analytics Reports
Quality Reports
CEO / COO Direction
```

## 9.3 Outputs

```text
Validated Template
Resolved Template
Template Score
Template Error Report
Template Improvement Proposal
Template Version Report
```

## 9.4 KPI

```text
Template 검증 성공률
Template Score 평균
Template 재사용률
Template 기반 Channel 성공률
Template 오류 감소율
Locked Field 보호 성공률
Template 개선 반영 정확도
```

## 9.5 Failure Conditions

```text
필수 Template 파일 누락을 감지하지 못함
낮은 점수 Template을 사용 가능 상태로 둠
Locked Field Override를 허용함
버전 관리 없이 Template을 변경함
성과 데이터 없이 Template을 과도하게 변경함
Channel 정체성을 훼손하는 개선을 승인함
```

## 9.6 Owned Files

```text
templates/
templates/base/
templates/categories/
templates/channels/
reports/template_score.json
reports/template_error_report.json
reports/template_improvement_proposal.json
```

---

# 10. Channel Manager Employee

Channel Manager는 개별 Channel의 운영을 담당한다.

Channel은 실제 사업 단위이다.

Channel Manager는 채널 정체성, 성과, 프로젝트 방향을 관리한다.

## 10.1 Responsibilities

```text
Channel 설정 관리
Channel Memory 관리
Channel KPI 추적
Channel Brand 일관성 유지
Channel별 Topic 방향 관리
Channel별 Project 우선순위 제안
Channel별 AI Employee 설정 관리
Channel별 Growth Strategy 관리
Template 개선 필요성 감지
```

## 10.2 Inputs

```text
channel.yaml
brand.yaml
growth.yaml
quality.yaml
Channel Memory
Template Snapshot
Project Reports
Analytics Reports
Learning Reports
Portfolio Direction
```

## 10.3 Outputs

```text
Channel Status Report
Channel Strategy
Topic Direction
Channel Memory Update
Brand Consistency Report
Channel Growth Report
Template Improvement Signal
```

## 10.4 KPI

```text
채널 성장률
CTR 개선
Retention 개선
구독 전환율 개선
브랜드 일관성 점수
Topic 추천 성공률
Channel Quality Average
Channel Revenue Growth
```

## 10.5 Failure Conditions

```text
Channel 정체성과 맞지 않는 Project 승인
브랜드 일관성 훼손
실패한 Topic 패턴 반복
성과 데이터를 Memory에 반영하지 않음
Template 개선 필요성을 놓침
단기 조회수 때문에 장기 브랜드를 해침
```

## 10.6 Owned Files

```text
channels/{channel_id}/channel.yaml
channels/{channel_id}/brand.yaml
channels/{channel_id}/growth.yaml
channels/{channel_id}/memory.yaml
channels/{channel_id}/reports/channel_status.json
channels/{channel_id}/reports/growth_report.json
```

---

# 11. Project Manager Employee

Project Manager는 영상 1개 단위의 Project 실행을 총괄한다.

Project Manager는 직접 대본을 쓰거나 이미지를 만들지 않는다.

Project Manager는 각 Department가 올바른 순서와 기준으로 작업하도록 관리한다.

## 11.1 Responsibilities

```text
Project 생성
Project 상태 관리
Stage 실행 순서 관리
Task 생성
Department Handoff 관리
필수 파일 생성 여부 확인
Lock 관리
Snapshot 관리
Quality Gate 확인
Auto Fix 요청
Retry 관리
Escalation 관리
Package 생성 요청
Final Report 생성
```

## 11.2 Inputs

```text
Project Request
Channel Snapshot
Template Snapshot
Topic
Project Status
Department Outputs
Quality Reports
Communication Logs
Error Logs
```

## 11.3 Outputs

```text
project.json
Task Queue
State Change
Snapshot
Handoff Request
Auto Fix Request
Escalation Request
Final Project Report
```

## 11.4 KPI

```text
Project 완료율
상태 전환 정확도
필수 파일 생성률
Stage 지연 감소율
오류 복구율
품질 기준 통과율
Package 완성률
```

## 11.5 Failure Conditions

```text
잘못된 상태 전환 허용
필수 파일 누락 방치
Lock 충돌 방치
Quality Gate 미통과 Project를 Package로 넘김
실패 원인 기록 누락
Handoff 없이 다음 Stage 진행
```

## 11.6 Owned Files

```text
projects/{channel_id}/{year}/{month}/{project_id}/project.json
projects/{channel_id}/{year}/{month}/{project_id}/logs/
projects/{channel_id}/{year}/{month}/{project_id}/snapshots/
projects/{channel_id}/{year}/{month}/{project_id}/reports/final_report.json
```

---

# 12. Department Structure

Project 제작에는 다음 Department가 참여한다.

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

각 Department는 Department Lead와 Specialist Employees를 가진다.

---

# 13. Research Department

Research Department는 좋은 영상의 기반이 되는 정보를 수집한다.

## 13.1 Mission

```text
주제에 대해 신뢰 가능한 정보를 수집하고,
영상 제작에 사용할 수 있는 사실과 맥락을 확보한다.
```

## 13.2 Specialist Employees

```text
Trend Research Employee
Fact Research Employee
Source Research Employee
Competitor Research Employee
Audience Research Employee
```

## 13.3 Inputs

```text
topic.json
channel.yaml
growth.yaml
brand.yaml
Template Research Rules
Channel Memory
```

## 13.4 Outputs

```text
research/research.json
research/sources.json
research/facts.json
research/competitors.json
research/trend.json
```

## 13.5 KPI

```text
정보 정확도
출처 신뢰도
최신성
스토리 활용 가능성
경쟁 콘텐츠 분석 품질
불확실성 표시 정확도
```

## 13.6 Failure Conditions

```text
출처 없는 주장 사용
오래된 정보를 최신 정보처럼 사용
불확실한 내용을 확정적으로 전달
경쟁 영상 분석 누락
Story에 사용할 수 없는 정보만 수집
```

---

# 14. Knowledge Department

Knowledge Department는 Research 결과를 영상 제작에 사용할 수 있는 지식으로 정리한다.

## 14.1 Mission

```text
Research 결과를 Claim, Context, Risk로 정리하여 Story Department가 사용할 수 있게 만든다.
```

## 14.2 Specialist Employees

```text
Knowledge Organizer Employee
Claim Builder Employee
Fact Check Employee
Risk Check Employee
Source Mapping Employee
```

## 14.3 Inputs

```text
research/research.json
research/sources.json
research/facts.json
research/trend.json
```

## 14.4 Outputs

```text
knowledge/knowledge.json
knowledge/claims.json
knowledge/fact_check.json
knowledge/risk_notes.json
```

## 14.5 KPI

```text
Claim 명확성
Fact Check 완료율
Source Mapping 정확도
위험 주장 감지율
Story 활용 가능성
```

## 14.6 Failure Conditions

```text
검증되지 않은 Claim 전달
사실과 추측을 구분하지 않음
Source와 Claim 연결 누락
과장 위험을 감지하지 못함
```

---

# 15. Story Department

Story Department는 시청자가 끝까지 볼 수 있는 이야기 구조와 대본을 만든다.

## 15.1 Mission

```text
Knowledge를 Channel Brand에 맞는 강한 Story로 변환한다.
```

## 15.2 Specialist Employees

```text
Hook Writer Employee
Outline Writer Employee
Script Writer Employee
Story Editor Employee
Retention Writer Employee
Localization Writer Employee
Story Reviewer Employee
```

## 15.3 Inputs

```text
knowledge/knowledge.json
knowledge/claims.json
knowledge/fact_check.json
brand.yaml
story.yaml
growth.yaml
Channel Memory
```

## 15.4 Outputs

```text
story/outline.json
story/hook.json
story/script_master.json
story/script_master.md
story/story_review.json
languages/{lang}/script.json
```

## 15.5 KPI

```text
Hook Score
Retention Potential
Story Clarity
Emotional Arc
Brand Tone Match
Visual Potential
Factual Safety
```

## 15.6 Failure Conditions

```text
첫 10초가 약함
첫 30초 안에 궁금증이 없음
Generic Introduction 사용
정보 나열식 대본
감정 변화 없음
Visual Department가 장면화하기 어려움
Fact Check를 무시함
```

---

# 16. Direction Department

Direction Department는 대본을 장면과 연출로 변환한다.

## 16.1 Mission

```text
Story를 Scene, Camera, Emotion, Visual Goal로 변환한다.
```

## 16.2 Specialist Employees

```text
Scene Planner Employee
Emotion Planner Employee
Camera Planner Employee
Director Notes Employee
Scene Continuity Employee
```

## 16.3 Inputs

```text
story/script_master.json
story/outline.json
brand.yaml
visual.yaml
story.yaml
```

## 16.4 Outputs

```text
direction/scene_plan.json
direction/emotion_plan.json
direction/camera_plan.json
direction/director_notes.md
```

## 16.5 KPI

```text
Scene Clarity
Scene Flow
Emotional Continuity
Camera Variety
Visual Feasibility
Brand Fit
```

## 16.6 Failure Conditions

```text
대본과 장면 불일치
같은 구도 반복
감정 흐름 단절
Visual Provider가 만들기 어려운 장면 설계
Scene 목적 불명확
```

---

# 17. Timeline Department

Timeline Department는 영상 전체의 시간 구조를 만든다.

## 17.1 Mission

```text
Scene, Voice, Subtitle, Visual, Motion, Editing 정보를 하나의 시간 구조로 연결한다.
```

## 17.2 Specialist Employees

```text
Timeline Architect Employee
Scene Timing Employee
Asset Mapping Employee
Language Timing Employee
Timeline Reviewer Employee
```

## 17.3 Inputs

```text
direction/scene_plan.json
direction/camera_plan.json
story/script_master.json
languages/{lang}/script.json
visual.yaml
voice.yaml
subtitle.yaml
```

## 17.4 Outputs

```text
timeline/timeline.json
timeline/timeline_review.json
timeline/timeline_lock.json
```

## 17.5 KPI

```text
Scene ID 일관성
시간 구조 정확도
장면 밀도
언어별 길이 대응
Asset Mapping 완성도
Timeline Integrity
```

## 17.6 Failure Conditions

```text
Scene ID 불일치
장면 시간 누락
Asset 연결 누락
Voice 길이와 Scene 길이 불일치
언어별 Timeline 붕괴
```

---

# 18. Visual Department

Visual Department는 Timeline에 맞는 이미지 프롬프트와 이미지 자산을 만든다.

## 18.1 Mission

```text
각 Scene의 목적과 Brand에 맞는 Visual Asset을 생성할 수 있게 만든다.
```

## 18.2 Specialist Employees

```text
Midjourney Prompt Employee
Image Reviewer Employee
Visual Consistency Employee
Asset Naming Employee
Thumbnail Visual Employee
```

## 18.3 Inputs

```text
timeline/timeline.json
direction/scene_plan.json
brand.yaml
visual.yaml
Channel Memory
```

## 18.4 Outputs

```text
prompts/midjourney_image_prompts.json
prompts/thumbnail_prompt.json
prompts/prompt_review.json
assets/images/
assets/thumbnails/
```

## 18.5 KPI

```text
Image Prompt Quality
Scene Match
Brand Consistency
Visual Variety
Midjourney Success Rate
Regeneration Reduction
```

## 18.6 Failure Conditions

```text
프롬프트가 너무 추상적임
Scene 목적과 이미지 불일치
브랜드 색감 불일치
Generic AI Image 반복
Midjourney 생성 실패 가능성이 높음
이미지 파일명 규칙 위반
```

---

# 19. Motion Department

Motion Department는 중요한 Scene을 Motion 영상으로 변환한다.

현재 기본 Motion Provider는 Midjourney Video이다.

## 19.1 Mission

```text
Hook, Climax, Emotional Turn 장면에 필요한 Motion을 설계한다.
```

## 19.2 Specialist Employees

```text
Motion Planner Employee
Midjourney Video Prompt Employee
Motion Reviewer Employee
Motion Asset Manager Employee
```

## 19.3 Inputs

```text
timeline/timeline.json
assets/images/
visual.yaml
motion rules
brand.yaml
```

## 19.4 Outputs

```text
prompts/midjourney_video_prompts.json
assets/motion/
motion_review.json
```

## 19.5 KPI

```text
Motion Necessity Accuracy
Hook 강화 효과
Climax 강화 효과
Motion Prompt Success Rate
Unnecessary Motion Reduction
```

## 19.6 Failure Conditions

```text
모든 장면을 불필요하게 Motion화
중요 장면에 Motion 누락
장면 감정과 맞지 않는 움직임
5초 Motion 한계 무시
Source Image와 Motion Prompt 불일치
```

---

# 20. Voice Department

Voice Department는 언어별 자연스러운 나레이션 음성을 만든다.

현재 기본 Voice Provider는 Typecast이다.

## 20.1 Mission

```text
Brand Tone과 Timeline에 맞는 언어별 Voice Script와 음성 자산을 만든다.
```

## 20.2 Specialist Employees

```text
Narration Localization Employee
Typecast Voice Employee
Voice Emotion Employee
Audio QA Employee
Language Voice Reviewer Employee
```

## 20.3 Inputs

```text
languages/{lang}/script.json
voice.yaml
timeline/timeline.json
brand.yaml
```

## 20.4 Outputs

```text
languages/{lang}/narration.txt
languages/{lang}/voice.json
assets/audio/
```

## 20.5 KPI

```text
Voice Naturalness
Pronunciation Accuracy
Emotion Match
Timeline Fit
Language Quality
Audio Usability
```

## 20.6 Failure Conditions

```text
로봇 같은 음성
지나치게 빠른 말투
장면 감정과 음성 불일치
언어별 길이 차이로 Timeline 붕괴
Typecast 설정 오류
Audio File 누락
```

---

# 21. Subtitle Department

Subtitle Department는 언어별 자막을 만든다.

## 21.1 Mission

```text
읽기 쉽고 Timeline에 맞는 자막을 만든다.
```

## 21.2 Specialist Employees

```text
Subtitle Generator Employee
Subtitle Timing Employee
Subtitle Readability Employee
Translation QA Employee
Subtitle Reviewer Employee
```

## 21.3 Inputs

```text
languages/{lang}/narration.txt
languages/{lang}/voice.json
timeline/timeline.json
subtitle.yaml
```

## 21.4 Outputs

```text
languages/{lang}/subtitle.srt
assets/subtitles/
subtitle_review.json
```

## 21.5 KPI

```text
Subtitle Sync
Readability
Line Break Quality
Translation Naturalness
Brand Tone Match
```

## 21.6 Failure Conditions

```text
자막 싱크 불량
한 줄이 너무 김
의미 단위가 끊김
기계 번역 느낌
음성과 자막 내용 불일치
```

---

# 22. Editing Department

Editing Department는 Timeline에 따라 최종 영상을 조립한다.

## 22.1 Mission

```text
Visual, Motion, Voice, Subtitle을 Timeline 기준으로 조립하여 최종 영상 파일을 만든다.
```

## 22.2 Specialist Employees

```text
Edit Planner Employee
Render Planner Employee
Final Timeline Employee
Render QA Employee
File Package Employee
```

## 22.3 Inputs

```text
timeline/timeline.json
assets/images/
assets/motion/
assets/audio/
assets/subtitles/
edit rules
```

## 22.4 Outputs

```text
edit/edit_plan.json
edit/render_plan.json
edit/final_timeline.json
package/final_video_ko.mp4
package/final_video_en.mp4
```

## 22.5 KPI

```text
Render Success Rate
Timeline Sync Accuracy
Final Video Integrity
Language Output Completion
Subtitle Burn-in or File Accuracy
```

## 22.6 Failure Conditions

```text
음성과 영상 싱크 불일치
자막 누락
최종 영상 파일 깨짐
언어별 영상 누락
Timeline 반영 실패
```

---

# 23. Quality Department

Quality Department는 95점 미만 Project를 통과시키지 않는다.

Quality Department는 매우 강한 권한을 가진다.

## 23.1 Mission

```text
채널 성장에 해가 되는 저품질 Project를 차단하고, 수정 또는 재생성을 요청한다.
```

## 23.2 Specialist Employees

```text
Story Quality Employee
Visual Quality Employee
Voice Quality Employee
Subtitle Quality Employee
Timeline Quality Employee
Factuality Quality Employee
Brand Consistency Employee
Final Quality Employee
Hard Fail Detector Employee
```

## 23.3 Inputs

```text
All Project Outputs
quality.yaml
brand.yaml
timeline/timeline.json
reports/
package/
```

## 23.4 Outputs

```text
reports/quality_report.json
reports/auto_fix_report.json
quality_gate_decision.json
```

## 23.5 KPI

```text
Issue Detection Accuracy
Hard Fail Detection Rate
Quality Score Accuracy
Auto Fix Success Rate
False Pass Reduction
95+ Pass Integrity
```

## 23.6 Failure Conditions

```text
사실 오류 통과
Hook 약한 영상 통과
Timeline 깨진 영상 통과
브랜드 불일치 영상 통과
품질 점수 과대평가
Hard Fail 감지 실패
```

## 23.7 Authority

Quality Department는 다음 권한을 가진다.

```text
Project Stage 통과 거부
Auto Fix 요청
Partial Regeneration 요청
Hard Fail 선언
Human Review 요청
Project Manager Escalation
```

Quality Department는 다음 권한은 없다.

```text
Project 상태 직접 변경
Template 직접 변경
Channel 전략 직접 변경
CEO 승인 없이 Published 처리
```

---

# 24. Growth Department

Growth Department는 채널 성장과 수익 가능성을 높인다.

## 24.1 Mission

```text
Topic, Title, SEO, Retention, Revenue 가능성을 분석하여 Channel 성장을 돕는다.
```

## 24.2 Specialist Employees

```text
Topic Score Employee
CTR Prediction Employee
Retention Prediction Employee
SEO Employee
Revenue Potential Employee
Growth Reviewer Employee
```

## 24.3 Inputs

```text
topic.json
project outputs
channel memory
analytics reports
growth.yaml
```

## 24.4 Outputs

```text
reports/growth_prediction.json
next_topic_candidates.json
metadata_suggestions.json
```

## 24.5 KPI

```text
Topic Score Accuracy
CTR Prediction Accuracy
Retention Prediction Accuracy
SEO Quality
Revenue Potential Accuracy
Channel Fit
```

## 24.6 Failure Conditions

```text
클릭bait만 우선
채널 정체성 무시
수익성만 보고 브랜드 훼손
품질과 성장의 충돌 무시
성과 낮은 Topic 패턴 반복 추천
```

---

# 25. Publishing Department

Publishing Department는 업로드 가능한 패키지를 준비한다.

v1.0에서는 실제 자동 업로드보다 Upload Package 생성이 우선이다.

## 25.1 Mission

```text
Quality를 통과한 Project를 업로드 가능한 상태로 패키징한다.
```

## 25.2 Specialist Employees

```text
Title Employee
Description Employee
Tag Employee
Thumbnail QA Employee
Upload Package Employee
Publish QA Employee
Pinned Comment Employee
```

## 25.3 Inputs

```text
package/final_video_{lang}.mp4
thumbnail.png
languages/{lang}/subtitle.srt
growth suggestions
brand.yaml
publishing rules
```

## 25.4 Outputs

```text
package/upload_package.json
package/metadata_ko.json
package/metadata_en.json
package/final_report.json
```

## 25.5 KPI

```text
Package Completion Rate
Metadata Quality
SEO Readiness
Language Consistency
Missing File Rate 0%
```

## 25.6 Failure Conditions

```text
제목/설명/태그 누락
언어별 메타데이터 불일치
썸네일 누락
최종 영상 누락
Subtitle 누락
Quality 통과 전 Package 생성
```

---

# 26. Analytics Department

Analytics Department는 업로드 후 성과 데이터를 분석한다.

## 26.1 Mission

```text
Published Project의 성과를 분석하여 Learning Department가 사용할 수 있는 데이터로 정리한다.
```

## 26.2 Specialist Employees

```text
View Analytics Employee
CTR Analytics Employee
Retention Analytics Employee
Revenue Analytics Employee
Audience Analytics Employee
```

## 26.3 Inputs

```text
Published Project Data
YouTube Analytics Export
Manual Performance Data
Channel Memory
Growth Goals
```

## 26.4 Outputs

```text
reports/analytics_report.json
reports/performance_summary.json
```

## 26.5 KPI

```text
성과 데이터 완성도
CTR 분석 정확도
Retention Drop Point 감지
Revenue 분석 정확도
Learning 가능성
```

## 26.6 Failure Conditions

```text
성과 데이터 누락
잘못된 지표 해석
조회수만 보고 성공 판단
Retention 문제를 감지하지 못함
Learning으로 연결하지 못함
```

---

# 27. Learning Department

Learning Department는 성과와 실패를 학습하여 다음 제작과 Template 개선에 반영한다.

## 27.1 Mission

```text
Project 결과에서 성공 패턴과 실패 패턴을 찾아 Memory와 Template에 반영한다.
```

## 27.2 Specialist Employees

```text
Performance Learning Employee
Success Pattern Employee
Failure Pattern Employee
Template Evolution Employee
Memory Update Employee
Provider Learning Employee
```

## 27.3 Inputs

```text
reports/analytics_report.json
reports/quality_report.json
reports/growth_prediction.json
channel memory
template memory
project memory
```

## 27.4 Outputs

```text
reports/learning_report.json
memory updates
template_improvement_proposal.json
channel_strategy_update.json
```

## 27.5 KPI

```text
반복 실패 감소
성공 패턴 재사용률
Template 개선 정확도
다음 Project 품질 향상
잘못된 학습 감소
```

## 27.6 Failure Conditions

```text
성과 데이터를 Memory에 반영하지 않음
데이터 1개로 과도하게 일반화
운 좋은 성공을 구조적 성공으로 오해
실패 원인을 잘못 분석
Template 개선으로 연결하지 못함
```

---

# 28. Memory Department

Memory Department는 CHUNG COMPANY의 기억을 관리한다.

## 28.1 Mission

```text
Company, Template, Channel, Project Memory를 안전하게 저장하고 필요한 시점에 제공한다.
```

## 28.2 Specialist Employees

```text
Company Memory Employee
Template Memory Employee
Channel Memory Employee
Project Memory Employee
Failure Memory Employee
Success Memory Employee
```

## 28.3 Inputs

```text
Learning Reports
Quality Reports
Analytics Reports
Decision Records
Error Logs
Communication Logs
```

## 28.4 Outputs

```text
Company Memory Update
Template Memory Update
Channel Memory Update
Project Memory Update
Success Pattern Memory
Failure Pattern Memory
```

## 28.5 KPI

```text
Memory Recall Accuracy
Memory Update Accuracy
Duplicate Memory Reduction
Useful Pattern Reuse
Failure Pattern Detection
```

## 28.6 Failure Conditions

```text
중요한 학습을 저장하지 않음
잘못된 정보를 Memory에 저장
중복 Memory 과다 생성
오래된 실패 패턴을 계속 사용
필요한 Context를 제공하지 못함
```

---

# 29. Stage Ownership Matrix

Project 상태별 담당 부서는 다음과 같다.

```text
NEW                    → Project Manager
INITIALIZED            → Project Manager
RESEARCH               → Research Department
KNOWLEDGE              → Knowledge Department
STORY                  → Story Department
DIRECTION              → Direction Department
TIMELINE               → Timeline Department
VISUAL                 → Visual Department
MOTION                 → Motion Department
VOICE                  → Voice Department
SUBTITLE               → Subtitle Department
EDITING                → Editing Department
QUALITY                → Quality Department
AUTO_FIX               → Project Manager + Failed Department
PACKAGE                → Publishing Department
READY                  → Project Manager
PUBLISHED              → Publishing Department
ANALYTICS              → Analytics Department
LEARNING               → Learning Department
COMPLETE               → Project Manager
```

Project Manager는 Stage Owner가 생성한 Output을 검증한 뒤 다음 상태로 전환한다.

---

# 30. Approval Authority Matrix

```text
작업 결과 제출:
모든 Employee

Self Review:
작업 수행 Employee

Peer Review:
Reviewer Employee 또는 다음 Department

Quality Approval:
Quality Department

Project State Change:
Project Manager

Channel Strategy Change:
Channel Manager

Portfolio Priority Change:
Portfolio Manager

Template Version Change:
Template Manager

Full Regeneration Approval:
COO

Full Auto Publish Approval:
CEO / USER

Major Business Direction:
CEO / USER
```

---

# 31. Employee Standard Schema

모든 AI Employee는 다음 Schema를 따른다.

```yaml
employee:
  id: story_writer
  name: Story Writer Employee
  department: Story Department
  level: specialist
  status: active

  role: ""
  responsibilities: []

  input_files: []
  output_files: []

  required_context:
    - company_memory
    - template_rules
    - channel_memory
    - project_status

  kpi: []
  quality_rules: []
  failure_conditions: []

  reports_to: Project Manager Employee

  authority:
    can_create_outputs: true
    can_request_review: true
    can_peer_review: false
    can_quality_approve: false
    can_change_project_state: false
    can_escalate: true

  communication:
    must_create_handoff: true
    must_log_decisions: true
    must_report_errors: true

  thinking:
    must_self_review: true
    must_check_evidence: true
    must_write_decision_record: true
```

---

# 32. Department Standard Schema

모든 Department는 다음 Schema를 따른다.

```yaml
department:
  id: story_department
  name: Story Department
  status: active

  mission: ""
  stage_owner_for:
    - STORY

  lead_employee: story_lead
  specialist_employees:
    - hook_writer
    - outline_writer
    - script_writer
    - story_editor

  input_files: []
  output_files: []

  kpi: []
  failure_conditions: []

  required_reviews:
    - self_review
    - peer_review
    - quality_review

  handoff_to:
    - Direction Department
```

---

# 33. Human Review Policy

초기 운영 단계에서는 Human Review가 필요하다.

```yaml
human_review:
  initial_mode: true
  required_before_publish: true
  allow_auto_publish_after_trust: true
  minimum_successful_projects_before_full_auto: 10
  minimum_average_quality_score: 95
  maximum_critical_errors: 0
```

Full Auto 전환 조건:

```text
연속 10개 Project 품질 점수 95 이상
Critical Error 0개
Package 누락 0개
사용자 수정 개입 감소
채널 톤 안정화
CEO 승인
```

---

# 34. Escalation Policy

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

Escalation Trigger:

```text
같은 오류 3회 반복
품질 점수 70 미만
Critical Risk 발생
필수 파일 누락
Locked Field Override 시도
Template 검증 실패
Project 중단 위험
브랜드/수익/품질 충돌
Full Regeneration 필요
```

---

# 35. Organization Memory Policy

AI 조직은 Memory와 연결되어야 한다.

각 Employee는 작업 전 다음 Memory를 확인한다.

```text
Company Memory
Template Memory
Channel Memory
Project Memory
Success Memory
Failure Memory
Provider Memory
Quality Memory
```

각 Employee는 작업 후 다음을 남긴다.

```text
Decision Record
Self Review
Handoff Summary
Risk Note
Learning Candidate
```

---

# 36. Organization Logging Policy

조직 활동은 반드시 로그로 남긴다.

로그 대상:

```text
Task Assignment
Task Acceptance
Task Rejection
Task Result
Review Result
Approval Result
Revision Request
Escalation
Meeting Result
State Change
Decision Record
Error Report
```

로그 위치:

```text
projects/{channel_id}/{year}/{month}/{project_id}/logs/
channels/{channel_id}/logs/
memory/company_events.jsonl
```

---

# 37. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

## 37.1 Core Organization Classes

```text
AIEmployee
Department
OrganizationRegistry
EmployeeRegistry
DepartmentRegistry
Role
Authority
KPI
FailureCondition
```

## 37.2 Manager Classes

```text
COOEmployee
PortfolioManagerEmployee
TemplateManagerEmployee
ChannelManagerEmployee
ProjectManagerEmployee
```

## 37.3 Runner Classes

```text
DepartmentRunner
EmployeeRunner
TaskRunner
ReviewRunner
ApprovalRunner
```

## 37.4 Governance Classes

```text
ApprovalAuthority
EscalationManager
KPITracker
FailureDetector
HumanReviewPolicy
OrganizationMemoryManager
OrganizationLogger
```

---

# 38. Suggested Code Mapping

문서와 코드의 매핑 방향은 다음과 같다.

```text
docs/04_AI_ORGANIZATION.md
→ employees/
→ employees/base/
→ employees/departments/
→ employees/managers/
```

예시 구조:

```text
employees/
├── base/
│   ├── ai_employee.py
│   ├── department.py
│   ├── authority.py
│   └── kpi.py
│
├── managers/
│   ├── coo_employee.py
│   ├── portfolio_manager.py
│   ├── template_manager.py
│   ├── channel_manager.py
│   └── project_manager.py
│
├── departments/
│   ├── research_department.py
│   ├── knowledge_department.py
│   ├── story_department.py
│   ├── direction_department.py
│   ├── timeline_department.py
│   ├── visual_department.py
│   ├── motion_department.py
│   ├── voice_department.py
│   ├── subtitle_department.py
│   ├── editing_department.py
│   ├── quality_department.py
│   ├── growth_department.py
│   ├── publishing_department.py
│   ├── analytics_department.py
│   ├── learning_department.py
│   └── memory_department.py
│
└── registry/
    ├── employee_registry.py
    └── department_registry.py
```

---

# 39. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
AI Employee를 등록할 수 있다.
Department를 등록할 수 있다.
Employee별 책임을 조회할 수 있다.
Department별 입력/출력 파일을 조회할 수 있다.
Project 상태에 맞는 Stage Owner를 찾을 수 있다.
Employee별 KPI를 추적할 수 있다.
Failure Condition을 감지할 수 있다.
승인 권한을 구분할 수 있다.
상태 변경 권한을 제한할 수 있다.
Escalation 대상을 찾을 수 있다.
Human Review Mode와 Full Auto Mode를 구분할 수 있다.
Department Handoff 규칙을 적용할 수 있다.
```

---

# 40. Non Goals

v1.0에서는 다음을 구현하지 않는다.

```text
복잡한 실시간 AI 회의 UI
사람 직원용 권한 관리 시스템
외부 사용자용 조직 관리 대시보드
AI Employee 자동 채용 Marketplace
다중 회사 조직 구조
```

v1.0에서는 내부 ADOS 운영에 필요한 AI 조직 구조를 먼저 만든다.

---

# 41. Critical Organization Rules

반드시 지켜야 할 규칙:

```text
1. AI Agent가 아니라 AI Employee이다.

2. 모든 Employee는 책임과 Output을 가진다.

3. 모든 작업에는 Owner가 있어야 한다.

4. 모든 Stage에는 담당 Department가 있어야 한다.

5. 승인 권한은 제한된다.

6. Quality Department는 품질 통과에 강한 권한을 가진다.

7. Project Manager만 Project 상태를 변경할 수 있다.

8. COO 승인 없이 전체 재생성을 수행하지 않는다.

9. CEO 승인 없이 완전 자동 업로드로 전환하지 않는다.

10. Handoff 없이 다음 Stage로 넘어가지 않는다.

11. 실패는 반드시 기록된다.

12. 중요한 판단은 Decision Record로 남긴다.

13. 조직 구조는 Template, Channel, Project 흐름과 연결되어야 한다.
```

---

# 42. Final Principle

CHUNG COMPANY의 품질은 AI 모델 하나에서 나오지 않는다.

CHUNG COMPANY의 품질은 조직 구조에서 나온다.

조직은 책임을 만든다.

책임은 검토를 만든다.

검토는 품질을 만든다.

품질은 채널 성장을 만든다.

따라서 ADOS의 AI Employee는 혼자 일하지 않는다.

AI Employee는 조직 안에서 일하고, 책임지고, 검토하고, 수정하고, 학습한다.
