# 35_AI_DOCUMENTARY_ENGINE_V1.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: AI Documentary Engine v1 — Premium Documentary Direction Layer  

---

# 1. Purpose

이 문서는 ADOS의 AI Documentary Engine v1(연출 계층)을 정의한다.

지금까지의 파이프라인은 SC001 hook / SC002 explanation / SC003 ending +
이미지 3장 구조의 기술 검증용 트라이얼이었다. 이 계층은 그것을
"넷플릭스 미래 다큐멘터리" 급 기획 엔진으로 끌어올린다.

목표 문장은 하나다.

```text
우리 채널 영상은 "AI가 만든 영상"처럼 보이면 안 된다.
"넷플릭스에서 만든 미래 다큐멘터리"처럼 보여야 한다.
```

이 계층은 연출(Direction)을 업그레이드하는 계층이지,
Provider 자동화를 업그레이드하는 계층이 아니다.

관련 구현:

```text
config/documentary_engine.yaml
engines/documentary/documentary_bible.py
engines/documentary/asset_mix_planner.py
engines/documentary/shot_planner.py
engines/documentary/prompt_blueprint_engine.py
engines/documentary/flagship_episode_planner.py
scripts/run_documentary_engine_v1_demo.py
tests/test_documentary_engine_v1.py
```

---

# 2. Why AI Video Should Not Be Overused

Kling / Runway / Luma / Pika 등 모든 AI 영상은 5초 구간은 훌륭하지만,
20~30초 이상 이어지면 시청자가 "AI 같다"를 느끼기 시작한다.

또한 전체를 AI 영상으로 만들면 비용이 폭발한다.

```text
25분 전부 AI 영상  → 300 Scene → 300 영상 → 비용 폭발
60 영상 + 240 이미지 → 거의 티 안 남 → 오히려 더 프리미엄해 보임
```

영화도 같은 방식이다 — 마블도 계속 CG가 아니다.
사람 → 풍경 → 클로즈업 → 손 → 눈 → 하늘 → CG → 사람으로 계속 바뀐다.

---

# 3. Scene Change Principle (핵심 원칙)

```text
사람들은 "영상"을 보는 게 아니다.
"장면 전환(Scene Change)"을 본다.
```

5초 영상 → 2초 이미지 → 4초 영상 → 3초 이미지 → 6초 지도 → 5초 뉴스 화면
의 혼합이, 30초 영상 하나보다 훨씬 비싸 보인다.

사람은 움직임보다 스토리를 본다. 넷플릭스 다큐도 실제로는
정적인 장면이 훨씬 많다.

```text
영상       = 영화 (감정·임팩트)
이미지     = 설명
인포그래픽 = 이해
텍스트     = 강조
```

모든 것을 움직이게 만드는 것이 목표가 아니라,
시청자의 감정이 움직이게 만드는 것이 목표다.

---

# 4. Recommended 25-Minute Asset Ratio

25분 기준 자산 비율 (config/documentary_engine.yaml):

| 요소 | 비율 | 이유 |
|---|---|---|
| AI 영상 (Kling 등) | 20~25% | 감정과 임팩트가 필요한 장면만 사용 |
| Midjourney 이미지 + 카메라 무빙 | 50~60% | 가장 자연스럽고 비용 효율적 |
| 인포그래픽/지도/타임라인/UI/홀로그램 | 10~15% | 정보 전달과 리듬 변화 |
| 텍스트·숫자·강조 연출 | 5~10% | 핵심 메시지와 몰입 유지 |

구간별 전략 (25분 기준):

```text
Intro      1분   → 100% 영상 (임팩트)
본론       15분  → 70% 이미지 / 30% 영상
클라이맥스 5분   → 70% 영상 / 30% 이미지
엔딩       4분   → 거의 이미지 + 음악
```

이유: 사람은 처음과 끝만 기억한다. 돈도 엄청 절약된다.

담당 엔진: `AssetMixPlanner` → `direction/asset_mix_plan.json`

---

# 5. Scene-to-Shot Breakdown

한 씬 = 이미지 1장이 아니다. 영화는 Scene 하나를 여러 Shot으로 쪼갠다.

```text
Shot1  Ultra Wide   도시 전체    5초
Shot2  발            걸어감      2초
Shot3  헬멧          클로즈업    3초
Shot4  어깨 뒤                  5초
Shot5  드론샷                   3초
Shot6  눈            클로즈업    2초
Shot7  기지          Wide       4초
```

갑자기 영화가 된다.

담당 엔진: `DocumentaryShotPlanner` → `direction/documentary_shot_list.json`

각 샷 필드:

```text
shot_id / scene_id / order / duration_seconds
asset_type: ai_video | image_camera_movement | infographic | text_emphasis
narrative_function: hook | explanation | transition | emotional_beat | evidence | climax | ending
camera_type / lens / movement
subject_type: human | city | hand | eye | sky | planet | map | ui | hologram | object_detail
visual_motif / color_palette / prompt_intent / no_text_risk / notes
```

---

# 6. Shot Count and Duration Rules

shot_duration_rules (config/documentary_engine.yaml):

```text
ai_video_max_seconds: 5        ← AI 영상은 절대 5초 초과 금지
image_shot_seconds_min: 2
image_shot_seconds_max: 6
infographic_seconds_min: 4
infographic_seconds_max: 10
text_emphasis_seconds_min: 2
text_emphasis_seconds_max: 5
```

주의 — 샷 개수에 대한 의도적 결정:

초기 스펙은 25분 기준 120~180샷을 예상했지만, 위 shot_duration_rules를
그대로 지키면 평균 샷 길이가 약 4.8초가 되어 25분 기준 약 280~330샷이
생성된다. 두 기준이 충돌할 때 이 엔진은 **shot_duration_rules(장면 전환
원칙)를 우선**한다. 샷 수를 줄이고 싶으면 config의 max 값을 올리면 된다
(예: image_shot_seconds_max를 10으로 → 3분 트라이얼 실측처럼 샷당 ~11초).

---

# 7. Shot Variety Principle

모든 장면이 같은 카메라면 절대 넷플릭스처럼 보이지 않는다.
"뒤에서 사람 → 넓은 화면 → 뒤에서 → 넓은 화면" 반복은 금지다.

Camera Bible (11종):

```text
ultra_wide_establishing (24mm) / close_up (85mm) / extreme_close_up (100mm macro)
drone_orbit (35mm) / over_the_shoulder (50mm) / side_profile (50mm)
pov (28mm) / low_angle (35mm) / high_angle (35mm)
macro_detail (100mm macro) / handheld_tracking (35mm)
```

피사체도 계속 바뀌어야 한다:

```text
도시 → 발 → 손 → 헬멧 → 우주 → 기지 → 하늘 → 사람 → UI → 지도
```

ShotPlanner는 서로소 보폭(coprime stride) 순환으로 인접 샷의
카메라/피사체 반복을 결정적으로(난수 없이) 방지한다.

검증 규칙:
- 한 카메라 타입이 전체 샷의 40%를 초과하면 FAIL
- 카메라 타입 4종 미만이면 FAIL
- 피사체 타입 5종 미만이면 FAIL
- ai_video 샷이 5초를 초과하면 FAIL

---

# 8. Visual Motif / Character / Camera / Color Bible

많은 AI 유튜브 채널이 놓치는 부분 — 반복되는 비주얼 모티프를 만들면
시청자는 몇 초만 봐도 "아, 이 채널 영상이다"라고 인식한다.

담당 엔진: `DocumentaryBibleEngine` → `channels/{channel_id}/documentary_bible.yaml`

```text
visual_motifs:            earth_hologram / hud_year_display / simulation_start_opening
                          / cyan_orange_grade / atmosphere_particles
recurring_opening_motif:  매 에피소드 동일한 오프닝 애니메이션
color_bible:              earth=blue / mars=orange / moon=gray / future=cyan
                          / danger=red / memory=warm / master_grade=cyan_orange_dark
camera_bible:             #7의 11종
character_bible:          future_human_type_a (190cm, transparent bio skin,
                          no visible pupils, nano fabric, calm, slow confident)
                          → 100편 동안 캐릭터 일관성 유지
forbidden_visual_patterns: 같은 카메라 3연속 / 뒷모습 와이드 반복 / 프레임 내
                          읽을 수 있는 텍스트 / 5초 초과 연속 AI 영상
```

---

# 9. Documentary Prompt Template

프롬프트는 "문장 하나 = 이미지 하나"가 아니다. 필드를 분리해 조립한다.

담당 엔진: `PromptBlueprintEngine` → `prompts/midjourney_prompt_blueprints.json`

```text
Subject:       Transparent cybernetic human
Environment:   Megacity with floating architecture
Camera:        Wide establishing shot
Lens:          24mm
Lighting:      Golden sunrise
Atmosphere:    Morning mist
Mood:          Hopeful but mysterious
Composition:   Centered composition
Film:          ARRI Alexa 65, IMAX documentary, Kodak Vision3
Aspect Ratio:  16:9
```

규칙:
- 씬당 제네릭 프롬프트 1개 금지 — **샷당** 블루프린트를 만든다.
- no-text 안전: 책/종이/화면/UI/간판/번호판/인용 텍스트 금지,
  필요한 경우 시각적 메타포로 치환한다.
- 모든 final_prompt는 `--no text, letters, ...` negative prompt를 포함한다.
- infographic / text_emphasis 샷은 MJ가 아니라 내부 그래픽으로 제작하므로
  블루프린트 생성 대상에서 제외하고 `skipped_by_asset_type`에 기록한다.

---

# 10. First Flagship Episode Criteria

첫 영상은 자동화 성능 과시용이 아니다. 채널 방향성 + 제작 기준 +
검증 루프 확정용이다.

```text
첫 영상 = 80점짜리 자동화 결과물   ❌
첫 영상 = 95점짜리 수동+ADOS 혼합 레퍼런스 ✅
```

담당 엔진: `FlagshipEpisodePlanner` → `reports/flagship_episode_blueprint.json`

- target_quality_score: **95** (최소 90, 진짜 목표 95)
- intro/middle/climax/ending 전략은 #4의 구간별 전략을 따른다
- required_human_review_focus에 "자막이 최종 영상에 실제로 보이는지"를
  반드시 포함한다 (docs/36 참고)

---

# 11. Data Flow

```text
project.json + story/story_outline.json (+ direction/direction_plan.json)
        ↓
AssetMixPlanner        → direction/asset_mix_plan.json
        ↓
DocumentaryShotPlanner → direction/documentary_shot_list.json
        ↓
PromptBlueprintEngine  → prompts/midjourney_prompt_blueprints.json
        ↓
FlagshipEpisodePlanner → reports/flagship_episode_blueprint.json

채널 레벨 (프로젝트와 독립):
DocumentaryBibleEngine → channels/{channel_id}/documentary_bible.yaml
```

---

# 12. Non-Goals (v1)

```text
실제 외부 API 호출 없음 (Midjourney/Kling/Typecast 호출 금지)
실제 렌더링 없음 (렌더링·자막 번인은 docs/36 Composition 계층 담당)
업로드 없음
실제 미디어 파일 생성 없음
난수 사용 없음 — 모든 산출물은 결정적(deterministic)이고 테스트 가능해야 한다
```
