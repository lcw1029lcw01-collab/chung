# -*- coding: utf-8 -*-
"""Timeline validator (walking skeleton).

timeline.json의 최소 규칙을 검증한다 (docs/16_TIMELINE_ENGINE.md 기준의 축소판).
"""
from core import ADOSValidationError, ADOSValidator

TIMELINE_REQUIRED_FIELDS = [
    "project_id",
    "channel_id",
    "total_duration_seconds",
    "target_languages",
    "scenes",
]

SCENE_REQUIRED_FIELDS = [
    "scene_id",
    "order",
    "purpose",
    "duration_seconds",
    "visual",
    "voice",
    "subtitle",
    "motion",
]

# 장면 합계와 전체 길이의 허용 오차 (초). "대략 일치"의 기준.
_DURATION_TOLERANCE_SECONDS = 2


class TimelineValidator:
    @staticmethod
    def validate(timeline: dict) -> None:
        loc = "TimelineValidator.validate"
        ADOSValidator.require_fields(timeline, TIMELINE_REQUIRED_FIELDS, location=loc)

        scenes = timeline["scenes"]
        if not isinstance(scenes, list) or not scenes:
            raise ADOSValidationError("scenes가 비어 있습니다.", location=loc)

        problems = []
        seen_ids = set()
        total = 0
        for i, scene in enumerate(scenes, start=1):
            ADOSValidator.require_fields(scene, SCENE_REQUIRED_FIELDS, location=loc)
            scene_id = scene["scene_id"]
            if scene_id in seen_ids:
                problems.append(f"scene_id 중복: {scene_id}")
            seen_ids.add(scene_id)
            if not str(scene_id).startswith("SC"):
                problems.append(f"scene_id는 SC로 시작해야 합니다: {scene_id}")
            if scene["order"] != i:
                problems.append(f"order가 순차적이지 않습니다: {scene_id} (기대 {i}, 실제 {scene['order']})")
            if not scene["duration_seconds"] or scene["duration_seconds"] <= 0:
                problems.append(f"duration_seconds는 0보다 커야 합니다: {scene_id}")
            else:
                total += scene["duration_seconds"]
            for part in ("visual", "voice", "subtitle", "motion"):
                if not isinstance(scene[part], dict) or "required" not in scene[part]:
                    problems.append(f"{scene_id}.{part}.required가 없습니다.")

        expected = timeline["total_duration_seconds"]
        if abs(total - expected) > _DURATION_TOLERANCE_SECONDS:
            problems.append(
                f"장면 길이 합({total}s)이 전체 길이({expected}s)와 일치하지 않습니다."
            )

        if problems:
            raise ADOSValidationError(
                f"timeline 검증 실패: {'; '.join(problems)}",
                location=loc,
                suggested_fix="문제 장면을 수정한 뒤 다시 검증하세요.",
            )
