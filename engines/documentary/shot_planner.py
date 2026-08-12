# -*- coding: utf-8 -*-
"""Documentary shot planner (direction layer v1).

씬(스토리 구간)을 샷 단위로 분해한다 — 카메라/렌즈/무브먼트/피사체를
계속 바꿔 "장면 전환(Scene Change)"의 리듬을 만든다.
근거: docs/35_AI_DOCUMENTARY_ENGINE_V1.md #5~#7

주의: 같은 카메라 반복 금지, 인물 뒷모습 와이드 샷 반복 금지.
결정적(deterministic)으로 생성한다 — 난수를 쓰지 않는다.
실제 미디어는 만들지 않는다.
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
from engines.documentary.asset_mix_planner import (
    AssetMixPlanner,
    load_documentary_engine_config,
)
from engines.documentary.documentary_bible import CAMERA_BIBLE, VISUAL_MOTIFS

DIRECTION_DIR = "direction"
SHOT_LIST_FILE = "documentary_shot_list.json"

SHOT_REQUIRED_FIELDS = [
    "shot_id",
    "scene_id",
    "order",
    "duration_seconds",
    "asset_type",
    "narrative_function",
    "camera_type",
    "lens",
    "movement",
    "subject_type",
    "visual_motif",
    "color_palette",
    "prompt_intent",
    "no_text_risk",
    "notes",
]

# 스토리 구조 5구간의 길이 배분 (인트로 임팩트 → 이미지 중심 본론 → 영상 중심 클라이맥스 → 이미지+음악 엔딩)
SECTION_RATIOS = {
    "hook": 0.06,
    "setup": 0.24,
    "development": 0.38,
    "payoff": 0.18,
    "ending": 0.14,
}

# 구간별 자산 타입 패턴 (반복 사이클) — 전역 합계가 asset_mix 목표에 수렴하도록 설계
SECTION_ASSET_PATTERNS = {
    "hook": ["ai_video", "ai_video", "image_camera_movement", "ai_video"],
    "setup": [
        "image_camera_movement", "image_camera_movement", "infographic",
        "image_camera_movement", "ai_video", "image_camera_movement", "text_emphasis",
    ],
    "development": [
        "image_camera_movement", "image_camera_movement", "ai_video",
        "image_camera_movement", "infographic", "image_camera_movement",
        "image_camera_movement", "text_emphasis",
    ],
    "payoff": [
        "ai_video", "image_camera_movement", "ai_video",
        "ai_video", "image_camera_movement", "infographic",
    ],
    "ending": [
        "image_camera_movement", "image_camera_movement",
        "text_emphasis", "image_camera_movement",
    ],
}

# 구간별 내러티브 기능 사이클
SECTION_FUNCTION_CYCLES = {
    "hook": ["hook"],
    "setup": ["explanation", "explanation", "transition", "evidence"],
    "development": ["explanation", "evidence", "emotional_beat", "explanation", "transition"],
    "payoff": ["climax", "emotional_beat", "climax"],
    "ending": ["ending"],
}

# 구간별 컬러 팔레트 (컬러 바이블 기반)
SECTION_COLOR_PALETTES = {
    "hook": "cyan_orange_dark",
    "setup": "blue_earth",
    "development": "cyan_orange_dark",
    "payoff": "orange_amber",
    "ending": "warm_memory",
}

# 타입별 샷 길이 사이클 (min~max 안에서 순환 — 리듬 변화)
# 실제 생성 시에는 config shot_duration_rules로 클램프된다 (_duration_cycles_from_rules)
DURATION_CYCLES = {
    "ai_video": [5, 4, 5, 5],
    "image_camera_movement": [4, 5, 3, 6, 4, 5, 2, 6],
    "infographic": [6, 8, 4, 10, 7],
    "text_emphasis": [3, 4, 2, 5],
}


def _duration_cycles_from_rules(rules: dict) -> dict:
    """기본 길이 사이클을 config shot_duration_rules 범위로 클램프한다.

    config에서 ai_video_max_seconds를 낮추면 생성되는 샷도 함께 짧아져
    생성과 검증이 항상 같은 규칙을 본다.
    """
    def clamp(value: int, low: int, high: int) -> int:
        return max(low, min(high, value))

    return {
        "ai_video": [
            min(v, rules["ai_video_max_seconds"]) for v in DURATION_CYCLES["ai_video"]
        ],
        "image_camera_movement": [
            clamp(v, rules["image_shot_seconds_min"], rules["image_shot_seconds_max"])
            for v in DURATION_CYCLES["image_camera_movement"]
        ],
        "infographic": [
            clamp(v, rules["infographic_seconds_min"], rules["infographic_seconds_max"])
            for v in DURATION_CYCLES["infographic"]
        ],
        "text_emphasis": [
            clamp(v, rules["text_emphasis_seconds_min"], rules["text_emphasis_seconds_max"])
            for v in DURATION_CYCLES["text_emphasis"]
        ],
    }

# 시각 피사체 사이클 (도시→인물→손→눈→하늘→행성→디테일 — 계속 바뀐다)
VISUAL_SUBJECT_CYCLE = ["city", "human", "hand", "eye", "sky", "planet", "object_detail"]
INFOGRAPHIC_SUBJECT_CYCLE = ["map", "ui", "hologram"]
TEXT_SUBJECT_CYCLE = ["ui", "hologram"]

CAMERA_TYPES = list(CAMERA_BIBLE.keys())

# 서로소 보폭(stride)으로 순환시켜 인접 샷의 카메라/피사체 반복을 막는다
_CAMERA_STRIDE = 3   # len(CAMERA_TYPES)=11과 서로소
_SUBJECT_STRIDE = 3  # len(VISUAL_SUBJECT_CYCLE)=7과 서로소

NO_TEXT_RISK_SUBJECTS = {"map", "ui", "hologram"}
NO_TEXT_RISK_ASSET_TYPES = {"infographic", "text_emphasis"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class DocumentaryShotPlanner:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def shot_list_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / DIRECTION_DIR / SHOT_LIST_FILE

    # --- 내부 헬퍼 ---
    @staticmethod
    def _section_budgets(structure_keys: list[str], total_seconds: int) -> dict:
        """스토리 구조 키 순서대로 초 예산을 배분한다."""
        ratios = {key: SECTION_RATIOS.get(key, 0.0) for key in structure_keys}
        unknown = [key for key, ratio in ratios.items() if ratio == 0.0]
        known_total = sum(ratios.values())
        if unknown:
            remaining = max(0.0, 1.0 - known_total)
            for key in unknown:
                ratios[key] = remaining / len(unknown)
        ratio_total = sum(ratios.values()) or 1.0
        budgets = {
            key: int(round(total_seconds * ratio / ratio_total))
            for key, ratio in ratios.items()
        }
        # 반올림 오차는 가장 큰 구간에 흡수
        diff = total_seconds - sum(budgets.values())
        if diff:
            biggest = max(budgets, key=budgets.get)
            budgets[biggest] += diff
        return budgets

    @staticmethod
    def _units_from_scene_script(scenes: list[dict], total_seconds: int) -> list[dict]:
        """장면 대본의 장면들을 샷 예산 단위로 바꾼다.

        장면 길이 비율대로 전체 초를 배분한다 (최대 잔여 방식) —
        합이 정확히 total_seconds가 되고, 각 장면은 최소 2초를 보장한다.
        전체 길이가 장면 수 × 2초보다 짧으면 배분이 불가능하므로 에러다.
        """
        count = len(scenes)
        if total_seconds < 2 * count:
            raise ADOSValidationError(
                f"영상 길이({total_seconds}초)가 장면 수({count}개 × 최소 2초)보다 짧습니다.",
                location="DocumentaryShotPlanner._units_from_scene_script",
                suggested_fix="장면 수를 줄이거나 프로젝트 길이를 늘리세요.",
            )
        weights = [max(0.1, float(scene["duration_seconds"])) for scene in scenes]
        weight_total = sum(weights)
        raw = [total_seconds * weight / weight_total for weight in weights]
        budgets = [max(2, int(value)) for value in raw]
        remainders = [value - int(value) for value in raw]
        add_order = sorted(range(count), key=lambda i: (-remainders[i], i))
        sub_order = sorted(range(count), key=lambda i: (remainders[i], i))
        diff = total_seconds - sum(budgets)
        cursor = 0
        while diff > 0:
            budgets[add_order[cursor % count]] += 1
            diff -= 1
            cursor += 1
        cursor = 0
        while diff < 0:
            candidate = sub_order[cursor % count]
            if budgets[candidate] > 2:
                budgets[candidate] -= 1
                diff += 1
            cursor += 1
        units = []
        for scene, budget in zip(scenes, budgets):
            units.append(
                {
                    "scene_id": scene["scene_id"],
                    "section": scene.get("section", "development"),
                    "budget": budget,
                    "prompt_context": (
                        f"{scene['year']}년 {scene['location']} {scene['time_of_day']} — {scene['action']}"
                    ),
                    "visual_focus": scene.get("visual_focus"),
                }
            )
        return units

    @staticmethod
    def _pick_subject(asset_type: str, index: int) -> str:
        if asset_type == "infographic":
            return INFOGRAPHIC_SUBJECT_CYCLE[index % len(INFOGRAPHIC_SUBJECT_CYCLE)]
        if asset_type == "text_emphasis":
            return TEXT_SUBJECT_CYCLE[index % len(TEXT_SUBJECT_CYCLE)]
        return VISUAL_SUBJECT_CYCLE[(index * _SUBJECT_STRIDE) % len(VISUAL_SUBJECT_CYCLE)]

    @staticmethod
    def _pick_motif(section: str, shot_index: int, first_shot: bool) -> str:
        if first_shot and section == "hook":
            return "simulation_start_opening"
        if shot_index % 9 == 0:
            return VISUAL_MOTIFS[(shot_index // 9) % len(VISUAL_MOTIFS)]
        return "none"

    def create_documentary_shot_list(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        for required in ("project.json", "story/story_outline.json"):
            if not (project_path / required).is_file():
                raise ADOSFileNotFoundError(
                    f"{required}가 없습니다: {project_path / required}",
                    location="DocumentaryShotPlanner.create_documentary_shot_list",
                    suggested_fix="ProjectEngine과 StoryEngine을 먼저 실행하세요.",
                )
        project = load_json(project_path / "project.json")
        outline = load_json(project_path / "story" / "story_outline.json")
        config = load_documentary_engine_config(project_path)
        rules = config["shot_duration_rules"]

        direction_plan = None
        direction_path = project_path / "direction" / "direction_plan.json"
        if direction_path.is_file():
            direction_plan = load_json(direction_path)

        mix_path = AssetMixPlanner().plan_path(project_path)
        if mix_path.is_file():
            mix_plan = load_json(mix_path)
            total_seconds = int(mix_plan["total_duration_seconds"])
        else:
            mix_plan = None
            total_seconds = int(project["duration"]["target_seconds"])

        structure_keys = list(outline["structure"].keys())
        duration_cycles = _duration_cycles_from_rules(rules)

        # 장면 대본(scene_script)이 있으면 장면이 샷을 끌고 간다 —
        # 영상은 글이 아니라 장면(Scene)으로 만든다 (docs/37 #2).
        scene_script = None
        scene_script_path = project_path / "story" / "scene_script.json"
        if scene_script_path.is_file():
            scene_script = load_json(scene_script_path)

        # 감독 연출 결정(Director Engine)이 있으면 장면별 카메라/색감을 감독이 정한다
        decisions_by_scene: dict[str, dict] = {}
        decisions_path = project_path / DIRECTION_DIR / "director_decisions.json"
        if decisions_path.is_file():
            director = load_json(decisions_path)
            decisions_by_scene = {
                decision["scene_id"]: decision for decision in director.get("decisions", [])
            }

        if scene_script and scene_script.get("scenes"):
            units = self._units_from_scene_script(scene_script["scenes"], total_seconds)
            scene_source = "scene_script"
        else:
            budgets = self._section_budgets(structure_keys, total_seconds)
            units = [
                {
                    "scene_id": f"SC{order:03d}",
                    "section": key,
                    "budget": budgets[key],
                    "prompt_context": None,
                    "visual_focus": None,
                }
                for order, key in enumerate(structure_keys, start=1)
            ]
            scene_source = "story_structure"

        shots: list[dict] = []
        scenes_summary: list[dict] = []
        shot_index = 0

        for unit in units:
            scene_id = unit["scene_id"]
            section = unit["section"]
            pattern = SECTION_ASSET_PATTERNS.get(section, SECTION_ASSET_PATTERNS["development"])
            functions = SECTION_FUNCTION_CYCLES.get(section, ["explanation"])
            palette = SECTION_COLOR_PALETTES.get(section, "cyan_orange_dark")
            decision = decisions_by_scene.get(scene_id)
            if decision:
                palette = decision.get("color", palette)
            remaining = unit["budget"]
            section_shot_count = 0

            while remaining > 0:
                asset_type = pattern[section_shot_count % len(pattern)]
                cycle = duration_cycles[asset_type]
                duration = cycle[section_shot_count % len(cycle)]
                if duration > remaining:
                    duration = remaining
                # 잔여 1초가 남지 않도록 이번 샷에서 미리 조정한다.
                # AI 영상 최대 길이 규칙은 어떤 경우에도 깨지 않는다 —
                # ai_video를 늘리는 대신 줄이거나, 잔여는 이미지 샷으로 채운다.
                if remaining - duration == 1:
                    if duration > 2:
                        duration -= 1
                    elif asset_type != "ai_video":
                        duration = remaining
                if duration < 2:
                    # 섹션 예산이 최소 샷 길이보다 작다 — 남은 초를 짧은 이미지 샷으로 채운다
                    asset_type = "image_camera_movement"
                    duration = remaining

                camera = CAMERA_TYPES[(shot_index * _CAMERA_STRIDE) % len(CAMERA_TYPES)]
                if shot_index == 0:
                    camera = "ultra_wide_establishing"
                # 장면의 첫 샷 카메라는 감독 결정이 우선한다 (Prompt는 결과물)
                if (
                    section_shot_count == 0
                    and decision
                    and decision.get("camera") in CAMERA_BIBLE
                ):
                    camera = decision["camera"]
                camera_spec = CAMERA_BIBLE[camera]
                subject = self._pick_subject(asset_type, shot_index)
                # 장면의 visual_focus는 그 장면 첫 샷의 피사체가 된다
                if (
                    section_shot_count == 0
                    and unit["visual_focus"]
                    and asset_type not in NO_TEXT_RISK_ASSET_TYPES
                    and unit["visual_focus"] in VISUAL_SUBJECT_CYCLE
                ):
                    subject = unit["visual_focus"]
                function = functions[section_shot_count % len(functions)]
                motif = self._pick_motif(section, shot_index, first_shot=(shot_index == 0))
                no_text_risk = (
                    subject in NO_TEXT_RISK_SUBJECTS
                    or asset_type in NO_TEXT_RISK_ASSET_TYPES
                )
                if unit["prompt_context"]:
                    prompt_intent = f"{unit['prompt_context']} — {subject} 중심의 {asset_type} 샷 ({function})"
                else:
                    prompt_intent = f"{section} 구간 — {subject} 중심의 {asset_type} 샷 ({function})"

                shot_index += 1
                section_shot_count += 1
                shots.append(
                    {
                        "shot_id": f"SH{shot_index:04d}",
                        "scene_id": scene_id,
                        "order": shot_index,
                        "duration_seconds": duration,
                        "asset_type": asset_type,
                        "narrative_function": function,
                        "camera_type": camera,
                        "lens": camera_spec["lens"],
                        "movement": camera_spec["movement"],
                        "subject_type": subject,
                        "visual_motif": motif,
                        "color_palette": palette,
                        "prompt_intent": prompt_intent,
                        "no_text_risk": no_text_risk,
                        "notes": "",
                    }
                )
                remaining -= duration

            scenes_summary.append(
                {
                    "scene_id": scene_id,
                    "section": section,
                    "budget_seconds": unit["budget"],
                    "shot_count": section_shot_count,
                }
            )

        shot_list = {
            "project_id": project["project_id"],
            "topic": project["topic"]["title"],
            "shot_list_mode": "documentary_v1",
            "total_duration_seconds": total_seconds,
            "planned_duration_seconds": sum(s["duration_seconds"] for s in shots),
            "total_shots": len(shots),
            "asset_mix_plan_ref": f"{DIRECTION_DIR}/asset_mix_plan.json" if mix_plan else None,
            "direction_plan_ref": "direction/direction_plan.json" if direction_plan else None,
            "visual_style": (
                direction_plan["visual_style"]
                if direction_plan
                else config["style_defaults"]["visual_style"]
            ),
            "scene_change_principle": "사람은 영상이 아니라 장면 전환(Scene Change)을 본다",
            "scene_source": scene_source,
            "scene_script_ref": "story/scene_script.json" if scene_source == "scene_script" else None,
            "director_decisions_ref": (
                f"{DIRECTION_DIR}/director_decisions.json" if decisions_by_scene else None
            ),
            "ai_video_max_seconds": rules["ai_video_max_seconds"],
            "scenes": scenes_summary,
            "shots": shots,
            "created_at": _now_iso(),
        }
        write_json(self.shot_list_path(project_path), shot_list)
        if self.logger:
            self.logger.info(
                f"다큐멘터리 샷 리스트 생성: {project['project_id']} ({len(shots)}샷)",
                metadata={"project_id": project["project_id"], "total_shots": len(shots)},
            )
        return shot_list

    def load_documentary_shot_list(self, project_path: str | Path) -> dict:
        path = self.shot_list_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"documentary_shot_list.json이 없습니다: {path}",
                location="DocumentaryShotPlanner.load_documentary_shot_list",
                suggested_fix="create_documentary_shot_list를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_documentary_shot_list(self, project_path: str | Path) -> bool:
        shot_list = self.load_documentary_shot_list(project_path)
        shots = shot_list.get("shots", [])
        if not shots:
            raise ADOSValidationError(
                "샷이 하나도 없습니다.",
                location="DocumentaryShotPlanner.validate_documentary_shot_list",
                suggested_fix="create_documentary_shot_list를 다시 실행하세요.",
            )
        for shot in shots:
            ADOSValidator.require_fields(
                shot,
                SHOT_REQUIRED_FIELDS,
                location="DocumentaryShotPlanner.validate_documentary_shot_list",
            )
        max_ai = shot_list.get("ai_video_max_seconds", 5)
        for shot in shots:
            if shot["asset_type"] == "ai_video" and shot["duration_seconds"] > max_ai:
                raise ADOSValidationError(
                    f"AI 영상 샷 {shot['shot_id']}이 {max_ai}초를 초과합니다: {shot['duration_seconds']}초",
                    location="DocumentaryShotPlanner.validate_documentary_shot_list",
                    suggested_fix="AI 영상은 5초 이하 조각으로 나누세요.",
                )
        # 샷 다양성 — 같은 카메라가 전체를 지배하면 안 된다
        camera_counts: dict[str, int] = {}
        subject_counts: dict[str, int] = {}
        for shot in shots:
            camera_counts[shot["camera_type"]] = camera_counts.get(shot["camera_type"], 0) + 1
            subject_counts[shot["subject_type"]] = subject_counts.get(shot["subject_type"], 0) + 1
        if len(camera_counts) < min(4, len(shots)):
            raise ADOSValidationError(
                f"카메라 타입 다양성이 부족합니다: {sorted(camera_counts)}",
                location="DocumentaryShotPlanner.validate_documentary_shot_list",
                suggested_fix="카메라 바이블의 다양한 타입을 사용하세요.",
            )
        dominant = max(camera_counts.values())
        if len(shots) >= 10 and dominant > len(shots) * 0.4:
            raise ADOSValidationError(
                f"한 카메라 타입이 샷의 40%를 초과합니다 ({dominant}/{len(shots)}).",
                location="DocumentaryShotPlanner.validate_documentary_shot_list",
                suggested_fix="카메라 순환 보폭을 확인하세요.",
            )
        if len(subject_counts) < min(5, len(shots)):
            raise ADOSValidationError(
                f"피사체 다양성이 부족합니다: {sorted(subject_counts)}",
                location="DocumentaryShotPlanner.validate_documentary_shot_list",
                suggested_fix="도시/손/눈/하늘/행성/지도 등 피사체를 섞으세요.",
            )
        return True
