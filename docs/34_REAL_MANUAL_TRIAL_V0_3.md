# 34_REAL_MANUAL_TRIAL_V0_3.md

Version: 0.3.0
Status: Active
Owner: CHUNG COMPANY
Priority: High

---

# 1. Purpose

이 문서는 ADOS v0.3의 실제 수동 제작 트라이얼 준비 계층을 정의한다.

v0.2 수동 제작 루프(docs/33)는 사람이 배치한 파일을 **존재 여부만으로**
메타데이터 등록했다. v0.3은 사람이 첫 실제 파일 기반 트라이얼을 안전하게
수행할 수 있도록 다음을 제공한다.

1. 프로젝트별 실제 수동 트라이얼 가이드 생성
2. 결정적(deterministic) 기대 파일명·배치 경로 정의
3. 사람이 배치한 실제 파일의 존재·확장자·최소 크기 검증
4. 실제 파일에 대한 사람 검토 체크리스트 생성
5. 엄격한 조건 충족 시에만 최종 수동 업로드 패키지 생성
6. API 호출·업로드는 계속 비활성 유지

---

# 2. Scope

- 실제 수동 트라이얼 가이드 (`reports/manual_trial_guide.json`,
  `reports/manual_trial_checklist.json`, 워크스페이스 마크다운 가이드)
- 자산 파일 검증 (`assets/asset_file_validation_report.json`)
- 실자산 준비도 보고 (`assets/real_asset_readiness_report.json`)
- 검증 설정 (`config/asset_validation.yaml`)
- 트라이얼 준비 → 검증 → 검토 → 최종화 러너

---

# 3. Non-Goals

v0.3에서 하지 않는 것:

```text
실제 Midjourney / Midjourney Video / Typecast API 호출
실제 AI 미디어 생성
미디어 내용 검사 (ffmpeg/코덱/해상도/오디오 분석 없음)
실제 YouTube 업로드
API 키·secret 저장
자산 품질(내용) 자동 검증
upload_ready 자동 승격
```

---

# 4. Difference Between v0.2 and v0.3

```text
v0.2 (docs/33)                          v0.3 (이 문서)
─────────────────────────────────────   ─────────────────────────────────────
파일 존재 여부만 확인                    존재 + 확장자 + 최소 크기 검증
intake manifest 중심                     사람용 트라이얼 가이드·체크리스트 추가
기대 파일명은 intake item 단위           결정적 기대 파일명/경로를 가이드로 제시
게이트 재실행만 제공                     준비→검증→검토→최종화 러너 제공
TEST ONLY placeholder로 게이트 증명      실제 파일 트라이얼을 위한 준비 완성
```

v0.2의 게이트 규칙(docs/32 #10, docs/33 #8)은 그대로 유지된다.
v0.3 검증은 **추가 계층**이며 기존 게이트를 대체하지 않는다.

---

# 5. Real Manual Trial Flow

```text
1. 준비 (prepare)
   scripts/run_real_manual_trial_prepare.py
   - 전체 dummy 파이프라인 + 업로드 준비 완주
   - provider export pack 3종 생성
   - 수동 워크스페이스 + intake manifest 생성
   - 트라이얼 가이드·체크리스트 생성
↓
2. 사람 작업 (human)
   - 가이드의 기대 경로에 실제 파일을 배치
   - intake manifest에 actual_file_path 기록
↓
3. 검증 (validate)
   scripts/run_real_manual_trial_validate.py {project_path}
   - intake 파일 메타데이터 등록 (복사 없음)
   - 파일 존재·확장자·최소 크기 검증
   - 실자산 준비도 보고 생성
   - 최종 게이트·업로드 준비 재실행
↓
4. 사람 검토 승인 (명시적 호출만)
↓
5. 최종화 (finalize)
   scripts/run_real_manual_trial_finalize.py {project_path}
   - 검증·준비도·게이트·업로드 패키지 전체 재실행
   - upload_ready 판정 (강제 승격 없음)
```

---

# 6. Required Human Actions

```text
1. 가이드(REAL_MANUAL_TRIAL_GUIDE.md)의 기대 파일 목록을 확인한다.
2. 외부 도구(Midjourney/Typecast 등)에서 직접 자산을 생성한다.
3. 생성한 파일을 manual_assets/{project_id}/의 기대 경로에 배치한다.
4. intake manifest에 actual_file_path를 기록한다.
5. validate 스크립트로 검증 결과를 확인하고 FAIL 항목을 수정한다.
6. 검토 체크포인트를 승인한다.
7. finalize 후 manual_upload_instructions에 따라 직접 업로드한다.
```

---

# 7. Expected manual_assets Structure

```text
manual_assets/{project_id}/
├── REAL_MANUAL_TRIAL_GUIDE.md
├── images/SC001.png, SC002.png, SC003.png ...
├── motion/SC001.mp4 ...
├── audio/voice_ko.mp3
├── subtitles/subtitles_ko.srt, subtitles_en.srt
├── video/final_video.mp4
└── thumbnail/thumbnail.jpg
```

기대 파일명은 plan(visual/motion/subtitle)과 프로젝트 언어 설정에서
결정적으로 생성된다. 실제 파일은 사람이 직접 만들어 배치한다 —
ADOS는 실제 미디어 파일을 만들지 않는다.

---

# 8. Supported File Types

```yaml
image:     [.png, .jpg, .jpeg, .webp]
motion:    [.mp4, .mov, .webm]
audio:     [.mp3, .wav, .m4a]
subtitle:  [.srt, .vtt, .json]
video:     [.mp4, .mov]
thumbnail: [.png, .jpg, .jpeg, .webp]
```

설정: `config/asset_validation.yaml`

---

# 9. Asset Validation Rules

각 등록 자산에 대해 다음만 검사한다:

```text
1. 파일 존재 (exists)
2. 확장자 허용 여부 (allowed_extensions[asset_type])
3. 파일 크기 >= 최소 크기 (minimum_file_sizes[asset_type])
4. asset_type 지원 여부
```

검사 결과는 `assets/asset_file_validation_report.json`에 PASS/FAIL로 기록한다.

주의:

```text
미디어 내용은 검사하지 않는다. ffmpeg을 실행하지 않는다.
업로드하지 않는다. 존재/확장자/크기 검사만 수행한다.
```

---

# 10. Human Review Rules

v0.2의 검토 규칙(docs/33 #7)을 그대로 따른다.

1. 기본 체크포인트 6종을 사용한다.
2. 승인은 명시적 호출(`approve_real_manual_trial_reviews`)로만 이루어진다.
3. 일반 준비(prepare) 단계는 검토를 자동 승인하지 않는다.
4. 검토 승인만으로는 upload_ready가 true가 되지 않는다.
5. 사람은 검증 보고서(PASS/FAIL)와 실제 파일을 직접 확인한 뒤 승인한다.

---

# 11. Upload Preparation Rules

최종 수동 업로드 패키지는 기존 게이트 규칙이 **실제로** 통과할 때만
upload_ready: true가 된다 (docs/32 #10과 동일):

```text
1. 필수 자산 타입 전부 실존 파일 등록
2. 사람 검토 체크포인트 전체 승인
3. 기본 품질 게이트 PASS
4. 실제 최종 영상 자산 존재
```

v0.3의 `production_ready_candidate`(실자산 준비도 보고)는 참고 지표이며
게이트를 대체하지 않는다. 어떤 단계도 upload_ready를 강제로 true로
만들지 않는다. 업로드는 항상 사람이 수동으로 수행한다.

---

# 12. Safety Rules

```text
1. 외부 API를 호출하지 않는다.
2. 업로드하지 않는다.
3. 실제 AI 미디어를 생성하지 않는다.
4. secret을 저장하지 않는다.
5. 파일을 복사하지 않는다 — 메타데이터만 기록한다.
6. 미디어 내용을 검사하지 않는다 (존재/확장자/크기만).
7. manual_assets/ 등 런타임 산출물은 gitignore를 유지한다.
8. upload_ready를 강제로 true로 만들지 않는다.
9. 테스트는 임시 디렉터리만 사용한다.
```

---

# 13. v0.3 Completion Criteria

```text
1. 트라이얼 가이드·체크리스트·마크다운 가이드가 생성된다.
2. 기대 파일명이 plan 기반으로 결정적으로 생성된다.
3. 등록 자산이 존재/확장자/최소 크기로 검증된다.
4. 실자산 준비도 보고가 required/registered/valid 수량을 기록한다.
5. 파일이 없으면 준비도·게이트가 false/BLOCKED를 유지한다.
6. 유효한 파일 + 전체 검토 승인 시에만 게이트가 PASS할 수 있다.
7. 전 과정에서 외부 호출·업로드·실미디어 생성이 없다.
8. 모든 동작이 테스트로 검증된다.
```
