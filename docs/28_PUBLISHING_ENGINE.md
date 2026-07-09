# 28_PUBLISHING_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Publishing Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Publishing Engine을 정의한다.

Publishing Engine은 Quality Engine을 통과한 Project를 YouTube 업로드 또는 수동 게시 준비가 가능한 Upload Package로 정리하는 엔진이다.

v1.0에서 Publishing Engine의 핵심은 실제 자동 업로드가 아니다.

v1.0의 핵심은 다음이다.

```text
Quality 통과 확인
언어별 Render Variant 확인
제목 / 설명 / 태그 / 썸네일 방향 정리
업로드 파일 구조 정리
최종 게시 체크리스트 생성
Human Review 준비
Publishing Package 생성
Analytics Engine이 추적할 Publishing Record 생성
```

Publishing Engine은 다음을 담당한다.

```text
Quality Result 확인
Growth Output 로드
Final Timeline 로드
Render Plan 로드
Asset Registry 로드
언어별 Metadata 생성
Thumbnail Brief 생성
Upload Package 생성
Publishing Checklist 생성
Publishing Review 생성
Manual Upload Guide 생성
Published Record 구조 준비
Analytics Engine Handoff 생성
```

이 문서는 다음 문서들과 직접 연결된다.

```text
07_PROJECT_SPEC.md
10_BRAND_SYSTEM.md
12_PROJECT_ENGINE.md
13_MEMORY_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
25_EDITING_ENGINE.md
26_QUALITY_ENGINE.md
27_GROWTH_ENGINE.md
29_ANALYTICS_ENGINE.md
30_LEARNING_ENGINE.md
```

---

# 2. Core Definition

Publishing Engine은 제작 완료된 Project를 게시 가능한 패키지로 변환하는 엔진이다.

전체 흐름:

```text
Quality PASS
↓
Growth Metadata
↓
Render Plan
↓
Publishing Engine
↓
Upload Package
↓
Human Review
↓
Manual Publish or Future Auto Publish
↓
Analytics
```

Publishing Engine의 핵심 목표는 다음이다.

```text
Quality를 통과하지 않은 Project가 게시되지 않게 한다.
언어별 업로드 정보를 정리한다.
Title / Description / Tags / Thumbnail 방향을 정리한다.
Final Video 또는 Render Plan을 Package에 연결한다.
업로드 전 사람이 확인할 체크리스트를 만든다.
게시 이후 Analytics가 추적할 기준 정보를 남긴다.
```

---

# 3. Publishing Philosophy

## 3.1 Quality Before Publishing

Publishing Engine은 Quality Gate를 우회하지 않는다.

```text
Quality PASS 또는 Human Approved 상태가 아니면 Publishing Package를 생성하지 않는다.
```

금지:

```text
Quality Report 없이 Upload Package 생성
Hard Fail이 있는데 Publishing 진행
필수 언어 Metadata 누락
Final Video 또는 Render Plan 누락
Brand 위반 Title 사용
Factual Risk가 있는 Thumbnail 사용
```

## 3.2 Publishing Is Not Just Upload

Publishing은 파일 업로드만이 아니다.

Publishing은 다음을 포함한다.

```text
영상 파일
제목
설명
태그
썸네일 방향
언어별 메타데이터
게시 시점
체크리스트
리스크 확인
추적 기준
```

## 3.3 Human Review Initially

ADOS v1.0에서는 자동 게시보다 Human Review가 우선이다.

기본 운영:

```text
Generate Upload Package
↓
Human Review
↓
Manual Upload
↓
Published Record 등록
↓
Analytics Tracking
```

Full Auto Publishing은 Quality와 Analytics가 안정화된 이후에만 고려한다.

## 3.4 Metadata Must Match the Video

Title, Description, Tags, Thumbnail은 영상 내용과 일치해야 한다.

금지:

```text
영상에 없는 약속
거짓 Clickbait
확정되지 않은 내용을 확정 표현
Brand Tone과 다른 자극적 제목
무관한 인기 키워드
```

---

# 4. Publishing Engine Responsibilities

Publishing Engine의 책임:

```text
Quality PASS 확인
Growth Handoff 로드
Editing Render Plan 로드
Final Timeline 로드
Asset Registry 로드
언어별 Render Variant 확인
언어별 Metadata 생성
Title Candidate 최종 선택 구조 생성
Description 생성
Tags 생성
Thumbnail Brief 생성
Upload Package 생성
Manual Upload Guide 생성
Publishing Checklist 생성
Publishing Review 생성
Published Record Template 생성
Analytics Engine Handoff 생성
```

Publishing Engine이 하지 않는 것:

```text
Quality Gate를 우회하지 않는다.
Final Video를 직접 렌더링하지 않는다.
Thumbnail 이미지를 직접 생성하지 않는다.
YouTube에 자동 업로드하지 않는다.
Analytics를 직접 수집하지 않는다.
수익을 보장하지 않는다.
Story나 영상 내용을 임의 수정하지 않는다.
Brand Rule을 무시하지 않는다.
```

---

# 5. Inputs

Publishing Engine의 입력:

```text
project.json
topic.json
channel_snapshot.json
template_snapshot.json

reports/quality_report.json
reports/quality_issues.json
workflow/handoffs/QUALITY_to_PACKAGE.json

reports/growth_report.json
reports/growth_prediction.json
reports/title_candidates.json
reports/thumbnail_direction.json
reports/seo_keywords.json
workflow/handoffs/GROWTH_to_PUBLISHING.json

edit/render_plan.json
edit/final_timeline.json
edit/edit_plan.json

assets/asset_registry.json
reports/editing_review.json

channels/{channel_id}/brand.yaml
channels/{channel_id}/growth.yaml
channels/{channel_id}/publishing.yaml

workflow/memory_context_PUBLISHING.json
```

필수 입력:

```text
project.json
channel_snapshot.json
reports/quality_report.json
edit/render_plan.json
edit/final_timeline.json
assets/asset_registry.json
```

권장 입력:

```text
reports/growth_report.json
reports/title_candidates.json
reports/thumbnail_direction.json
reports/seo_keywords.json
workflow/handoffs/GROWTH_to_PUBLISHING.json
```

Growth Output이 없으면 Publishing Engine은 최소 Metadata를 생성할 수 있다.

하지만 ADOS 기본 운영에서는 Growth Stage 이후 Publishing을 권장한다.

---

# 6. Outputs

Publishing Engine의 출력:

```text
package/upload_package.json
package/metadata_ko.json
package/metadata_en.json
package/title_candidates.json
package/thumbnail_brief.json
package/description_brief.json
package/tags_candidates.json
package/manual_upload_guide.md
package/publishing_checklist.json
package/published_record_template.json
reports/publishing_review.json
workflow/stage_results/PUBLISHING_result.json
workflow/handoffs/PUBLISHING_to_ANALYTICS.json
```

v1.0 최소 출력:

```text
package/upload_package.json
package/metadata_{lang}.json
package/manual_upload_guide.md
package/publishing_checklist.json
reports/publishing_review.json
workflow/handoffs/PUBLISHING_to_ANALYTICS.json
```

---

# 7. Publishing Execution Flow

Publishing Engine 실행 흐름:

```text
Load Project Context
↓
Load Quality Report
↓
Confirm Quality Gate
↓
Load Growth Outputs
↓
Load Render Plan
↓
Load Final Timeline
↓
Load Asset Registry
↓
Validate Publishing Inputs
↓
Build Language Metadata
↓
Build Thumbnail Brief
↓
Build Upload Package
↓
Build Manual Upload Guide
↓
Build Publishing Checklist
↓
Build Publishing Review
↓
Build Published Record Template
↓
Handoff to Analytics Engine
```

---

# 8. Quality Gate Requirement

Publishing Engine은 반드시 Quality Result를 확인한다.

허용 상태:

```text
PASS
HUMAN_REVIEW_RECOMMENDED with human_approved = true
```

조건부 허용:

```text
HUMAN_REVIEW_RECOMMENDED
→ Human Review 대기 Package 생성은 가능
→ 실제 Publish Ready 표시는 불가
```

금지 상태:

```text
AUTO_FIX_REQUIRED
PARTIAL_REGENERATION_REQUIRED
FAIL
ESCALATION_REQUIRED
```

Quality Gate 검사 예시:

```json
{
  "quality_gate_check": {
    "quality_result": "PASS",
    "quality_score": 96,
    "hard_fail": false,
    "can_create_upload_package": true,
    "can_publish": false,
    "reason": "Human review is still required in v1.0."
  }
}
```

v1.0 기본값:

```text
can_create_upload_package = true
can_publish_automatically = false
```

---

# 9. Upload Package

Upload Package는 업로드 준비에 필요한 모든 정보를 모은 중심 파일이다.

파일:

```text
package/upload_package.json
```

포함 내용:

```text
Project 정보
Quality 상태
Render Variant
언어별 Metadata
Thumbnail Brief
Asset 목록
Manual Upload Guide
Checklist
Publishing Risk
Analytics Tracking 기준
```

---

# 10. upload_package.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "PUBLISHING",

  "package_status": {
    "status": "READY_FOR_HUMAN_REVIEW",
    "quality_result": "PASS",
    "quality_score": 96,
    "auto_publish_allowed": false,
    "human_review_required": true
  },

  "video": {
    "format": "youtube_longform",
    "aspect_ratio": "16:9",
    "target_languages": [
      "ko",
      "en"
    ],
    "render_plan_ref": "edit/render_plan.json",
    "final_timeline_ref": "edit/final_timeline.json"
  },

  "render_variants": [
    {
      "language": "ko",
      "video_ref": "package/final_video_ko.mp4",
      "metadata_ref": "package/metadata_ko.json",
      "subtitle_ref": "assets/subtitles/subtitle_ko_v001.srt",
      "voice_ref": "assets/audio/voice_ko_v001.wav",
      "status": "READY_FOR_UPLOAD_OR_RENDER"
    },
    {
      "language": "en",
      "video_ref": "package/final_video_en.mp4",
      "metadata_ref": "package/metadata_en.json",
      "subtitle_ref": "assets/subtitles/subtitle_en_v001.srt",
      "voice_ref": "assets/audio/voice_en_v001.wav",
      "status": "READY_FOR_UPLOAD_OR_RENDER"
    }
  ],

  "thumbnail": {
    "thumbnail_brief_ref": "package/thumbnail_brief.json",
    "thumbnail_asset_ref": null,
    "status": "BRIEF_READY"
  },

  "checks": {
    "quality_passed": true,
    "metadata_complete": true,
    "asset_registry_valid": true,
    "language_variants_ready": true,
    "manual_upload_guide_created": true
  },

  "analytics": {
    "tracking_ready": true,
    "published_record_template_ref": "package/published_record_template.json"
  },

  "created_at": "2026-07-10T18:00:00",
  "updated_at": "2026-07-10T18:00:00"
}
```

---

# 11. Metadata Rules

Metadata는 언어별로 분리한다.

```text
package/metadata_ko.json
package/metadata_en.json
```

Metadata 구성:

```text
title
description
tags
category
language
thumbnail text suggestion
pinned comment suggestion
risk notes
publishing notes
```

규칙:

```text
Title은 영상 내용과 일치해야 한다.
Description은 과장 없이 핵심 내용을 설명해야 한다.
Tags는 실제 내용과 관련 있어야 한다.
Speculative Claim은 확정 표현으로 쓰지 않는다.
Brand Tone을 유지한다.
```

---

# 12. metadata_{lang}.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "language": "ko",

  "metadata": {
    "title": "100만 년 후 인간은 어떤 모습일까?",

    "description": "100만 년 뒤 인간은 지금의 우리와 얼마나 달라질 수 있을까요?\n\n이 영상은 인간 진화, 기술, 우주 이주, 그리고 미래 문명의 가능성을 바탕으로 미래 인간의 모습을 하나의 시나리오로 탐험합니다.\n\n단, 영상 속 미래 장면은 확정된 예측이 아니라 가능한 미래를 상상한 시뮬레이션입니다.",

    "tags": [
      "미래 인간",
      "인간 진화",
      "100만 년 후",
      "AI와 인간",
      "우주 이주",
      "미래 문명"
    ],

    "category": "Education",
    "language": "ko",

    "thumbnail_text_candidates": [
      "100만 년 후?",
      "인간일까?"
    ],

    "pinned_comment": "당신은 100만 년 뒤의 인간도 지금의 우리와 같은 인간이라고 생각하나요?",

    "disclosure_or_note": "Future scenarios are presented as possibilities, not confirmed predictions."
  },

  "source_refs": {
    "title_candidates_ref": "reports/title_candidates.json",
    "seo_keywords_ref": "reports/seo_keywords.json",
    "growth_report_ref": "reports/growth_report.json",
    "quality_report_ref": "reports/quality_report.json"
  },

  "risk_check": {
    "factual_safety": "PASS",
    "brand_fit": "PASS",
    "clickbait_risk": "LOW",
    "speculation_framing_preserved": true
  }
}
```

---

# 13. Title Selection Rules

Publishing Engine은 Growth Engine의 Title Candidates를 우선 사용한다.

Title 선택 기준:

```text
recommended = true
score가 높음
Brand Fit 높음
Factual Safety 통과
Clickbait Risk 낮음
언어별 자연스러움
```

금지:

```text
forbidden_titles에 포함된 제목
Speculation을 확정으로 표현하는 제목
영상 내용과 다른 제목
Brand Tone을 해치는 제목
```

Title이 여러 개이면 `package/title_candidates.json`에 복사하고 최종 선택값을 표시한다.

---

# 14. Description Rules

Description은 다음을 포함해야 한다.

```text
영상의 핵심 질문
영상에서 다루는 내용
Factual Framing
Channel 정체성
관련 키워드
필요 시 Disclaimer
```

금지:

```text
허위 수익 약속
영상에 없는 내용 약속
과도한 공포 조장
무관한 키워드 나열
확정되지 않은 내용을 확정 표현
```

---

# 15. Tags Rules

Tags는 SEO Keywords를 기반으로 생성한다.

Tag 종류:

```text
primary tags
secondary tags
long-tail tags
channel identity tags
```

규칙:

```text
영상 내용과 관련 있어야 한다.
너무 많은 무관 태그를 넣지 않는다.
금지 키워드를 사용하지 않는다.
언어별로 자연스럽게 생성한다.
```

---

# 16. Thumbnail Brief

Publishing Engine은 Thumbnail 최종 이미지를 직접 만들지 않는다.

대신 Thumbnail Brief를 생성한다.

파일:

```text
package/thumbnail_brief.json
```

포함 내용:

```text
main concept
visual elements
text candidates
composition
brand rules
factual risk
avoid rules
asset candidate
```

---

# 17. thumbnail_brief.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "thumbnail_brief": {
    "main_concept": "A mysterious future human silhouette under alien light, contrasted with a present-day human silhouette.",

    "visual_elements": [
      "future human silhouette",
      "alien sunlight",
      "present human comparison",
      "cinematic dark blue background"
    ],

    "composition": "Strong central silhouette, clear contrast between present and future, minimal background noise.",

    "text_candidates": [
      "100만 년 후?",
      "인간일까?"
    ],

    "text_policy": {
      "max_words": 3,
      "large_readable_text": true,
      "avoid_too_much_text": true
    },

    "brand_rules": [
      "cinematic",
      "mysterious",
      "intelligent",
      "not cheap sci-fi"
    ],

    "factual_risk": {
      "level": "MEDIUM",
      "required_treatment": "question framing",
      "forbidden": [
        "Do not show the future human as a confirmed scientific prediction."
      ]
    },

    "avoid": [
      "monster-like human",
      "cheap horror",
      "fake scientific certainty",
      "generic robot face",
      "too much text"
    ],

    "source_refs": {
      "growth_thumbnail_direction": "reports/thumbnail_direction.json",
      "visual_assets": "assets/asset_registry.json"
    }
  }
}
```

---

# 18. Manual Upload Guide

v1.0에서는 Manual Upload Guide가 중요하다.

파일:

```text
package/manual_upload_guide.md
```

포함 내용:

```text
업로드 대상 언어
영상 파일 위치
제목
설명
태그
자막 파일
썸네일 지시
업로드 전 체크리스트
게시 후 Published Record 작성 방법
```

---

# 19. manual_upload_guide.md Format

권장 형식:

```markdown
# Manual Upload Guide

Project ID: 20260710-093500-future-million-year-human  
Channel: future  

---

## Korean Upload

Video File:
package/final_video_ko.mp4

Title:
100만 년 후 인간은 어떤 모습일까?

Description:
See package/metadata_ko.json

Subtitle:
assets/subtitles/subtitle_ko_v001.srt

Thumbnail:
Use package/thumbnail_brief.json

---

## Before Upload

- Confirm Quality Result is PASS.
- Confirm title does not overpromise.
- Confirm thumbnail matches actual video.
- Confirm subtitles are attached or burned in.
- Confirm language is correct.

---

## After Upload

Record the video URL and publish time in:
package/published_record.json
```

---

# 20. Publishing Checklist

Publishing Checklist는 업로드 전 최종 확인표이다.

파일:

```text
package/publishing_checklist.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",

  "checklist": [
    {
      "item_id": "PUB-CHECK-001",
      "category": "QUALITY",
      "item": "Quality result is PASS or human-approved.",
      "required": true,
      "status": "PASS"
    },
    {
      "item_id": "PUB-CHECK-002",
      "category": "METADATA",
      "item": "Title matches the video content.",
      "required": true,
      "status": "PASS"
    },
    {
      "item_id": "PUB-CHECK-003",
      "category": "THUMBNAIL",
      "item": "Thumbnail does not present speculative content as fact.",
      "required": true,
      "status": "PASS"
    },
    {
      "item_id": "PUB-CHECK-004",
      "category": "LANGUAGE",
      "item": "All target language variants have metadata.",
      "required": true,
      "status": "PASS"
    }
  ],

  "overall": {
    "required_items_passed": true,
    "ready_for_human_review": true,
    "ready_for_auto_publish": false
  }
}
```

---

# 21. Published Record Template

Published Record는 게시 후 Analytics가 추적할 기준 파일이다.

게시 전에는 Template만 생성한다.

파일:

```text
package/published_record_template.json
```

게시 후 실제 값은 다음 파일에 기록할 수 있다.

```text
package/published_record.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "published": {
    "status": "NOT_PUBLISHED",
    "platform": "youtube",
    "video_id": null,
    "video_url": null,
    "published_at": null,
    "language": null
  },

  "metadata_used": {
    "title": null,
    "description_ref": null,
    "tags_ref": null,
    "thumbnail_ref": null
  },

  "tracking": {
    "analytics_required": true,
    "first_check_after_hours": 24,
    "checkpoints": [
      "24h",
      "72h",
      "7d",
      "28d"
    ]
  }
}
```

---

# 22. Publishing Review

Publishing Review는 Publishing Package가 정상적으로 생성되었는지 검사한다.

파일:

```text
reports/publishing_review.json
```

Schema:

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "PUBLISHING",

  "score": 94,
  "status": "READY_FOR_HUMAN_REVIEW",

  "checks": {
    "quality_gate_valid": true,
    "render_plan_loaded": true,
    "metadata_complete": true,
    "title_safe": true,
    "description_safe": true,
    "tags_valid": true,
    "thumbnail_brief_ready": true,
    "language_variants_ready": true,
    "manual_upload_guide_created": true,
    "analytics_handoff_ready": true
  },

  "issues": [
    {
      "severity": "LOW",
      "issue_type": "THUMBNAIL_ASSET_NOT_FINAL",
      "description": "Thumbnail brief is ready, but final thumbnail asset is not registered.",
      "suggested_fix": "Create final thumbnail before manual upload."
    }
  ],

  "handoff_notes": [
    "Package is ready for human review.",
    "Do not publish automatically in v1.0."
  ]
}
```

---

# 23. Publishing Scoring

Publishing Score 기준:

```yaml
publishing_score:
  quality_gate_valid: 20
  render_plan_ready: 15
  metadata_completeness: 20
  title_safety: 10
  thumbnail_brief_quality: 10
  language_variant_readiness: 10
  checklist_completion: 10
  analytics_handoff_readiness: 5
```

점수 기준:

```text
95~100
Ready for human review / package complete

90~94
Ready with notes

80~89
Revision required

70~79
Partial fix required

70 미만
Publishing fail
```

Hard Fail 조건:

```text
Quality Gate 미통과
필수 Metadata 누락
언어별 Render Variant 누락
Title이 Forbidden Title과 일치
Thumbnail Brief가 Factual Risk 위반
Upload Package 생성 실패
Analytics Handoff 생성 실패
```

---

# 24. Publishing Validation Rules

Publishing Validator는 다음을 확인해야 한다.

```text
package/upload_package.json 존재
package/metadata_{lang}.json 존재
package/manual_upload_guide.md 존재
package/publishing_checklist.json 존재
package/published_record_template.json 존재
reports/publishing_review.json 존재
project_id 일치
channel_id 일치
Quality Gate 통과 여부
target_languages와 metadata 파일 일치
Title 존재
Description 존재
Tags 존재
Thumbnail Brief 존재
Render Plan 연결
Asset Registry 연결
Publishing Checklist required items PASS
Analytics Handoff 존재
```

검증 실패 시 READY 또는 PUBLISHED 상태로 이동할 수 없다.

---

# 25. Analytics Engine Handoff

Publishing Engine은 Analytics Engine에 Handoff를 생성해야 한다.

파일:

```text
workflow/handoffs/PUBLISHING_to_ANALYTICS.json
```

포함 내용:

```text
project_id
channel_id
published_record_template
metadata used
growth prediction refs
quality report ref
checkpoints
expected analytics metrics
```

예시:

```json
{
  "from_stage": "PUBLISHING",
  "to_stage": "ANALYTICS",
  "project_id": "20260710-093500-future-million-year-human",

  "analytics_inputs": [
    "package/published_record_template.json",
    "reports/growth_prediction.json",
    "reports/growth_report.json",
    "reports/quality_report.json",
    "package/upload_package.json"
  ],

  "tracking_plan": {
    "platform": "youtube",
    "checkpoints": [
      "24h",
      "72h",
      "7d",
      "28d"
    ],
    "metrics": [
      "views",
      "ctr",
      "average_view_duration",
      "retention",
      "watch_time",
      "subscribers_gained",
      "revenue",
      "rpm"
    ]
  },

  "note": "Analytics can start only after published_record.json has real video_id and video_url."
}
```

---

# 26. Published State Rules

Publishing Engine은 실제 게시 완료 후 Project 상태를 업데이트할 수 있는 구조를 준비한다.

게시 전:

```text
READY_FOR_HUMAN_REVIEW
READY_FOR_MANUAL_UPLOAD
NOT_PUBLISHED
```

게시 후:

```text
PUBLISHED
ANALYTICS_PENDING
```

v1.0에서는 실제 게시 후 사용자가 다음 정보를 기록할 수 있다.

```text
video_id
video_url
published_at
language
metadata_used
thumbnail_used
```

Project Engine은 이 정보가 입력되면 Project 상태를 `PUBLISHED`로 변경할 수 있다.

---

# 27. Auto Publishing Policy

v1.0 기본 정책:

```text
auto_publish: false
```

Auto Publishing이 허용되려면:

```text
Quality Score 95 이상
Hard Fail 없음
Publishing Checklist 모두 PASS
Human Review 정책에서 auto_publish 허용
Channel이 auto_publish_enabled
Publishing Provider가 안전하게 구성됨
```

하지만 v1.0에서는 자동 업로드 구현을 필수로 하지 않는다.

---

# 28. Auto Fix Rules

Publishing 문제 발생 시 부분 수정이 우선이다.

수정 대상:

```text
Title
Description
Tags
Thumbnail Brief
Metadata 파일
Manual Upload Guide
Checklist
Upload Package
Analytics Handoff
```

금지:

```text
Quality Gate 우회
Forbidden Title 사용
Brand Rule 위반
Speculative Claim 확정 표현
영상 내용과 다른 Metadata
Project 전체 재생성
```

Auto Fix 예시:

```text
Issue:
Title implies a confirmed future prediction.

Fix:
Rewrite title as a question and update metadata_ko.json and title_candidates package copy.
```

---

# 29. Memory Integration

Publishing Engine은 작업 전 Memory Context를 사용한다.

사용 가능한 Memory:

```text
Successful Title Publishing Memory
Failed Title Publishing Memory
Thumbnail Publishing Memory
Description Pattern Memory
Tag Pattern Memory
Manual Upload Issue Memory
Publishing Checklist Memory
```

Publishing Engine은 작업 후 Memory Candidate를 만들 수 있다.

예시:

```text
특정 Channel에서 좋은 Description 구조
업로드 전 자주 누락되는 Checklist 항목
특정 Title 표현이 Brand Risk를 자주 만듦
썸네일 텍스트가 너무 길면 가독성이 떨어짐
```

Memory 확정은 Memory Engine 또는 Learning Engine이 담당한다.

---

# 30. Error Types

Publishing Engine의 Error Type:

```text
PublishingInputMissingError
QualityGateNotPassedError
RenderPlanMissingError
MetadataCreationError
TitleSelectionError
TitleSafetyError
DescriptionCreationError
TagsCreationError
ThumbnailBriefError
UploadPackageCreationError
PublishingChecklistError
PublishingReviewError
PublishedRecordTemplateError
AnalyticsHandoffError
PublishingValidationError
```

Error 예시:

```json
{
  "error_type": "QualityGateNotPassedError",
  "message": "Publishing package cannot be created because Quality result is AUTO_FIX_REQUIRED.",
  "project_id": "20260710-093500-future-million-year-human",
  "stage": "PUBLISHING",
  "severity": "HIGH",
  "suggested_fix": "Return to AUTO_FIX and re-run Quality before Publishing.",
  "created_at": "2026-07-10T18:00:00"
}
```

---

# 31. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
PublishingEngine
PublishingInputLoader
PublishingInputValidator
QualityGateChecker
MetadataBuilder
TitleSelector
TitleSafetyChecker
DescriptionBuilder
TagsBuilder
ThumbnailBriefBuilder
UploadPackageBuilder
ManualUploadGuideBuilder
PublishingChecklistBuilder
PublishedRecordTemplateBuilder
PublishingReviewBuilder
PublishingValidator
AnalyticsHandoffBuilder
PublishingMemoryCandidateBuilder
PublishingErrorReporter
```

---

# 32. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/28_PUBLISHING_ENGINE.md
→ engines/publishing/
```

예시 구조:

```text
engines/
└── publishing/
    ├── publishing_engine.py
    ├── publishing_input_loader.py
    ├── publishing_input_validator.py
    ├── quality_gate_checker.py
    ├── metadata_builder.py
    ├── title_selector.py
    ├── title_safety_checker.py
    ├── description_builder.py
    ├── tags_builder.py
    ├── thumbnail_brief_builder.py
    ├── upload_package_builder.py
    ├── manual_upload_guide_builder.py
    ├── publishing_checklist_builder.py
    ├── published_record_template_builder.py
    ├── publishing_review_builder.py
    ├── publishing_validator.py
    ├── analytics_handoff_builder.py
    ├── publishing_memory_candidate_builder.py
    └── publishing_error_reporter.py
```

---

# 33. Main Public Operations

Publishing Engine은 최소 다음 작업을 제공해야 한다.

```text
run_publishing(project_id)
load_publishing_inputs(project_id)
validate_publishing_inputs(project_id)
check_quality_gate(project_id)
build_metadata(project_id, language)
build_all_language_metadata(project_id)
select_title(project_id, language)
check_title_safety(project_id, language)
build_description(project_id, language)
build_tags(project_id, language)
build_thumbnail_brief(project_id)
build_upload_package(project_id)
build_manual_upload_guide(project_id)
build_publishing_checklist(project_id)
build_published_record_template(project_id)
build_publishing_review(project_id)
validate_publishing_outputs(project_id)
build_handoff_to_analytics(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
Quality Gate 확인
Brand Rule 준수
Factual Risk 준수
언어별 Metadata 분리
Growth Output 우선 활용
Upload Package 구조 생성
Human Review 기본 정책 유지
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 34. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Quality Report 로드
Quality Gate 확인
Render Plan 로드
Asset Registry 로드
Growth Output 로드
Publishing 입력 검증
언어별 metadata_{lang}.json 생성
thumbnail_brief.json 생성
upload_package.json 생성
manual_upload_guide.md 생성
publishing_checklist.json 생성
published_record_template.json 생성
publishing_review.json 생성
Analytics Engine Handoff 생성
Publishing Validation 수행
```

v1.0에서 하지 않아도 되는 것:

```text
YouTube 자동 업로드
최종 Thumbnail 이미지 직접 생성
Final Video 자동 렌더링
실시간 Metadata A/B 테스트
Analytics 직접 수집
자동 게시 시간 최적화
수익 보장
```

v1.0에서는 사람이 안전하게 업로드할 수 있는 Upload Package를 안정적으로 만드는 것이 우선이다.

---

# 35. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Quality Report를 로드할 수 있다.
Quality Gate를 확인할 수 있다.
Quality 미통과 Project의 Publishing을 막을 수 있다.
Growth Output을 기반으로 Metadata를 생성할 수 있다.
언어별 metadata_{lang}.json을 생성할 수 있다.
Thumbnail Brief를 생성할 수 있다.
Upload Package를 생성할 수 있다.
Manual Upload Guide를 생성할 수 있다.
Publishing Checklist를 생성할 수 있다.
Published Record Template을 생성할 수 있다.
Publishing Review를 생성할 수 있다.
Analytics Engine으로 Handoff를 만들 수 있다.
Publishing Validation 실패 시 READY 또는 PUBLISHED 상태 진행을 막을 수 있다.
```

---

# 36. Non Goals

v1.0에서 Publishing Engine이 하지 않는 것:

```text
YouTube 직접 업로드
Final Video 직접 렌더링
Thumbnail 최종 이미지 직접 생성
Quality Gate 우회
Analytics 직접 수집
수익 예측 보장
Story 수정
Video Asset 수정
자동 게시 결정
```

v1.0에서는 Upload Package, Metadata, Checklist, Manual Upload Guide, Analytics Handoff를 만드는 것이 핵심이다.

---

# 37. Critical Publishing Rules

반드시 지켜야 할 규칙:

```text
1. Publishing Engine은 Quality Report 없이 실행하지 않는다.

2. Quality Gate를 통과하지 않으면 Upload Package를 생성하지 않는다.

3. v1.0에서는 자동 게시하지 않는다.

4. Human Review를 기본 정책으로 한다.

5. Title은 영상 내용과 일치해야 한다.

6. Description은 과장 없이 작성해야 한다.

7. Tags는 영상과 관련 있어야 한다.

8. Thumbnail Brief는 Factual Risk를 위반하면 안 된다.

9. Speculative Claim을 확정 사실처럼 표현하지 않는다.

10. 언어별 Metadata를 분리한다.

11. Render Variant와 Metadata 언어가 일치해야 한다.

12. Published Record Template을 생성해야 한다.

13. Analytics Engine이 추적할 수 있는 Handoff를 만들어야 한다.

14. Publishing Validation 실패 시 READY 또는 PUBLISHED 상태로 넘어가지 않는다.

15. 중요한 Publishing 판단은 Review와 Handoff에 기록한다.
```

---

# 38. Final Principle

Publishing Engine은 콘텐츠를 세상에 내보내기 직전의 마지막 정리 엔진이다.

좋은 Publishing은 단순 업로드가 아니다.

좋은 Publishing은 Quality를 확인하고,

Growth의 판단을 반영하고,

Brand를 지키고,

시청자에게 정직한 약속을 만들고,

Analytics가 학습할 수 있는 기준을 남긴다.

Publishing Engine의 목적은 영상을 빨리 올리는 것이 아니다.

Publishing Engine의 목적은 올려도 되는 상태인지 확인하고, 사람이 안전하게 업로드할 수 있는 완성된 패키지를 만드는 것이다.
