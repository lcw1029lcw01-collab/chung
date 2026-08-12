# -*- coding: utf-8 -*-
"""Scene script engine (scene layer v1).

대본을 "글"이 아니라 "장면(Scene)"으로 만든다.
나쁜 대본은 문장 하나 = 이미지 하나로 끝나지만, Scene Script는
[연도/장소/시간대/날씨/행동]이 있는 장면의 연속이라 문장 하나가
이미지 5~10장이 된다. 영상은 글이 아니라 장면으로 만드는 것이다.
근거: docs/37_SCENE_SCRIPT_AND_WORLD_ENGINE_V1.md #2

주의: 엔진은 LLM을 호출하지 않는다 — dummy 모드는 결정적 placeholder를
만들고, 실제 장면 집필은 scene_script_guide.md를 따라 CTO(GPT)가 채운다.
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSFileNotFoundError,
    ADOSLogger,
    ADOSPathManager,
    ADOSValidationError,
    ADOSValidator,
    load_json,
    load_yaml,
    write_json,
    write_text,
)

STORY_DIR = "story"
SCENE_SCRIPT_FILE = "scene_script.json"
SCENE_GUIDE_FILE = "scene_script_guide.md"

SCENE_REQUIRED_FIELDS = [
    "scene_id",
    "narration_block_id",
    "section",
    "year",
    "location",
    "time_of_day",
    "weather",
    "action",
    "narration_text",
    "emotion",
    "duration_seconds",
    "visual_focus",
]

VISUAL_FOCUS_CYCLE = [
    "city", "human", "hand", "eye", "sky", "planet", "object_detail", "map", "hologram",
]

LOCATION_CYCLE = [
    "거대 도시 상공", "도시의 거리", "연구 시설", "주거 구역", "행성 지평선", "궤도 정거장",
]

# config/scene_script_engine.yaml과 동일한 안전 기본값
DEFAULT_SCENE_CONFIG = {
    "scene_rules": {
        "scene_seconds_min": 6,
        "scene_seconds_max": 15,
        "scenes_per_25min_min": 120,
        "scenes_per_25min_max": 180,
        "max_scenes_per_narration_block": 3,
    },
    "emotion_by_section": {
        "hook": "wonder",
        "setup": "calm",
        "development": "tension",
        "payoff": "awe",
        "ending": "hope",
    },
    "motion_micro_motions": [
        "wind blowing gently",
        "dust particles drifting in the air",
        "natural eye blinking",
        "soft breathing movement",
        "fabric rippling slightly",
        "distant lights flickering",
        "thin mist flowing slowly",
        "loose hair strands moving",
    ],
    "time_of_day_cycle": ["dawn", "morning", "noon", "dusk", "night"],
    "weather_cycle": ["clear", "rain", "fog", "dust_wind", "snow"],
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_scene_engine_config(start: str | Path | None = None) -> dict:
    """config/scene_script_engine.yaml을 읽는다. 없으면 안전 기본값을 쓴다."""
    try:
        root = ADOSPathManager.find_project_root(start)
    except Exception:
        return dict(DEFAULT_SCENE_CONFIG)
    config_path = root / "config" / "scene_script_engine.yaml"
    if not config_path.is_file():
        return dict(DEFAULT_SCENE_CONFIG)
    config = load_yaml(config_path)
    if not isinstance(config, dict):
        config = {}
    merged: dict = {}
    for key, default in DEFAULT_SCENE_CONFIG.items():
        value = config.get(key)
        if isinstance(default, dict):
            section = dict(default)
            if isinstance(value, dict):
                section.update(value)
            merged[key] = section
        else:
            merged[key] = default if value is None else value
    for key, value in config.items():
        if key not in merged:
            merged[key] = value
    return merged


class SceneScriptEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def script_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / STORY_DIR / SCENE_SCRIPT_FILE

    def guide_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / STORY_DIR / SCENE_GUIDE_FILE

    # --- 내부 헬퍼 ---
    @staticmethod
    def _resolve_world_anchor(project_path: Path, project: dict) -> dict | None:
        """채널 world_bible이 있으면 토픽에 맞는 연표 앵커를 가져온다."""
        try:
            from engines.worldbuilding import WorldBibleEngine

            root = ADOSPathManager.find_project_root(project_path)
            channel_path = root / "channels" / project["channel"]["channel_id"]
            engine = WorldBibleEngine()
            if not engine.bible_path(channel_path).is_file():
                return None
            return engine.resolve_episode_anchor(channel_path, project["topic"]["title"])
        except Exception:
            return None

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        parts = [part.strip() for part in text.replace("?", "?|").replace(".", ".|").split("|")]
        return [part for part in parts if part]

    def create_dummy_scene_script(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        for required in ("project.json", "story/story_outline.json", "story/script_draft.json"):
            if not (project_path / required).is_file():
                raise ADOSFileNotFoundError(
                    f"{required}가 없습니다: {project_path / required}",
                    location="SceneScriptEngine.create_dummy_scene_script",
                    suggested_fix="ProjectEngine과 StoryEngine을 먼저 실행하세요.",
                )
        project = load_json(project_path / "project.json")
        draft = load_json(project_path / "story" / "script_draft.json")
        config = load_scene_engine_config(project_path)
        rules = config["scene_rules"]
        emotions = config["emotion_by_section"]
        times = config["time_of_day_cycle"]
        weathers = config["weather_cycle"]

        anchor = self._resolve_world_anchor(project_path, project)
        anchor_year = anchor["year"] if anchor else 2100

        blocks = draft["narration_blocks"]
        # 블록별 길이가 없으면 대본 전체 길이를 블록 수로 나눈다 (StoryEngine
        # 더미는 script 레벨 길이만 기록한다 — 블록당 10초 고정 가정 금지)
        script_total = float(draft.get("estimated_duration_seconds") or 0)
        default_block_duration = (
            script_total / len(blocks) if script_total > 0 and blocks else 10.0
        )

        scenes = []
        scene_index = 0
        for block in blocks:
            block_duration = float(
                block.get("estimated_duration_seconds") or default_block_duration
            )
            max_split = max(1, int(rules["max_scenes_per_narration_block"]))
            ideal = (rules["scene_seconds_min"] + rules["scene_seconds_max"]) / 2
            n_scenes = max(1, min(max_split, round(block_duration / ideal)))
            sentences = self._split_sentences(block["text"]) or [block["text"]]

            # 문장을 장면에 연속 분배한다 — 중복·유실 없이 전부 커버
            if len(sentences) >= n_scenes:
                head_count = len(sentences) - n_scenes + 1
                narration_parts = [" ".join(sentences[:head_count])] + sentences[head_count:]
            else:
                narration_parts = sentences + ["(장면 지속 — 나레이션 없음)"] * (
                    n_scenes - len(sentences)
                )

            base = round(block_duration / n_scenes, 1)
            for i in range(n_scenes):
                duration = base if i < n_scenes - 1 else round(block_duration - base * (n_scenes - 1), 1)
                narration = narration_parts[i]
                section = block.get("section", "development")
                scene_index += 1
                scenes.append(
                    {
                        "scene_id": f"SCN{scene_index:03d}",
                        "narration_block_id": block["block_id"],
                        "section": section,
                        "year": anchor_year,
                        "location": LOCATION_CYCLE[scene_index % len(LOCATION_CYCLE)],
                        "time_of_day": times[scene_index % len(times)],
                        "weather": weathers[(scene_index // len(times)) % len(weathers)],
                        "action": f"{VISUAL_FOCUS_CYCLE[scene_index % len(VISUAL_FOCUS_CYCLE)]} 중심의 장면이 전개된다 (placeholder)",
                        "narration_text": narration,
                        "emotion": emotions.get(section, "calm"),
                        "duration_seconds": duration,
                        "visual_focus": VISUAL_FOCUS_CYCLE[scene_index % len(VISUAL_FOCUS_CYCLE)],
                    }
                )

        script = {
            "project_id": project["project_id"],
            "topic": project["topic"]["title"],
            "scene_script_mode": "dummy",
            "disclaimer": "Dummy scene script. 실제 장면 집필은 scene_script_guide.md를 따라 교체한다.",
            "world_anchor": anchor,
            "principle": "영상은 글이 아니라 장면(Scene)으로 만든다",
            "total_scenes": len(scenes),
            "total_duration_seconds": round(sum(scene["duration_seconds"] for scene in scenes), 1),
            "scenes": scenes,
            "created_at": _now_iso(),
        }
        write_json(self.script_path(project_path), script)
        self._write_guide(project_path, project, anchor)
        write_json(
            project_path / STORY_DIR / "scene_script_review.json",
            {
                "project_id": project["project_id"],
                "scene_script_mode": "dummy",
                "status": "PENDING_REVIEW",
                "notes": ["더미 장면 대본 — 실제 장면 집필 후 사람이 검토한다."],
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"장면 대본 생성: {project['project_id']} ({len(scenes)}장면)",
                metadata={"project_id": project["project_id"], "total_scenes": len(scenes)},
            )
        return script

    def _write_guide(self, project_path: Path, project: dict, anchor: dict | None) -> None:
        """CTO(GPT)가 실제 장면 대본을 쓸 때 따르는 지침을 만든다."""
        anchor_line = (
            f"- 세계관 앵커: {anchor['year']}년 — {anchor['event']}" if anchor else "- 세계관 앵커: (world_bible 미생성)"
        )
        guide = f"""# Scene Script 작성 가이드 — {project['topic']['title']}

## 원칙: "글"을 쓰지 말고 "영화"를 써라

나쁜 대본 (문장 하나 = 이미지 하나):
> AI는 앞으로 인간의 일자리를 대체할 것입니다.

좋은 대본 (장면의 연속 = 이미지 8~10장):
> 2048년. 서울. 새벽 7시. 알람이 울린다.
> 하지만 당신은 오늘 회사에 가지 않는다.
> 당신의 직업은 어젯밤 AI에게 사라졌다.

## 규칙

1. 장면마다 반드시 채운다: 연도 / 장소 / 시간대 / 날씨 / 행동 / 나레이션 / 감정
2. 한 장면은 6~15초. 25분 영상이면 120~180장면.
3. 추상 명사 금지 — 카메라에 찍히는 것만 쓴다 (개념 → 사물/행동으로 치환).
4. 피사체를 계속 바꾼다: 도시 → 발 → 손 → 헬멧 → 하늘 → 사람 → UI → 지도.
5. 나레이션 한 문장이 장면 여러 개가 될 수 있다 — 장면이 나레이션을 쪼갠다.
6. 감정은 Typecast 지시가 된다: wonder / calm / tension / awe / hope.
{anchor_line}
- 연표와 모순되는 사건 금지 (channels/{{channel_id}}/world_bible.yaml 참고)

## 산출물 형식

story/scene_script.json의 scenes 배열을 이 스키마로 교체한다:

```json
{{
  "scene_id": "SCN001",
  "narration_block_id": "NB001",
  "section": "hook",
  "year": 1000000,
  "location": "세 개의 달이 뜬 거대 도시",
  "time_of_day": "dawn",
  "weather": "fog",
  "action": "투명한 피부의 인간이 도시를 향해 걸어온다",
  "narration_text": "100만 년 후, 인간은 어떤 모습일까요?",
  "emotion": "wonder",
  "duration_seconds": 8.0,
  "visual_focus": "human"
}}
```
"""
        write_text(self.guide_path(project_path), guide)

    def load_scene_script(self, project_path: str | Path) -> dict:
        path = self.script_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"scene_script.json이 없습니다: {path}",
                location="SceneScriptEngine.load_scene_script",
                suggested_fix="create_dummy_scene_script를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_scene_script(self, project_path: str | Path) -> bool:
        script = self.load_scene_script(project_path)
        scenes = script.get("scenes", [])
        if not scenes:
            raise ADOSValidationError(
                "장면이 하나도 없습니다.",
                location="SceneScriptEngine.validate_scene_script",
                suggested_fix="create_dummy_scene_script를 다시 실행하세요.",
            )
        config = load_scene_engine_config(project_path)
        for scene in scenes:
            ADOSValidator.require_fields(
                scene,
                SCENE_REQUIRED_FIELDS,
                location="SceneScriptEngine.validate_scene_script",
            )
            if scene["duration_seconds"] <= 0:
                raise ADOSValidationError(
                    f"{scene['scene_id']} 길이가 0 이하입니다.",
                    location="SceneScriptEngine.validate_scene_script",
                    suggested_fix="duration_seconds를 채우세요.",
                )
        # 나레이션 블록 커버리지 — 모든 블록이 최소 1장면을 가진다
        draft_path = Path(project_path) / "story" / "script_draft.json"
        if draft_path.is_file():
            draft = load_json(draft_path)
            block_ids = {block["block_id"] for block in draft["narration_blocks"]}
            covered = {scene["narration_block_id"] for scene in scenes}
            missing = block_ids - covered
            if missing:
                raise ADOSValidationError(
                    f"장면이 없는 나레이션 블록: {sorted(missing)}",
                    location="SceneScriptEngine.validate_scene_script",
                    suggested_fix="모든 나레이션 블록을 장면으로 덮으세요.",
                )
        # 피사체 다양성 — 전부 같은 피사체면 실패
        focuses = {scene["visual_focus"] for scene in scenes}
        if len(scenes) >= 5 and len(focuses) < 3:
            raise ADOSValidationError(
                f"피사체 다양성이 부족합니다: {sorted(focuses)}",
                location="SceneScriptEngine.validate_scene_script",
                suggested_fix="도시/손/눈/하늘/지도 등 visual_focus를 섞으세요.",
            )
        _ = config
        return True
