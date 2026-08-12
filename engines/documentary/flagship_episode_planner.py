# -*- coding: utf-8 -*-
"""Flagship episode planner (documentary direction layer v1).

첫 대표작(플래그십 에피소드)의 제작 청사진을 만든다 — 채널 기준을 보여주는
95점급 레퍼런스 영상의 전략과 리스크를 정리한다.
근거: docs/35_AI_DOCUMENTARY_ENGINE_V1.md #10

주의: 첫 영상은 자동화 과시용이 아니라 채널 방향성·제작 기준·검증 루프
확정용이다. 실제 미디어는 만들지 않는다.
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
from engines.documentary.asset_mix_planner import AssetMixPlanner
from engines.documentary.shot_planner import DocumentaryShotPlanner

REPORTS_DIR = "reports"
BLUEPRINT_FILE = "flagship_episode_blueprint.json"

TARGET_QUALITY_SCORE = 95

BLUEPRINT_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "flagship_goal",
    "target_quality_score",
    "why_this_topic_represents_channel",
    "intro_strategy",
    "middle_strategy",
    "climax_strategy",
    "ending_strategy",
    "visual_motif_usage",
    "required_human_review_focus",
    "production_risks",
    "created_at",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class FlagshipEpisodePlanner:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def blueprint_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / REPORTS_DIR / BLUEPRINT_FILE

    def create_flagship_episode_blueprint(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project_json = project_path / "project.json"
        if not project_json.is_file():
            raise ADOSFileNotFoundError(
                f"project.json이 없습니다: {project_json}",
                location="FlagshipEpisodePlanner.create_flagship_episode_blueprint",
                suggested_fix="ProjectEngine.create_project를 먼저 실행하세요.",
            )
        project = load_json(project_json)
        topic_title = project["topic"]["title"]
        channel_name = project["channel"]["channel_name"]

        shot_stats = None
        shot_list_path = DocumentaryShotPlanner().shot_list_path(project_path)
        if shot_list_path.is_file():
            shot_list = load_json(shot_list_path)
            shot_stats = {
                "total_shots": shot_list["total_shots"],
                "planned_duration_seconds": shot_list["planned_duration_seconds"],
            }
        mix_ref = None
        if AssetMixPlanner().plan_path(project_path).is_file():
            mix_ref = "direction/asset_mix_plan.json"

        blueprint = {
            "project_id": project["project_id"],
            "topic": topic_title,
            "flagship_goal": (
                "채널의 기준을 보여주는 첫 대표작 — 업로드 가능한 수동+ADOS 혼합 레퍼런스. "
                "자동화 성능 과시가 아니라 채널 방향성과 제작 기준을 확정한다."
            ),
            "target_quality_score": TARGET_QUALITY_SCORE,
            "why_this_topic_represents_channel": (
                f"'{topic_title}'는 {channel_name}의 정체성(미래·과학·상상력)을 가장 잘 보여주는 "
                "대표 주제다 — 시청자가 몇 초만 봐도 채널의 톤을 인식해야 한다."
            ),
            "intro_strategy": (
                "인트로는 100% 시네마틱 영상 임팩트 — 우주→도시→인간으로 이어지는 "
                "고품질 AI 영상 조각(각 5초 이하)과 오프닝 모티프로 시작한다."
            ),
            "middle_strategy": (
                "본론은 이미지+카메라 무빙 중심(70% 이미지 / 30% 영상) — 나레이션이 스토리를 끌고, "
                "장면 전환 리듬(2~6초 이미지 샷)과 인포그래픽이 이해를 돕는다."
            ),
            "climax_strategy": (
                "클라이맥스는 영상 중심(70% 영상 / 30% 이미지) — 드론 오빗·로우 앵글 등 "
                "임팩트 샷과 감정 비트를 몰아 배치한다."
            ),
            "ending_strategy": (
                "엔딩은 거의 이미지+음악 — 따뜻한 색감의 스틸과 여운으로 마무리하고 "
                "채널 정체성(다음 에피소드 예고)을 강화한다."
            ),
            "visual_motif_usage": (
                "지구 홀로그램, HUD 연도 표시, 동일 오프닝 애니메이션, 청록+주황 색감을 "
                "매 에피소드 반복해 몇 초만 봐도 채널을 인식하게 한다."
            ),
            "required_human_review_focus": [
                "자막이 최종 영상에 실제로 보이는지 (번인 확인)",
                "프레임 안에 읽을 수 있는 텍스트가 없는지 (no-text 규칙)",
                "같은 카메라/피사체가 연속 반복되지 않는지 (샷 다양성)",
                "나레이션과 장면 전환 타이밍이 맞는지",
                "색감이 컬러 바이블과 일치하는지",
            ],
            "production_risks": [
                "AI 영상 과다 사용 시 'AI 같다'는 인상과 비용 폭발",
                "이미지 업스케일 품질 저하 (원본 해상도 확인 필요)",
                "MJ 결과물에 텍스트가 섞여 나오는 경우 재생성 필요",
                "수동 제작 단계에서 파일 경로/이름 불일치",
            ],
            "shot_statistics": shot_stats,
            "asset_mix_plan_ref": mix_ref,
            "created_at": _now_iso(),
        }
        write_json(self.blueprint_path(project_path), blueprint)
        if self.logger:
            self.logger.info(
                f"플래그십 에피소드 청사진 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"]},
            )
        return blueprint

    def load_flagship_episode_blueprint(self, project_path: str | Path) -> dict:
        path = self.blueprint_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"flagship_episode_blueprint.json이 없습니다: {path}",
                location="FlagshipEpisodePlanner.load_flagship_episode_blueprint",
                suggested_fix="create_flagship_episode_blueprint를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_flagship_episode_blueprint(self, project_path: str | Path) -> bool:
        blueprint = self.load_flagship_episode_blueprint(project_path)
        ADOSValidator.require_fields(
            blueprint,
            BLUEPRINT_REQUIRED_FIELDS,
            location="FlagshipEpisodePlanner.validate_flagship_episode_blueprint",
        )
        if blueprint["target_quality_score"] != TARGET_QUALITY_SCORE:
            raise ADOSValidationError(
                f"target_quality_score는 {TARGET_QUALITY_SCORE}여야 합니다: "
                f"{blueprint['target_quality_score']}",
                location="FlagshipEpisodePlanner.validate_flagship_episode_blueprint",
                suggested_fix="첫 대표작의 목표는 95점이다 — 90점 최소, 95점 진짜 목표.",
            )
        return True
