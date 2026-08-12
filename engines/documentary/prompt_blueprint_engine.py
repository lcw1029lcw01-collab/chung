# -*- coding: utf-8 -*-
"""Midjourney prompt blueprint engine (documentary direction layer v1).

샷 리스트의 샷마다 구조화된 프롬프트 블루프린트를 만든다 —
Subject / Environment / Camera / Lens / Lighting / Atmosphere / Mood /
Composition / Film / Aspect Ratio를 분리해 조립한다.
근거: docs/35_AI_DOCUMENTARY_ENGINE_V1.md #9

주의: 씬당 제네릭 프롬프트 1개가 아니라 샷당 블루프린트를 만든다.
no-text 안전 규칙(책/종이/화면/UI/간판/번호판/인용 텍스트 금지)을 포함한다.
실제 이미지는 생성하지 않는다.
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSFileNotFoundError,
    ADOSLogger,
    ADOSValidationError,
    ADOSValidator,
    load_json,
    write_json,
)
from engines.documentary.shot_planner import DocumentaryShotPlanner

PROMPTS_DIR = "prompts"
BLUEPRINTS_FILE = "midjourney_prompt_blueprints.json"

BLUEPRINT_REQUIRED_FIELDS = [
    "shot_id",
    "subject",
    "environment",
    "camera",
    "lens",
    "lighting",
    "atmosphere",
    "mood",
    "composition",
    "film_reference",
    "aspect_ratio",
    "negative_prompt",
    "no_text_safety_notes",
    "final_prompt",
]

# MJ 블루프린트를 만드는 샷 타입 — 인포그래픽/텍스트 강조는 내부 그래픽으로 제작
MJ_ELIGIBLE_ASSET_TYPES = {"image_camera_movement", "ai_video"}

FILM_REFERENCE = "ARRI Alexa 65, IMAX documentary, Kodak Vision3 500T"
ASPECT_RATIO = "16:9"

NEGATIVE_PROMPT = (
    "text, letters, words, typography, captions, subtitles, watermark, "
    "signature, logo, ui, screen, sign, poster, book, newspaper, license plate"
)

NO_TEXT_SAFETY_NOTES = [
    "책/종이/화면/UI/간판/번호판/인용 텍스트가 프레임에 들어가지 않게 한다.",
    "정보 전달이 필요한 소재는 시각적 메타포(빛/홀로그램 형상/입자)로 치환한다.",
    "생성 결과에 텍스트가 보이면 해당 샷은 재생성 대상이다.",
]

SUBJECT_DESCRIPTIONS = {
    "human": "a lone evolved future human figure, subtle anatomical changes visible, calm posture",
    "city": "a vast futuristic megacity skyline with floating architecture",
    "hand": "a close view of a human hand with faintly translucent bio-skin",
    "eye": "an extreme close-up of a human eye with a faint bioluminescent iris",
    "sky": "an alien-tinted sky with layered clouds over a future settlement",
    "planet": "a planet seen from orbit with a thin glowing atmosphere",
    "object_detail": "a detailed futuristic artifact surface with organic micro-patterns",
    # 인포그래픽 계열 피사체가 섞여 들어와도 no-text 안전 형태로 치환
    "map": "abstract glowing terrain relief seen from above, no symbols or labels",
    "ui": "abstract volumetric light panels suggesting data, no readable symbols",
    "hologram": "a translucent holographic sphere of light particles, no readable symbols",
}

PALETTE_ENVIRONMENTS = {
    "cyan_orange_dark": "teal-and-amber cinematic grade, dark atmospheric backdrop",
    "blue_earth": "cool blue earth-toned grade, grounded natural backdrop",
    "orange_amber": "warm amber high-contrast grade, dramatic backdrop",
    "warm_memory": "soft warm nostalgic grade, gentle hazy backdrop",
    "red_danger": "high-contrast crimson-tinted grade, oppressive dark backdrop",
}

# 감독 결정의 지배 감정 → 프롬프트 무드 (Director가 먼저, Prompt는 결과물)
EMOTION_MOODS = {
    "loneliness": "quiet solitude and vast emptiness",
    "fear": "creeping dread and unease",
    "hope": "hopeful warmth breaking through",
    "mystery": "enigmatic veiled wonder",
    "wonder": "wide-eyed awe and curiosity",
    "calm": "serene contemplative stillness",
    "tension": "coiled tension about to break",
    "awe": "overwhelming epic grandeur",
}

CAMERA_DESCRIPTIONS = {
    "ultra_wide_establishing": "ultra wide establishing shot",
    "close_up": "close-up shot",
    "extreme_close_up": "extreme close-up shot",
    "drone_orbit": "aerial drone orbit shot",
    "over_the_shoulder": "over-the-shoulder shot",
    "side_profile": "side profile shot",
    "pov": "first-person POV shot",
    "low_angle": "low angle shot",
    "high_angle": "high angle shot",
    "macro_detail": "macro detail shot",
    "handheld_tracking": "handheld tracking shot",
}

COMPOSITIONS = {
    "ultra_wide_establishing": "centered composition with vast negative space",
    "close_up": "rule of thirds, shallow depth of field",
    "extreme_close_up": "tight central framing, extremely shallow focus",
    "drone_orbit": "sweeping circular composition, horizon low in frame",
    "over_the_shoulder": "foreground shoulder framing, deep background",
    "side_profile": "profile silhouette against light source",
    "pov": "natural human eye-level framing",
    "low_angle": "towering subject, dramatic perspective lines",
    "high_angle": "overhead observational framing",
    "macro_detail": "abstract macro framing, texture-filled frame",
    "handheld_tracking": "dynamic off-center framing with motion blur hints",
}

LIGHTING_CYCLE = [
    "golden sunrise rim light",
    "cool blue hour ambience",
    "volumetric god rays through haze",
    "soft overcast diffusion",
    "neon-tinged night glow",
]

ATMOSPHERE_CYCLE = [
    "morning mist",
    "drifting dust particles",
    "thin atmospheric haze",
    "clear crisp air",
    "light rain shimmer",
]

MOODS_BY_FUNCTION = {
    "hook": "awe and mystery",
    "explanation": "calm curiosity",
    "evidence": "grounded realism",
    "transition": "quiet momentum",
    "emotional_beat": "intimate wonder",
    "climax": "epic intensity",
    "ending": "hopeful reflection",
}

# 장면 대본의 시간대/날씨 → 프롬프트 어휘 (scene_script 연동 시 사용)
TIME_OF_DAY_LIGHTING = {
    "dawn": "first light of dawn",
    "morning": "soft morning light",
    "noon": "clear midday light",
    "dusk": "golden dusk light",
    "night": "deep night ambience",
}

WEATHER_ATMOSPHERE = {
    "clear": "clear crisp air",
    "rain": "light rain shimmer",
    "fog": "dense atmospheric fog",
    "dust_wind": "wind-blown dust haze",
    "snow": "gently falling snow",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class PromptBlueprintEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def blueprints_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / PROMPTS_DIR / BLUEPRINTS_FILE

    @staticmethod
    def _build_blueprint(
        shot: dict, index: int, scene: dict | None = None, decision: dict | None = None
    ) -> dict:
        camera = shot["camera_type"]
        subject = SUBJECT_DESCRIPTIONS.get(
            shot["subject_type"],
            "abstract cinematic future scene, no readable symbols",
        )
        environment = PALETTE_ENVIRONMENTS.get(
            shot["color_palette"], PALETTE_ENVIRONMENTS["cyan_orange_dark"]
        )
        camera_desc = CAMERA_DESCRIPTIONS.get(camera, camera.replace("_", " "))
        composition = COMPOSITIONS.get(camera, "balanced cinematic composition")
        lighting = LIGHTING_CYCLE[index % len(LIGHTING_CYCLE)]
        atmosphere = ATMOSPHERE_CYCLE[index % len(ATMOSPHERE_CYCLE)]
        mood = MOODS_BY_FUNCTION.get(shot["narrative_function"], "calm curiosity")

        # 장면 대본이 있으면 시간대/날씨가 조명/공기를 결정한다 (장면 → 프롬프트)
        scene_context = None
        if scene:
            lighting = TIME_OF_DAY_LIGHTING.get(scene.get("time_of_day"), lighting)
            atmosphere = WEATHER_ATMOSPHERE.get(scene.get("weather"), atmosphere)
            scene_context = {
                "scene_id": scene["scene_id"],
                "year": scene.get("year"),
                "location": scene.get("location"),
                "time_of_day": scene.get("time_of_day"),
                "weather": scene.get("weather"),
                "action": scene.get("action"),
            }

        # 감독 결정이 있으면 감독이 우선한다 — 조명·무드는 감정에서 나온다
        director_context = None
        if decision:
            lighting = decision.get("lighting", lighting)
            mood = EMOTION_MOODS.get(decision.get("dominant_emotion"), mood)
            director_context = {
                "dominant_emotion": decision.get("dominant_emotion"),
                "color": decision.get("color"),
                "music": decision.get("music"),
                "pace": decision.get("pace"),
            }

        final_prompt = (
            f"{subject}, {environment}, {camera_desc}, {shot['lens']} lens, "
            f"{lighting}, {atmosphere}, {mood}, {composition}, {FILM_REFERENCE} "
            f"--ar {ASPECT_RATIO} --no {NEGATIVE_PROMPT}"
        )
        return {
            "shot_id": shot["shot_id"],
            "asset_type": shot["asset_type"],
            "scene_context": scene_context,
            "director_context": director_context,
            "subject": subject,
            "environment": environment,
            "camera": camera_desc,
            "lens": shot["lens"],
            "lighting": lighting,
            "atmosphere": atmosphere,
            "mood": mood,
            "composition": composition,
            "film_reference": FILM_REFERENCE,
            "aspect_ratio": ASPECT_RATIO,
            "negative_prompt": NEGATIVE_PROMPT,
            "no_text_safety_notes": list(NO_TEXT_SAFETY_NOTES),
            "final_prompt": final_prompt,
        }

    def create_midjourney_prompt_blueprints(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        planner = DocumentaryShotPlanner()
        shot_list_path = planner.shot_list_path(project_path)
        if not shot_list_path.is_file():
            raise ADOSFileNotFoundError(
                f"documentary_shot_list.json이 없습니다: {shot_list_path}",
                location="PromptBlueprintEngine.create_midjourney_prompt_blueprints",
                suggested_fix="DocumentaryShotPlanner.create_documentary_shot_list를 먼저 실행하세요.",
            )
        shot_list = load_json(shot_list_path)
        shots = shot_list["shots"]

        # 장면 대본 기반 샷 리스트면 scene_id → 장면 매핑으로 프롬프트를 보강한다
        scenes_by_id: dict[str, dict] = {}
        if shot_list.get("scene_source") == "scene_script":
            scene_script_path = project_path / "story" / "scene_script.json"
            if scene_script_path.is_file():
                scene_script = load_json(scene_script_path)
                scenes_by_id = {
                    scene["scene_id"]: scene for scene in scene_script.get("scenes", [])
                }

        # 감독 연출 결정이 있으면 조명·무드는 감독이 정한다
        decisions_by_scene: dict[str, dict] = {}
        if shot_list.get("director_decisions_ref"):
            decisions_path = project_path / shot_list["director_decisions_ref"]
            if decisions_path.is_file():
                director = load_json(decisions_path)
                decisions_by_scene = {
                    decision["scene_id"]: decision
                    for decision in director.get("decisions", [])
                }

        blueprints = []
        skipped: dict[str, int] = {}
        for shot in shots:
            if shot["asset_type"] in MJ_ELIGIBLE_ASSET_TYPES:
                scene = scenes_by_id.get(shot["scene_id"])
                decision = decisions_by_scene.get(shot["scene_id"])
                blueprints.append(
                    self._build_blueprint(shot, len(blueprints), scene, decision)
                )
            else:
                skipped[shot["asset_type"]] = skipped.get(shot["asset_type"], 0) + 1

        result = {
            "project_id": shot_list["project_id"],
            "blueprint_mode": "documentary_v1",
            "provider_hint": "midjourney",
            "provider_rule": "이미지·영상은 무조건 미드저니 (감독 결정, docs/38 #6)",
            "total_shots": len(shots),
            "blueprint_count": len(blueprints),
            "skipped_by_asset_type": skipped,
            "skip_reason": "인포그래픽/텍스트 강조 샷은 MJ가 아니라 내부 그래픽으로 제작한다 (no-text 규칙).",
            "no_text_rule": True,
            "blueprints": blueprints,
            "created_at": _now_iso(),
            "disclaimer": "Prompt blueprints only. No real images generated.",
        }
        write_json(self.blueprints_path(project_path), result)
        if self.logger:
            self.logger.info(
                f"MJ 프롬프트 블루프린트 생성: {shot_list['project_id']} ({len(blueprints)}건)",
                metadata={"project_id": shot_list["project_id"], "blueprint_count": len(blueprints)},
            )
        return result

    def load_midjourney_prompt_blueprints(self, project_path: str | Path) -> dict:
        path = self.blueprints_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"midjourney_prompt_blueprints.json이 없습니다: {path}",
                location="PromptBlueprintEngine.load_midjourney_prompt_blueprints",
                suggested_fix="create_midjourney_prompt_blueprints를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_midjourney_prompt_blueprints(self, project_path: str | Path) -> bool:
        result = self.load_midjourney_prompt_blueprints(project_path)
        blueprints = result.get("blueprints", [])
        if not blueprints:
            raise ADOSValidationError(
                "블루프린트가 하나도 없습니다.",
                location="PromptBlueprintEngine.validate_midjourney_prompt_blueprints",
                suggested_fix="create_midjourney_prompt_blueprints를 다시 실행하세요.",
            )
        for blueprint in blueprints:
            ADOSValidator.require_fields(
                blueprint,
                BLUEPRINT_REQUIRED_FIELDS,
                location="PromptBlueprintEngine.validate_midjourney_prompt_blueprints",
            )
            if "--no" not in blueprint["final_prompt"]:
                raise ADOSValidationError(
                    f"{blueprint['shot_id']} final_prompt에 negative prompt가 없습니다.",
                    location="PromptBlueprintEngine.validate_midjourney_prompt_blueprints",
                    suggested_fix="no-text 안전 규칙을 포함해 재생성하세요.",
                )
        # 샷당 블루프린트 — 씬당 1개 제네릭 프롬프트 금지
        shot_ids = {blueprint["shot_id"] for blueprint in blueprints}
        if len(shot_ids) != len(blueprints):
            raise ADOSValidationError(
                "shot_id가 중복된 블루프린트가 있습니다.",
                location="PromptBlueprintEngine.validate_midjourney_prompt_blueprints",
                suggested_fix="샷당 정확히 1개의 블루프린트를 생성하세요.",
            )
        return True
