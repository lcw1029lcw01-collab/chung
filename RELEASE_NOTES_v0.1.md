# ADOS v0.1 Skeleton — Release Notes

Release name: **ADOS v0.1 Skeleton**
Owner: CHUNG COMPANY

---

## Scope

이번 릴리스에 포함된 것:

- **Full dummy lifecycle** — INITIALIZED → RESEARCH → KNOWLEDGE → STORY → DIRECTION
  → TIMELINE → VISUAL → MOTION → VOICE → SUBTITLE → EDITING → QUALITY → AUTO_FIX
  → PACKAGE → READY → PUBLISHED → ANALYTICS → LEARNING → AI_EVOLUTION → COMPLETE
  (20단계 전체를 dummy 모드로 완주, Growth는 advisory 출력)
- **Provider placeholders** — Midjourney / Midjourney Video / Typecast
  (NOT_SUBMITTED, 외부 호출 없음)
- **Asset registry** — 자산 요구사항·제작 자산 manifest·준비도 보고
  (메타데이터만 기록, 파일 복사 없음)
- **Human review gate** — 6개 체크포인트(STORY/DIRECTION/VISUAL/EDITING/QUALITY/UPLOAD)
  승인/반려 관리
- **Final quality gate** — 4개 차단 규칙 기반 업로드 가능 판정
- **Upload preparation** — YouTube 메타데이터 패키지·준비도 체크리스트·수동 업로드 안내
- **Operation reporting** — 실행 보고서·산출물 인벤토리·운영/인수인계 보고서

## Explicit Non-Goals (이번 릴리스에서 하지 않는 것)

- ❌ 실제 Midjourney 호출 없음
- ❌ 실제 Midjourney Video 호출 없음
- ❌ 실제 Typecast 호출 없음
- ❌ 실제 영상 렌더링 없음
- ❌ 실제 YouTube 업로드 없음

## Main Commands

```bash
python scripts/run_full_dummy_pipeline.py
python scripts/run_upload_preparation_demo.py
python scripts/run_provider_placeholder_demo.py
```

## Safety Guarantees

- dummy 파이프라인에서 `upload_ready`는 **false를 유지**한다.
- provider placeholder는 **외부 호출을 하지 않는다** (`external_call_made: false`).
- 시뮬레이션 게시는 실제 업로드를 가장하지 않는다
  (`publication_status: SIMULATED_NOT_UPLOADED`, `video_url: null`).
- 최종 업로드 준비 완료(`upload_ready: true`)는 다음을 **모두** 충족해야만 가능하다:
  1. 실제 자산 등록 (실존 파일)
  2. 사람 검토 체크포인트 전체 승인
  3. 최종 품질 게이트 PASS
  4. 실제 최종 영상 자산 존재

## Current Test Count

**123 / 123 passing** (`python -m unittest discover -s tests`)

## Next Phase

- Provider integration design
- Manual / semi-automated Midjourney workflow
- Typecast workflow
- Real asset registration
- Final manual upload package
