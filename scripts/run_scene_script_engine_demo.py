# -*- coding: utf-8 -*-
"""Scene Script / World Bible / Motion / SEO 계층 데모.

세계관 바이블 → 더미 파이프라인(Direction까지) → 장면 대본 →
장면 기반 샷 리스트 → MJ/모션 프롬프트 블루프린트 → SEO 패키지 →
에피소드 앵커 등록까지 한 번에 실행한다.

외부 API 호출·업로드·실제 미디어 생성은 없다 (docs/37 #7).

실행: 프로젝트 루트에서
  python scripts/run_scene_script_engine_demo.py
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
    DirectorEngine,
    DocumentaryShotPlanner,
    MotionPromptEngine,
    PromptBlueprintEngine,
    SceneScriptEngine,
)
from engines.knowledge import KnowledgeEngine  # noqa: E402
from engines.project import ProjectEngine  # noqa: E402
from engines.research import ResearchEngine  # noqa: E402
from engines.seo import SEOEngine  # noqa: E402
from engines.story import StoryEngine  # noqa: E402
from engines.worldbuilding import WorldBibleEngine  # noqa: E402

SAMPLE_TOPIC = "100만 년 후 인간은 어떤 모습일까?"
SAMPLE_TOPIC_SLUG = "million-year-human-scene-script"
SAMPLE_DURATION_SECONDS = 1500

FALLBACK_CHANNEL_REQUEST = {
    "channel_id": "future",
    "channel_name": "Future Lab",
    "template_id": "future_documentary_template",
    "language": "ko",
}


def resolve_channel_id(paths: ADOSPathManager) -> str:
    if (paths.channels / "future_lab" / "channel.yaml").is_file():
        return "future_lab"
    if not (paths.channels / "future" / "channel.yaml").is_file():
        ChannelEngine(paths).create_channel(dict(FALLBACK_CHANNEL_REQUEST))
    return "future"


def main() -> int:
    paths = ADOSPathManager()
    channel_id = resolve_channel_id(paths)
    channel_path = paths.channels / channel_id

    world_engine = WorldBibleEngine()
    if not world_engine.bible_path(channel_path).is_file():
        world_engine.create_channel_world_bible(channel_path)
    world_engine.validate_channel_world_bible(channel_path)

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

    ResearchEngine().create_dummy_research(project_path)
    KnowledgeEngine().create_dummy_knowledge(project_path)
    StoryEngine().create_dummy_story(project_path)
    DirectionEngine().create_dummy_direction(project_path)

    scene_engine = SceneScriptEngine()
    scene_script = scene_engine.create_dummy_scene_script(project_path)
    scene_engine.validate_scene_script(project_path)

    # Director가 먼저 결정한다 — Prompt는 결과물 (docs/38)
    director_engine = DirectorEngine()
    director = director_engine.create_director_decisions(project_path)
    director_engine.validate_director_decisions(project_path)

    AssetMixPlanner().create_asset_mix_plan(
        project_path, duration_minutes=SAMPLE_DURATION_SECONDS // 60
    )
    shot_planner = DocumentaryShotPlanner()
    shot_list = shot_planner.create_documentary_shot_list(project_path)
    shot_planner.validate_documentary_shot_list(project_path)

    blueprint_engine = PromptBlueprintEngine()
    blueprints = blueprint_engine.create_midjourney_prompt_blueprints(project_path)
    blueprint_engine.validate_midjourney_prompt_blueprints(project_path)

    motion_engine = MotionPromptEngine()
    motions = motion_engine.create_motion_prompt_blueprints(project_path)
    motion_engine.validate_motion_prompt_blueprints(project_path)

    seo_engine = SEOEngine()
    seo = seo_engine.create_seo_package(project_path)
    seo_engine.validate_seo_package(project_path)

    anchor = scene_script["world_anchor"]
    if anchor:
        world_engine.register_episode_anchor(
            channel_path, project["project_id"], anchor["year"], anchor["event"]
        )

    print(f"project_id               : {project['project_id']}")
    print(f"channel_id               : {channel_id}")
    print(f"world_bible              : {world_engine.bible_path(channel_path)}")
    print(f"world_continuity         : {world_engine.continuity_path(channel_path)}")
    print(f"world_anchor             : {anchor['year'] if anchor else None}년 — {anchor['event'] if anchor else '-'}")
    print(f"scene_script             : {scene_engine.script_path(project_path)}")
    print(f"scene_script_guide       : {scene_engine.guide_path(project_path)}")
    print(f"total_scenes             : {scene_script['total_scenes']}")
    print(f"director_decisions       : {director_engine.decisions_path(project_path)}")
    first_decision = director["decisions"][0]
    print(
        f"director_sample          : {first_decision['scene_id']} "
        f"{first_decision['dominant_emotion']} → {first_decision['camera']} / "
        f"{first_decision['lens']} / {first_decision['color']} / {first_decision['music']}"
    )
    print(f"shot_list (scene 기반)    : {shot_planner.shot_list_path(project_path)}")
    print(f"scene_source             : {shot_list['scene_source']}")
    print(f"total_shots              : {shot_list['total_shots']}")
    print(f"mj_blueprints            : {blueprints['blueprint_count']}건")
    print(f"motion_blueprints        : {motions['total_ai_video_shots']}건")
    print(f"seo_package              : {seo_engine.package_path(project_path)}")
    print(f"title_candidates         : ko {len(seo['title_candidates_ko'])} / en {len(seo['title_candidates_en'])}")
    print(f"chapters                 : {len(seo['chapters'])}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
