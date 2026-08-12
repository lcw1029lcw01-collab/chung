# -*- coding: utf-8 -*-
"""Asset mix planner (documentary direction layer v1).

25분 기준 자산 비율(AI 영상 20~25% / 이미지+카메라 무빙 50~60% /
인포그래픽 10~15% / 텍스트 강조 5~10%)을 프로젝트 계획으로 만든다.
근거: docs/35_AI_DOCUMENTARY_ENGINE_V1.md #4

주의: 25분 전체를 AI 영상으로 계획하지 않는다. 실제 미디어는 만들지 않는다.
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

DIRECTION_DIR = "direction"
PLAN_FILE = "asset_mix_plan.json"

PLAN_REQUIRED_FIELDS = [
    "project_id",
    "duration_minutes",
    "total_duration_seconds",
    "target_mix",
    "planned_seconds_by_asset_type",
    "estimated_counts",
    "cost_saving_notes",
    "created_at",
]

ASSET_TYPES = [
    "ai_video",
    "image_camera_movement",
    "infographic",
    "text_emphasis",
]

# config/documentary_engine.yaml과 동일한 안전 기본값 (config 없으면 이 값 사용)
DEFAULT_ENGINE_CONFIG = {
    "default_duration_minutes": 25,
    "asset_mix": {
        "ai_video_percent": 22,
        "image_camera_movement_percent": 55,
        "infographic_percent": 15,
        "text_emphasis_percent": 8,
    },
    "shot_duration_rules": {
        "ai_video_max_seconds": 5,
        "image_shot_seconds_min": 2,
        "image_shot_seconds_max": 6,
        "infographic_seconds_min": 4,
        "infographic_seconds_max": 10,
        "text_emphasis_seconds_min": 2,
        "text_emphasis_seconds_max": 5,
    },
    "style_defaults": {
        "visual_style": "netflix_future_documentary",
        "color_palette": "cyan_orange_dark",
        "camera_language": "cinematic_documentary",
        "no_text_rule": True,
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_documentary_engine_config(start: str | Path | None = None) -> dict:
    """config/documentary_engine.yaml을 읽는다. 없으면 안전 기본값을 쓴다.

    부분만 정의된 config(예: asset_mix에 키 1개)도 안전하다 —
    섹션별로 기본값 위에 얹어(deep merge) 빠진 키는 기본값을 유지한다.
    비어 있거나 dict가 아닌 config도 기본값으로 처리한다.
    """
    try:
        root = ADOSPathManager.find_project_root(start)
    except Exception:
        return dict(DEFAULT_ENGINE_CONFIG)
    config_path = root / "config" / "documentary_engine.yaml"
    if not config_path.is_file():
        return dict(DEFAULT_ENGINE_CONFIG)
    config = load_yaml(config_path)
    if not isinstance(config, dict):
        config = {}
    merged: dict = {}
    for key, default in DEFAULT_ENGINE_CONFIG.items():
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


class AssetMixPlanner:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def plan_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / DIRECTION_DIR / PLAN_FILE

    def create_asset_mix_plan(
        self, project_path: str | Path, duration_minutes: int = 25
    ) -> dict:
        project_path = Path(project_path)
        project_json = project_path / "project.json"
        if not project_json.is_file():
            raise ADOSFileNotFoundError(
                f"project.json이 없습니다: {project_json}",
                location="AssetMixPlanner.create_asset_mix_plan",
                suggested_fix="ProjectEngine.create_project를 먼저 실행하세요.",
            )
        project = load_json(project_json)
        config = load_documentary_engine_config(project_path)
        mix = config["asset_mix"]
        rules = config["shot_duration_rules"]

        total_seconds = int(duration_minutes * 60)
        percent_by_type = {
            "ai_video": mix["ai_video_percent"],
            "image_camera_movement": mix["image_camera_movement_percent"],
            "infographic": mix["infographic_percent"],
            "text_emphasis": mix["text_emphasis_percent"],
        }
        percent_total = sum(percent_by_type.values())
        planned_seconds = {
            asset_type: round(total_seconds * percent / percent_total)
            for asset_type, percent in percent_by_type.items()
        }

        # 타입별 평균 샷 길이로 필요 샷 수를 추정한다
        avg_ai = rules["ai_video_max_seconds"]  # AI 영상은 대부분 최대 길이(5초 이하)로 계획
        avg_image = (rules["image_shot_seconds_min"] + rules["image_shot_seconds_max"]) / 2
        avg_info = (rules["infographic_seconds_min"] + rules["infographic_seconds_max"]) / 2
        avg_text = (rules["text_emphasis_seconds_min"] + rules["text_emphasis_seconds_max"]) / 2
        estimated_counts = {
            "ai_video_shots": max(1, round(planned_seconds["ai_video"] / avg_ai)),
            "image_shots": max(1, round(planned_seconds["image_camera_movement"] / avg_image)),
            "infographic_shots": max(1, round(planned_seconds["infographic"] / avg_info)),
            "text_emphasis_shots": max(1, round(planned_seconds["text_emphasis"] / avg_text)),
        }

        plan = {
            "project_id": project["project_id"],
            "duration_minutes": duration_minutes,
            "total_duration_seconds": total_seconds,
            "target_mix": percent_by_type,
            "planned_seconds_by_asset_type": planned_seconds,
            "estimated_counts": estimated_counts,
            "shot_duration_rules": dict(rules),
            "cost_saving_notes": [
                "전체를 AI 영상으로 만들면 비용이 폭발한다 — 이미지+카메라 무빙이 대부분을 담당한다.",
                "AI 영상은 감정·임팩트가 필요한 장면에만 5초 이하로 사용한다.",
                "사람은 영상 자체가 아니라 장면 전환(Scene Change)을 본다 — 짧은 샷의 혼합이 더 비싸 보인다.",
                "인포그래픽/텍스트는 정보 전달과 리듬 변화를 담당한다.",
            ],
            "created_at": _now_iso(),
        }
        write_json(self.plan_path(project_path), plan)
        if self.logger:
            self.logger.info(
                f"자산 비율 계획 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"], "duration_minutes": duration_minutes},
            )
        return plan

    def load_asset_mix_plan(self, project_path: str | Path) -> dict:
        path = self.plan_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"asset_mix_plan.json이 없습니다: {path}",
                location="AssetMixPlanner.load_asset_mix_plan",
                suggested_fix="create_asset_mix_plan을 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_asset_mix_plan(self, project_path: str | Path) -> bool:
        plan = self.load_asset_mix_plan(project_path)
        ADOSValidator.require_fields(
            plan, PLAN_REQUIRED_FIELDS, location="AssetMixPlanner.validate_asset_mix_plan"
        )
        mix = plan["target_mix"]
        if mix["ai_video"] >= mix["image_camera_movement"]:
            raise ADOSValidationError(
                "AI 영상 비율이 이미지 비율보다 큽니다 — 이미지가 지배해야 한다.",
                location="AssetMixPlanner.validate_asset_mix_plan",
                suggested_fix="config/documentary_engine.yaml의 asset_mix를 확인하세요.",
            )
        planned = plan["planned_seconds_by_asset_type"]
        total = plan["total_duration_seconds"]
        planned_total = sum(planned[t] for t in ASSET_TYPES)
        if abs(planned_total - total) > max(4, total * 0.02):
            raise ADOSValidationError(
                f"타입별 계획 초 합계({planned_total})가 전체 길이({total})와 다릅니다.",
                location="AssetMixPlanner.validate_asset_mix_plan",
                suggested_fix="create_asset_mix_plan을 다시 실행하세요.",
            )
        return True
