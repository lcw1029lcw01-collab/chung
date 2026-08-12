# 37_SCENE_SCRIPT_AND_WORLD_ENGINE_V1.md

Version: 1.0.0  
Status: Active  
Owner: CHUNG COMPANY  
System: ADOS  
Purpose: Scene Script / World Bible / Motion Prompt / SEO Layer v1  

---

# 1. Purpose

이 문서는 "AI 콘텐츠 스튜디오" 관점의 4개 계층을 정의한다.

파이프라인(ChatGPT → Claude Code → Midjourney → Kling → Typecast → 편집 →
업로드)이 자동이라면 병목은 오직 하나 — **대본**이다. 그리고 대본보다
더 중요한 것이 있다:

```text
영상은 글로 만드는 것이 아니라 "장면(Scene)"으로 만드는 것이다.
```

관련 구현:

```text
config/scene_script_engine.yaml
engines/documentary/scene_script_engine.py   (Scene Engine)
engines/worldbuilding/world_bible_engine.py  (World Bible Engine)
engines/documentary/motion_prompt_engine.py  (Kling 모션 프롬프트)
engines/seo/seo_engine.py                    (SEO Engine)
scripts/run_scene_script_engine_demo.py
tests/test_scene_script_world_seo.py
```

docs/35의 카메라 믹스·피사체 다양화·구조화 프롬프트(Subject/Environment/
Camera/Lens/Lighting/Mood/Film 분리 조합)는 이 계층의 전제이며 이미
구현되어 있다. 이 문서는 그 위에 "장면"과 "세계관"을 얹는다.

---

# 2. Scene Script Principle (핵심)

대부분의 AI 유튜브가 망하는 이유:

```text
나쁜 대본: "AI는 앞으로 인간의 일자리를 대체할 것입니다."
→ 이미지 1장 (AI 로봇 하나). 끝. 재미없다.

Scene Script: "2048년. 서울. 새벽 7시. 알람이 울린다.
하지만 당신은 오늘 회사에 가지 않는다.
당신의 직업은 어젯밤 AI에게 사라졌다."
→ 이미지 8~10장. 몰입된다.
```

규칙:

- 장면마다 반드시: **연도 / 장소 / 시간대 / 날씨 / 행동 / 나레이션 / 감정**
- 한 장면 6~15초. **25분 = 120~180 장면.**
- 장면 하나는 다시 2~6초 샷 여러 개로 분해된다(docs/35 샷 규칙).
  → docs/35 #6에서 언급한 "120~180" 모순의 해소: 그 수는 **장면 수**이고,
  샷 수는 그보다 많다(약 300).
- 추상 명사 금지 — 카메라에 찍히는 것만 쓴다.
- 감정(emotion)은 Typecast 음성 지시가 된다.

담당 엔진: `SceneScriptEngine`
- `story/scene_script.json` — 장면 배열 (dummy 모드는 결정적 placeholder)
- `story/scene_script_guide.md` — CTO(GPT)가 실제 장면을 집필할 때 따르는 지침
- 엔진은 LLM을 호출하지 않는다. 구조·검증·통합만 담당한다.

장면 스키마:

```text
scene_id / narration_block_id / section / year / location / time_of_day
/ weather / action / narration_text / emotion / duration_seconds / visual_focus
```

**통합**: scene_script.json이 있으면 DocumentaryShotPlanner는 장면이 샷을
끌고 가게 동작한다 — 장면 길이가 샷 예산이 되고, 장면의 visual_focus가
첫 샷의 피사체가 되며, 장면의 [연도/장소/시간대/행동]이 prompt_intent와
MJ 블루프린트의 조명(time_of_day)·공기(weather)를 결정한다.

---

# 3. World Bible Engine (연속된 미래 역사)

시청자는 영상을 보는 것이 아니라 **하나의 연속된 미래 역사**를 따라간다.
이것이 다른 AI 채널과 결정적으로 차별화되는 부분이다.

```text
영상 1   2050년 AI가 대부분의 사무직을 대체한다
영상 7   2068년 AI 정부가 등장한다
영상 21  2095년 인간과 AI 시민권 논쟁이 시작된다
영상 63  2140년 최초의 화성 독립국이 선언된다
영상 120 3000년 지구는 더 이상 인류의 중심이 아니다
```

담당 엔진: `WorldBibleEngine`
- `channels/{channel_id}/world_bible.yaml` — 연표(연도/사건/기술/정치/경제/
  도시/인간의 모습/AI의 역할), 연속성 규칙
- `channels/{channel_id}/world_continuity.yaml` — 에피소드 앵커 레지스트리
- `resolve_episode_anchor(channel_path, topic)` — 토픽의 연도에 가장 가까운
  연표 시점을 결정적으로 선택
- `register_episode_anchor(...)` — 에피소드가 다룬 시점을 기록 (연속성 유지)

규칙: 에피소드는 연표와 모순되면 안 된다. 새 사건은 연표에 등록한다
(자동 수정 금지 — 사람이 승인). 세계관 파일은 함부로 재생성하지 않는다.

---

# 4. Motion Prompt Engine (midjourney_video)

좋은 모션 프롬프트 = **큰 카메라 무브 1개 + 미세 모션 2개**.
미세 모션이 화면을 살아있게 만든다:

```text
Slow cinematic dolly in.
Wind blowing. Dust particles.
Natural eye blinking. Soft breathing.
```

담당 엔진: `MotionPromptEngine` → `prompts/motion_prompt_blueprints.json`
- **Provider 규칙 (감독 결정)**: 설계 대화에서는 Kling으로 논의됐지만,
  이미지·영상은 무조건 미드저니다 — provider_hint는 `midjourney_video`
  (MJ 애니메이트)로 고정한다 (docs/38 #6).
- ai_video 샷마다 1건 (5초 초과 금지 — docs/35 규칙 그대로)
- base_camera_motion은 샷의 movement 필드에서, 미세 모션은
  config의 motion_micro_motions에서 결정적으로 순환 선택
- 영상화 원본은 같은 shot_id의 MJ 이미지 (start_image_ref)

---

# 5. SEO Engine

담당 엔진: `SEOEngine` → `package/seo_package.json`

```text
한국어 제목 후보 20개 / 영어 제목 후보 20개 (결정적 공식 템플릿)
설명 (챕터 타임스탬프 포함 — scene_script의 구간 경계에서 생성)
태그 (기본 태그 + 토픽 키워드, 최대 20개)
썸네일 문구 후보 / 고정 댓글
```

규칙: 제목은 후보일 뿐이다 — 최종 선택은 사람이 한다. 업로드는 하지 않는다.

---

# 6. Data Flow

```text
채널 레벨:
WorldBibleEngine → channels/{id}/world_bible.yaml + world_continuity.yaml

프로젝트 레벨:
story/script_draft.json (+ world_bible 앵커)
        ↓
SceneScriptEngine      → story/scene_script.json (+ 작성 가이드)
        ↓  (장면이 샷을 끌고 간다)
DocumentaryShotPlanner → direction/documentary_shot_list.json (scene_source: scene_script)
        ↓
PromptBlueprintEngine  → prompts/midjourney_prompt_blueprints.json (장면의 시간대/날씨 반영)
MotionPromptEngine     → prompts/motion_prompt_blueprints.json (ai_video 샷)
        ↓
SEOEngine              → package/seo_package.json (챕터 = 장면 구간)
```

---

# 7. Non-Goals (v1)

```text
LLM 호출 없음 — 장면 집필은 CTO(GPT)가 guide를 따라 수행하고 파일로 교체한다
실제 미디어 생성 없음 / 업로드 없음
난수 없음 — 모든 산출물은 결정적이고 테스트 가능해야 한다
World Bible 자동 수정 없음 — 연표 변경은 사람이 승인한다
```
