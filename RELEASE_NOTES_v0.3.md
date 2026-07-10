# ADOS v0.3 Real Manual Trial — Release Notes

Release name: **ADOS v0.3 Real Manual Trial**
Owner: CHUNG COMPANY

---

## Summary

First real file-based manual production trial preparation.

v0.2 수동 제작 루프 위에, 사람이 첫 실제 파일 기반 제작 트라이얼을
안전하게 수행할 수 있는 준비 계층을 추가했다 — 트라이얼 가이드,
결정적 기대 파일 경로, 존재/확장자/최소 크기 검증, 실자산 준비도 보고.

## Scope

이번 릴리스에 포함된 것:

- **Real manual trial guide** — 사람용 트라이얼 가이드·체크리스트
  (`reports/manual_trial_guide.json`, `reports/manual_trial_checklist.json`,
  워크스페이스 `REAL_MANUAL_TRIAL_GUIDE.md`)
- **Manual workspace expected file paths** — 배치 경로를 결정적으로 제시
- **Asset validation config** — `config/asset_validation.yaml`
  (허용 확장자·최소 크기, 업로드/외부 호출 비활성)
- **File existence validation** — 등록 자산의 실존 확인
- **Extension validation** — asset_type별 허용 확장자 검사
- **Minimum file size validation** — asset_type별 최소 크기 검사
- **Real asset readiness report** — `assets/real_asset_readiness_report.json`
  (required/registered/valid 수량, production_ready_candidate)
- **Manual trial prepare / validate / finalize scripts** — 트라이얼 3단계 러너
- **Intake manifest as source of truth** — 가이드 기대 파일명이 intake
  manifest의 expected_file_path를 그대로 따른다

## Main Commands

```bash
python scripts/run_real_manual_trial_prepare.py
python scripts/run_real_manual_trial_validate.py {project_path}
python scripts/run_real_manual_trial_finalize.py {project_path}
```

## Safety Guarantees

- 외부 API 호출 없음
- Midjourney 호출 없음
- Midjourney Video 호출 없음
- Typecast 호출 없음
- YouTube 업로드 없음
- ffmpeg·영상 렌더링 없음
- secret 저장 없음
- 런타임 산출물(`channels/`, `projects/`, `manual_assets/`)은 gitignore 대상
- upload_ready는 다음을 **모두** 충족할 때만 true가 될 수 있다:
  파일 실존 + 허용 확장자 + 최소 크기 통과 + 자산 등록 +
  검토 전체 승인 + 최종 게이트 PASS
- 자산 검증은 존재/확장자/크기만 확인한다 — **미디어 품질은 검증하지 않는다**

## Current Test Count

**172 / 172 passing** (`python -m unittest discover -s tests`)

## Known Limitations

- 실제 미디어 품질 검증 없음
- 매직 바이트/파일 시그니처 검증 없음
- 저작권·사실성 검증 없음
- 자동 업로드 없음
- Provider API 자동화 없음

## Next Phase

- 첫 실제 수동 제작 트라이얼 수행
- 실제 Midjourney / Midjourney Video / Typecast 산출물을 manual_assets/에 배치
- 실제 파일 검증
- 사람 검토 체크포인트 승인
- 최종 수동 업로드 패키지 생성
- (검토) v0.4 자산 포맷 검증·Typecast API 설계
