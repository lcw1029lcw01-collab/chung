# 36_VIDEO_COMPOSITION_V1.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Video Composition Layer v1 — Subtitle Burn-in and Final Assembly  

---

# 1. Purpose

이 문서는 ADOS의 Composition 계층(VideoComposer)을 정의한다.

배경 — v0.3 실제 수동 트라이얼에서 발견된 문제:

```text
자막 파일(subtitles_ko.srt)은 만들어졌지만
최종 영상에는 자막이 전혀 나오지 않았다.
```

원인: 최종 영상 합성이 시스템 밖(세션 즉석 ffmpeg 빌드)에 있었고,
그 빌드에 자막 번인 단계가 통째로 빠져 있었다. 시스템의 검증 게이트는
"srt 파일이 존재하는가"만 확인했고, 영상 안에 자막이 실제로 보이는지는
아무도 검사하지 않았다.

이 계층은 두 가지를 시스템 안으로 가져온다.

```text
1. 최종 영상 조립 (세그먼트 concat + 나레이션 mux + 자막 burn-in)
2. 자막 가시성 검증 (영상 프레임을 실제로 열어 자막 픽셀을 확인)
```

관련 구현:

```text
engines/composition/video_composer.py
scripts/compose_final_video.py
tests/test_video_composition.py
```

EditingEngine(docs/25)과의 관계: EditingEngine은 조립 **계획**을 만들고,
VideoComposer는 그 계획대로 실제 조립을 **실행**한다. docs/25의 v1.0
Non-Goal("자막 Burn-in 자동 렌더링 제외")은 이 문서로 대체된다 —
번인은 Editing이 아니라 Composition 계층의 책임이다.

---

# 2. Composition Flow

```text
빌드 폴더 (video_list.txt / audio_list.txt / narration.wav / seg*.mp4)
        ↓  concat_from_lists()
무자막 베이스 영상 (base, video+narration)
        ↓  validate_subtitles()        ← SRT 내용 검증 (큐/순서/겹침/커버리지)
        ↓  burn_subtitles()            ← 자막 번인 (libass)
자막 포함 최종 영상
        ↓  verify_burned_subtitles()   ← 자막 가시성 검증 (프레임 밝기 분석)
검증 리포트 (PASS/FAIL)
```

실행 스크립트:

```text
python scripts/compose_final_video.py {workspace_dir} [build_subdir] [lang]
예) python scripts/compose_final_video.py manual_assets/20260710-141033-future-million-year-human notes/build3min ko
```

---

# 3. Windows / 한글 경로 규칙 (중요)

ffmpeg의 `subtitles=` 필터 인자는 필터 그래프 파서를 거치므로
드라이브 콜론(`C:`)과 한글 경로가 그대로 들어가면 깨진다.

이 계층의 강제 규칙:

```text
- subtitles 필터에는 절대 경로를 넣지 않는다.
- 항상 srt가 있는 폴더를 ffmpeg의 cwd로 삼고, 필터에는 파일명만 쓴다.
- 입력/출력 영상 경로는 argv로 전달되므로 한글 절대 경로여도 안전하다.
```

---

# 4. Subtitle Style

기본 스타일 (1080p 기준, libass force_style):

```text
FontName=Malgun Gothic   ← Windows 기본 한글 폰트 (항상 존재)
Fontsize=15
PrimaryColour=&H00FFFFFF (흰색)
OutlineColour=&H00000000 (검은 외곽선)
BorderStyle=1, Outline=1.3, Shadow=0.6
MarginV=40               ← 하단 여백
```

채널 브랜드 폰트(예: GmarketSans)를 쓰려면 burn_subtitles의 style
인자로 FontName을 넘긴다. 폰트가 시스템에 설치되어 있어야 한다.

---

# 4.5. BGM 믹싱 (v1.1)

배경음악(BGM)은 나레이션과 함께 깔린다 — 감독은 음악의 무드까지
결정하지만(docs/38 #3), 실제 트랙은 사람이 음악 생성 AI로 만들어
`bgm_library/`에 둔다. 합성 순서에서 BGM은 **나레이션 mux 후 / 자막
번인 전**에 섞인다 (베이스 영상의 나레이션 위에 얹음).

```text
VideoComposer.mix_bgm(video, bgm, out, ...)
- BGM을 영상 길이에 맞춰 자동 루프 + 시작/끝 페이드
- 나레이션(영상 오디오)을 사이드체인 신호로 사용
  → 말소리가 나오는 구간에서 BGM 음량을 자동으로 내린다 (덕킹)
- 영상 스트림은 재인코딩하지 않는다 (-c:v copy)
```

설정: `config/bgm_library.yaml`
```text
default_track     — bgm_library/의 기본 트랙 (없으면 BGM 생략)
mix.music_gain_db — BGM 기본 음량 (-20)
mix.duck_gain_db  — 나레이션 구간 목표 음량 (-32) → sidechaincompress ratio로 근사
mix.fade_in/out   — 시작/끝 페이드 (초)
```

원칙: 음원이 없으면 BGM 없이 합성된다 (선택). 넣는 순간부터 자동 적용.
검증: 덕킹은 나레이션 구간 vs 무음 구간의 BGM 레벨 차이로 확인한다.

---

# 5. Verification Rules

번인은 성공 주장만으로 끝나지 않는다. 검증을 통과해야 한다.

```text
1. SRT 내용 검증 (번인 전):
   - 큐가 1개 이상 존재
   - 큐 시간이 양수이고 순서대로이며 겹치지 않음
   - 마지막 큐가 영상 길이를 넘지 않음
   - 커버리지(마지막 큐 종료 / 영상 길이) 50% 이상

2. 자막 가시성 검증 (번인 후):
   - 샘플 큐들의 중간 시점에서 번인 전(base)/후 영상의 같은 프레임을
     하단 25% 밴드로 잘라 차분(blend=difference) + signalstats로 비교한다.
   - 자막(흰 글자 + 검은 외곽선)이 있으면 차이 YMAX ≥ 48 이어야 한다.
     밝기 절대값 방식은 밝은 배경(하늘/흰 화면)에서 오탐이 있어 쓰지 않는다.
   - 재인코딩 노이즈는 보통 YMAX 20 이하라 오탐하지 않는다.
   - 하나라도 미달이면 FAIL — 업로드 금지.

3. 길이 검증:
   - 번인 전/후 영상 길이 차이가 0.2초 이내여야 한다.
```

사람 검토 항목(필수): 검증 PASS 후에도 최소 1개 프레임을 눈으로 확인한다
— 한글 글리프가 깨져(tofu) 나오는 경우는 픽셀 검증만으로 잡히지 않을 수 있다.

---

# 6. Upload Package Rules

```text
- 번인판(ko)이 video/final_video.mp4가 된다 (기본 시청 경험).
- 원본 srt(ko/en)는 계속 subtitles/에 유지한다 — YouTube CC 업로드용.
- 완성영상/ 보관함으로의 복사는 여전히 사람이 최종 확인 후 수행한다.
```

---

# 7. Non-Goals (v1)

```text
BGM 믹싱 없음 (나레이션 mux까지만)
씬 전환 효과(크로스페이드 등) 없음 — concat 하드컷
업로드 없음
Ken Burns 세그먼트 생성 자동화 없음 (기존 빌드 세그먼트를 입력으로 받는다)
```
