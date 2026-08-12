# -*- coding: utf-8 -*-
"""Motion prompt engine (documentary direction layer v1).

AI 영상 샷마다 영상화(모션) 프롬프트를 만든다.
좋은 모션 프롬프트는 큰 카메라 무브 하나 + 미세 모션(바람/먼지/
눈 깜빡임/호흡)의 조합이다 — 미세 모션이 화면을 살아있게 만든다.
근거: docs/37_SCENE_SCRIPT_AND_WORLD_ENGINE_V1.md #4

Provider 규칙 (감독 결정, docs/38 #6): 이미지·영상은 무조건 미드저니다.
설계 대화에서 Kling이 언급됐지만 실제 제작은 midjourney_video
(MJ 애니메이트)로 고정한다 — provider_hint가 이를 명시한다.

주의: 실제 영상을 생성하지 않는다. 프롬프트 블루프린트만 만든다.
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
from engines.documentary.scene_script_engine import load_scene_engine_config
from engines.documentary.shot_planner import DocumentaryShotPlanner

PROMPTS_DIR = "prompts"
MOTION_BLUEPRINTS_FILE = "motion_prompt_blueprints.json"

MOTION_REQUIRED_FIELDS = [
    "shot_id",
    "duration_seconds",
    "base_camera_motion",
    "micro_motions",
    "atmosphere",
    "final_prompt",
    "start_image_ref",
]

# 샷의 movement 필드 → Kling 카메라 무브 문장
CAMERA_MOTION_PHRASES = {
    "slow_dolly_in": "Slow cinematic dolly in",
    "static": "Locked-off static camera, subject moves subtly",
    "orbit": "Slow drone orbit around the subject",
    "handheld_drift": "Gentle handheld drift, barely perceptible sway",
    "slow_pan": "Very slow horizontal pan",
    "walking": "First-person walking movement, natural gait",
    "slow_tilt_up": "Slow tilt up revealing scale",
    "slow_crane_down": "Slow crane descent toward the subject",
    "rack_focus": "Static frame with slow rack focus shift",
    "tracking": "Smooth tracking shot following the subject",
}

ATMOSPHERE_BY_PALETTE = {
    "cyan_orange_dark": "dark teal-and-amber atmosphere",
    "blue_earth": "cool grounded blue atmosphere",
    "orange_amber": "warm dramatic amber atmosphere",
    "warm_memory": "soft nostalgic warm atmosphere",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MotionPromptEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def blueprints_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / PROMPTS_DIR / MOTION_BLUEPRINTS_FILE

    def create_motion_prompt_blueprints(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        planner = DocumentaryShotPlanner()
        shot_list_path = planner.shot_list_path(project_path)
        if not shot_list_path.is_file():
            raise ADOSFileNotFoundError(
                f"documentary_shot_list.json이 없습니다: {shot_list_path}",
                location="MotionPromptEngine.create_motion_prompt_blueprints",
                suggested_fix="DocumentaryShotPlanner.create_documentary_shot_list를 먼저 실행하세요.",
            )
        shot_list = load_json(shot_list_path)
        config = load_scene_engine_config(project_path)
        micro_motions = config["motion_micro_motions"]

        # 감독 연출 결정이 있으면 movement_hint가 모션에 반영된다
        decisions_by_scene: dict[str, dict] = {}
        decisions_path = project_path / "direction" / "director_decisions.json"
        if decisions_path.is_file():
            director = load_json(decisions_path)
            decisions_by_scene = {
                decision["scene_id"]: decision for decision in director.get("decisions", [])
            }

        blueprints = []
        for shot in shot_list["shots"]:
            if shot["asset_type"] != "ai_video":
                continue
            index = len(blueprints)
            camera = CAMERA_MOTION_PHRASES.get(
                shot["movement"], "Slow cinematic camera movement"
            )
            decision = decisions_by_scene.get(shot["scene_id"])
            movement_hint = decision.get("movement_hint") if decision else None
            picked = [
                micro_motions[index % len(micro_motions)],
                micro_motions[(index + 3) % len(micro_motions)],
            ]
            atmosphere = ATMOSPHERE_BY_PALETTE.get(
                shot["color_palette"], ATMOSPHERE_BY_PALETTE["cyan_orange_dark"]
            )
            hint_sentence = f" {movement_hint.capitalize()}." if movement_hint else ""
            final_prompt = (
                f"{camera}.{hint_sentence} {picked[0].capitalize()}. {picked[1].capitalize()}. "
                f"{atmosphere.capitalize()}. Slow cinematic pace, photorealistic motion, "
                f"stable smooth camera, no sudden cuts, no text."
            )
            blueprints.append(
                {
                    "shot_id": shot["shot_id"],
                    "duration_seconds": shot["duration_seconds"],
                    "base_camera_motion": camera,
                    "micro_motions": picked,
                    "atmosphere": atmosphere,
                    "final_prompt": final_prompt,
                    # MJ 애니메이트의 원본 = 같은 샷의 MJ 이미지
                    "start_image_ref": f"{shot['shot_id']} (midjourney_prompt_blueprints의 동일 shot_id 이미지)",
                }
            )

        result = {
            "project_id": shot_list["project_id"],
            "motion_mode": "documentary_v1",
            "provider_hint": "midjourney_video",
            "provider_rule": "이미지·영상은 무조건 미드저니 (감독 결정, docs/38 #6)",
            "total_ai_video_shots": len(blueprints),
            "max_shot_seconds": shot_list.get("ai_video_max_seconds", 5),
            "principle": "큰 카메라 무브 1개 + 미세 모션 2개 — 미세 모션이 화면을 살린다",
            "blueprints": blueprints,
            "created_at": _now_iso(),
            "disclaimer": "Motion prompt blueprints only. No real video generated.",
        }
        write_json(self.blueprints_path(project_path), result)
        if self.logger:
            self.logger.info(
                f"모션 프롬프트 블루프린트 생성: {shot_list['project_id']} ({len(blueprints)}건)",
                metadata={"project_id": shot_list["project_id"], "count": len(blueprints)},
            )
        return result

    def load_motion_prompt_blueprints(self, project_path: str | Path) -> dict:
        path = self.blueprints_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"motion_prompt_blueprints.json이 없습니다: {path}",
                location="MotionPromptEngine.load_motion_prompt_blueprints",
                suggested_fix="create_motion_prompt_blueprints를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_motion_prompt_blueprints(self, project_path: str | Path) -> bool:
        result = self.load_motion_prompt_blueprints(project_path)
        blueprints = result.get("blueprints", [])
        if not blueprints:
            raise ADOSValidationError(
                "모션 블루프린트가 하나도 없습니다.",
                location="MotionPromptEngine.validate_motion_prompt_blueprints",
                suggested_fix="샷 리스트에 ai_video 샷이 있는지 확인하세요.",
            )
        max_seconds = result.get("max_shot_seconds", 5)
        for blueprint in blueprints:
            ADOSValidator.require_fields(
                blueprint,
                MOTION_REQUIRED_FIELDS,
                location="MotionPromptEngine.validate_motion_prompt_blueprints",
            )
            if blueprint["duration_seconds"] > max_seconds:
                raise ADOSValidationError(
                    f"{blueprint['shot_id']} 모션이 {max_seconds}초를 초과합니다.",
                    location="MotionPromptEngine.validate_motion_prompt_blueprints",
                    suggested_fix="AI 영상 샷은 5초 이하로 유지하세요.",
                )
            if len(blueprint["micro_motions"]) < 2:
                raise ADOSValidationError(
                    f"{blueprint['shot_id']}에 미세 모션이 부족합니다.",
                    location="MotionPromptEngine.validate_motion_prompt_blueprints",
                    suggested_fix="미세 모션을 2개 이상 포함하세요.",
                )
        return True
