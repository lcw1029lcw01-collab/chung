# 다국어 자막 · 경쟁 채널 스캐너 · SEO 심리 트리거 5축 설계

- 날짜: 2026-07-17
- 상태: 승인됨 (사용자 approve)
- 관련 코드: `engines/composition/`, `engines/research/`, `engines/seo/`, `scripts/`
- 관련 문서: docs/17_RESEARCH_ENGINE.md(#15 competitors), docs/24_SUBTITLE_ENGINE.md, docs/37(#5 SEO)
- 출처: 유튜브 강연 「클로드 코드 활용법 9가지」의 TIP 3(경쟁 분석)·TIP 6(심리 트리거)·TIP 7(다국어 자막)을 ADOS에 맞게 흡수

## 배경 / 문제

1. **다국어 자막 부재** — 자막 엔진 v1은 정확한 타이밍의 한국어 SRT/ASS를 만들지만 해외 시청자
   도달 수단이 없다. 타임코드를 유지한 번역 SRT를 유튜브 자막 탭에 올리면 비용 0으로 해외
   유입이 생긴다(검증된 사례: 동남아 골프 유입).
2. **데이터 기반 주제 선정 부재** — research/growth/analytics 엔진은 전부 더미 스텁. 경쟁 채널의
   "평균 대비 배수" 신호 없이 감으로 주제를 고르고 있다.
3. **SEO 템플릿에 심리 축 없음** — `seo_engine.py`의 제목/썸네일 템플릿 20개가 전부 주제 서술형.
   5대 심리 트리거(손실공포·호기심은폐·권위증거·효율이득·욕망정체성) 축이 없어 A/B 조 구성에
   논리가 없다.

세 기능은 코드 공유가 없는 독립 작업이다. 구현 순서: ① 다국어 자막 ② 경쟁 스캐너 ③ SEO 5축.

---

## 1. 다국어 자막 (기본 EN + JA, 파이프라인 필수)

### 확정된 결정

- 기본 언어 세트: **영어(en) + 일본어(ja)**. 언어 목록은 인자/설정으로 확장 가능.
- 통합 수준: **파이프라인 필수** — 품질 게이트가 번역 SRT 존재·정합성을 검사한다.
- 번역 주체: **Claude 제작 세션** — 엔진은 잡 내보내기/조립/검증만 하는 결정적 코드.
  LLM·번역 API를 호출하지 않는다 (provider_jobs의 export→fill→import 패턴과 동일).

### 데이터 흐름

```
subtitles/subtitles_ko.srt (문장 단위 나레이션 큐, 리플로우 전)
  → [--export] subtitles/translation_job.json (번역 슬롯 비움)
  → Claude 세션이 translations를 채움
  → [--assemble] subtitles/subtitles_en.srt + subtitles_ja.srt
                + subtitles/translation_report.json (검증 리포트)
  → quality_gate 검사 → 유튜브 스튜디오 자막 탭에 수동 업로드
```

- **원문은 반드시 리플로우 전 문장 단위 큐**를 쓴다. 리플로우된 표시 큐(문장 조각)를 조각별로
  번역하면 어순 차이(한↔영/일)로 품질이 깨진다.
- 번역 SRT는 리플로우/번인하지 않는다 — 소프트 자막은 유튜브 플레이어가 줄바꿈을 처리한다.

### translation_job.json 스키마

```json
{
  "source_lang": "ko",
  "target_languages": ["en", "ja"],
  "source_srt": "subtitles/subtitles_ko.srt",
  "cue_count": 42,
  "translation_notes": [
    "다큐멘터리 내레이션 톤 유지 (구어체 금지)",
    "고유명사는 통용 표기, 숫자·단위는 현지 관례",
    "큐 단위 1:1 번역 — 큐 간 내용 이동 금지"
  ],
  "cues": [
    {
      "index": 1,
      "start_seconds": 0.0,
      "end_seconds": 4.2,
      "source_text": "서기 2100년, 인류는 선택의 기로에 섰습니다.",
      "translations": { "en": null, "ja": null }
    }
  ],
  "created_at": "..."
}
```

### 컴포넌트

`engines/composition/subtitle_translation.py` — 순수 함수만 (파일 IO·네트워크 없음):

- `build_translation_job(cues, target_languages) -> dict` — 위 스키마 생성.
- `assemble_srt(job, lang) -> str` — 타임코드를 **원본 그대로** 복사한 SRT 텍스트.
- `validate_translation_job(job) -> list[str]` — 미번역(null/빈) 큐, 언어 누락을 이슈 목록으로.
- `validate_translated_srt(source_cues, translated_cues, lang) -> dict`
  - 큐 수 일치, 타임코드 원본과 완전 동일, 빈 텍스트 없음.
  - en/ja 텍스트에 한글(가-힣) 잔존 시 FAIL.
  - 리포트 형식은 `VideoComposer.validate_subtitles`와 같은 `{issues, status}` 관례.

`scripts/translate_subtitles.py` — CLI:

- `--export <workspace>` : `subtitles_ko.srt` → `translation_job.json`. 이미 있으면 덮어쓰기 전에
  기존 잡에 채워진 번역이 있으면 보존(재실행 안전).
- `--assemble <workspace>` : 채워진 잡 → 언어별 SRT + `translation_report.json`.
  검증 FAIL이면 SRT를 쓰되 exit code 1 (파이프라인이 감지).
- `--langs en,ja` : 기본값 `en,ja`.

### 파이프라인 통합

- `scripts/quality_gate.py`에 다국어 검사 추가: `--langs en,ja`(기본값) 각각에 대해
  `subtitles_{lang}.srt` 존재 + `validate_translated_srt` PASS를 점수 항목으로 반영.
  하나라도 실패하면 게이트 FAIL.
- 수동 업로드 가이드 생성기(`engines/manual_trial/manual_trial_guide.py` — 이미
  `subtitles_{lang}.srt`를 자산 목록에 갖고 있음)의 체크리스트에 "유튜브 자막 탭에
  en/ja SRT 업로드" 항목 추가.

### 에러 처리

- 원본 SRT 없음 → `ADOSFileNotFoundError` + suggested_fix.
- 잡 미완성 상태로 `--assemble` → 미번역 큐 인덱스를 나열한 `ADOSValidationError`.

---

## 2. 경쟁 채널 스캐너 (yt-dlp, API 키 불필요)

### 컴포넌트

`engines/research/competitor_scanner.py` — 순수 함수만:

- `parse_flat_playlist(raw: dict) -> dict` — yt-dlp `-J --flat-playlist` 출력을 정규화:
  `{channel_name, channel_url, videos: [{video_id, title, url, view_count, duration_seconds, upload_date}]}`.
  view_count가 없는 항목(멤버십/예정 영상)은 건너뛰고 `skipped_count`에 기록.
- `analyze_channel(parsed, recent_n=25) -> dict` — 최근 N편 기준:
  - `avg_views`, `median_views`, 영상별 `multiple_vs_avg`, `multiple_vs_median`.
  - **신호 판정: `multiple_vs_median >= 2.0` → `signal: "HIGH"`** (바이럴 1편이 평균을 왜곡하므로
    중앙값이 기본, 평균 배수는 병기).
- `build_report(analyses: list[dict]) -> dict` — 채널별 요약 + 전 채널 HIGH 신호를
  `multiple_vs_median` 내림차순으로 랭킹.
- `report_to_csv_rows(report) -> list[list[str]]` — CSV 저장용 평탄화. 컬럼:
  `channel, title, url, view_count, multiple_vs_median, multiple_vs_avg, signal, upload_date, duration_seconds`.

`scripts/scan_competitors.py` — CLI:

- 입력: `python scripts/scan_competitors.py <channel_url> [<channel_url> ...] [--channel <id>] [--recent-n 25]`
  - URL 인자가 없고 `--channel`이 있으면 `channels/<id>/competitors.yaml`의
    `competitors: [{name, url}]` 목록을 사용.
- 실행: 채널당 `yt-dlp -I 1:{recent_n} -J <url>/videos` (범위 지정 전체 메타 추출).
  - 구현 중 변경(2026-07-17): 원래 `--flat-playlist` 방식이었으나, 현행 yt-dlp(2026.06)의
    flat 채널 탭 엔트리는 view_count가 전부 null로 확인되어 범위 전체 추출로 전환.
    조회수·정확한 업로드일을 얻는 대신 채널당 추출이 느리다(영상당 약 4초).
  - 영상 0편 추출은 성공이 아니라 채널 실패로 기록한다 (`failed_channels`).
- 출력: `channels/<id>/research/competitor_scan_YYYYMMDD/` (channel 미지정 시 cwd 하위)
  - `raw_<채널슬러그>.json` (재분석용 원본), `report.json`, `report.csv`.
- 에러 처리: yt-dlp 미설치 → 설치 안내와 함께 실패. 개별 채널 추출 실패 → 경고 후 나머지 계속,
  리포트에 `failed_channels` 기록.

### 한계 (문서화)

- 범위 전체 추출은 영상당 약 4초가 걸린다 — 채널당 최근 25편 기준 1~2분.
  research 배치 도구 특성상 허용하며, 더 빠른 경로가 필요해지면 flat 추출이
  view_count를 다시 제공하는지 재확인 후 fast path를 추가한다.

---

## 3. SEO 심리 트리거 5축

### config/seo_templates.yaml (신설)

```yaml
# 5대 심리 트리거 — 출처: 썸네일 170개 → 20개 구조 압축 강연 자료
triggers:
  loss_fear:        # 금기, 놓침, 기간 한정
    label: "손실·공포"
    ko_titles: [ "...{topic}..." x4+ ]
    en_titles: [ "...{topic_en}..." x4+ ]
    thumbnail_texts: [ ... 1+ ]
  curiosity_gap:    # 미공개, 반전            (구조는 loss_fear와 동일)
  authority_proof:  # 내부자 목격, 수치·데이터  (동일)
  efficiency_gain:  # 시간 확보, 초저가        (동일)
  desire_identity:  # 변신, 특별함             (동일)
```

위 예시는 스키마 축약이다 — 실제 파일은 5축 모두 `label`/`ko_titles`(≥4)/`en_titles`(≥4)/
`thumbnail_texts`(≥1)를 채운다.

- 기존 하드코딩 템플릿 20개(ko/en)를 5축에 재배치·보강. 다큐 채널 신뢰성을 위해 과장·허위형
  카피는 금지하고 축의 심리만 차용한다.
- 템플릿 변수는 기존과 동일: `{topic}`, `{topic_en}`, `{year}`.

### seo_engine.py 변경

- 템플릿을 YAML에서 로드. 파일 없으면 `ADOSFileNotFoundError` (config 필수).
- `title_candidates_ko/en`, `thumbnail_text_candidates` 항목을 `{text, trigger}` dict로 확장.
- 신규 `ab_test_sets`: 서로 다른 축끼리 짝지은 A/B 3세트. 결정적 규칙 —
  축 고정 순서 `[loss_fear, curiosity_gap, authority_proof, efficiency_gain, desire_identity]`에서
  `(1축 첫 템플릿 vs 2축 첫), (3축 첫 vs 4축 첫), (5축 첫 vs 1축 둘째)`.
- `seo_mode: "formula_v2_triggers"`로 갱신.
- 검증 갱신: 5축 전부 존재, 축당 ko/en 각 ≥3, 총 ≥20(언어별), 태그 값이 5축 안에 있는지.
- config 내용 오류는 raw KeyError가 아니라 `ADOSValidationError`로 승격한다 —
  축당 개수 부족은 로더(load 시점)에서, 템플릿 변수 오타는 포맷 시점 헬퍼에서 잡는다.
- 다운스트림 소비처(`title_candidates_*` 등 참조하는 코드·테스트)를 grep해서 함께 수정.

---

## 테스트 전략 (TDD, 네트워크 없음)

- `tests/test_subtitle_translation.py` — 잡 생성/보존 병합/조립(타임코드 불변)/검증(큐 수·타임코드·
  빈 텍스트·한글 잔존) 단위 테스트 + 더미 번역 라운드트립 통합 테스트.
- `tests/test_competitor_scanner.py` — 픽스처 flat-playlist JSON으로 파싱/배수 계산/신호 판정/
  랭킹/CSV 평탄화. view_count 결측·빈 채널 에지 케이스.
- SEO — 기존 SEO 테스트를 5축 스키마로 갱신 + ab_test_sets 결정성·검증 규칙 테스트.
- 실행: 기존 249개 테스트 전부 통과 유지.

## 범위 제외 (YAGNI)

- 유튜브 업로드 자동화(자막 탭 포함) — 수동 유지 (기존 원칙).
- 번역 SRT의 언어별 리플로우·번인, 국가별 썸네일.
- 번역 API(DeepL 등) 연동.
- 내 채널 성과 분석(TIP 2) — 업로드 데이터가 쌓인 뒤 별도 설계.
