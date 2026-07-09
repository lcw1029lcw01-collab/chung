# 07_PROJECT_SPEC.md

Version: 1.2.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Project Specification  

---

# 1. Purpose

이 문서는 CHUNG COMPANY / ADOS에서 하나의 영상 제작 단위인 Project의 구조를 정의한다.

Project는 단순한 영상 파일이 아니다.

Project는 하나의 유튜브 영상을 만들기 위해 필요한 모든 정보, 파일, 상태, 작업 기록, 품질 검사, 언어별 결과물, 학습 결과를 담는 작업 단위이다.

이 문서는 다음을 정의한다.

```text
Project란 무엇인가
Project가 어디에서 생성되는가
Project 폴더 구조는 어떻게 구성되는가
Project 상태는 어떻게 변경되는가
Project에 필요한 필수 파일은 무엇인가
Timeline과 Asset은 어떻게 연결되는가
언어별 결과물은 어떻게 관리되는가
Quality Gate는 어떻게 적용되는가
Auto Fix는 어떻게 적용되는가
Project 완료 기준은 무엇인가
Claude Code가 어떤 구조로 구현해야 하는가
```

이 문서는 다음 문서들과 직접 연결된다.

```text
03_ARCHITECTURE.md
04_AI_ORGANIZATION.md
05_INTER_AI_COMMUNICATION.md
06_AI_THINKING_FRAMEWORK.md
08_TEMPLATE_SYSTEM.md
09_CHANNEL_ENGINE.md
12_PROJECT_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
16_TIMELINE_ENGINE.md
26_QUALITY_ENGINE.md
28_PUBLISHING_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Project는 Channel 아래에서 생성되는 영상 제작 단위이다.

전체 구조는 다음 순서를 따른다.

```text
Company
↓
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
Analytics
↓
Learning
↓
Template Improvement
```

중요 규칙:

```text
Template 없이 Channel을 만들지 않는다.
Channel 없이 Project를 만들지 않는다.
Project 없이 Production Engine을 실행하지 않는다.
Timeline 없이 Asset을 최종 연결하지 않는다.
Quality Gate 없이 Package를 만들지 않는다.
Learning 없이 Project를 Complete 처리하지 않는다.
```

---

# 3. Project Philosophy

## 3.1 Project Is Not Just a Video

Project는 `final_video.mp4` 하나가 아니다.

Project는 다음을 포함한다.

```text
Topic
Research
Knowledge
Story
Direction
Timeline
Visual Prompt
Motion Prompt
Voice Script
Subtitle
Editing Plan
Assets
Quality Report
Upload Package
Analytics Report
Learning Report
Logs
Snapshots
```

## 3.2 Timeline First

영상 제작의 중심은 최종 영상 파일이 아니라 `timeline.json`이다.

Timeline은 다음을 연결한다.

```text
Scene
Narration
Subtitle
Image
Motion
Audio
Transition
Timing
Quality Check
```

## 3.3 One Project, Multiple Languages

하나의 Project는 여러 언어 버전을 만들 수 있다.

공유되는 것:

```text
Story Structure
Scene Plan
Timeline Base
Images
Motion Clips
Thumbnail Base
```

언어별로 분리되는 것:

```text
Script Localization
Voice
Subtitle
Title
Description
Tags
SEO
Pinned Comment
Final Video
```

## 3.4 Snapshot for Reproducibility

Project는 생성 시점의 Channel과 Template을 Snapshot으로 저장해야 한다.

이유:

```text
나중에 Channel 설정이 바뀌어도 해당 Project를 재현할 수 있어야 한다.
Template이 업데이트되어도 당시 제작 기준을 확인할 수 있어야 한다.
Quality 문제 발생 시 원인을 추적할 수 있어야 한다.
Learning 시 어떤 설정이 성과에 영향을 주었는지 분석할 수 있어야 한다.
```

## 3.5 Partial Regeneration First

문제가 발생하면 전체 Project를 다시 만들지 않는다.

문제가 있는 Stage, Scene, Language, Asset만 수정한다.

---

# 4. Project Lifecycle

Project 상태는 다음 순서를 따른다.

```text
NEW
↓
INITIALIZED
↓
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
AUTO_FIX
↓
PACKAGE
↓
READY
↓
PUBLISHED
↓
ANALYTICS
↓
LEARNING
↓
COMPLETE
```

---

# 5. Project Status Meaning

## NEW

Project 생성 요청이 만들어졌지만 아직 폴더와 기본 파일이 생성되지 않은 상태.

## INITIALIZED

Project 폴더, `project.json`, `topic.json`, `channel_snapshot.json`, `template_snapshot.json`이 생성된 상태.

## RESEARCH

주제에 대한 정보 수집 단계.

## KNOWLEDGE

Research 결과를 영상 제작용 지식과 Claim으로 정리하는 단계.

## STORY

대본, Hook, Outline, Master Script를 만드는 단계.

## DIRECTION

대본을 Scene, Emotion, Camera, Visual Direction으로 변환하는 단계.

## TIMELINE

Scene과 시간 구조, Asset Mapping을 만드는 단계.

## VISUAL

이미지 프롬프트와 이미지 자산을 만드는 단계.

## MOTION

필요한 Scene에 Motion Prompt와 Motion Asset을 만드는 단계.

## VOICE

언어별 나레이션 스크립트와 음성 파일을 만드는 단계.

## SUBTITLE

언어별 자막 파일을 만드는 단계.

## EDITING

Timeline 기준으로 최종 편집 구조와 영상 파일을 만드는 단계.

## QUALITY

Project 전체 품질을 검사하는 단계.

## AUTO_FIX

Quality 문제를 부분 수정하는 단계.

## PACKAGE

업로드 가능한 패키지를 만드는 단계.

## READY

업로드 준비가 완료된 상태.

## PUBLISHED

사용자 또는 시스템이 실제 업로드 완료를 기록한 상태.

## ANALYTICS

성과 데이터를 수집하고 분석하는 단계.

## LEARNING

성과와 실패를 학습하는 단계.

## COMPLETE

Project가 학습까지 완료된 상태.

---

# 6. Project Creation Input

사용자가 직접 Topic을 입력하는 경우:

```yaml
create_project:
  channel_id: future
  topic_source: user
  topic: "100만 년 후 인간은 어떤 모습일까?"
  target_languages:
    - ko
    - en
  publish_mode: human_review
```

AI 추천 Topic을 사용하는 경우:

```yaml
create_project:
  channel_id: future
  topic_source: ai
  topic_id: recommended_topic_001
  target_languages:
    - ko
    - en
  publish_mode: human_review
```

필수 입력:

```text
channel_id
topic_source
topic 또는 topic_id
target_languages
publish_mode
```

---

# 7. Project ID Rule

Project ID 형식:

```text
YYYYMMDD-HHMMSS-{channel_id}-{topic_slug}
```

예시:

```text
20260710-093500-future-million-year-human
```

규칙:

```text
소문자 사용
공백 금지
특수문자 금지
한글 Topic은 영어 slug로 변환
너무 긴 Topic은 5~8단어로 축약
동일 시간에 생성된 Project가 있으면 suffix 추가
```

예시:

```text
20260710-093500-future-million-year-human
20260710-093500-future-million-year-human-02
```

---

# 8. Project Directory Structure

Project는 다음 위치에 생성된다.

```text
projects/{channel_id}/{year}/{month}/{project_id}/
```

전체 구조:

```text
projects/
└── {channel_id}/
    └── {year}/
        └── {month}/
            └── {project_id}/
                ├── project.json
                ├── topic.json
                ├── channel_snapshot.json
                ├── template_snapshot.json
                │
                ├── research/
                │   ├── research.json
                │   ├── sources.json
                │   ├── facts.json
                │   ├── competitors.json
                │   └── trend.json
                │
                ├── knowledge/
                │   ├── knowledge.json
                │   ├── claims.json
                │   ├── fact_check.json
                │   └── risk_notes.json
                │
                ├── story/
                │   ├── outline.json
                │   ├── hook.json
                │   ├── script_master.json
                │   ├── script_master.md
                │   └── story_review.json
                │
                ├── direction/
                │   ├── scene_plan.json
                │   ├── emotion_plan.json
                │   ├── camera_plan.json
                │   └── director_notes.md
                │
                ├── timeline/
                │   ├── timeline.json
                │   ├── timeline_review.json
                │   └── timeline_lock.json
                │
                ├── languages/
                │   ├── ko/
                │   │   ├── script.json
                │   │   ├── narration.txt
                │   │   ├── voice.json
                │   │   ├── subtitle.srt
                │   │   └── metadata.json
                │   │
                │   └── en/
                │       ├── script.json
                │       ├── narration.txt
                │       ├── voice.json
                │       ├── subtitle.srt
                │       └── metadata.json
                │
                ├── prompts/
                │   ├── midjourney_image_prompts.json
                │   ├── midjourney_video_prompts.json
                │   ├── thumbnail_prompt.json
                │   └── prompt_review.json
                │
                ├── assets/
                │   ├── images/
                │   ├── motion/
                │   ├── audio/
                │   ├── subtitles/
                │   ├── thumbnails/
                │   └── temp/
                │
                ├── edit/
                │   ├── edit_plan.json
                │   ├── render_plan.json
                │   └── final_timeline.json
                │
                ├── package/
                │   ├── final_video_ko.mp4
                │   ├── final_video_en.mp4
                │   ├── thumbnail.png
                │   ├── upload_package.json
                │   ├── metadata_ko.json
                │   └── metadata_en.json
                │
                ├── reports/
                │   ├── quality_report.json
                │   ├── auto_fix_report.json
                │   ├── growth_prediction.json
                │   ├── analytics_report.json
                │   ├── learning_report.json
                │   └── final_report.json
                │
                ├── snapshots/
                │
                └── logs/
                    ├── communication.jsonl
                    ├── decision_records.jsonl
                    ├── self_reviews.jsonl
                    ├── risk_register.jsonl
                    ├── error_log.jsonl
                    ├── meeting_log.jsonl
                    └── project.log
```

---

# 9. project.json Schema

`project.json`은 Project의 중심 상태 파일이다.

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "project_name": "100만 년 후 인간은 어떤 모습일까?",
  "version": "1.0.0",

  "status": "INITIALIZED",
  "current_stage": "RESEARCH",

  "created_at": "2026-07-10T09:35:00",
  "updated_at": "2026-07-10T09:35:00",

  "company": {
    "name": "CHUNG COMPANY",
    "system": "ADOS"
  },

  "channel": {
    "channel_id": "future",
    "channel_name": "Beyond Humanity",
    "template_id": "future",
    "template_version": "1.0.0"
  },

  "topic": {
    "topic_id": "million-year-human",
    "topic_source": "USER",
    "title": "100만 년 후 인간은 어떤 모습일까?",
    "category": "future",
    "keywords": [
      "future",
      "human evolution",
      "AI",
      "space civilization"
    ]
  },

  "languages": {
    "master_language": "ko",
    "target_languages": [
      "ko",
      "en"
    ],
    "visual_shared": true,
    "motion_shared": true,
    "voice_per_language": true,
    "subtitle_per_language": true,
    "metadata_per_language": true
  },

  "duration": {
    "strategy": "retention_optimized",
    "target_minutes": null,
    "min_minutes": 12,
    "max_minutes": 35,
    "estimated_minutes": null
  },

  "providers": {
    "visual": "midjourney",
    "motion": "midjourney_video",
    "voice": "typecast",
    "subtitle": "internal",
    "editing": "internal"
  },

  "automation": {
    "mode": "human_review",
    "allow_auto_publish_after_trust": false,
    "partial_regeneration": true,
    "max_retry_per_issue": 3,
    "max_total_retry_per_project": 10
  },

  "quality": {
    "pass_score": 95,
    "current_score": null,
    "quality_status": "NOT_REVIEWED",
    "hard_fail": false
  },

  "organization": {
    "coo": "coo_employee",
    "portfolio_manager": "portfolio_manager",
    "channel_manager": "channel_manager",
    "project_manager": "project_manager",
    "current_owner_department": "Research Department",
    "current_owner_employee": null
  },

  "communication": {
    "message_log": "logs/communication.jsonl",
    "open_messages": [],
    "open_escalations": []
  },

  "thinking": {
    "decision_records_path": "logs/decision_records.jsonl",
    "self_reviews_path": "logs/self_reviews.jsonl",
    "risk_register_path": "logs/risk_register.jsonl"
  }
}
```

---

# 10. topic.json Schema

```json
{
  "topic_id": "million-year-human",
  "source": "USER",
  "title": "100만 년 후 인간은 어떤 모습일까?",
  "slug": "million-year-human",
  "category": "future",
  "description": "A documentary-style future video exploring possible human evolution over one million years.",
  "keywords": [
    "future",
    "human evolution",
    "AI",
    "space",
    "civilization"
  ],
  "target_audience": [
    "science curious audience",
    "future technology audience",
    "AI and civilization audience"
  ],
  "topic_score": null,
  "growth_notes": [],
  "risk_notes": [
    "Future predictions must be framed as possibilities, not certainties."
  ]
}
```

---

# 11. Snapshot Files

Project 생성 시 반드시 저장한다.

```text
channel_snapshot.json
template_snapshot.json
```

Snapshot 목적:

```text
Project 재현성 확보
나중에 Channel 설정 변경과 분리
Template 버전 변경 영향 분리
Quality 문제 원인 추적
Learning 분석 가능
```

Snapshot 규칙:

```text
Project 생성 후 임의 수정하지 않는다.
수정이 필요하면 새 Snapshot을 snapshots/에 저장한다.
원본 Snapshot은 보존한다.
```

---

# 12. Stage Output Requirements

각 Stage는 최소 Output을 생성해야 한다.

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
package/final_video_{lang}.mp4
```

## QUALITY

```text
reports/quality_report.json
reports/auto_fix_report.json
```

## PACKAGE

```text
package/upload_package.json
package/metadata_ko.json
package/metadata_en.json
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

# 13. Timeline Specification

`timeline/timeline.json`은 Project의 핵심 파일이다.

기본 구조:

```json
{
  "timeline_id": "TL001",
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "version": "1.0.0",

  "video": {
    "aspect_ratio": "16:9",
    "fps": 30,
    "estimated_total_duration_seconds": null
  },

  "languages": {
    "base_language": "ko",
    "target_languages": [
      "ko",
      "en"
    ]
  },

  "scenes": [
    {
      "scene_id": "SC001",
      "order": 1,
      "start_time": "00:00:00",
      "end_time": "00:00:05",
      "duration_seconds": 5,

      "purpose": "hook",
      "emotion": "mystery",
      "importance": "critical",

      "story": {
        "script_ref": "story/script_master.json",
        "summary": "Opening future scenario."
      },

      "visual": {
        "image_required": true,
        "image_asset": null,
        "prompt_ref": "prompts/midjourney_image_prompts.json"
      },

      "motion": {
        "motion_required": true,
        "motion_provider": "midjourney_video",
        "motion_duration_seconds": 5,
        "motion_asset": null
      },

      "voice": {
        "narration_required": true,
        "language_tracks": [
          "ko",
          "en"
        ]
      },

      "subtitle": {
        "subtitle_required": true
      },

      "quality": {
        "scene_score": null,
        "requires_review": true,
        "hard_fail": false
      }
    }
  ]
}
```

Timeline 규칙:

```text
Scene ID는 SC001 형식을 사용한다.
Scene ID는 Project 안에서 변경하지 않는다.
모든 Scene은 order를 가진다.
모든 Scene은 purpose를 가진다.
모든 Scene은 visual, voice, subtitle 연결 정보를 가진다.
Motion은 필요한 Scene에만 적용한다.
Timeline은 언어별 Voice 길이 차이를 고려해야 한다.
```

---

# 14. Asset Naming Rules

Asset 파일명은 Scene ID를 기준으로 한다.

이미지:

```text
SC001_image_v001.png
SC001_image_v002.png
```

Motion:

```text
SC001_motion_v001.mp4
SC001_motion_v002.mp4
```

Voice:

```text
SC001_voice_ko_v001.wav
SC001_voice_en_v001.wav
```

Subtitle:

```text
subtitle_ko_v001.srt
subtitle_en_v001.srt
```

Final Video:

```text
final_video_ko.mp4
final_video_en.mp4
```

Thumbnail:

```text
thumbnail.png
thumbnail_v001.png
thumbnail_v002.png
```

규칙:

```text
공백 사용 금지
한글 파일명 사용 금지
Scene ID 포함
version 포함
언어별 파일은 language code 포함
```

---

# 15. Language Structure

언어별 결과물은 `languages/{lang}/`에 저장한다.

예시:

```text
languages/ko/
languages/en/
```

각 언어 폴더에는 다음 파일을 둘 수 있다.

```text
script.json
narration.txt
voice.json
subtitle.srt
metadata.json
```

언어 규칙:

```text
Master Story는 공유 가능하다.
언어별 Script는 자연스럽게 Localize한다.
직역하지 않는다.
Voice 길이 차이를 Timeline에 반영한다.
SEO Metadata는 언어별로 최적화한다.
```

---

# 16. Quality Gate Rules

품질 기준:

```text
95~100
통과

90~94
사람 확인 권장

80~89
Auto Fix

70~79
Partial Regeneration

70 미만
Fail / Escalation
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
Quality Report 누락
Upload Package 누락
```

Project는 Quality Gate를 통과하지 못하면 READY 상태가 될 수 없다.

---

# 17. Auto Fix Rules

Auto Fix는 부분 수정이 기본이다.

흐름:

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

예시:

```text
Scene 7 이미지 문제
→ Scene 7 Prompt 수정
→ Scene 7 Image 재생성
→ Visual Review
→ Quality Recheck
```

```text
영어 Voice 길이 문제
→ English narration 수정
→ English voice 재생성
→ Timeline Recheck
```

전체 재생성은 COO 승인 없이는 수행하지 않는다.

---

# 18. Retry Policy

```yaml
retry_policy:
  max_retry_per_issue: 3
  max_total_retry_per_project: 10
  prefer_partial_regeneration: true
  full_regeneration_allowed: false
  full_regeneration_requires_coo_approval: true
```

같은 문제가 3회 이상 반복되면 Escalation한다.

---

# 19. Logs

Project는 다음 로그를 가진다.

```text
logs/communication.jsonl
logs/decision_records.jsonl
logs/self_reviews.jsonl
logs/risk_register.jsonl
logs/error_log.jsonl
logs/meeting_log.jsonl
logs/project.log
```

로그 대상:

```text
Project 생성
Stage 시작
Stage 완료
Stage 실패
Message 생성
Review 결과
Approval 결과
Decision Record
Self Review
Risk
Error
Auto Fix
Escalation
Quality Gate
Package 생성
Learning 완료
```

---

# 20. Snapshots

Project는 중요한 시점마다 Snapshot을 만들 수 있다.

권장 Snapshot 시점:

```text
INITIALIZED
STORY_COMPLETE
TIMELINE_COMPLETE
VISUAL_COMPLETE
VOICE_COMPLETE
QUALITY_COMPLETE
PACKAGE_COMPLETE
```

저장 위치:

```text
snapshots/
```

Snapshot 예시:

```text
snapshots/INITIALIZED_20260710_093500/
snapshots/TIMELINE_COMPLETE_20260710_120000/
snapshots/QUALITY_COMPLETE_20260710_150000/
```

Snapshot 목적:

```text
복구
비교
디버깅
Learning
재현성
```

---

# 21. Lock Rules

Project 안에서 일부 파일은 특정 Stage 이후 Lock될 수 있다.

Lock 대상 예시:

```text
channel_snapshot.json
template_snapshot.json
timeline/timeline_lock.json
approved story files
approved timeline files
```

Lock 규칙:

```text
Locked File은 직접 수정하지 않는다.
수정이 필요하면 Revision Request를 생성한다.
수정 전 Snapshot을 만든다.
수정 후 Review를 다시 수행한다.
```

---

# 22. Validation Rules

Project Validator는 다음을 확인해야 한다.

```text
project.json 존재
topic.json 존재
channel_snapshot.json 존재
template_snapshot.json 존재
Project ID 형식 유효
Channel ID 유효
Target Languages 유효
Current Stage 유효
필수 폴더 존재
Stage별 필수 Output 존재
Timeline Scene ID 일관성
Asset Naming 규칙 준수
Quality Report 존재
Open Critical Message 없음
Open Escalation 없음
```

검증 실패 시 다음 Stage로 이동할 수 없다.

---

# 23. State Transition Rules

Project 상태 전환은 Workflow Orchestrator와 Project Manager가 관리한다.

허용 예시:

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

금지 예시:

```text
NEW → STORY
RESEARCH → VISUAL
TIMELINE → PACKAGE
QUALITY → COMPLETE
```

---

# 24. Organization Integration

Project는 AI Organization과 연결된다.

`project.json`에는 현재 Owner 정보가 있어야 한다.

```json
{
  "organization": {
    "coo": "coo_employee",
    "portfolio_manager": "portfolio_manager",
    "channel_manager": "channel_manager",
    "project_manager": "project_manager",
    "current_owner_department": "Story Department",
    "current_owner_employee": "story_writer"
  }
}
```

Stage별 Owner는 `04_AI_ORGANIZATION.md`의 Stage Ownership Matrix를 따른다.

---

# 25. Communication Integration

Project는 Communication Log를 가져야 한다.

필수 조건:

```text
Stage 시작 시 TASK_REQUEST 생성
Stage 완료 시 TASK_RESULT 생성
중요 Output은 REVIEW_REQUEST 생성
Stage 전환 전 APPROVAL_RESULT 필요
Department 변경 시 HANDOFF 생성
오류 발생 시 ERROR_REPORT 생성
Critical Issue 발생 시 ESCALATION 생성
```

Project는 Open Critical Message가 있으면 다음 Stage로 넘어갈 수 없다.

---

# 26. Thinking Integration

Project는 Thinking Record를 가져야 한다.

필수 기록:

```text
Decision Record
Self Review
Risk Register
Handoff Summary
Learning Candidate
```

저장 위치:

```text
logs/decision_records.jsonl
logs/self_reviews.jsonl
logs/risk_register.jsonl
logs/handoff.log
```

---

# 27. Package Specification

Package는 업로드 준비 결과물이다.

필수 파일:

```text
package/upload_package.json
package/metadata_ko.json
package/metadata_en.json
package/thumbnail.png
```

언어별 Final Video가 생성된 경우:

```text
package/final_video_ko.mp4
package/final_video_en.mp4
```

`upload_package.json` 예시:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "status": "READY",
  "languages": [
    "ko",
    "en"
  ],
  "files": {
    "thumbnail": "package/thumbnail.png",
    "ko": {
      "video": "package/final_video_ko.mp4",
      "metadata": "package/metadata_ko.json",
      "subtitle": "languages/ko/subtitle.srt"
    },
    "en": {
      "video": "package/final_video_en.mp4",
      "metadata": "package/metadata_en.json",
      "subtitle": "languages/en/subtitle.srt"
    }
  },
  "quality": {
    "score": 96,
    "status": "PASS"
  },
  "publish_mode": "human_review",
  "auto_publish_allowed": false
}
```

---

# 28. Project Completion Rules

Project가 COMPLETE가 되기 위한 조건:

```text
PUBLISHED 상태 기록 완료
Analytics Report 생성
Learning Report 생성
Memory Update 완료 또는 Update Candidate 생성
Open Critical Message 없음
Open Escalation 없음
Final Report 생성
```

v1.0에서 실제 YouTube 업로드가 자동화되지 않은 경우, 사용자가 수동 업로드 후 PUBLISHED 상태를 기록할 수 있다.

---

# 29. Error Types

Project 관련 Error Type:

```text
ProjectAlreadyExistsError
InvalidProjectRequestError
MissingProjectFileError
InvalidProjectStatusError
InvalidStateTransitionError
MissingChannelSnapshotError
MissingTemplateSnapshotError
TimelineValidationError
AssetValidationError
QualityGateError
PackageValidationError
OpenCriticalMessageError
OpenEscalationError
```

---

# 30. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
ProjectFactory
ProjectValidator
ProjectStateManager
ProjectConfigLoader
ProjectPathBuilder
ProjectSnapshotManager
ProjectLockManager
ProjectReportBuilder
ProjectPackageBuilder
ProjectOwnershipManager
ProjectLogManager
ProjectCompletionChecker
```

---

# 31. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/07_PROJECT_SPEC.md
→ engines/project/
```

예시 구조:

```text
engines/
└── project/
    ├── project_factory.py
    ├── project_validator.py
    ├── project_state_manager.py
    ├── project_path_builder.py
    ├── project_snapshot_manager.py
    ├── project_lock_manager.py
    ├── project_report_builder.py
    ├── project_package_builder.py
    └── project_completion_checker.py
```

---

# 32. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Project 생성 요청을 검증할 수 있다.
Project ID를 생성할 수 있다.
Project 폴더 구조를 생성할 수 있다.
project.json을 생성할 수 있다.
topic.json을 생성할 수 있다.
channel_snapshot.json을 저장할 수 있다.
template_snapshot.json을 저장할 수 있다.
Project 상태를 관리할 수 있다.
잘못된 상태 전환을 막을 수 있다.
Stage별 필수 Output을 검증할 수 있다.
Timeline 존재와 기본 구조를 검증할 수 있다.
Asset Naming 규칙을 검증할 수 있다.
Quality Gate 전 READY 상태 전환을 막을 수 있다.
Upload Package를 검증할 수 있다.
Learning 완료 전 COMPLETE 상태 전환을 막을 수 있다.
```

---

# 33. Non Goals

v1.0에서 하지 않는 것:

```text
복잡한 웹 기반 Project 관리 UI
외부 사용자용 Project Dashboard
자동 YouTube 업로드 강제
고급 클라우드 렌더링
복잡한 병렬 렌더링 시스템
다중 사용자 권한 관리
```

v1.0에서는 내부 ADOS 운영에 필요한 Project 구조와 상태 관리부터 완성한다.

---

# 34. Critical Project Rules

반드시 지켜야 할 규칙:

```text
1. Project는 Channel 없이 생성하지 않는다.

2. Project 생성 시 Channel Snapshot과 Template Snapshot을 저장한다.

3. Project 상태는 Workflow Orchestrator와 Project Manager가 관리한다.

4. Stage별 필수 Output이 없으면 다음 단계로 이동하지 않는다.

5. Timeline은 모든 Asset 연결의 기준이다.

6. Scene ID는 임의 변경하지 않는다.

7. 언어별 결과물은 languages/{lang}/에 저장한다.

8. Provider 결과물은 Asset Naming 규칙을 따른다.

9. Quality Gate를 통과하지 못하면 READY가 될 수 없다.

10. Open Critical Message가 있으면 다음 Stage로 이동하지 않는다.

11. Open Escalation이 있으면 다음 Stage로 이동하지 않는다.

12. 전체 재생성보다 부분 수정이 우선이다.

13. COMPLETE 전 Learning Report가 필요하다.

14. 중요한 결정과 실패는 로그로 남긴다.
```

---

# 35. Final Principle

Project는 CHUNG COMPANY의 영상 제작 단위이다.

하지만 Project의 목적은 단순히 영상을 만드는 것이 아니다.

Project의 목적은 Channel을 성장시키는 고품질 콘텐츠를 만드는 것이다.

좋은 Project는 좋은 Timeline을 만들고,

좋은 Timeline은 좋은 Asset을 만들고,

좋은 Asset은 좋은 Video를 만들고,

좋은 Video는 좋은 Data를 만들고,

좋은 Data는 좋은 Learning을 만들고,

좋은 Learning은 Template을 성장시킨다.
