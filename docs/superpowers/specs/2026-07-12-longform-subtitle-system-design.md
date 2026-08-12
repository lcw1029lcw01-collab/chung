# 롱폼 자막 시스템 설계 (Subtitle Engine v1)

- 날짜: 2026-07-12
- 상태: 승인됨 (사용자 approve)
- 관련 코드: `engines/composition/`, `config/subtitle_styles.yaml`, `channels/*/brand_profile.yaml`
- 관련 문서: docs/36_VIDEO_COMPOSITION_V1.md

## 배경 / 문제

EP01 v3 최종본에서 자막이 (1) 화면 밖으로 **양쪽 짤리고**, (2) **위치가 큐마다 들쭉날쭉**하며,
(3) **글자가 과대**하다. 근본 원인:

- `DEFAULT_SUBTITLE_STYLE`의 `WrapStyle: "2"` = 자동 줄바꿈 없음. 나레이션 SRT의 큐가
  문장 통째(최대 ~26자)로 한 줄이라, 줄바꿈 없이 화면 밖으로 넘침 → 짤림.
- SRT를 `subtitles` 필터에 넘길 때 PlayRes를 지정하지 않아 ffmpeg 기본 384×288 기준으로
  스케일 → Fontsize 20이 1080p에서 ~75~100px로 뻥튀기.
- 큐별 줄 수가 달라 하단 앵커 기준 세로 위치가 불안정.

## 리서치 근거 (롱폼 자막 최적값)

- **넷플릭스 한국어 자막 가이드(표준)**: 줄당 ≤16자(한글), 최대 2줄, 되도록 1줄, 읽기 속도
  초당 ≤12자(성인물), 줄 끝 마침표·쉼표 회피, 2줄일 때 위쪽을 짧게, 하단 중앙.
- **유튜브 롱폼/다큐 리서치**: 1080p 기준 폰트 높이 24~32px+ (다큐는 프레임 높이 ~4.6%),
  산세리프 고정(중간에 폰트 교체 금지=리텐션↓), 의미 단위 줄바꿈, 위치 일관성, 고대비.

## 설계 — 2계층

### 계층 1: 자막 리플로우 (내용 최적화, 순수 함수)

`engines/composition/subtitle_reflow.py`

- 입력: 파싱된 큐 목록(문장 단위). 출력: 표시 최적화된 큐 목록.
- 규칙:
  - 줄당 ≤ `max_chars_per_line`(기본 16, 한글 기준. 영문/공백/문장부호 0.5자), 최대 `max_lines`(기본 2).
  - 줄바꿈은 공백·쉼표 등 의미 경계에서만. 명사구/단어 중간 분할 금지(공백 없는 초장문은
    부득이 하드 분할).
  - 한 큐가 max_lines를 초과하면, 그 큐의 시간대를 글자수 비례로 나눠 여러 큐로 분할.
  - 읽기 속도(초당 12자) 초과 큐는 리포트에 경고. 타이밍은 나레이션 오디오에 묶여 있으므로
    강제 변경하지 않음.
- 핵심 함수: `reflow_cues(cues, max_chars_per_line=16, max_lines=2) -> list[cue]`
  (각 cue에 `lines: list[str]` 추가). 순수 함수라 단위 테스트로 검증.

### 계층 2: 스타일 렌더링 (ASS 직접 생성)

`engines/composition/subtitle_style.py`

- SRT + force_style 대신 `.ass`를 직접 생성해 PlayRes 문제를 원천 제거.
- `[Script Info]`: PlayResX 1920, PlayResY 1080, WrapStyle 0(안전망), ScaledBorderAndShadow yes.
- `[V4+ Styles]`: 해석된 프리셋 1줄(Style: Default,...). 픽셀 정확 폰트 크기.
- `[Events]`: 리플로우된 큐, 줄바꿈은 `\N`.
- 핵심 함수:
  - `load_styles(path) -> dict` : config/subtitle_styles.yaml 로드.
  - `resolve_style(styles, preset_name, overrides) -> dict` : 기본 ← 프리셋 ← 오버라이드.
  - `build_ass(cues, style) -> str` : 완성된 .ass 텍스트.

### 채널별 시스템 (프리셋 라이브러리)

`config/subtitle_styles.yaml`:

```yaml
default: { ... }          # 모든 프리셋의 베이스
presets:
  documentary: { ... }    # 흰글자·얇은외곽선·박스없음·하단중앙 (civ2100)
  punchy:      { ... }    # 크게·반투명박스·정보성
  cinematic:   { ... }    # 작게·여백큼·영화톤
```

`channels/<ch>/brand_profile.yaml`:

```yaml
subtitle_style: documentary
subtitle_overrides: { Fontsize: 50 }   # 선택
```

### documentary 프리셋 값 (1080p)

| 항목 | 값 |
|---|---|
| FontName | Malgun Gothic |
| Fontsize | 50 |
| Bold | 1 |
| PrimaryColour | &H00FFFFFF (흰색) |
| OutlineColour | &H00000000 (검정) |
| Outline | 2.4 |
| Shadow | 1.2 |
| BorderStyle | 1 (외곽선+그림자, 박스 없음) |
| Alignment | 2 (하단 중앙) |
| MarginV | 70 |
| MarginL / MarginR | 160 |
| max_chars_per_line | 16 |
| max_lines | 2 |

## video_composer.py 변경

- `burn_subtitles()`가 `.ass` 입력을 그대로 받도록 확장(파일명만 넘기고 cwd=폴더 유지).
- 신규 `burn_subtitles_from_cues(video, cues, style, output)`: 리플로우 결과 큐 + 해석된 스타일로
  ASS 생성 → 임시 .ass 기록 → 번인. 기존 `verify_burned_subtitles` 재사용.
- 기존 `DEFAULT_SUBTITLE_STYLE` / force_style 경로는 하위호환으로 남기되, 신규 경로가 표준.

## 데이터 흐름

`나레이션 SRT → parse_srt → reflow_cues(16,2) → resolve_style(documentary) → build_ass → .ass → burn → verify`
→ EP01 v3 자막판 재출력.

## 테스트

- `tests/test_subtitle_reflow.py`: 짧은 문장 1줄 유지, 긴 문장 2줄 분할, 초장문 큐 분할,
  의미 경계 줄바꿈, 16자 초과 없음, 읽기속도 경고.
- `tests/test_subtitle_style.py`: 프리셋 로드·해석(오버라이드 우선), ASS 헤더 PlayRes,
  스타일 라인, Events `\N` 직렬화.

## 범위 밖 (YAGNI)

- 키워드 색상 강조(예능형)·애니메이션 효과는 이번 범위 아님. punchy 프리셋에 자리만 남김.
- 영문/다국어 자막 트랙, 자막 자동 번역.
