# -*- coding: utf-8 -*-
"""AI Documentary Engine v1 데모.

더미 파이프라인을 Direction까지 실행한 뒤, 다큐멘터리 연출 계층
(바이블 → 자산 비율 → 샷 리스트 → 프롬프트 블루프린트 → 플래그십 청사진)을
샘플 프로젝트에 적용한다.

외부 API 호출·업로드·실제 미디어 생성은 없다 (docs/35 #12).

실행: 프로젝트 루트에서
  python scripts/run_documentary_engine_v1_demo.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import ADOSPathManager  # noqa: E402
from engines.channel import ChannelEngine  # noqa: E402
from engines.direction import DirectionEngine  # noqa: E402
from engines.documentary import (  # noqa: E402
    AssetMixPlanner,
    DocumentaryBibleEngine,
    DocumentaryShotPlanner,
    FlagshipEpisodePlanner,
    PromptBlueprintEngine,
)
from engines.knowledge import KnowledgeEngine  # noqa: E402
from engines.project import ProjectEngine  # noqa: E402
from engines.research import ResearchEngine  # noqa: E402
from engines.story import StoryEngine  # noqa: E402

SAMPLE_TOPIC = "100만 년 후 인간은 어떤 모습일까?"
SAMPLE_TOPIC_SLUG = "million-year-human-documentary"
SAMPLE_DURATION_SECONDS = 1500  # 25분

FALLBACK_CHANNEL_REQUEST = {
    "channel_id": "future",
    "channel_name": "Future Lab",
    "template_id": "future_documentary_template",
    "language": "ko",
}


def resolve_channel_id(paths: ADOSPathManager) -> str:
    """future_lab 채널이 있으면 쓰고, 없으면 future 샘플 채널을 안전하게 확보한다."""
    if (paths.channels / "future_lab" / "channel.yaml").is_file():
        return "future_lab"
    if not (paths.channels / "future" / "channel.yaml").is_file():
        ChannelEngine(paths).create_channel(dict(FALLBACK_CHANNEL_REQUEST))
    return "future"


def main() -> int:
    paths = ADOSPathManager()
    channel_id = resolve_channel_id(paths)
    channel_path = paths.channels / channel_id

    project = ProjectEngine(paths).create_project(
        {
            "channel_id": channel_id,
            "topic": SAMPLE_TOPIC,
            "topic_slug": SAMPLE_TOPIC_SLUG,
            "target_languages": ["ko", "en"],
            "duration_seconds": SAMPLE_DURATION_SECONDS,
        }
    )
    project_path = Path(project["path"])

    # 더미 파이프라인을 Direction까지 실행
    ResearchEngine().create_dummy_research(project_path)
    KnowledgeEngine().create_dummy_knowledge(project_path)
    StoryEngine().create_dummy_story(project_path)
    DirectionEngine().create_dummy_direction(project_path)

    # 다큐멘터리 연출 계층
    bible_engine = DocumentaryBibleEngine()
    if bible_engine.bible_path(channel_path).is_file():
        bible_engine.load_channel_documentary_bible(channel_path)
    else:
        bible_engine.create_channel_documentary_bible(channel_path)
    bible_engine.validate_channel_documentary_bible(channel_path)

    mix_planner = AssetMixPlanner()
    mix_planner.create_asset_mix_plan(project_path, duration_minutes=SAMPLE_DURATION_SECONDS // 60)
    mix_planner.validate_asset_mix_plan(project_path)

    shot_planner = DocumentaryShotPlanner()
    shot_list = shot_planner.create_documentary_shot_list(project_path)
    shot_planner.validate_documentary_shot_list(project_path)

    blueprint_engine = PromptBlueprintEngine()
    blueprints = blueprint_engine.create_midjourney_prompt_blueprints(project_path)
    blueprint_engine.validate_midjourney_prompt_blueprints(project_path)

    flagship_planner = FlagshipEpisodePlanner()
    flagship = flagship_planner.create_flagship_episode_blueprint(project_path)
    flagship_planner.validate_flagship_episode_blueprint(project_path)

    shots_by_type: dict[str, int] = {}
    for shot in shot_list["shots"]:
        shots_by_type[shot["asset_type"]] = shots_by_type.get(shot["asset_type"], 0) + 1

    print(f"project_id                  : {project['project_id']}")
    print(f"project_path                : {project_path}")
    print(f"channel_id                  : {channel_id}")
    print(f"documentary_bible           : {bible_engine.bible_path(channel_path)}")
    print(f"asset_mix_plan              : {mix_planner.plan_path(project_path)}")
    print(f"documentary_shot_list       : {shot_planner.shot_list_path(project_path)}")
    print(f"midjourney_prompt_blueprints: {blueprint_engine.blueprints_path(project_path)}")
    print(f"flagship_episode_blueprint  : {flagship_planner.blueprint_path(project_path)}")
    print(f"total_shots                 : {shot_list['total_shots']}")
    print(f"shots_by_asset_type         : {shots_by_type}")
    print(f"blueprint_count             : {blueprints['blueprint_count']}")
    print(f"target_quality_score        : {flagship['target_quality_score']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
