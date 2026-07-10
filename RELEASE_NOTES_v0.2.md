# ADOS v0.2 Manual Production — Release Notes

Release name: **ADOS v0.2 Manual Production**
Owner: CHUNG COMPANY

---

## Summary

Safe manual/semi-automated provider integration preparation and manual production loop.

v0.1 Skeleton의 dummy 라이프사이클 위에, 실제 Provider(Midjourney / Midjourney Video
/ Typecast)와 **수동/반자동으로** 연결될 수 있는 준비 계층과, 사람이 외부에서
생성한 자산을 안전하게 들여오는 수동 제작 루프를 추가했다.

## Scope

이번 릴리스에 포함된 것:

- **Provider integration preparation** — provider 모드 설정(`config/provider_modes.yaml`),
  manual 모드 기본 (docs/32)
- **Provider job queue** — 3개 provider의 job 생성·상태 추적
  (CREATED → EXPORTED → WAITING_MANUAL_WORK → … → COMPLETED)
- **Manual provider export packs** — Midjourney/Midjourney Video/Typecast용
  복사·붙여넣기 작업 팩 (`providers/exports/`)
- **Provider asset import metadata** — 외부 생성 자산의 메타데이터 import
  (파일 복사 없음, `providers/imports/`)
- **Asset Registry linking** — import된 자산의 production manifest 연결
- **Manual asset workspace** — `manual_assets/{project_id}/` gitignore된
  수동 자산 워크스페이스 (docs/33)
- **Asset intake manifest** — 필요 자산 명세·상태 추적
  (WAITING_FOR_HUMAN → FILE_ASSIGNED → REGISTERED)
- **Human review workflow** — 6개 체크포인트 승인 흐름과 수동 루프 연결
- **Final upload gate** — 4개 차단 규칙 기반 재실행·재판정
- **Upload preparation reports** — 메타데이터 패키지·체크리스트·수동 업로드 안내·
  수동 제작 루프 보고서 재생성
- **TEST ONLY upload gate simulation marker** — 게이트 증명 전용 시뮬레이션 산출물에
  `test_only_simulation: true` / `real_media_verified: false` 마커 기록

## Main Commands

```bash
python scripts/run_provider_integration_prep_demo.py
python scripts/run_manual_production_loop_demo.py
python scripts/run_manual_review_demo.py
python scripts/run_test_only_upload_gate_simulation.py
```

## Safety Guarantees

- 실제 Midjourney 호출 없음
- 실제 Midjourney Video 호출 없음
- 실제 Typecast 호출 없음
- 외부 API 호출 없음
- YouTube 업로드 없음
- secret 저장 없음
- 런타임 산출물(`channels/`, `projects/`, `manual_assets/`)은 gitignore 대상
- 일반 수동 제작 데모는 `upload_ready` **false를 유지**한다
- 검토 전용 데모도 `upload_ready` **false를 유지**한다 (승인만으로는 부족)
- TEST ONLY 시뮬레이션은 출력·placeholder 파일·보고서 마커로
  가짜/테스트 전용임을 명시한다
- 최종 업로드 게이트는 다음을 **모두** 충족할 때만 PASS할 수 있다:
  1. 필수 자산의 실존 파일 등록
  2. 사람 검토 체크포인트 전체 승인
  3. 기본 품질 게이트 PASS
  4. 실제 최종 영상 자산 존재

## Current Test Count

**154 / 154 passing** (`python -m unittest discover -s tests`)

## Known Limitations

- 실제 미디어 생성 없음
- 자산 품질 자동 검증 없음
- 자산 존재 검사는 파일 경로 존재 확인만 수행한다
- Provider 워크플로우는 수동/반자동 준비 단계까지만 지원한다

## Next Phase

- 실제 파일을 사용한 수동 제작 트라이얼
- 자산 품질 검증
- Provider 워크플로우 강화
- 최종 업로드 패키지 정제
- (선택) 실제 API 통합 설계
