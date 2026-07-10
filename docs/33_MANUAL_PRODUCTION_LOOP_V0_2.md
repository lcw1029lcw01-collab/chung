# 33_MANUAL_PRODUCTION_LOOP_V0_2.md

Version: 0.2.0
Status: Active
Owner: CHUNG COMPANY
Priority: High

---

# 1. Purpose

이 문서는 ADOS v0.2의 수동 제작 루프(Manual Production Loop)를 정의한다.

docs/32의 Provider 통합 준비 계층 위에서, 사람이 외부 도구로 생성한
실제 자산을 안전하게 ADOS로 들여오는 폐루프(closed loop)를 제공한다.

이 루프에서 ADOS는:

1. 프로젝트별 수동 자산 워크스페이스를 만들고,
2. 어떤 자산이 필요한지 intake manifest로 명세하고,
3. 사람이 외부에서 생성한 파일을 gitignore된 위치에 두게 하고,
4. 그 파일들을 메타데이터로만 등록하고(복사 없음),
5. Asset Registry에 연결하고,
6. 사람 검토 승인/반려를 거치고,
7. 최종 품질 게이트와 업로드 준비를 재실행하고,
8. 엄격한 조건이 전부 충족되기 전까지 upload_ready를 false로 유지한다.

---

# 2. Scope

- 수동 자산 워크스페이스 생성·검증 (`manual_assets/{project_id}/`)
- Asset intake manifest 생성·갱신·검증
- 외부 생성 파일의 메타데이터 등록 및 Asset Registry 연결
- 사람 검토 체크포인트 승인 흐름 연결
- 최종 품질 게이트·업로드 준비 재실행
- 수동 제작 루프 종합 보고서 생성

---

# 3. Non-Goals

v0.2 수동 제작 루프에서 하지 않는 것:

```text
실제 Midjourney / Midjourney Video / Typecast API 호출
실제 미디어 생성 (이미지·영상·음성·자막 렌더링)
파일 복사·이동 (메타데이터만 기록)
실제 YouTube 업로드
API 키·secret 저장
자산 품질 자동 검증
upload_ready 자동 승격
```

---

# 4. Manual Production Flow

```text
전체 dummy 파이프라인 + 업로드 준비 완주
↓
ManualProductionLoop.prepare_manual_loop()
  - asset_requirements / production_asset_manifest 없으면 생성
  - 수동 워크스페이스 생성 (manual_assets/{project_id}/)
  - asset_intake_manifest.json 생성
  - human review checkpoints 없으면 생성
↓
사람이 외부 도구에서 자산을 생성해 워크스페이스에 배치
↓
ManualIntakeManager.update_asset_intake_item()
  - item별 actual_file_path 기록
↓
ManualProductionLoop.import_ready_assets()
  - ProviderImporter로 메타데이터 import (파일 복사 없음)
  - Asset Registry 연결
↓
사람 검토 승인 (HumanReviewEngine — 명시적 호출만)
↓
ManualProductionLoop.rerun_final_readiness()
  - asset readiness → final quality gate → 업로드 준비 재생성
↓
ManualProductionLoop.create_manual_loop_report()
  - reports/manual_production_loop_report.json
```

---

# 5. Manual Asset Workspace Structure

워크스페이스는 ADOS 루트 아래 `manual_assets/{project_id}/`에 만든다.
`manual_assets/`는 **gitignore 대상**이며 절대 커밋하지 않는다.

```text
manual_assets/{project_id}/
├── workspace_info.json
├── README.md
├── asset_intake_manifest.json
├── images/       ← Midjourney 등에서 생성한 이미지
├── motion/       ← Midjourney Video 등에서 생성한 모션 클립
├── audio/        ← Typecast 등에서 생성한 나레이션 오디오
├── subtitles/    ← 언어별 자막 파일
├── video/        ← 최종 편집 영상
├── thumbnail/    ← 썸네일
└── notes/        ← 사람 작업 메모
```

workspace_info.json 필수 필드:

```text
project_id, project_path, workspace_path, asset_folders,
allow_file_copy: false, upload_ready: false, created_at, disclaimer
```

disclaimer는 항상 다음을 유지한다:
"Manual workspace only. Files placed here are not automatically uploaded."

---

# 6. Asset Intake Manifest Format

`manual_assets/{project_id}/asset_intake_manifest.json`

생성 근거(존재하는 것만 사용):

- `assets/asset_requirements.json` (필수 자산 타입·기대 수량)
- `providers/exports/` export pack (provider hint)
- visual / motion / voice / subtitle / editing plan (item 세분화)

item 형식:

```json
{
  "item_id": "MI001",
  "asset_type": "image",
  "source_stage": "VISUAL",
  "provider_hint": "midjourney",
  "required": true,
  "expected_file_path": "manual_assets/{project_id}/images/SC001_v1.png",
  "actual_file_path": null,
  "status": "WAITING_FOR_HUMAN",
  "notes": null
}
```

item 상태 전이:

```text
WAITING_FOR_HUMAN → FILE_ASSIGNED (actual_file_path 기록)
                  → REGISTERED    (import_ready_assets로 등록 완료)
```

---

# 7. Human Review Workflow

docs/32 및 HumanReviewEngine의 기본 체크포인트 6종을 그대로 사용한다.

```text
STORY_REVIEW / DIRECTION_REVIEW / VISUAL_REVIEW /
EDITING_REVIEW / QUALITY_REVIEW / UPLOAD_REVIEW
```

규칙:

1. 검토 승인은 **명시적 호출**(`approve_required_reviews`)로만 이루어진다.
2. 일반 데모는 검토를 자동 승인하지 않는다. (검토 전용 데모만 승인 수행)
3. 반려(REJECTED)가 하나라도 있으면 upload_allowed_by_human_review는 false다.
4. 검토 승인만으로는 upload_ready가 true가 되지 않는다 — 실자산·최종 영상이
   함께 충족되어야 한다.

---

# 8. Final Upload Readiness Rules

`upload_ready: true`가 되려면 다음을 **모두** 충족해야 한다 (docs/32 #10과 동일):

```text
1. 필수 자산 타입 전부에 대해 실존 파일이 등록됨 (exists: true)
2. 사람 검토 체크포인트 전체 승인
3. 기본 품질 게이트 PASS
4. 실제 최종 영상 자산 존재 (asset_type: video, exists: true)
```

수동 제작 루프의 어떤 단계도 upload_ready를 직접 true로 만들지 않는다.
판정은 오직 FinalQualityGate 재실행으로만 갱신된다.

일반 dummy 데모에서는 실자산이 없으므로 **BLOCKED / upload_ready: false가 정상**이다.
gate가 PASS로 전이하는 것은 테스트 전용 시뮬레이션(placeholder 파일)에서만
증명하며, 이는 실제 제작 준비 완료를 의미하지 않는다.

---

# 9. Safety Rules

```text
1. 외부 API를 호출하지 않는다 (Midjourney / Midjourney Video / Typecast).
2. 업로드하지 않는다.
3. 실제 AI 미디어를 생성하지 않는다.
4. secret을 저장하지 않는다.
5. 파일을 복사하지 않는다 — 메타데이터만 기록한다.
6. manual_assets/는 gitignore를 유지하고 커밋하지 않는다.
7. upload_ready를 강제로 true로 만들지 않는다.
8. 테스트는 임시 디렉터리만 사용하고 실제 channels/·projects/에
   런타임 산출물을 만들지 않는다.
9. 테스트 전용 placeholder 파일은 실제 미디어 품질을 주장하지 않는다.
```

설정: `config/manual_production.yaml` (allow_file_copy: false,
allow_upload: false, require_human_review: true, require_real_final_video: true)

---

# 10. v0.2 Completion Criteria

```text
1. 수동 워크스페이스가 manual_assets/{project_id}/ 아래에 생성된다.
2. asset intake manifest가 asset requirements 기반으로 생성된다.
3. 사람이 배치한 파일을 메타데이터로 등록하고 Asset Registry에 연결할 수 있다.
4. 파일 복사·업로드·외부 호출이 전 과정에서 발생하지 않는다.
5. 일반 데모에서 upload_ready가 false로 유지된다.
6. 검토 승인만으로는 upload_ready가 true가 되지 않는다.
7. 모든 필수 실존 파일 + 전체 검토 승인 조건에서만 gate가 PASS할 수 있음이
   테스트 전용 시뮬레이션으로 증명된다.
8. 수동 제작 루프 보고서가 생성된다.
9. 모든 동작이 테스트로 검증된다.
```
