# 32_PROVIDER_INTEGRATION_V0_2.md

Version: 0.2.0
Status: Active
Owner: CHUNG COMPANY
Priority: High

---

# 1. Purpose

이 문서는 ADOS v0.2의 Provider 통합 준비 계층을 정의한다.

v0.1 Skeleton은 전체 라이프사이클을 dummy로 완주했다.
v0.2는 실제 Provider(Midjourney, Midjourney Video, Typecast)와
**수동/반자동으로** 연결될 수 있도록 준비하는 단계다.

이 단계에서 ADOS는:

1. Provider job 요청을 생성하고,
2. 수동 Provider 작업을 추적하고,
3. Midjourney / Midjourney Video / Typecast용 프롬프트·작업 팩을 내보내고,
4. 외부에서 생성된 자산을 메타데이터로 가져오고,
5. 가져온 자산을 Asset Registry에 연결하고,
6. 실자산 + 사람 검토 + 최종 게이트 통과 전까지 upload_ready를 false로 유지한다.

---

# 2. Scope

- Provider job queue 및 job 레코드 관리
- Provider별 수동 작업 팩(export pack) 생성
- 외부 생성 자산의 메타데이터 import
- Asset Registry 연결
- 기존 업로드 게이트 규칙 유지

---

# 3. Non-Goals

v0.2에서 하지 않는 것:

```text
실제 Midjourney API 호출
실제 Midjourney Video API 호출
실제 Typecast API 호출
실제 영상 렌더링
실제 YouTube 업로드
API 키 저장
자동 production_ready 승격
```

---

# 4. Provider Modes

모든 Provider는 다음 모드 중 하나를 가진다.

## placeholder

외부 호출 없이 NOT_SUBMITTED 기록만 반환한다. (v0.1 기본)

## manual

ADOS가 작업 팩을 내보내고, 사람이 외부 도구에서 직접 생성한 뒤,
결과 자산을 메타데이터로 등록한다. (v0.2 기본)

## semi_automated

일부 단계(프롬프트 준비, 상태 추적)는 자동, 생성·확인은 사람이 수행한다.

## api_future

향후 실제 API 통합을 위한 예약 모드. v0.2에서는 활성화하지 않는다.

모드 설정: `config/provider_modes.yaml`

---

# 5. Safety Rules

```text
1. 저장소에 secret(API 키·토큰)을 두지 않는다.
2. 테스트에서 외부 호출을 하지 않는다.
3. 실제 업로드를 하지 않는다.
4. production_ready를 자동으로 true로 만들지 않는다.
5. 모든 job/export/import 레코드는 external_call_made: false를 유지한다.
```

---

# 6. Provider Flow

```text
visual_prompts.json (및 motion/voice plan)
↓
Provider Job Request (providers/job_queue.json)
↓
Export Pack 생성 (providers/exports/)
↓
사람이 외부 도구에서 수동 생성 (Midjourney / Typecast)
↓
Asset 메타데이터 Import (providers/imports/)
↓
Asset Registry 연결 (assets/production_asset_manifest.json)
↓
Human Review (reports/human_review_checkpoints.json)
↓
Final Quality Gate (reports/final_upload_gate.json)
```

---

# 7. Provider Job Lifecycle

Job 상태:

```text
CREATED
↓
EXPORTED
↓
WAITING_MANUAL_WORK
↓
ASSET_IMPORTED
↓
REVIEW_REQUIRED
↓
COMPLETED
```

취소 시: `CANCELLED`

---

# 8. Provider-Specific Notes

## 8.1 Midjourney (image)

- 입력: `prompts/visual_prompts.json`, `assets/images/visual_plan.json`
- Export: `providers/exports/midjourney_prompt_pack.json`
- 사람이 Midjourney에서 프롬프트를 실행하고 결과 이미지를 저장한다.
- 결과는 ProviderImporter로 메타데이터 등록 후 Asset Registry에 연결한다.

## 8.2 Midjourney Video (motion)

- 입력: `assets/motion/motion_plan.json`
- Export: `providers/exports/midjourney_video_prompt_pack.json`
- 원본 이미지를 기반으로 모션 클립을 수동 생성한다.

## 8.3 Typecast (voice)

- 입력: `assets/audio/voice_plan.json`, `story/script_draft.json`
- Export: `providers/exports/typecast_script_pack.json`
- 블록별 나레이션을 Typecast에서 수동 생성하고 오디오 파일을 저장한다.

---

# 9. Manual Asset Import Workflow

```text
1. 외부 도구에서 자산 생성 완료
2. ProviderImporter.import_provider_asset_metadata()로 메타데이터 기록
   (파일 복사 없음, exists 여부만 확인)
3. link_import_to_asset_registry()로 Asset Registry에 등록
   (copied: false, production_ready: false 유지)
4. AssetRegistry.create_asset_readiness_report()로 준비도 갱신
```

---

# 10. Review and Upload Gate Rules

v0.1의 게이트 규칙을 그대로 유지한다.

`upload_ready: true`가 되려면 다음을 **모두** 충족해야 한다:

```text
1. 실제 자산 등록 (실존 파일)
2. 사람 검토 체크포인트 전체 승인
3. 최종 품질 게이트 PASS
4. 실제 최종 영상 자산 존재
```

Provider job·export·import 어느 단계도 upload_ready를 직접 변경하지 않는다.

---

# 11. v0.2 Completion Criteria

```text
1. Provider job queue가 3개 Provider의 job을 생성·추적할 수 있다.
2. 3종 export pack이 수동 작업용으로 생성된다.
3. 외부 생성 자산을 메타데이터로 import하고 Asset Registry에 연결할 수 있다.
4. 전체 흐름에서 external_call_made가 false로 유지된다.
5. 실자산·검토·게이트 충족 전 upload_ready가 false로 유지된다.
6. 모든 동작이 테스트로 검증된다.
```
