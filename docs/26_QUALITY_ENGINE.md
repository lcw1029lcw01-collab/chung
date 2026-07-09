# 26_QUALITY_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Quality Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Quality Engine을 정의한다.

Quality Engine은 Project의 Research, Knowledge, Story, Direction, Timeline, Visual, Motion, Voice, Subtitle, Editing 결과물을 종합 검수하고, Project가 Package 단계로 넘어갈 수 있는지 판단하는 엔진이다.

Quality Engine은 단순히 점수를 매기는 엔진이 아니다.

Quality Engine은 다음을 판단한다.

```text
이 영상은 사실적으로 안전한가?
Story가 강한가?
Brand와 맞는가?
Timeline이 깨지지 않았는가?
Scene별 Asset이 제대로 연결되었는가?
Voice와 Subtitle이 맞는가?
언어별 결과물이 완성되었는가?
Visual / Motion이 품질 기준을 통과했는가?
Editing 구조가 Package로 넘어갈 수 있는가?
Auto Fix가 필요한가?
Partial Regeneration이 필요한가?
Human Review가 필요한가?
```

Quality Engine의 결과는 Workflow Orchestrator의 다음 분기를 결정한다.

```text
PASS
→ PACKAGE

HUMAN_REVIEW_RECOMMENDED
→ WAITING_FOR_HUMAN_REVIEW 또는 PACKAGE

AUTO_FIX_REQUIRED
→ AUTO_FIX

PARTIAL_REGENERATION_REQUIRED
→ 특정 Stage로 Revision

FAIL
→ ESCALATION
```

이 문서는 다음 문서들과 직접 연결된다.

```text
06_AI_THINKING_FRAMEWORK.md
07_PROJECT_SPEC.md
10_BRAND_SYSTEM.md
12_PROJECT_ENGINE.md
13_MEMORY_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
16_TIMELINE_ENGINE.md
17_RESEARCH_ENGINE.md
18_KNOWLEDGE_ENGINE.md
19_STORY_ENGINE.md
20_DIRECTION_ENGINE.md
21_VISUAL_ENGINE.md
22_MOTION_ENGINE.md
23_VOICE_ENGINE.md
24_SUBTITLE_ENGINE.md
25_EDITING_ENGINE.md
27_GROWTH_ENGINE.md
28_PUBLISHING_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Quality Engine은 제작된 Project가 공개 가능한 수준인지 판단하는 최종 품질 게이트이다.

전체 흐름:

```text
Editing
↓
Quality Engine
↓
Quality Report
↓
Workflow Decision
↓
Package / Auto Fix / Revision / Escalation
```

Quality Engine의 핵심 목표는 다음이다.

```text
품질 기준 미달 Project가 Package로 넘어가는 것을 막는다.
Hard Fail을 사전에 감지한다.
부분 수정 가능한 문제를 정확히 분리한다.
전체 재생성보다 부분 수정을 우선한다.
Quality 결과를 Learning과 Memory로 연결한다.
```

---

# 3. Quality Philosophy

## 3.1 Quality Gate Is Mandatory

Quality Stage를 통과하지 않은 Project는 Package 또는 READY 상태가 될 수 없다.

금지:

```text
Quality Report 없이 Package 생성
Quality Fail인데 READY 처리
Hard Fail이 있는데 Human Review 없이 통과
Asset 누락 상태에서 Publishing 준비
```

## 3.2 Quality Is Multi-Dimensional

좋은 영상은 한 가지 점수로만 판단할 수 없다.

Quality Engine은 다음을 함께 본다.

```text
Factual Accuracy
Story Strength
Brand Consistency
Timeline Integrity
Visual Quality
Motion Quality
Voice Quality
Subtitle Quality
Editing Readiness
Language Completeness
Asset Integrity
Publishing Readiness
```

## 3.3 Hard Fail Overrides Score

전체 점수가 높아도 Hard Fail이 있으면 통과할 수 없다.

예시:

```text
전체 점수 96
하지만 영어 자막 누락
→ FAIL 또는 AUTO_FIX_REQUIRED

전체 점수 94
하지만 Forbidden Claim 사용
→ FAIL 또는 ESCALATION

전체 점수 92
하지만 Timeline Scene ID 불일치
→ AUTO_FIX_REQUIRED 또는 FAIL
```

## 3.4 Partial Fix First

Quality 문제 발생 시 전체 Project 재생성은 마지막 수단이다.

우선순위:

```text
1. 특정 파일 수정
2. 특정 Scene 수정
3. 특정 언어 수정
4. 특정 Stage 부분 재실행
5. 특정 Stage 전체 재실행
6. Project 전체 재생성
```

Project 전체 재생성은 COO 승인 없이는 수행하지 않는다.

---

# 4. Quality Engine Responsibilities

Quality Engine의 책임:

```text
Quality Input 로드
Stage별 Report 로드
Final Timeline 검증
Asset Registry 검증
Research / Knowledge 검증
Story 검증
Brand Consistency 검증
Timeline Integrity 검증
Visual / Motion 검증
Voice / Subtitle Sync 검증
Editing Readiness 검증
언어별 완성도 검증
Hard Fail 감지
Quality Score 계산
Quality Issues 생성
Auto Fix Plan 생성
Human Review 필요 여부 판단
Quality Report 생성
Workflow Orchestrator에 결과 전달
Learning Engine에 품질 데이터 제공
```

Quality Engine이 하지 않는 것:

```text
Research를 직접 다시 수행하지 않는다.
Story를 직접 다시 작성하지 않는다.
이미지를 직접 생성하지 않는다.
Voice를 직접 생성하지 않는다.
Subtitle을 직접 생성하지 않는다.
Final Video를 직접 렌더링하지 않는다.
Publishing을 직접 수행하지 않는다.
Memory를 직접 확정하지 않는다.
```

Quality Engine은 문제를 감지하고, 수정 방향을 제안하고, Gate 결과를 결정한다.

실제 수정 실행은 Workflow Orchestrator와 해당 Stage Engine이 담당한다.

---

# 5. Inputs

Quality Engine의 입력:

```text
project.json
topic.json
channel_snapshot.json
template_snapshot.json

research/research.json
research/sources.json
research/facts.json
research/risk_notes.json

knowledge/knowledge.json
knowledge/claims.json
knowledge/fact_check.json
knowledge/risk_notes.json

story/outline.json
story/hook.json
story/script_master.json
story/script_master.md
story/story_review.json

direction/scene_plan.json
direction/emotion_plan.json
direction/camera_plan.json
direction/director_notes.md
direction/direction_review.json

timeline/timeline.json
timeline/timeline_review.json
timeline/timeline_lock.json

prompts/midjourney_image_prompts.json
prompts/prompt_review.json
reports/visual_review.json

prompts/midjourney_video_prompts.json
reports/motion_review.json

languages/{lang}/narration.txt
languages/{lang}/voice.json
reports/voice_review.json

languages/{lang}/subtitle.srt
languages/{lang}/subtitle.json
reports/subtitle_review.json

edit/edit_plan.json
edit/render_plan.json
edit/final_timeline.json
reports/editing_review.json
reports/missing_asset_report.json

assets/asset_registry.json
workflow/handoffs/EDITING_to_QUALITY.json
workflow/memory_context_QUALITY.json
```

필수 입력:

```text
project.json
channel_snapshot.json
timeline/timeline.json
timeline/timeline_lock.json
edit/final_timeline.json
edit/render_plan.json
assets/asset_registry.json
reports/editing_review.json
```

Quality Engine은 가능한 한 전체 Stage Report를 읽어야 한다.

Stage Report가 누락되면 Quality Issue로 기록한다.

---

# 6. Outputs

Quality Engine의 출력:

```text
reports/quality_report.json
reports/quality_issues.json
reports/quality_score_breakdown.json
reports/auto_fix_plan.json
reports/human_review_recommendation.json
workflow/stage_results/QUALITY_result.json
workflow/handoffs/QUALITY_to_PACKAGE.json
workflow/handoffs/QUALITY_to_AUTO_FIX.json
```

v1.0 최소 출력:

```text
reports/quality_report.json
reports/quality_issues.json
reports/auto_fix_plan.json
workflow/stage_results/QUALITY_result.json
```

Quality 통과 시:

```text
workflow/handoffs/QUALITY_to_PACKAGE.json
```

Auto Fix 필요 시:

```text
workflow/handoffs/QUALITY_to_AUTO_FIX.json
```

---

# 7. Quality Execution Flow

Quality Engine 실행 흐름:

```text
Load Project Context
↓
Load Quality Inputs
↓
Validate Required Files
↓
Load Stage Reports
↓
Check Hard Fails
↓
Check Factual Accuracy
↓
Check Brand Consistency
↓
Check Story Quality
↓
Check Timeline Integrity
↓
Check Visual Quality
↓
Check Motion Quality
↓
Check Voice Quality
↓
Check Subtitle Quality
↓
Check Editing Readiness
↓
Check Language Completeness
↓
Check Asset Registry Integrity
↓
Calculate Quality Score
↓
Classify Issues
↓
Build Auto Fix Plan
↓
Decide Quality Gate Result
↓
Write quality_report.json
↓
Write quality_issues.json
↓
Write auto_fix_plan.json
↓
Handoff to Package or Auto Fix
```

---

# 8. Quality Gate Results

Quality Gate 결과는 다음 중 하나이다.

```text
PASS
HUMAN_REVIEW_RECOMMENDED
AUTO_FIX_REQUIRED
PARTIAL_REGENERATION_REQUIRED
FAIL
ESCALATION_REQUIRED
```

## PASS

Project가 Package 단계로 넘어갈 수 있다.

조건:

```text
Quality Score 95 이상
Hard Fail 없음
Critical Issue 없음
필수 Asset 누락 없음
```

## HUMAN_REVIEW_RECOMMENDED

통과 가능하지만 사람 검토가 권장된다.

조건:

```text
Quality Score 90~94
Hard Fail 없음
Critical Issue 없음
주요 Issue가 Medium 이하
```

## AUTO_FIX_REQUIRED

부분 수정으로 해결 가능한 문제가 있다.

조건:

```text
Quality Score 80~89
Hard Fail 없음 또는 수정 가능한 Hard Fail
Issue Scope가 명확함
```

## PARTIAL_REGENERATION_REQUIRED

특정 Stage 또는 특정 Scene을 다시 만들어야 한다.

조건:

```text
Quality Score 70~79
특정 Stage 품질이 낮음
특정 Scene 또는 언어 문제가 반복됨
```

## FAIL

현재 Project 상태로는 진행 불가.

조건:

```text
Quality Score 70 미만
Critical Issue 다수
Hard Fail 해결 불가
핵심 구조 오류
```

## ESCALATION_REQUIRED

COO 또는 사용자 판단이 필요하다.

조건:

```text
Full Regeneration 필요
Template Lock 위반
Brand 핵심 충돌
중대한 사실 오류
반복 Auto Fix 실패
```

---

# 9. Quality Score Thresholds

Quality Score 기준:

```text
95~100
PASS

90~94
HUMAN_REVIEW_RECOMMENDED

80~89
AUTO_FIX_REQUIRED

70~79
PARTIAL_REGENERATION_REQUIRED

70 미만
FAIL / ESCALATION_REQUIRED
```

단, Hard Fail은 점수보다 우선한다.

---

# 10. Quality Score Breakdown

기본 Quality Score 구성:

```yaml
quality_score:
  factual_accuracy: 15
  brand_consistency: 10
  story_strength: 10
  retention_potential: 10
  timeline_integrity: 10
  visual_quality: 10
  motion_quality: 5
  voice_quality: 10
  subtitle_quality: 10
  editing_readiness: 10
  asset_integrity: 5
  language_completeness: 5
```

총점은 100점 기준으로 환산한다.

Motion이 선택 사항인 Project에서는 motion_quality 비중을 visual_quality 또는 editing_readiness에 재분배할 수 있다.

---

# 11. quality_report.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "QUALITY",

  "quality_gate": {
    "result": "AUTO_FIX_REQUIRED",
    "score": 87,
    "hard_fail": false,
    "critical_issue_count": 0,
    "human_review_required": false,
    "can_continue_to_package": false
  },

  "score_breakdown": {
    "factual_accuracy": 92,
    "brand_consistency": 94,
    "story_strength": 88,
    "retention_potential": 86,
    "timeline_integrity": 95,
    "visual_quality": 84,
    "motion_quality": 90,
    "voice_quality": 91,
    "subtitle_quality": 89,
    "editing_readiness": 92,
    "asset_integrity": 95,
    "language_completeness": 100
  },

  "summary": {
    "overall": "Project is close to package-ready but requires visual auto-fix for two scenes.",
    "main_strengths": [
      "Strong story hook",
      "Timeline structure is stable",
      "Voice and subtitle are mostly aligned"
    ],
    "main_issues": [
      "SC004 visual is too generic",
      "SC007 image does not match brand visual tone"
    ],
    "recommended_next_action": "Run AUTO_FIX for Visual Stage only."
  },

  "created_at": "2026-07-10T16:00:00",
  "updated_at": "2026-07-10T16:00:00"
}
```

---

# 12. quality_issues.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "issues": [
    {
      "issue_id": "QISSUE-000001",
      "severity": "MEDIUM",
      "category": "VISUAL",
      "stage": "VISUAL",
      "scene_id": "SC004",
      "language": null,

      "title": "Visual prompt produced generic sci-fi image.",
      "description": "SC004 image does not sufficiently reflect the specific scene purpose and brand tone.",

      "evidence": [
        "reports/visual_review.json",
        "assets/asset_registry.json"
      ],

      "blocking": true,
      "hard_fail": false,

      "recommended_action": {
        "type": "AUTO_FIX",
        "target_stage": "VISUAL",
        "target_files": [
          "prompts/midjourney_image_prompts.json",
          "assets/images/SC004_image_v001.png"
        ],
        "instruction": "Revise only SC004 prompt with stronger composition, lighting, and brand visual direction."
      }
    }
  ]
}
```

---

# 13. Quality Issue Severity

Issue Severity는 다음을 사용한다.

```text
LOW
MEDIUM
HIGH
CRITICAL
```

## LOW

Package 진행에 큰 영향은 없지만 개선 가능.

## MEDIUM

품질 저하가 있으며 Auto Fix 권장.

## HIGH

Package 진행 전 수정 필요.

## CRITICAL

Quality Gate를 막는 문제. Escalation 또는 반드시 수정 필요.

---

# 14. Hard Fail Conditions

Hard Fail 조건:

```text
필수 파일 누락
Timeline Scene ID 불일치
Asset Registry 누락
필수 Scene Image 누락
필수 언어 Voice 누락
필수 언어 Subtitle 누락
Forbidden Claim 사용
Unsupported Claim을 사실처럼 표현
Speculative Claim을 확정 사실처럼 표현
Brand 핵심 위반
Subtitle Sync 붕괴
Voice와 Script 의미 불일치
Final Timeline 생성 불가
Package에 필요한 파일 누락
Template Lock 위반
```

Hard Fail이 발생하면 기본적으로 PASS가 불가능하다.

단, 명확한 Auto Fix로 해결 가능한 Hard Fail은 `AUTO_FIX_REQUIRED`로 분류할 수 있다.

---

# 15. Factual Accuracy Check

Quality Engine은 Knowledge와 Story의 Fact Safety를 검사한다.

검사 대상:

```text
knowledge/claims.json
knowledge/fact_check.json
knowledge/risk_notes.json
story/script_master.json
story/script_master.md
languages/{lang}/script.json
languages/{lang}/narration.txt
```

검사 항목:

```text
Forbidden Claim 사용 여부
Unsupported Claim 사용 여부
Speculative Claim Framing 유지 여부
Claim ID 연결 여부
Risk Note 반영 여부
언어별 번역에서 의미 왜곡 여부
```

중대한 사실 오류는 Hard Fail이다.

---

# 16. Brand Consistency Check

Quality Engine은 Brand System 기준으로 전체 결과물을 검사한다.

검사 대상:

```text
story/script_master.md
direction/director_notes.md
prompts/midjourney_image_prompts.json
reports/visual_review.json
languages/{lang}/narration.txt
edit/final_timeline.json
```

검사 항목:

```text
Channel Tone 일치
Visual Identity 일치
Language Style 일치
금지 스타일 회피
Cheap Clickbait 여부
장기 Channel 정체성 훼손 여부
```

Brand 핵심 위반은 Hard Fail 또는 Auto Fix 대상이다.

---

# 17. Story Quality Check

Story 검사 항목:

```text
Hook Strength
First 30 Seconds
Core Question
Retention Flow
Emotional Arc
Voice Readability
Direction Readiness
Factual Safety
```

Story 관련 Hard Fail:

```text
Hook 없음
Core Question 없음
Forbidden Claim 사용
Generic Introduction 사용
Retention Flow 붕괴
```

Story 문제는 보통 Story Stage로 Revision Request를 보낸다.

---

# 18. Timeline Integrity Check

Timeline 검사 항목:

```text
Scene ID 중복 없음
Scene 순서 유효
Timing 구조 유효
Timeline Lock 존재
Visual / Motion / Voice / Subtitle Ref 연결
Language Track 완성도
Final Timeline과 Timeline 일치
```

Timeline 관련 Hard Fail:

```text
Scene ID 불일치
Scene 누락
Timing 겹침
Language Track 누락
Timeline Lock 위반
Final Timeline과 Timeline 불일치
```

---

# 19. Visual Quality Check

Visual 검사 항목:

```text
Scene별 Image 존재
Prompt 품질
Direction 반영
Brand Visual Fit
Generic AI Look 여부
Text / Logo / Watermark 여부
Speculative Visual Safety
Asset Registry 연결
```

Visual 관련 Hard Fail:

```text
필수 Image 누락
Scene ID 불일치
Brand 심각한 위반
Text / Watermark 포함
Speculative Scene을 확정 사실처럼 표현
Asset Registry 누락
```

---

# 20. Motion Quality Check

Motion 검사 항목:

```text
Motion 필요한 Scene 선별 적절성
Source Image 존재
Motion Asset 존재
Motion Distortion 여부
Direction Motion Hint 반영
Editing Readiness
Fallback 적절성
```

Motion 관련 Hard Fail:

```text
required Motion Asset 누락
Source Image 누락
심각한 Motion 왜곡
Scene ID 불일치
Timeline Lock 위반
```

Motion이 선택 사항인 경우, Skip 자체는 Fail이 아니다.

---

# 21. Voice Quality Check

Voice 검사 항목:

```text
언어별 Narration 존재
언어별 Voice Config 존재
언어별 Audio Asset 존재
Brand Voice Tone 일치
Pace 적절성
Timeline Fit
Speculative Claim 표현 유지
Asset Registry 연결
```

Voice 관련 Hard Fail:

```text
필수 언어 Audio 누락
Voice Asset Registry 누락
Script 의미와 Audio 내용 불일치
Brand와 심각한 불일치
Timeline 대비 과도한 길이 차이
```

---

# 22. Subtitle Quality Check

Subtitle 검사 항목:

```text
언어별 SRT 존재
SRT 형식 유효
Timestamp 겹침 없음
Reading Speed 적절성
Line Break 품질
Voice Sync
Speculative Claim 표현 유지
Asset Registry 연결
```

Subtitle 관련 Hard Fail:

```text
필수 언어 Subtitle 누락
SRT 형식 오류
Timestamp 겹침
Voice Sync 심각한 불일치
Reading Speed 과도
Speculative Claim 의미 변경
```

---

# 23. Editing Readiness Check

Editing 검사 항목:

```text
edit_plan.json 존재
render_plan.json 존재
final_timeline.json 존재
Scene Asset Mapping 완성
Language Render Variant 존재
Missing Asset Report blocking=false
Quality Handoff 준비
```

Editing 관련 Hard Fail:

```text
Final Timeline 누락
Render Plan 누락
Missing Asset blocking=true
필수 언어 Render Variant 누락
Asset Mapping 불일치
```

---

# 24. Asset Integrity Check

Asset Integrity 검사 항목:

```text
Asset Registry 존재
Asset ID 중복 없음
Scene ID와 Asset 연결
언어별 Asset 연결
파일 경로 유효
selected asset 명확
Provider Request / Response 연결
```

Asset 관련 Hard Fail:

```text
Asset Registry 누락
필수 Asset 누락
Scene ID와 파일명 불일치
언어 코드 불일치
Provider Result 미등록
```

---

# 25. Language Completeness Check

다국어 Project에서는 언어별 완성도를 검사해야 한다.

검사 대상:

```text
languages/{lang}/script.json
languages/{lang}/narration.txt
languages/{lang}/voice.json
languages/{lang}/subtitle.srt
assets/audio/voice_{lang}_v001.wav
assets/subtitles/subtitle_{lang}_v001.srt
edit/render_plan.json
```

검사 항목:

```text
target_languages 모두 존재
언어별 Voice 존재
언어별 Subtitle 존재
언어별 Render Variant 존재
언어별 Metadata 준비 가능
번역에서 의미 왜곡 없음
```

필수 언어 누락은 Hard Fail이다.

---

# 26. Auto Fix Plan

Quality Engine은 수정 가능한 문제에 대해 Auto Fix Plan을 생성해야 한다.

파일:

```text
reports/auto_fix_plan.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "quality_result": "AUTO_FIX_REQUIRED",

  "auto_fix": {
    "required": true,
    "strategy": "partial_fix",
    "total_issues": 2,
    "estimated_risk": "LOW"
  },

  "fix_tasks": [
    {
      "fix_id": "FIX-000001",
      "issue_id": "QISSUE-000001",
      "target_stage": "VISUAL",
      "target_engine": "VisualEngine",
      "target_scene_id": "SC004",
      "target_files": [
        "prompts/midjourney_image_prompts.json",
        "assets/images/SC004_image_v001.png"
      ],
      "fix_type": "prompt_revision_and_asset_regeneration",
      "instruction": "Revise SC004 prompt to reduce generic sci-fi look and match brand visual tone.",
      "requires_provider": true,
      "requires_human_review": false
    }
  ],

  "retry_policy": {
    "max_retry_per_issue": 3,
    "max_total_retry_per_project": 10,
    "full_regeneration_allowed": false
  }
}
```

---

# 27. Auto Fix Rules

Auto Fix 원칙:

```text
문제 범위를 좁힌다.
해당 Stage만 수정한다.
해당 Scene만 수정한다.
해당 언어만 수정한다.
전체 Project 재생성은 금지한다.
Retry Count를 기록한다.
같은 Issue 3회 실패 시 Escalation한다.
```

Stage별 Auto Fix 예시:

```text
Research Issue
→ Research Risk Note 보강

Knowledge Issue
→ Claim Framing 수정

Story Issue
→ Hook 또는 특정 Section 수정

Direction Issue
→ 특정 Scene Visual Goal 수정

Timeline Issue
→ Timeline Revision Request

Visual Issue
→ 특정 Scene Prompt / Image 수정

Motion Issue
→ 특정 Scene Motion Prompt / Motion Asset 수정

Voice Issue
→ 특정 언어 Narration / Voice 재생성

Subtitle Issue
→ 특정 언어 또는 특정 Caption 수정

Editing Issue
→ Asset Mapping / Fallback / Render Plan 수정
```

---

# 28. Human Review Recommendation

Quality Engine은 Human Review가 필요한 경우 별도 Report를 생성한다.

파일:

```text
reports/human_review_recommendation.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "recommended": true,
  "required": false,

  "reason": [
    "Quality score is between 90 and 94.",
    "Speculative future claims require careful final review."
  ],

  "review_focus": [
    "Opening hook factual framing",
    "English narration naturalness",
    "Subtitle sync in final render"
  ],

  "suggested_decision_options": [
    "approve",
    "request_minor_revision",
    "send_to_auto_fix",
    "escalate"
  ]
}
```

Human Review가 필요한 경우:

```text
Quality Score 90~94
Speculative Risk가 중간 이상
Brand 핵심 장면
Full Auto Publish 전환 전
Critical Issue는 없지만 판단이 애매함
```

---

# 29. Quality Handoff to Package

Quality 통과 시 Package Engine 또는 Publishing Engine에 Handoff를 생성한다.

파일:

```text
workflow/handoffs/QUALITY_to_PACKAGE.json
```

예시:

```json
{
  "from_stage": "QUALITY",
  "to_stage": "PACKAGE",
  "project_id": "20260710-093500-future-million-year-human",

  "quality_gate": {
    "result": "PASS",
    "score": 96,
    "hard_fail": false
  },

  "approved_inputs": [
    "edit/render_plan.json",
    "edit/final_timeline.json",
    "assets/asset_registry.json",
    "reports/quality_report.json"
  ],

  "package_notes": [
    "Project is ready for upload package generation.",
    "Use render variants from render_plan.json."
  ]
}
```

---

# 30. Quality Handoff to Auto Fix

Quality가 Auto Fix를 요구하면 Workflow Orchestrator에 Handoff를 생성한다.

파일:

```text
workflow/handoffs/QUALITY_to_AUTO_FIX.json
```

예시:

```json
{
  "from_stage": "QUALITY",
  "to_stage": "AUTO_FIX",
  "project_id": "20260710-093500-future-million-year-human",

  "quality_gate": {
    "result": "AUTO_FIX_REQUIRED",
    "score": 87
  },

  "auto_fix_plan_ref": "reports/auto_fix_plan.json",

  "target_stages": [
    "VISUAL"
  ],

  "instructions": [
    "Run Visual Engine partial fix for SC004 and SC007.",
    "After fix, return to QUALITY stage for recheck."
  ]
}
```

---

# 31. Recheck Rules

Auto Fix 이후 Quality Engine은 반드시 재검사해야 한다.

Recheck 흐름:

```text
Auto Fix Completed
↓
Updated Files Registered
↓
Quality Engine Recheck
↓
Compare Previous Issues
↓
Update quality_report.json
↓
Decide PASS / Additional Fix / Escalation
```

Recheck 시 확인:

```text
이전 Issue 해결 여부
새 Issue 발생 여부
Retry Count
Quality Score 변화
Hard Fail 제거 여부
```

같은 Issue가 3회 이상 반복되면 Escalation한다.

---

# 32. Quality Memory Integration

Quality Engine은 반복 품질 문제를 Memory Candidate로 만들 수 있다.

Memory Candidate 예시:

```text
특정 Channel에서 반복되는 Brand Visual Mismatch
특정 Template에서 반복되는 Timeline Issue
Typecast Voice가 영어에서 자주 길어지는 문제
Midjourney Prompt에서 반복되는 Generic AI Look
Subtitle Sync가 특정 언어에서 자주 실패
```

Memory Update Candidate 예시:

```json
{
  "target_memory": "quality_memory",
  "scope": "CHANNEL",
  "channel_id": "future",
  "type": "failure_pattern",
  "summary": "Future channel visual prompts become generic when scene composition is not specific enough.",
  "evidence": [
    "reports/quality_report.json",
    "reports/visual_review.json"
  ],
  "confidence": "MEDIUM"
}
```

Quality Engine은 Memory를 직접 확정하지 않는다.

Memory Engine 또는 Learning Engine에 Candidate를 전달한다.

---

# 33. Quality Report for Learning

Learning Engine은 Quality Report를 주요 입력으로 사용한다.

Quality Engine은 Learning이 사용할 수 있도록 다음을 남겨야 한다.

```text
최종 Quality Score
Stage별 Score
반복 Issue
Hard Fail 여부
Auto Fix 성공 여부
Auto Fix 횟수
Human Review 필요 여부
Project가 Package로 갈 수 있었는지
```

---

# 34. Quality Validation Rules

Quality Validator는 다음을 확인해야 한다.

```text
reports/quality_report.json 존재
reports/quality_issues.json 존재
reports/auto_fix_plan.json 존재
project_id 일치
channel_id 일치
quality_gate.result 존재
quality_gate.score 존재
score_breakdown 존재
issues 배열 존재
Hard Fail 조건 확인
Auto Fix 필요 시 fix_tasks 존재
PASS일 경우 can_continue_to_package=true
FAIL일 경우 recommended_next_action 존재
```

Quality Report 자체가 유효하지 않으면 Project는 Package로 갈 수 없다.

---

# 35. Error Types

Quality Engine의 Error Type:

```text
QualityInputMissingError
QualityReportCreationError
QualityValidationError
QualityScoreCalculationError
HardFailDetectedError
FactualAccuracyError
BrandConsistencyError
StoryQualityError
TimelineIntegrityError
VisualQualityError
MotionQualityError
VoiceQualityError
SubtitleQualityError
EditingReadinessError
AssetIntegrityError
LanguageCompletenessError
AutoFixPlanError
HumanReviewRecommendationError
QualityHandoffError
```

Error 예시:

```json
{
  "error_type": "HardFailDetectedError",
  "message": "Required English subtitle asset is missing.",
  "project_id": "20260710-093500-future-million-year-human",
  "stage": "QUALITY",
  "severity": "CRITICAL",
  "suggested_fix": "Return to SUBTITLE stage and generate/register English subtitle asset.",
  "created_at": "2026-07-10T16:00:00"
}
```

---

# 36. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
QualityEngine
QualityInputLoader
QualityInputValidator
QualityScoreCalculator
HardFailDetector
FactualAccuracyChecker
BrandConsistencyChecker
StoryQualityChecker
TimelineIntegrityChecker
VisualQualityChecker
MotionQualityChecker
VoiceQualityChecker
SubtitleQualityChecker
EditingReadinessChecker
AssetIntegrityChecker
LanguageCompletenessChecker
QualityIssueBuilder
AutoFixPlanBuilder
HumanReviewRecommendationBuilder
QualityReportBuilder
QualityValidator
QualityHandoffBuilder
QualityMemoryCandidateBuilder
QualityErrorReporter
```

---

# 37. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/26_QUALITY_ENGINE.md
→ engines/quality/
```

예시 구조:

```text
engines/
└── quality/
    ├── quality_engine.py
    ├── quality_input_loader.py
    ├── quality_input_validator.py
    ├── quality_score_calculator.py
    ├── hard_fail_detector.py
    ├── factual_accuracy_checker.py
    ├── brand_consistency_checker.py
    ├── story_quality_checker.py
    ├── timeline_integrity_checker.py
    ├── visual_quality_checker.py
    ├── motion_quality_checker.py
    ├── voice_quality_checker.py
    ├── subtitle_quality_checker.py
    ├── editing_readiness_checker.py
    ├── asset_integrity_checker.py
    ├── language_completeness_checker.py
    ├── quality_issue_builder.py
    ├── auto_fix_plan_builder.py
    ├── human_review_recommendation_builder.py
    ├── quality_report_builder.py
    ├── quality_validator.py
    ├── quality_handoff_builder.py
    ├── quality_memory_candidate_builder.py
    └── quality_error_reporter.py
```

---

# 38. Main Public Operations

Quality Engine은 최소 다음 작업을 제공해야 한다.

```text
run_quality(project_id)
load_quality_inputs(project_id)
validate_quality_inputs(project_id)
detect_hard_fails(project_id)
check_factual_accuracy(project_id)
check_brand_consistency(project_id)
check_story_quality(project_id)
check_timeline_integrity(project_id)
check_visual_quality(project_id)
check_motion_quality(project_id)
check_voice_quality(project_id)
check_subtitle_quality(project_id)
check_editing_readiness(project_id)
check_asset_integrity(project_id)
check_language_completeness(project_id)
calculate_quality_score(project_id)
build_quality_issues(project_id)
build_auto_fix_plan(project_id)
build_human_review_recommendation(project_id)
build_quality_report(project_id)
validate_quality_report(project_id)
build_handoff_to_package(project_id)
build_handoff_to_auto_fix(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
입력 검증
Hard Fail 우선 감지
Stage별 Report 확인
Asset Registry 기준 사용
Timeline Lock 준수
Quality Gate 결과 명확화
Auto Fix 가능 범위 명시
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 39. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Quality Input 로드
필수 파일 존재 검증
Hard Fail 기본 감지
Factual Accuracy 기본 검사
Brand Consistency 기본 검사
Timeline Integrity 기본 검사
Asset Registry Integrity 검사
Visual / Voice / Subtitle / Editing Report 검사
Language Completeness 검사
Quality Score 계산
quality_report.json 생성
quality_issues.json 생성
auto_fix_plan.json 생성
PASS / AUTO_FIX / FAIL 결과 분기
Workflow Handoff 생성
Quality Validation 수행
```

v1.0에서 하지 않아도 되는 것:

```text
완전 자동 영상 시청 기반 품질 평가
고급 컴퓨터 비전 기반 이미지 품질 분석
음성 감정 고급 분석
정밀 음소 단위 자막 Sync 검증
실시간 품질 대시보드
사람 수준의 최종 창작 판단 완전 대체
자동 Publishing 결정
```

v1.0에서는 파일, 구조, 규칙, Stage Report 기반의 안정적인 Quality Gate를 만드는 것이 우선이다.

---

# 40. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Quality 입력 파일을 로드할 수 있다.
필수 파일 누락을 감지할 수 있다.
Hard Fail을 감지할 수 있다.
Stage별 Report를 읽고 종합할 수 있다.
Factual Accuracy를 기본 검사할 수 있다.
Brand Consistency를 기본 검사할 수 있다.
Timeline Integrity를 검사할 수 있다.
Asset Registry Integrity를 검사할 수 있다.
언어별 완성도를 검사할 수 있다.
Visual / Motion / Voice / Subtitle / Editing 품질을 종합할 수 있다.
Quality Score를 계산할 수 있다.
quality_report.json을 생성할 수 있다.
quality_issues.json을 생성할 수 있다.
auto_fix_plan.json을 생성할 수 있다.
Quality Gate 결과를 PASS / AUTO_FIX / FAIL 등으로 분류할 수 있다.
Package 또는 Auto Fix로 Handoff를 만들 수 있다.
Quality Validation 실패 시 Package Stage 진행을 막을 수 있다.
```

---

# 41. Non Goals

v1.0에서 Quality Engine이 하지 않는 것:

```text
콘텐츠 직접 수정
Research 직접 재수행
Story 직접 재작성
Image 직접 생성
Voice 직접 생성
Subtitle 직접 생성
Final Video 직접 렌더링
Publishing 직접 수행
Memory 직접 확정
CEO 승인 없는 Full Regeneration
```

v1.0에서는 Project가 Package 단계로 갈 수 있는지 판단하는 품질 게이트와 Auto Fix 계획을 만드는 것이 핵심이다.

---

# 42. Critical Quality Rules

반드시 지켜야 할 규칙:

```text
1. Quality Engine은 Package 전 반드시 실행되어야 한다.

2. Quality Report 없이 Package로 넘어가지 않는다.

3. Hard Fail은 전체 점수보다 우선한다.

4. 필수 Asset 누락은 통과할 수 없다.

5. Timeline Integrity 문제는 통과할 수 없다.

6. Forbidden Claim 사용은 통과할 수 없다.

7. Speculative Claim을 사실처럼 표현하면 통과할 수 없다.

8. Brand 핵심 위반은 통과할 수 없다.

9. Voice / Subtitle 필수 언어 누락은 통과할 수 없다.

10. Auto Fix는 부분 수정이 우선이다.

11. 같은 Issue 3회 실패 시 Escalation한다.

12. Full Regeneration은 COO 승인 없이는 수행하지 않는다.

13. Quality Engine은 직접 콘텐츠를 수정하지 않는다.

14. Quality Engine은 Provider를 직접 호출하지 않는다.

15. Quality 결과는 Learning과 Memory에 사용될 수 있어야 한다.
```

---

# 43. Final Principle

Quality Engine은 ADOS의 마지막 방어선이다.

좋은 Quality Engine은 점수만 계산하지 않는다.

좋은 Quality Engine은 무엇이 통과 가능한지,

무엇을 고쳐야 하는지,

무엇이 위험한지,

어디로 되돌려야 하는지,

언제 멈춰야 하는지를 판단한다.

Quality Engine의 목적은 완벽주의가 아니다.

Quality Engine의 목적은 CHUNG COMPANY의 영상이 반복적으로 일정 수준 이상의 품질을 유지하고, 실패를 학습으로 바꾸고, 다음 Project를 더 좋게 만드는 것이다.
