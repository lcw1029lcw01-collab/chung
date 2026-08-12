# -*- coding: utf-8 -*-
"""Director engine (direction layer v1) — ADOS의 두뇌.

ADOS는 프롬프트를 만드는 프로그램이 아니다. ADOS는 감독이다.
감독은 이미지를 만드는 사람이 아니라 결정을 내리는 사람이다:

    감정 → 카메라 → 렌즈 → 색감 → 조명 → 음악 → 속도 → (그 다음) Prompt

장면의 감정 스코어(예: 외로움 80 / 공포 60 / 신비 70)에서 지배 감정을
찾고, director_rules(config/director_rules.yaml)에 따라 연출을 결정한다.
Prompt는 결과물이다 — Director가 먼저다.
근거: docs/38_DIRECTOR_EMOTION_ENGINE_V1.md

주의: LLM 호출 없음. 결정은 전부 룰 기반·결정적이다.
실제 미디어를 생성하지 않는다.
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
)
from engines.documentary.documentary_bible import CAMERA_BIBLE

DIRECTION_DIR = "direction"
DECISIONS_FILE = "director_decisions.json"

DECISION_REQUIRED_FIELDS = [
    "scene_id",
    "dominant_emotion",
    "emotion_scores",
    "camera",
    "lens",
    "color",
    "lighting",
    "weather",
    "music",
    "pace",
    "movement_hint",
]

# config/director_rules.yaml과 동일한 안전 기본값 (config 없으면 이 값 사용)
DEFAULT_DIRECTOR_RULES = {
    "default_emotion": "calm",
    "aliases": {
        "외로움": "loneliness",
        "공포": "fear",
        "희망": "hope",
        "신비": "mystery",
        "경이": "wonder",
        "평온": "calm",
        "긴장": "tension",
        "경외": "awe",
    },
    "emotions": {
        "loneliness": {
            "camera": "ultra_wide_establishing", "lens": "24mm", "color": "blue_earth",
            "lighting": "cold dawn light", "weather_hint": ["rain", "fog"],
            "music": "low solo piano", "pace": "slow", "movement_hint": "slow dolly",
        },
        "fear": {
            "camera": "close_up", "lens": "85mm", "color": "red_danger",
            "lighting": "hard shadow light", "weather_hint": ["storm"],
            "music": "heartbeat pulse", "pace": "fast", "movement_hint": "subtle handheld shake",
        },
        "hope": {
            "camera": "ultra_wide_establishing", "lens": "35mm", "color": "orange_amber",
            "lighting": "golden sunrise", "weather_hint": ["clear"],
            "music": "slow warm piano", "pace": "slow", "movement_hint": "slow rise",
        },
        "mystery": {
            "camera": "drone_orbit", "lens": "35mm", "color": "cyan_orange_dark",
            "lighting": "diffused fog glow", "weather_hint": ["fog"],
            "music": "ambient drone", "pace": "slow", "movement_hint": "slow orbit",
        },
        "wonder": {
            "camera": "low_angle", "lens": "24mm", "color": "cyan_orange_dark",
            "lighting": "volumetric god rays", "weather_hint": ["clear"],
            "music": "swelling strings", "pace": "medium", "movement_hint": "slow tilt up",
        },
        "calm": {
            "camera": "high_angle", "lens": "50mm", "color": "blue_earth",
            "lighting": "soft overcast light", "weather_hint": ["clear"],
            "music": "gentle ambient", "pace": "medium", "movement_hint": "static",
        },
        "tension": {
            "camera": "extreme_close_up", "lens": "100mm_macro", "color": "red_danger",
            "lighting": "hard side light", "weather_hint": ["dust_wind"],
            "music": "ticking percussion", "pace": "fast", "movement_hint": "rack focus",
        },
        "awe": {
            "camera": "drone_orbit", "lens": "24mm", "color": "orange_amber",
            "lighting": "epic backlight", "weather_hint": ["clear"],
            "music": "deep orchestral swell", "pace": "slow", "movement_hint": "slow crane",
        },
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_director_rules(start: str | Path | None = None) -> dict:
    """config/director_rules.yaml을 읽는다. 없으면 안전 기본값을 쓴다.

    부분 정의된 config도 안전하다 — 섹션별 deep merge로 빠진 감정은
    기본 룰을 유지한다.
    """
    try:
        root = ADOSPathManager.find_project_root(start)
    except Exception:
        return dict(DEFAULT_DIRECTOR_RULES)
    config_path = root / "config" / "director_rules.yaml"
    if not config_path.is_file():
        return dict(DEFAULT_DIRECTOR_RULES)
    config = load_yaml(config_path)
    if not isinstance(config, dict):
        config = {}
    merged: dict = {}
    for key, default in DEFAULT_DIRECTOR_RULES.items():
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


class DirectorEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def decisions_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / DIRECTION_DIR / DECISIONS_FILE

    @staticmethod
    def _dominant_emotion(scene: dict, rules: dict) -> tuple[str, dict]:
        """장면의 지배 감정을 찾는다 (스코어 최대, 동점이면 이름순 — 결정적)."""
        aliases = rules["aliases"]
        scores = scene.get("emotion_scores")
        if isinstance(scores, dict) and scores:
            normalized = {}
            for name, score in scores.items():
                canonical = aliases.get(name, name)
                normalized[canonical] = max(normalized.get(canonical, 0), score)
            dominant = sorted(normalized.items(), key=lambda item: (-item[1], item[0]))[0][0]
            return dominant, normalized
        emotion = scene.get("emotion", rules["default_emotion"])
        canonical = aliases.get(emotion, emotion)
        return canonical, {canonical: 100}

    def create_director_decisions(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        script_path = project_path / "story" / "scene_script.json"
        if not script_path.is_file():
            raise ADOSFileNotFoundError(
                f"scene_script.json이 없습니다: {script_path}",
                location="DirectorEngine.create_director_decisions",
                suggested_fix="SceneScriptEngine.create_dummy_scene_script를 먼저 실행하세요.",
            )
        script = load_json(script_path)
        rules = load_director_rules(project_path)
        emotion_rules = rules["emotions"]
        default_rule = emotion_rules[rules["default_emotion"]]

        decisions = []
        for scene in script["scenes"]:
            dominant, scores = self._dominant_emotion(scene, rules)
            rule = emotion_rules.get(dominant, default_rule)
            decisions.append(
                {
                    "scene_id": scene["scene_id"],
                    "dominant_emotion": dominant,
                    "emotion_scores": scores,
                    "camera": rule["camera"],
                    "lens": rule["lens"],
                    "color": rule["color"],
                    "lighting": rule["lighting"],
                    # 날씨는 장면 대본이 이미 정했으면 장면이 이긴다 (감독은 존중한다)
                    "weather": scene.get("weather") or rule["weather_hint"][0],
                    "music": rule["music"],
                    "pace": rule["pace"],
                    "movement_hint": rule["movement_hint"],
                }
            )

        result = {
            "project_id": script["project_id"],
            "director_mode": "rules_v1",
            "principle": "Prompt는 결과물이다 — Director가 먼저 결정한다 (감정→카메라→렌즈→색감→조명→음악→속도)",
            "scene_script_ref": "story/scene_script.json",
            "total_scenes": len(decisions),
            "decisions": decisions,
            "created_at": _now_iso(),
        }
        write_json(self.decisions_path(project_path), result)
        if self.logger:
            self.logger.info(
                f"감독 연출 결정 생성: {script['project_id']} ({len(decisions)}장면)",
                metadata={"project_id": script["project_id"], "total_scenes": len(decisions)},
            )
        return result

    def load_director_decisions(self, project_path: str | Path) -> dict:
        path = self.decisions_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"director_decisions.json이 없습니다: {path}",
                location="DirectorEngine.load_director_decisions",
                suggested_fix="create_director_decisions를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_director_decisions(self, project_path: str | Path) -> bool:
        result = self.load_director_decisions(project_path)
        decisions = result.get("decisions", [])
        if not decisions:
            raise ADOSValidationError(
                "연출 결정이 하나도 없습니다.",
                location="DirectorEngine.validate_director_decisions",
                suggested_fix="create_director_decisions를 다시 실행하세요.",
            )
        for decision in decisions:
            ADOSValidator.require_fields(
                decision,
                DECISION_REQUIRED_FIELDS,
                location="DirectorEngine.validate_director_decisions",
            )
            if decision["camera"] not in CAMERA_BIBLE:
                raise ADOSValidationError(
                    f"{decision['scene_id']}의 카메라가 카메라 바이블에 없습니다: {decision['camera']}",
                    location="DirectorEngine.validate_director_decisions",
                    suggested_fix="director_rules의 camera 값을 CAMERA_BIBLE 키로 맞추세요.",
                )
        # 장면 대본과 1:1 커버리지
        script_path = Path(project_path) / "story" / "scene_script.json"
        if script_path.is_file():
            script = load_json(script_path)
            scene_ids = {scene["scene_id"] for scene in script["scenes"]}
            decided = {decision["scene_id"] for decision in decisions}
            missing = scene_ids - decided
            if missing:
                raise ADOSValidationError(
                    f"연출 결정이 없는 장면: {sorted(missing)}",
                    location="DirectorEngine.validate_director_decisions",
                    suggested_fix="모든 장면에 연출을 결정하세요.",
                )
        return True
