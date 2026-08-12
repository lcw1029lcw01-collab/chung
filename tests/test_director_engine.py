# -*- coding: utf-8 -*-
"""Director/Emotion Engine + Story 구조 템플릿 테스트.

규칙: 임시 루트만 사용, 실제 channels/·projects/에 산출물을 만들지 않는다.
실행: 프로젝트 루트에서  python -m unittest tests.test_director_engine -v
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import (  # noqa: E402
    ADOSFileNotFoundError,
    ADOSPathManager,
    ADOSValidationError,
    load_json,
    write_json,
)
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
from engines.story import StoryEngine  # noqa: E402

DOCS_DIR = PROJECT_ROOT / "docs"
_DOCS_SNAPSHOT = sorted(
    (p.name, p.stat().st_size, p.stat().st_mtime_ns)
    for p in DOCS_DIR.rglob("*.md")
)

SAMPLE_TEMPLATE_YAML = (
    PROJECT_ROOT / "templates" / "future_documentary_template" / "template.yaml"
)


def make_project_in_temp_root(tmp: Path, duration_seconds: int = 1500) -> Path:
    for d in ("docs", "config", "templates", "channels", "projects", "logs"):
        (tmp / d).mkdir(parents=True, exist_ok=True)
    dst = tmp / "templates" / "future_documentary_template"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy(SAMPLE_TEMPLATE_YAML, dst / "template.yaml")
    for config_name in (
        "documentary_engine.yaml",
        "scene_script_engine.yaml",
        "director_rules.yaml",
        "story_structures.yaml",
    ):
        shutil.copy(PROJECT_ROOT / "config" / config_name, tmp / "config" / config_name)
    pm = ADOSPathManager(tmp)
    ChannelEngine(pm).create_channel(
        {
            "channel_id": "future",
            "channel_name": "Future Lab",
            "template_id": "future_documentary_template",
            "language": "ko",
        }
    )
    result = ProjectEngine(pm).create_project(
        {
            "channel_id": "future",
            "topic": "100만 년 후 인간은 어떤 모습일까?",
            "topic_slug": "million-year-human-director",
            "target_languages": ["ko", "en"],
            "duration_seconds": duration_seconds,
        }
    )
    return Path(result["path"])


class DirectorBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.project_path = make_project_in_temp_root(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def run_to_scene_script(self, structure_template: str | None = None) -> dict:
        ResearchEngine().create_dummy_research(self.project_path)
        KnowledgeEngine().create_dummy_knowledge(self.project_path)
        StoryEngine().create_dummy_story(
            self.project_path, structure_template=structure_template
        )
        DirectionEngine().create_dummy_direction(self.project_path)
        return SceneScriptEngine().create_dummy_scene_script(self.project_path)


class TestDirectorEngine(DirectorBase):
    def test_requires_scene_script(self):
        with self.assertRaises(ADOSFileNotFoundError):
            DirectorEngine().create_director_decisions(self.project_path)

    def test_decisions_cover_all_scenes(self):
        script = self.run_to_scene_script()
        engine = DirectorEngine()
        result = engine.create_director_decisions(self.project_path)
        self.assertTrue(engine.validate_director_decisions(self.project_path))
        self.assertEqual(result["total_scenes"], script["total_scenes"])
        decided = {decision["scene_id"] for decision in result["decisions"]}
        self.assertEqual(
            decided, {scene["scene_id"] for scene in script["scenes"]}
        )

    def test_emotion_scores_pick_dominant(self):
        self.run_to_scene_script()
        # 장면 대본에 감정 스코어를 직접 기입 (CTO가 하는 일)
        script_path = self.project_path / "story" / "scene_script.json"
        script = load_json(script_path)
        script["scenes"][0]["emotion_scores"] = {"외로움": 80, "희망": 10, "공포": 60, "신비": 70}
        write_json(script_path, script)
        result = DirectorEngine().create_director_decisions(self.project_path)
        first = result["decisions"][0]
        self.assertEqual(first["dominant_emotion"], "loneliness")
        # 외로움 → Wide + Blue + Low Piano (director_rules)
        self.assertEqual(first["camera"], "ultra_wide_establishing")
        self.assertEqual(first["color"], "blue_earth")
        self.assertIn("piano", first["music"])

    def test_korean_emotion_alias(self):
        self.run_to_scene_script()
        script_path = self.project_path / "story" / "scene_script.json"
        script = load_json(script_path)
        script["scenes"][0]["emotion"] = "공포"
        write_json(script_path, script)
        result = DirectorEngine().create_director_decisions(self.project_path)
        first = result["decisions"][0]
        self.assertEqual(first["dominant_emotion"], "fear")
        self.assertEqual(first["camera"], "close_up")
        self.assertEqual(first["color"], "red_danger")

    def test_scene_weather_wins_over_rule(self):
        script = self.run_to_scene_script()
        result = DirectorEngine().create_director_decisions(self.project_path)
        for scene, decision in zip(script["scenes"], result["decisions"]):
            self.assertEqual(decision["weather"], scene["weather"])

    def test_deterministic(self):
        self.run_to_scene_script()
        engine = DirectorEngine()
        first = engine.create_director_decisions(self.project_path)["decisions"]
        second = engine.create_director_decisions(self.project_path)["decisions"]
        self.assertEqual(first, second)


class TestDirectorDrivesDownstream(DirectorBase):
    def prepare(self) -> dict:
        self.run_to_scene_script()
        script_path = self.project_path / "story" / "scene_script.json"
        script = load_json(script_path)
        script["scenes"][0]["emotion_scores"] = {"공포": 90}
        write_json(script_path, script)
        DirectorEngine().create_director_decisions(self.project_path)
        AssetMixPlanner().create_asset_mix_plan(self.project_path, duration_minutes=25)
        return DocumentaryShotPlanner().create_documentary_shot_list(self.project_path)

    def test_director_camera_and_color_flow_into_shots(self):
        shot_list = self.prepare()
        self.assertIsNotNone(shot_list["director_decisions_ref"])
        first_scene_id = shot_list["shots"][0]["scene_id"]
        first_scene_shots = [
            shot for shot in shot_list["shots"] if shot["scene_id"] == first_scene_id
        ]
        # 공포 → 첫 샷 카메라 close_up, 장면 색감 red_danger
        self.assertEqual(first_scene_shots[0]["camera_type"], "close_up")
        self.assertTrue(
            all(shot["color_palette"] == "red_danger" for shot in first_scene_shots)
        )
        self.assertTrue(
            DocumentaryShotPlanner().validate_documentary_shot_list(self.project_path)
        )

    def test_director_lighting_and_mood_flow_into_blueprints(self):
        self.prepare()
        result = PromptBlueprintEngine().create_midjourney_prompt_blueprints(self.project_path)
        self.assertEqual(result["provider_hint"], "midjourney")
        first = result["blueprints"][0]
        self.assertIsNotNone(first["director_context"])
        self.assertEqual(first["director_context"]["dominant_emotion"], "fear")
        self.assertEqual(first["lighting"], "hard shadow light")
        self.assertIn("dread", first["mood"])

    def test_movement_hint_flows_into_motion_prompts(self):
        self.prepare()
        result = MotionPromptEngine().create_motion_prompt_blueprints(self.project_path)
        self.assertEqual(result["provider_hint"], "midjourney_video")
        self.assertTrue(result["blueprints"])
        # 감독 결정이 있는 장면의 ai_video 샷은 movement_hint 문장을 포함한다
        shot_list = load_json(
            self.project_path / "direction" / "documentary_shot_list.json"
        )
        director = load_json(
            self.project_path / "direction" / "director_decisions.json"
        )
        hints = {d["scene_id"]: d["movement_hint"] for d in director["decisions"]}
        scene_of_shot = {s["shot_id"]: s["scene_id"] for s in shot_list["shots"]}
        for blueprint in result["blueprints"]:
            hint = hints.get(scene_of_shot[blueprint["shot_id"]])
            if hint:
                self.assertIn(hint.capitalize(), blueprint["final_prompt"])


class TestStoryStructureTemplates(DirectorBase):
    def run_story(self, template: str | None):
        ResearchEngine().create_dummy_research(self.project_path)
        KnowledgeEngine().create_dummy_knowledge(self.project_path)
        return StoryEngine().create_dummy_story(
            self.project_path, structure_template=template
        )

    def test_default_template_unchanged(self):
        outline = self.run_story(None)
        self.assertEqual(outline["structure_template"], "documentary_default")
        self.assertEqual(
            list(outline["structure"].keys()),
            ["hook", "setup", "development", "payoff", "ending"],
        )
        self.assertTrue(StoryEngine().validate_story(self.project_path))

    def test_history_template(self):
        outline = self.run_story("history")
        self.assertEqual(
            list(outline["structure"].keys()),
            ["hook", "conflict", "turning_point", "battle", "ending"],
        )
        self.assertTrue(StoryEngine().validate_story(self.project_path))

    def test_unknown_template_raises(self):
        with self.assertRaises(ADOSValidationError):
            self.run_story("no_such_template")

    def test_custom_template_flows_to_scene_script_and_shots(self):
        self.run_story("psychology")
        DirectionEngine().create_dummy_direction(self.project_path)
        script = SceneScriptEngine().create_dummy_scene_script(self.project_path)
        sections = {scene["section"] for scene in script["scenes"]}
        self.assertIn("question", sections)
        self.assertTrue(SceneScriptEngine().validate_scene_script(self.project_path))
        shot_list = DocumentaryShotPlanner().create_documentary_shot_list(self.project_path)
        self.assertGreater(shot_list["total_shots"], 0)
        self.assertEqual(
            shot_list["planned_duration_seconds"], shot_list["total_duration_seconds"]
        )
        self.assertTrue(
            DocumentaryShotPlanner().validate_documentary_shot_list(self.project_path)
        )


class TestZDocsUntouched(unittest.TestCase):
    def test_docs_not_modified(self):
        snapshot = sorted(
            (p.name, p.stat().st_size, p.stat().st_mtime_ns)
            for p in DOCS_DIR.rglob("*.md")
        )
        self.assertEqual(snapshot, _DOCS_SNAPSHOT, "테스트가 docs/*.md를 변경함")


if __name__ == "__main__":
    unittest.main(verbosity=2)
