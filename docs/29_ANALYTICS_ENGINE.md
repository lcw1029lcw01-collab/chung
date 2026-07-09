# 29_ANALYTICS_ENGINE.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Analytics Engine Specification  

---

# 1. Purpose

이 문서는 ADOS의 Analytics Engine을 정의한다.

Analytics Engine은 게시된 영상의 실제 성과 데이터를 수집, 정리, 분석하고 Growth Engine의 예측과 비교하여 Learning Engine이 학습할 수 있는 구조화된 결과를 만드는 엔진이다.

Analytics Engine의 핵심 목적은 다음이다.

```text
실제 성과를 기록한다.
Growth 예측과 실제 결과를 비교한다.
CTR / Retention / Watch Time / Subscriber / Revenue를 분석한다.
Title / Thumbnail / Hook / Topic / Voice / Subtitle / Quality의 영향을 추적한다.
Channel 성장에 도움이 된 요소와 실패 요소를 분리한다.
Learning Engine이 다음 Project를 개선할 수 있는 데이터를 만든다.
```

Analytics Engine은 다음 문서들과 직접 연결된다.

```text
07_PROJECT_SPEC.md
11_PORTFOLIO_ENGINE.md
12_PROJECT_ENGINE.md
13_MEMORY_ENGINE.md
15_WORKFLOW_ORCHESTRATOR.md
26_QUALITY_ENGINE.md
27_GROWTH_ENGINE.md
28_PUBLISHING_ENGINE.md
30_LEARNING_ENGINE.md
31_AI_EVOLUTION_ENGINE.md
```

---

# 2. Core Definition

Analytics Engine은 게시 이후 실제 성과를 측정하는 엔진이다.

전체 흐름:

```text
Publishing
↓
Published Record
↓
Analytics Data Collection
↓
Performance Report
↓
Growth Prediction Comparison
↓
Learning Handoff
↓
Memory / Template / Channel Improvement
```

Analytics Engine의 핵심 질문:

```text
영상은 실제로 클릭되었는가?
시청자는 얼마나 오래 봤는가?
어디에서 이탈했는가?
구독 전환이 있었는가?
수익 가능성은 실제와 맞았는가?
Growth Engine의 예측은 맞았는가?
Quality Score와 실제 성과는 어떤 관계가 있는가?
다음 영상에서 무엇을 반복하고 무엇을 피해야 하는가?
```

---

# 3. Analytics Philosophy

## 3.1 Analytics Is Feedback

Analytics는 단순 성과 기록이 아니다.

Analytics는 ADOS가 다음 Project를 더 잘 만들기 위한 피드백이다.

```text
Prediction
↓
Publishing
↓
Actual Data
↓
Comparison
↓
Learning
↓
Better Next Project
```

## 3.2 Do Not Overinterpret Early Data

초기 데이터는 불완전할 수 있다.

```text
24h 데이터는 초기 반응이다.
72h 데이터는 초반 추천 가능성이다.
7d 데이터는 비교적 안정된 초기 성과이다.
28d 데이터는 장기 평가에 더 적합하다.
```

Analytics Engine은 너무 적은 데이터로 과도한 결론을 내리면 안 된다.

## 3.3 Separate Signal and Noise

조회수가 낮다고 항상 영상이 나쁜 것은 아니다.

CTR이 낮은 이유는 Title / Thumbnail 문제일 수 있고, Retention이 낮은 이유는 Hook / Pacing / Topic mismatch일 수 있다.

Analytics Engine은 가능한 원인을 분리해서 기록해야 한다.

## 3.4 Analytics Must Feed Learning

Analytics Report는 Learning Engine이 사용할 수 있어야 한다.

Analytics Engine이 단순 숫자만 남기면 안 된다.

반드시 다음을 남겨야 한다.

```text
성과 요약
예측 대비 실제 차이
성공 요인 후보
실패 요인 후보
다음 Project 개선 제안
Learning Engine Handoff
```

---

# 4. Analytics Engine Responsibilities

Analytics Engine의 책임:

```text
Published Record 로드
Publishing Package 로드
Growth Prediction 로드
Quality Report 로드
성과 Checkpoint 관리
수동 / 반자동 Analytics 입력 수집
Raw Metrics 저장
Performance Metrics 계산
Growth Prediction과 실제 성과 비교
CTR 분석
Retention 분석
Watch Time 분석
Subscriber Conversion 분석
Revenue / RPM 분석
Traffic Source 분석
언어별 성과 분석
Analytics Report 생성
Learning Engine Handoff 생성
Portfolio Engine용 성과 Signal 생성
```

Analytics Engine이 하지 않는 것:

```text
영상을 직접 수정하지 않는다.
Metadata를 직접 수정하지 않는다.
YouTube에 직접 업로드하지 않는다.
Learning 결론을 직접 Memory에 확정하지 않는다.
실제 수익을 보장하지 않는다.
성과 부진의 원인을 단정하지 않는다.
충분한 데이터 없이 Template을 변경하지 않는다.
```

---

# 5. Analytics Modes

Analytics Engine은 세 가지 모드를 지원할 수 있다.

```text
manual
semi_automated
automated
```

## manual

사용자가 YouTube Studio에서 수치를 복사해 입력한다.

v1.0 기본 모드이다.

## semi_automated

CSV export, spreadsheet, 수동 다운로드 파일 등을 읽어서 분석한다.

## automated

YouTube Analytics API 등 외부 API를 통해 자동 수집한다.

v1.0에서는 필수 구현이 아니다.

---

# 6. Inputs

Analytics Engine의 입력:

```text
project.json
channel_snapshot.json
template_snapshot.json

package/upload_package.json
package/published_record.json
package/published_record_template.json
package/metadata_{lang}.json

reports/growth_prediction.json
reports/growth_report.json
reports/quality_report.json
reports/publishing_review.json

workflow/handoffs/PUBLISHING_to_ANALYTICS.json
workflow/memory_context_ANALYTICS.json
```

성과 입력 데이터:

```text
analytics/manual_metrics_input.json
analytics/raw_metrics_24h.json
analytics/raw_metrics_72h.json
analytics/raw_metrics_7d.json
analytics/raw_metrics_28d.json
```

선택 입력:

```text
YouTube Studio CSV Export
Revenue Report
Audience Retention Screenshot Data
Traffic Source Report
Channel Baseline Metrics
Historical Channel Analytics Memory
```

필수 입력:

```text
package/published_record.json
reports/growth_prediction.json
reports/quality_report.json
project.json
channel_snapshot.json
```

`published_record.json`에 실제 `video_id`, `video_url`, `published_at`이 없으면 Analytics는 대기 상태가 된다.

---

# 7. Outputs

Analytics Engine의 출력:

```text
analytics/analytics_state.json
analytics/raw_metrics.json
analytics/performance_summary.json
analytics/prediction_comparison.json
analytics/retention_report.json
analytics/traffic_source_report.json
analytics/revenue_report.json
reports/analytics_report.json
workflow/stage_results/ANALYTICS_result.json
workflow/handoffs/ANALYTICS_to_LEARNING.json
```

v1.0 최소 출력:

```text
analytics/raw_metrics.json
analytics/performance_summary.json
analytics/prediction_comparison.json
reports/analytics_report.json
workflow/handoffs/ANALYTICS_to_LEARNING.json
```

---

# 8. Analytics Execution Flow

Analytics Engine 실행 흐름:

```text
Load Project Context
↓
Load Published Record
↓
Check Published Status
↓
Load Growth Prediction
↓
Load Quality Report
↓
Load Publishing Package
↓
Load or Request Metrics Input
↓
Validate Metrics
↓
Normalize Metrics
↓
Build Performance Summary
↓
Compare Prediction vs Actual
↓
Analyze CTR
↓
Analyze Retention
↓
Analyze Watch Time
↓
Analyze Subscriber Conversion
↓
Analyze Revenue
↓
Build Analytics Report
↓
Build Learning Handoff
```

---

# 9. Analytics Checkpoints

Analytics Engine은 게시 후 체크포인트별로 성과를 관리한다.

기본 Checkpoints:

```text
24h
72h
7d
28d
```

각 체크포인트의 의미:

```text
24h
초기 클릭 반응, 구독자 초기 반응, 제목/썸네일 초기 평가

72h
추천 확산 초기 가능성, CTR 안정화, Retention 초기 패턴

7d
초기 성과 판단, Topic / Hook / Metadata 평가

28d
장기 성과, Evergreen 가능성, Revenue / Subscriber Conversion 평가
```

---

# 10. analytics_state.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "ANALYTICS",

  "published": {
    "status": "PUBLISHED",
    "platform": "youtube",
    "video_id": "VIDEO_ID_HERE",
    "video_url": "https://youtube.com/watch?v=VIDEO_ID_HERE",
    "published_at": "2026-07-10T20:00:00"
  },

  "analytics_status": {
    "status": "IN_PROGRESS",
    "mode": "manual",
    "completed_checkpoints": [
      "24h"
    ],
    "next_checkpoint": "72h",
    "last_updated": "2026-07-11T20:00:00"
  },

  "required_checkpoints": [
    "24h",
    "72h",
    "7d",
    "28d"
  ]
}
```

---

# 11. Raw Metrics

Raw Metrics는 사용자가 입력하거나 외부에서 가져온 원본 성과 데이터이다.

파일:

```text
analytics/raw_metrics.json
```

---

# 12. raw_metrics.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "platform": "youtube",

  "video": {
    "video_id": "VIDEO_ID_HERE",
    "video_url": "https://youtube.com/watch?v=VIDEO_ID_HERE",
    "published_at": "2026-07-10T20:00:00"
  },

  "checkpoints": [
    {
      "checkpoint": "24h",
      "collected_at": "2026-07-11T20:00:00",
      "collection_mode": "manual",

      "metrics": {
        "views": 1250,
        "impressions": 18000,
        "ctr_percent": 5.8,
        "average_view_duration_seconds": 210,
        "average_percentage_viewed": 42.5,
        "watch_time_hours": 72.9,
        "likes": 64,
        "comments": 11,
        "shares": 7,
        "subscribers_gained": 18,
        "revenue": 3.42,
        "rpm": 2.74,
        "cpm": 5.20
      },

      "traffic_sources": {
        "browse_features": 42.0,
        "suggested_videos": 28.0,
        "youtube_search": 18.0,
        "external": 8.0,
        "other": 4.0
      },

      "audience": {
        "top_countries": [
          {
            "country": "KR",
            "percent": 74.0
          }
        ],
        "top_languages": [
          {
            "language": "ko",
            "percent": 82.0
          }
        ]
      }
    }
  ]
}
```

---

# 13. Manual Metrics Input

v1.0에서는 수동 입력을 지원해야 한다.

파일:

```text
analytics/manual_metrics_input.json
```

사용 목적:

```text
YouTube Studio에서 확인한 값을 구조화해 입력
CSV 자동화 전 단계
API 연동 전 단계
```

Manual Input 규칙:

```text
수치의 기준 시간을 기록한다.
Checkpoint를 명확히 기록한다.
모르는 값은 null로 둔다.
추정값과 실제값을 구분한다.
```

---

# 14. Core Analytics Metrics

Analytics Engine이 추적할 기본 지표:

```text
views
impressions
ctr_percent
average_view_duration_seconds
average_percentage_viewed
watch_time_hours
likes
comments
shares
subscribers_gained
revenue
rpm
cpm
traffic_sources
audience_country
audience_language
```

v1.0 필수 지표:

```text
views
impressions
ctr_percent
average_view_duration_seconds
average_percentage_viewed
watch_time_hours
subscribers_gained
```

Revenue 관련 지표는 선택 입력일 수 있다.

---

# 15. Performance Summary

Performance Summary는 Raw Metrics를 사람이 이해하기 쉽게 요약한다.

파일:

```text
analytics/performance_summary.json
```

---

# 16. performance_summary.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "summary": {
    "checkpoint": "24h",
    "performance_level": "PROMISING",
    "overall_score": 82,

    "key_metrics": {
      "views": 1250,
      "ctr_percent": 5.8,
      "average_percentage_viewed": 42.5,
      "watch_time_hours": 72.9,
      "subscribers_gained": 18,
      "rpm": 2.74
    },

    "strengths": [
      "CTR is above baseline.",
      "Subscriber conversion is promising for early stage."
    ],

    "weaknesses": [
      "Average percentage viewed is moderate.",
      "Middle retention may need review."
    ],

    "recommended_learning_focus": [
      "Analyze hook-to-middle retention drop.",
      "Compare title performance with Growth prediction."
    ]
  }
}
```

---

# 17. Prediction Comparison

Analytics Engine은 Growth Engine의 예측과 실제 성과를 비교해야 한다.

비교 대상:

```text
CTR Potential vs Actual CTR
Retention Potential vs Average Percentage Viewed
Watch Time Potential vs Watch Time
Subscriber Conversion Potential vs Subscribers Gained
Revenue Potential vs RPM / Revenue
Search Potential vs YouTube Search Traffic
Recommendation Potential vs Browse / Suggested Traffic
```

---

# 18. prediction_comparison.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "growth_prediction_ref": "reports/growth_prediction.json",
  "actual_metrics_ref": "analytics/raw_metrics.json",

  "comparison": {
    "checkpoint": "24h",

    "ctr": {
      "predicted_score": 90,
      "actual_ctr_percent": 5.8,
      "result": "NEAR_EXPECTATION",
      "notes": "Actual CTR is promising but needs channel baseline comparison."
    },

    "retention": {
      "predicted_score": 88,
      "actual_average_percentage_viewed": 42.5,
      "result": "BELOW_EXPECTATION",
      "notes": "Retention lower than predicted; check middle pacing."
    },

    "subscriber_conversion": {
      "predicted_score": 80,
      "actual_subscribers_gained": 18,
      "result": "PROMISING",
      "notes": "Subscriber gain is positive for early checkpoint."
    },

    "revenue": {
      "predicted_score": 82,
      "actual_rpm": 2.74,
      "result": "UNKNOWN",
      "notes": "Revenue data too early to judge."
    }
  },

  "prediction_accuracy": {
    "overall": "PARTIAL_MATCH",
    "strong_predictions": [
      "CTR potential",
      "Subscriber conversion"
    ],
    "weak_predictions": [
      "Retention potential"
    ]
  }
}
```

---

# 19. CTR Analysis

CTR 분석은 Title과 Thumbnail의 실제 클릭 가능성을 평가한다.

검사 항목:

```text
Actual CTR
Impressions
Title Candidate
Thumbnail Brief
Traffic Source별 CTR
Channel Baseline 대비 CTR
```

CTR 해석 예시:

```text
CTR 높음 + Retention 높음
→ Topic / Title / Thumbnail / Content 모두 강할 가능성

CTR 높음 + Retention 낮음
→ Title / Thumbnail Promise와 실제 영상 불일치 가능성

CTR 낮음 + Retention 높음
→ 영상은 좋지만 Title / Thumbnail 개선 필요

CTR 낮음 + Retention 낮음
→ Topic / Packaging / Story 모두 재검토 필요
```

---

# 20. Retention Analysis

Retention 분석은 시청자가 어디에서 이탈했는지 확인한다.

v1.0에서는 정밀 그래프가 없어도 다음을 기록할 수 있다.

```text
average_view_duration_seconds
average_percentage_viewed
first_30_seconds_retention
first_60_seconds_retention
major_drop_points
estimated_drop_reasons
```

---

# 21. retention_report.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "retention": {
    "checkpoint": "24h",
    "average_view_duration_seconds": 210,
    "average_percentage_viewed": 42.5,

    "early_retention": {
      "first_30_seconds": null,
      "first_60_seconds": null,
      "status": "UNKNOWN"
    },

    "drop_points": [
      {
        "time": "00:03:20",
        "severity": "MEDIUM",
        "possible_reason": "Technical explanation section may be too long.",
        "related_scene_id": "SC006"
      }
    ],

    "interpretation": [
      "Hook likely works, but middle section may need pacing improvement.",
      "Future projects should add stronger visual transition before technical explanation."
    ]
  }
}
```

---

# 22. Traffic Source Analysis

Traffic Source는 영상이 어디에서 유입되었는지 분석한다.

기본 Traffic Sources:

```text
browse_features
suggested_videos
youtube_search
external
channel_pages
notifications
other
```

해석:

```text
browse_features 높음
→ YouTube 홈 추천 가능성

suggested_videos 높음
→ 관련 영상 추천 가능성

youtube_search 높음
→ Search SEO 성공 가능성

external 높음
→ 외부 공유 또는 링크 영향

notifications 높음
→ 기존 구독자 반응
```

---

# 23. traffic_source_report.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",

  "traffic_sources": {
    "checkpoint": "24h",
    "sources": [
      {
        "source": "browse_features",
        "percent": 42.0,
        "interpretation": "Strong home recommendation signal."
      },
      {
        "source": "youtube_search",
        "percent": 18.0,
        "interpretation": "Search contributes but is not dominant."
      }
    ],

    "growth_implication": [
      "Recommendation potential may be stronger than pure search potential.",
      "Future titles should preserve curiosity and browse appeal."
    ]
  }
}
```

---

# 24. Revenue Analysis

Revenue 데이터는 초기에는 불완전할 수 있다.

Analytics Engine은 Revenue를 확정적으로 해석하지 않는다.

Revenue 관련 지표:

```text
estimated_revenue
rpm
cpm
monetized_playbacks
ad_impressions
```

Revenue 해석 원칙:

```text
초기 수익 데이터는 변동성이 크다.
RPM은 국가, 주제, 시청 시간, 광고 상태에 따라 달라진다.
Revenue Potential은 실제 데이터로 계속 보정해야 한다.
```

---

# 25. revenue_report.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",

  "revenue": {
    "checkpoint": "7d",
    "estimated_revenue": 18.45,
    "rpm": 3.10,
    "cpm": 6.20,
    "revenue_level": "MODERATE",

    "comparison_to_prediction": {
      "predicted_revenue_score": 82,
      "result": "BELOW_EXPECTATION",
      "notes": "RPM is lower than expected; audience geography and monetized playback ratio should be reviewed."
    },

    "learning_notes": [
      "Future civilization topics may have global appeal but RPM depends heavily on audience geography.",
      "Revenue should be compared after 28d before making template-level conclusions."
    ]
  }
}
```

---

# 26. Language Performance

다국어 Project에서는 언어별 성과를 분리해야 한다.

검사 항목:

```text
언어별 video_id
언어별 views
언어별 CTR
언어별 retention
언어별 subscribers_gained
언어별 revenue
언어별 comments
```

언어별 업로드가 별도 영상이면 각각의 Published Record를 가져야 한다.

---

# 27. Analytics Report

Analytics Report는 전체 성과 분석의 중심 파일이다.

파일:

```text
reports/analytics_report.json
```

---

# 28. analytics_report.json Schema

```json
{
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",
  "stage": "ANALYTICS",

  "analytics_status": {
    "checkpoint": "24h",
    "status": "PARTIAL",
    "data_confidence": "MEDIUM"
  },

  "performance": {
    "overall_score": 82,
    "level": "PROMISING",

    "metrics_summary": {
      "views": 1250,
      "ctr_percent": 5.8,
      "average_percentage_viewed": 42.5,
      "watch_time_hours": 72.9,
      "subscribers_gained": 18
    }
  },

  "prediction_comparison": {
    "growth_prediction_accuracy": "PARTIAL_MATCH",
    "matched_predictions": [
      "CTR potential",
      "Subscriber conversion potential"
    ],
    "missed_predictions": [
      "Retention potential"
    ]
  },

  "insights": {
    "what_worked": [
      "Question-based title appears to generate healthy CTR.",
      "Topic has strong subscriber conversion potential."
    ],
    "what_did_not_work": [
      "Middle retention may be weaker than expected."
    ],
    "possible_causes": [
      "Explanation section may be too long.",
      "Visual rhythm may slow down after the hook."
    ],
    "next_project_recommendations": [
      "Add stronger midpoint visual reveal.",
      "Shorten technical explanation section.",
      "Keep question-based title structure."
    ]
  },

  "created_at": "2026-07-11T20:00:00"
}
```

---

# 29. Performance Level

Performance Level은 다음을 사용한다.

```text
EXCELLENT
STRONG
PROMISING
AVERAGE
WEAK
POOR
UNKNOWN
```

해석:

```text
EXCELLENT
채널 기준을 크게 초과

STRONG
주요 지표가 채널 기준보다 좋음

PROMISING
초기 신호가 좋지만 추가 데이터 필요

AVERAGE
채널 평균 수준

WEAK
개선 필요

POOR
큰 문제 가능성

UNKNOWN
데이터 부족
```

---

# 30. Data Confidence

Analytics Engine은 데이터 신뢰도를 표시해야 한다.

```text
HIGH
충분한 데이터와 안정된 체크포인트

MEDIUM
초기 판단 가능하지만 추가 관찰 필요

LOW
데이터 부족 또는 변동성 큼

UNKNOWN
판단 불가
```

예시:

```text
24h 데이터
→ 보통 LOW 또는 MEDIUM

7d 데이터
→ MEDIUM

28d 데이터
→ HIGH 가능
```

---

# 31. Baseline Comparison

Analytics Engine은 가능하면 Channel Baseline과 비교해야 한다.

Baseline 예시:

```json
{
  "channel_baseline": {
    "avg_ctr_percent": 4.2,
    "avg_average_percentage_viewed": 38.0,
    "avg_subscribers_gained_per_1000_views": 8.5,
    "avg_rpm": 2.60
  }
}
```

Baseline이 없는 경우:

```text
baseline_status = NOT_AVAILABLE
```

v1.0에서는 Baseline이 없어도 Analytics Report 생성은 가능하다.

---

# 32. Learning Handoff

Analytics Engine은 Learning Engine에 Handoff를 생성해야 한다.

파일:

```text
workflow/handoffs/ANALYTICS_to_LEARNING.json
```

포함 내용:

```text
Analytics Report
Raw Metrics
Performance Summary
Prediction Comparison
Retention Report
Revenue Report
성공 요인 후보
실패 요인 후보
다음 Project 개선 제안
Memory Candidate 후보
```

---

# 33. ANALYTICS_to_LEARNING.json Schema

```json
{
  "from_stage": "ANALYTICS",
  "to_stage": "LEARNING",
  "project_id": "20260710-093500-future-million-year-human",
  "channel_id": "future",

  "analytics_inputs": [
    "analytics/raw_metrics.json",
    "analytics/performance_summary.json",
    "analytics/prediction_comparison.json",
    "reports/analytics_report.json"
  ],

  "learning_focus": [
    "Compare predicted retention with actual retention.",
    "Extract title pattern if CTR remains above baseline.",
    "Review middle-section pacing for future projects."
  ],

  "candidate_insights": [
    {
      "type": "title_pattern",
      "confidence": "MEDIUM",
      "insight": "Question-based title may work well for future-channel speculative topics.",
      "evidence": [
        "CTR is above expected baseline.",
        "Growth prediction matched actual CTR direction."
      ]
    },
    {
      "type": "retention_failure_pattern",
      "confidence": "LOW",
      "insight": "Technical explanation sections may need stronger visual transitions.",
      "evidence": [
        "Retention was below prediction.",
        "Drop point estimated near explanation section."
      ]
    }
  ]
}
```

---

# 34. Portfolio Integration

Portfolio Engine은 Analytics 결과를 Channel / Project 우선순위 조정에 사용할 수 있다.

Portfolio에 제공할 정보:

```text
Project Performance Level
Growth Prediction Accuracy
Subscriber Conversion Signal
Revenue Signal
Topic Success Signal
Recommended Next Priority
```

예시:

```json
{
  "portfolio_analytics_signal": {
    "project_id": "20260710-093500-future-million-year-human",
    "channel_id": "future",
    "performance_level": "PROMISING",
    "priority_signal": "CONTINUE_TOPIC_CLUSTER",
    "reason": "CTR and subscriber conversion are promising."
  }
}
```

---

# 35. Auto Fix vs Future Learning

Analytics Engine은 게시된 영상을 직접 Auto Fix하지 않는다.

게시 이후 문제는 두 가지로 나눈다.

```text
이미 게시된 영상 수정 가능 항목
→ Title, Description, Thumbnail, Tags, Subtitle

다음 Project에 반영할 항목
→ Hook, Story Structure, Visual Rhythm, Topic Selection, Voice Pace
```

v1.0에서는 Analytics Engine이 자동 수정하지 않고 Learning 제안으로 넘긴다.

---

# 36. Analytics Validation Rules

Analytics Validator는 다음을 확인해야 한다.

```text
published_record.json 존재
video_id 또는 video_url 존재
published_at 존재
raw_metrics.json 존재
checkpoint 존재
metrics 필드 유효
숫자 필드 타입 유효
growth_prediction ref 존재
quality_report ref 존재
performance_summary.json 존재
prediction_comparison.json 존재
analytics_report.json 존재
Learning Handoff 존재
```

검증 실패 시 LEARNING Stage로 이동할 수 없다.

단, 아직 게시되지 않은 경우 Analytics Stage는 `WAITING_FOR_PUBLISHED_RECORD` 상태가 될 수 있다.

---

# 37. Analytics Waiting States

Analytics Engine은 다음 대기 상태를 가질 수 있다.

```text
WAITING_FOR_PUBLISHED_RECORD
WAITING_FOR_24H_METRICS
WAITING_FOR_72H_METRICS
WAITING_FOR_7D_METRICS
WAITING_FOR_28D_METRICS
WAITING_FOR_MANUAL_INPUT
```

대기 상태는 실패가 아니다.

필요한 시간이 지나지 않았거나, 사용자가 데이터를 아직 입력하지 않은 상태이다.

---

# 38. Memory Integration

Analytics Engine은 작업 전 Memory Context를 사용할 수 있다.

사용 가능한 Memory:

```text
Channel Baseline Memory
CTR Pattern Memory
Retention Pattern Memory
Topic Performance Memory
Revenue Pattern Memory
Subscriber Conversion Memory
Title Performance Memory
Thumbnail Performance Memory
```

Analytics Engine은 작업 후 Memory Candidate를 만들 수 있다.

예시:

```text
특정 Title 구조가 CTR을 높였을 가능성
특정 Topic Cluster가 구독 전환을 만들었을 가능성
특정 Section 구조가 Retention Drop을 만들었을 가능성
특정 언어 버전의 성과가 더 높았을 가능성
```

Memory 확정은 Learning Engine 또는 Memory Engine이 담당한다.

Analytics Engine은 Memory를 직접 확정하지 않는다.

---

# 39. Error Types

Analytics Engine의 Error Type:

```text
AnalyticsInputMissingError
PublishedRecordMissingError
VideoIdMissingError
MetricsInputMissingError
MetricsValidationError
CheckpointError
RawMetricsError
PerformanceSummaryError
PredictionComparisonError
RetentionAnalysisError
TrafficSourceAnalysisError
RevenueAnalysisError
LanguagePerformanceError
AnalyticsReportError
AnalyticsValidationError
AnalyticsHandoffError
```

Error 예시:

```json
{
  "error_type": "MetricsInputMissingError",
  "message": "24h metrics are not available yet.",
  "project_id": "20260710-093500-future-million-year-human",
  "stage": "ANALYTICS",
  "severity": "LOW",
  "suggested_fix": "Wait until the 24h checkpoint or enter manual metrics.",
  "created_at": "2026-07-11T10:00:00"
}
```

---

# 40. Implementation Classes

Claude Code는 다음 클래스 또는 동등한 구조를 구현해야 한다.

```text
AnalyticsEngine
AnalyticsInputLoader
AnalyticsInputValidator
PublishedRecordLoader
AnalyticsStateManager
ManualMetricsInputLoader
RawMetricsValidator
MetricsNormalizer
CheckpointManager
PerformanceSummaryBuilder
PredictionComparisonBuilder
CTRAnalyzer
RetentionAnalyzer
TrafficSourceAnalyzer
RevenueAnalyzer
LanguagePerformanceAnalyzer
BaselineComparator
AnalyticsReportBuilder
AnalyticsValidator
LearningHandoffBuilder
PortfolioAnalyticsSignalBuilder
AnalyticsMemoryCandidateBuilder
AnalyticsErrorReporter
```

---

# 41. Suggested Code Mapping

문서와 코드 매핑 방향:

```text
docs/29_ANALYTICS_ENGINE.md
→ engines/analytics/
```

예시 구조:

```text
engines/
└── analytics/
    ├── analytics_engine.py
    ├── analytics_input_loader.py
    ├── analytics_input_validator.py
    ├── published_record_loader.py
    ├── analytics_state_manager.py
    ├── manual_metrics_input_loader.py
    ├── raw_metrics_validator.py
    ├── metrics_normalizer.py
    ├── checkpoint_manager.py
    ├── performance_summary_builder.py
    ├── prediction_comparison_builder.py
    ├── ctr_analyzer.py
    ├── retention_analyzer.py
    ├── traffic_source_analyzer.py
    ├── revenue_analyzer.py
    ├── language_performance_analyzer.py
    ├── baseline_comparator.py
    ├── analytics_report_builder.py
    ├── analytics_validator.py
    ├── learning_handoff_builder.py
    ├── portfolio_analytics_signal_builder.py
    ├── analytics_memory_candidate_builder.py
    └── analytics_error_reporter.py
```

---

# 42. Main Public Operations

Analytics Engine은 최소 다음 작업을 제공해야 한다.

```text
run_analytics(project_id)
load_analytics_inputs(project_id)
validate_analytics_inputs(project_id)
load_published_record(project_id)
check_analytics_state(project_id)
load_manual_metrics(project_id, checkpoint)
validate_raw_metrics(project_id)
normalize_metrics(project_id)
build_performance_summary(project_id)
compare_prediction_to_actual(project_id)
analyze_ctr(project_id)
analyze_retention(project_id)
analyze_traffic_sources(project_id)
analyze_revenue(project_id)
analyze_language_performance(project_id)
compare_to_channel_baseline(project_id)
build_analytics_report(project_id)
validate_analytics_outputs(project_id)
build_handoff_to_learning(project_id)
build_portfolio_analytics_signal(project_id)
```

각 작업은 다음을 지켜야 한다.

```text
Published Record 확인
Checkpoint 명확화
Raw Metrics 보존
Growth Prediction과 비교
Quality Report와 연결
데이터 신뢰도 표시
과도한 단정 금지
Learning Engine이 사용할 수 있는 구조 생성
로그 기록
Error 발생 시 구조화된 Error 기록
```

---

# 43. v1.0 Minimal Implementation

v1.0에서 반드시 구현해야 하는 최소 기능:

```text
Published Record 로드
Analytics 상태 확인
Manual Metrics 입력 구조 지원
Raw Metrics 저장
Metrics 기본 검증
Performance Summary 생성
Growth Prediction과 실제 지표 비교
CTR 기본 분석
Retention 기본 분석
Subscriber Conversion 기본 분석
Revenue 기본 기록
analytics_report.json 생성
Learning Engine Handoff 생성
Analytics Validation 수행
```

v1.0에서 하지 않아도 되는 것:

```text
YouTube Analytics API 자동 연동
실시간 성과 대시보드
정밀 Retention Graph 자동 분석
고급 ML 성과 예측
자동 Metadata 수정
자동 Thumbnail 교체
자동 A/B 테스트 실행
수익 보장
```

v1.0에서는 게시 후 성과를 수동/반자동으로 안정적으로 기록하고 Learning에 넘길 수 있는 구조를 만드는 것이 우선이다.

---

# 44. Acceptance Criteria

이 문서가 구현되면 시스템은 다음을 수행할 수 있어야 한다.

```text
Published Record를 로드할 수 있다.
게시 전이면 Analytics 대기 상태를 만들 수 있다.
Manual Metrics 입력을 받을 수 있다.
Raw Metrics를 저장할 수 있다.
Checkpoint를 관리할 수 있다.
Performance Summary를 생성할 수 있다.
Growth Prediction과 실제 성과를 비교할 수 있다.
CTR 분석을 수행할 수 있다.
Retention 기본 분석을 수행할 수 있다.
Subscriber Conversion을 기록할 수 있다.
Revenue 데이터를 기록할 수 있다.
analytics_report.json을 생성할 수 있다.
Learning Engine으로 Handoff를 만들 수 있다.
Analytics Validation 실패 시 LEARNING Stage 진행을 막을 수 있다.
```

---

# 45. Non Goals

v1.0에서 Analytics Engine이 하지 않는 것:

```text
YouTube API 자동 수집 필수 구현
실시간 대시보드 구현
자동 영상 수정
자동 제목 변경
자동 썸네일 교체
자동 A/B 테스트
성과 원인 단정
실제 수익 보장
Learning 결론 직접 확정
Memory 직접 확정
```

v1.0에서는 실제 성과 데이터를 구조화하고 Growth 예측과 비교하여 Learning으로 넘기는 것이 핵심이다.

---

# 46. Critical Analytics Rules

반드시 지켜야 할 규칙:

```text
1. Analytics Engine은 Published Record 없이 실행 완료하지 않는다.

2. video_id 또는 video_url이 없으면 Analytics는 대기 상태가 된다.

3. Raw Metrics는 원본 형태를 보존한다.

4. Checkpoint를 명확히 기록한다.

5. 수동 입력 데이터는 collection_mode를 manual로 기록한다.

6. 데이터가 부족하면 UNKNOWN 또는 LOW confidence로 표시한다.

7. 초기 데이터를 과도하게 해석하지 않는다.

8. Growth Prediction과 Actual Metrics를 비교해야 한다.

9. Quality Report와 성과의 관계를 추적해야 한다.

10. Revenue는 보장이 아니라 실제 기록으로만 다룬다.

11. Analytics Engine은 게시된 영상을 직접 수정하지 않는다.

12. Analytics Engine은 Memory를 직접 확정하지 않는다.

13. Learning Engine이 사용할 수 있는 Handoff를 생성해야 한다.

14. Analytics Validation 실패 시 Learning Stage로 넘어가지 않는다.

15. 중요한 Analytics 판단은 Report와 Handoff에 기록한다.
```

---

# 47. Final Principle

Analytics Engine은 ADOS가 현실과 만나는 지점이다.

Growth는 예측하고,

Publishing은 게시를 준비하고,

Analytics는 실제 결과를 기록한다.

좋은 Analytics는 숫자를 모으는 데서 끝나지 않는다.

좋은 Analytics는 예측이 맞았는지 확인하고,

성과가 왜 나왔는지 조심스럽게 추정하고,

다음 영상에서 무엇을 반복하고 무엇을 피해야 하는지 Learning으로 넘긴다.

Analytics Engine의 목적은 성과를 자랑하거나 실패를 탓하는 것이 아니다.

Analytics Engine의 목적은 실제 데이터를 통해 CHUNG COMPANY의 콘텐츠 시스템이 점점 더 정확하게 판단하고 더 좋은 영상을 만들 수 있게 하는 것이다.
