# 38_DIRECTOR_EMOTION_ENGINE_V1.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Director Engine / Emotion Engine / Story Structure Templates / Provider Rule  

---

# 1. Purpose

이 문서는 ADOS의 정체성을 확정한다.

```text
우리가 만드는 것은 "AI 영상 제작기"가 아니다.
"AI 영화 감독"이다. 엄청 다르다.

우리 목표는 "유튜브 채널"이 아니다.
"AI 콘텐츠 제작 운영체제(OS)"다. 유튜브는 결과물일 뿐이다.
```

99%는 Prompt에 집착한다. 우리는 Prompt보다 Director가 중요하다.

```text
Prompt는 결과물이다. Director가 먼저다.

Story → Emotion → Director → Shot → Prompt → Video
```

감독은 이미지를 만드는 사람이 아니다. 감독은 결정을 내린다:

```text
이번 장면 → 비 와. 카메라는 멀리 있어. 색감은 차갑게.
음악은 조용하게. 5초 후 클로즈업.
```

관련 구현:

```text
config/director_rules.yaml                    ← ADOS의 두뇌 (첫 번째 문서)
config/story_structures.yaml
engines/documentary/director_engine.py
engines/story/story_engine.py                 (구조 템플릿 지원 확장)
tests/test_director_engine.py
```

---

# 2. Emotion Engine (거의 영혼)

장면마다 감정 스코어가 있다:

```text
Scene: 인류 마지막 날
감정: 외로움 80 / 희망 10 / 공포 60 / 신비 70
→ 지배 감정: 외로움
```

지배 감정이 연출을 자동으로 결정한다 (Emotion → 연출 룰):

| 감정 | 카메라 | 색감 | 조명/날씨 | 음악 | 속도 |
|---|---|---|---|---|---|
| 외로움 (loneliness) | Wide (24mm) | Blue | 차가운 새벽, 비/안개 | Low Piano | Slow |
| 공포 (fear) | Close Up (85mm) | Red | 강한 그림자 | Heartbeat + Shaking | Fast |
| 희망 (hope) | Wide (35mm) | Warm Amber | Sunrise | Slow Piano | Slow |
| 신비 (mystery) | Drone Orbit | Cyan | Fog | Ambient Drone | Slow |
| 경이 (wonder) | Low Angle | Cyan/Orange | 볼류메트릭 광선 | Swelling Strings | Medium |
| 평온 (calm) | High Angle (50mm) | Blue Earth | 부드러운 흐림 | Gentle Ambient | Medium |
| 긴장 (tension) | Extreme Close Up | Red | 강한 측광 | Ticking Percussion | Fast |
| 경외 (awe) | Drone Orbit (24mm) | Amber | 역광 | Deep Orchestral | Slow |

전체 룰: `config/director_rules.yaml` — **이것이 ADOS의 두뇌다.**
한국어 감정명(외로움/공포/희망/신비...)은 alias로 자동 인식한다.

그러면 Prompt는 자동으로 나온다:

```text
외로움 → Wide → Blue → Rain → Prompt 자동 생성
```

이게 AI다. Prompt를 사람이 안 쓴다.

---

# 3. Director Engine

담당 엔진: `DirectorEngine` → `direction/director_decisions.json`

```text
입력:  story/scene_script.json (장면별 emotion 또는 emotion_scores)
룰:    config/director_rules.yaml
출력:  장면마다 {dominant_emotion, camera, lens, color, lighting,
              weather, music, pace, movement_hint}
```

결정 규칙:
- 지배 감정 = emotion_scores 최대값 (동점이면 이름순 — 결정적)
- 날씨는 장면 대본이 이미 정했으면 장면이 이긴다 (감독은 각본을 존중한다)
- LLM 호출 없음 — 전부 룰 기반, 결정적, 테스트 가능

하류 통합 (Director가 먼저, 나머지는 따른다):
- **DocumentaryShotPlanner**: 장면 첫 샷의 카메라 = 감독 결정 카메라,
  장면 전체 색감 = 감독 결정 색감
- **PromptBlueprintEngine**: 조명 = 감독 결정 조명, 무드 = 지배 감정
- **MotionPromptEngine**: movement_hint가 모션 프롬프트에 반영
- music/pace는 결정 파일에 기록 — 편집(BGM) 계층이 소비할 예약 필드

---

# 4. Story Structure Templates (멀티 채널 확장)

6개월 뒤 다른 채널을 만들어도 **80%는 같은 코드다. Story Engine만 바뀐다.**

`config/story_structures.yaml`:

```text
documentary_default: hook → setup → development → payoff → ending
beyond_humanity:     hook → conflict → discovery → twist → ending → question
history:             hook → conflict → turning_point → battle → ending
psychology:          question → experiment → science → explanation → conclusion
civilization:        country → history → culture → economy → future
```

`StoryEngine.create_dummy_story(project_path, structure_template="history")`
로 템플릿을 지정한다. 하류(장면 대본→샷 플래너)는 어떤 구조 이름이 와도
동작한다 (미지 구간은 안전 기본값으로 처리).

---

# 5. AI Content Factory — 10 Levels와 ADOS Bible 매핑

대화에서 정의된 전체 지도와 현재 시스템의 대응:

| Level | 이름 | ADOS 구현 위치 |
|---|---|---|
| 1 | Idea | topic_bank / ProjectEngine |
| 2 | Story | StoryEngine + story_structures (docs/19, 38) |
| 3 | Scene | SceneScriptEngine (docs/37) |
| 4 | Direction | **DirectorEngine + director_rules (docs/38)** + ShotPlanner (docs/35) |
| 5 | Image | PromptBlueprintEngine → Midjourney (docs/35) |
| 6 | Video | MotionPromptEngine → midjourney_video (docs/37) |
| 7 | Voice | VoiceEngine + 장면 emotion → Typecast 감정 (docs/23, 37) |
| 8 | Editing | EditingEngine 계획 + VideoComposer 실행 (docs/25, 36) |
| 9 | SEO | SEOEngine (docs/37) |
| 10 | Publishing | PublishingEngine + UploadPreparer (docs/28) |

ADOS Bible 12부 대응: 01 Vision(본 문서 #7) / 02 Story(19+38) / 03 Director(38)
/ 04 Scene(37) / 05 Camera(35 카메라 바이블) / 06 Prompt(35) / 07 Character(35
캐릭터 바이블) / 08 World(37 World Bible) / 09 Emotion(38) / 10 Editing(25+36)
/ 11 SEO(37) / 12 Pipeline(15+34).

---

# 6. Provider Rule (감독 최종 결정 — 구속력 있음)

```text
이미지와 영상은 무조건 미드저니(Midjourney)로 만든다.
```

- 설계 대화에 Kling이 언급되어도, 실제 제작 라인은
  **MJ 이미지 (provider: midjourney) + MJ 애니메이트 (provider: midjourney_video)** 고정.
- 모든 프롬프트 블루프린트 산출물에 provider_hint가 기록된다.
- 이 규칙은 문서 간 충돌 시 다른 문서의 Kling 언급보다 우선한다.
- 예외(다른 프로바이더 사용)는 감독(사용자)의 명시적 지시로만 가능하다.

---

# 7. Vision — 절대 하지 말아야 하는 것

```text
우리는 AI로 넷플릭스급 다큐를 만든다.

❌ 유튜브 AI 느낌
❌ 슬라이드 쇼
❌ AI 티 나는 영상
❌ 프롬프트를 사람이 쓰는 것 (Director가 결정하고 Prompt는 결과물)
❌ 코드부터 짜는 것 (설계서 먼저 — Bible이 모든 시스템의 기준)
```

기록 — 장면 밀도의 진화: 초기 구상은 장면당 5~8초·180~200장면이었고,
최종 기준(docs/37)은 장면당 6~15초·120~180장면(25분)이다. 두 값이 다른
것은 대화가 진화한 결과이며, config(scene_script_engine.yaml)가 기준이다.

---

# 8. Non-Goals (v1)

```text
LLM 호출 없음 — 감정 스코어링은 CTO(GPT)가 장면 대본에 기입하고,
              Director Engine은 룰로 연출을 결정한다
BGM 자동 믹싱 없음 — music 결정은 기록까지만 (편집 계층 예약)
실제 미디어 생성 없음 / 업로드 없음 / 난수 없음
```
