# -*- coding: utf-8 -*-
"""Scene Script / World Bible / Motion / SEO 계층 테스트.

규칙: 임시 루트만 사용, 실제 channels/·projects/에 산출물을 만들지 않는다.
실행: 프로젝트 루트에서  python -m unittest tests.test_scene_script_world_seo -v
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
    DocumentaryShotPlanner,
    MotionPromptEngine,
    PromptBlueprintEngine,
    SceneScriptEngine,
)
from engines.knowledge import KnowledgeEngine  # noqa: E402
from engines.project import ProjectEngine  # noqa: E402
from engines.research import ResearchEngine  # noqa: E402
from engines.seo import SEOEngine, TRIGGER_AXES, load_seo_templates  # noqa: E402
from engines.story import StoryEngine  # noqa: E402
from engines.worldbuilding import WorldBibleEngine  # noqa: E402

DOCS_DIR = PROJECT_ROOT / "docs"
_DOCS_SNAPSHOT = sorted(
    (p.name, p.stat().st_size, p.stat().st_mtime_ns)
    for p in DOCS_DIR.rglob("*.md")
)

SAMPLE_TEMPLATE_YAML = (
    PROJECT_ROOT / "templates" / "future_documentary_template" / "template.yaml"
)

MEDIA_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".wav", ".mp3", ".m4a"}


def make_project_in_temp_root(tmp: Path, duration_seconds: int = 1500) -> Path:
    for d in ("docs", "config", "templates", "channels", "projects", "logs"):
        (tmp / d).mkdir(parents=True, exist_ok=True)
    dst = tmp / "templates" / "future_documentary_template"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy(SAMPLE_TEMPLATE_YAML, dst / "template.yaml")
    for config_name in (
        "documentary_engine.yaml", "scene_script_engine.yaml", "seo_templates.yaml"
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
            "topic_slug": "million-year-human-scene",
            "target_languages": ["ko", "en"],
            "duration_seconds": duration_seconds,
        }
    )
    return Path(result["path"])


def run_until_direction(project_path: Path) -> None:
    ResearchEngine().create_dummy_research(project_path)
    KnowledgeEngine().create_dummy_knowledge(project_path)
    StoryEngine().create_dummy_story(project_path)
    DirectionEngine().create_dummy_direction(project_path)


class SceneBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.project_path = make_project_in_temp_root(self.root)
        self.channel_path = self.root / "channels" / "future"

    def tearDown(self):
        self.tmp.cleanup()


class TestWorldBibleEngine(SceneBase):
    def test_requires_channel_yaml(self):
        with self.assertRaises(ADOSFileNotFoundError):
            WorldBibleEngine().create_channel_world_bible(self.root / "channels" / "nope")

    def test_world_bible_timeline_and_validation(self):
        engine = WorldBibleEngine()
        bible = engine.create_channel_world_bible(self.channel_path)
        self.assertTrue(engine.validate_channel_world_bible(self.channel_path))
        years = [entry["year"] for entry in bible["timeline"]]
        self.assertEqual(years, sorted(years))
        self.assertGreaterEqual(len(years), 5)
        for entry in bible["timeline"]:
            for field in ("technology", "politics", "economy", "cities", "human_form", "ai_role"):
                self.assertIn(field, entry)

    def test_create_twice_raises(self):
        engine = WorldBibleEngine()
        engine.create_channel_world_bible(self.channel_path)
        with self.assertRaises(ADOSValidationError):
            engine.create_channel_world_bible(self.channel_path)

    def test_anchor_resolution_picks_nearest_year(self):
        engine = WorldBibleEngine()
        engine.create_channel_world_bible(self.channel_path)
        anchor = engine.resolve_episode_anchor(self.channel_path, "2140년 화성에서 태어난 아이들")
        self.assertEqual(anchor["year"], 2140)
        fallback = engine.resolve_episode_anchor(self.channel_path, "미래의 어느 날")
        self.assertEqual(fallback["year"], 1000000)

    def test_register_episode_anchor_is_idempotent(self):
        engine = WorldBibleEngine()
        engine.create_channel_world_bible(self.channel_path)
        engine.register_episode_anchor(self.channel_path, "proj-1", 2140, "화성 독립")
        engine.register_episode_anchor(self.channel_path, "proj-1", 2140, "화성 독립")
        continuity = engine.load_continuity(self.channel_path)
        self.assertEqual(len(continuity["episodes"]), 1)


class TestSceneScriptEngine(SceneBase):
    def test_requires_story_outputs(self):
        with self.assertRaises(ADOSFileNotFoundError):
            SceneScriptEngine().create_dummy_scene_script(self.project_path)

    def test_scene_script_covers_all_narration_blocks(self):
        run_until_direction(self.project_path)
        engine = SceneScriptEngine()
        script = engine.create_dummy_scene_script(self.project_path)
        self.assertTrue(engine.validate_scene_script(self.project_path))
        draft = load_json(self.project_path / "story" / "script_draft.json")
        block_ids = {block["block_id"] for block in draft["narration_blocks"]}
        covered = {scene["narration_block_id"] for scene in script["scenes"]}
        self.assertEqual(block_ids, covered)
        self.assertGreaterEqual(script["total_scenes"], len(block_ids))

    def test_scene_fields_and_guide_written(self):
        run_until_direction(self.project_path)
        engine = SceneScriptEngine()
        script = engine.create_dummy_scene_script(self.project_path)
        scene = script["scenes"][0]
        for field in ("year", "location", "time_of_day", "weather", "action", "emotion", "visual_focus"):
            self.assertIn(field, scene, f"누락: {field}")
        self.assertTrue(engine.guide_path(self.project_path).is_file())
        guide = engine.guide_path(self.project_path).read_text(encoding="utf-8")
        self.assertIn("영화", guide)

    def test_world_anchor_used_when_bible_exists(self):
        WorldBibleEngine().create_channel_world_bible(self.channel_path)
        run_until_direction(self.project_path)
        script = SceneScriptEngine().create_dummy_scene_script(self.project_path)
        self.assertIsNotNone(script["world_anchor"])
        # 토픽 "100만 년 후..." → 1000000 앵커
        self.assertEqual(script["world_anchor"]["year"], 1000000)
        self.assertEqual(script["scenes"][0]["year"], 1000000)

    def test_deterministic(self):
        run_until_direction(self.project_path)
        engine = SceneScriptEngine()
        first = engine.create_dummy_scene_script(self.project_path)["scenes"]
        second = engine.create_dummy_scene_script(self.project_path)["scenes"]
        self.assertEqual(first, second)


class TestSceneDrivenShotList(SceneBase):
    def prepare(self) -> dict:
        WorldBibleEngine().create_channel_world_bible(self.channel_path)
        run_until_direction(self.project_path)
        SceneScriptEngine().create_dummy_scene_script(self.project_path)
        AssetMixPlanner().create_asset_mix_plan(self.project_path, duration_minutes=25)
        return DocumentaryShotPlanner().create_documentary_shot_list(self.project_path)

    def test_scene_script_drives_shot_list(self):
        shot_list = self.prepare()
        self.assertEqual(shot_list["scene_source"], "scene_script")
        self.assertEqual(shot_list["scene_script_ref"], "story/scene_script.json")
        scene_ids = {shot["scene_id"] for shot in shot_list["shots"]}
        self.assertTrue(all(scene_id.startswith("SCN") for scene_id in scene_ids))
        script = load_json(self.project_path / "story" / "scene_script.json")
        self.assertEqual(len(scene_ids), script["total_scenes"])
        self.assertTrue(
            DocumentaryShotPlanner().validate_documentary_shot_list(self.project_path)
        )

    def test_planned_duration_matches_total_in_scene_mode(self):
        shot_list = self.prepare()
        self.assertEqual(
            shot_list["planned_duration_seconds"], shot_list["total_duration_seconds"]
        )

    def test_prompt_intent_carries_scene_context(self):
        shot_list = self.prepare()
        first = shot_list["shots"][0]
        self.assertIn("년", first["prompt_intent"])  # 연도가 프롬프트 의도에 들어간다

    def test_fallback_without_scene_script_still_works(self):
        run_until_direction(self.project_path)
        shot_list = DocumentaryShotPlanner().create_documentary_shot_list(self.project_path)
        self.assertEqual(shot_list["scene_source"], "story_structure")
        self.assertIsNone(shot_list["scene_script_ref"])


class TestMotionPromptEngine(SceneBase):
    def prepare_shots(self):
        run_until_direction(self.project_path)
        SceneScriptEngine().create_dummy_scene_script(self.project_path)
        AssetMixPlanner().create_asset_mix_plan(self.project_path, duration_minutes=25)
        DocumentaryShotPlanner().create_documentary_shot_list(self.project_path)

    def test_motion_blueprints_for_ai_video_shots_only(self):
        self.prepare_shots()
        engine = MotionPromptEngine()
        result = engine.create_motion_prompt_blueprints(self.project_path)
        self.assertTrue(engine.validate_motion_prompt_blueprints(self.project_path))
        shot_list = load_json(
            self.project_path / "direction" / "documentary_shot_list.json"
        )
        ai_count = sum(1 for shot in shot_list["shots"] if shot["asset_type"] == "ai_video")
        self.assertEqual(result["total_ai_video_shots"], ai_count)

    def test_motion_prompts_include_camera_and_micro_motions(self):
        self.prepare_shots()
        result = MotionPromptEngine().create_motion_prompt_blueprints(self.project_path)
        blueprint = result["blueprints"][0]
        self.assertGreaterEqual(len(blueprint["micro_motions"]), 2)
        self.assertIn(blueprint["base_camera_motion"].split(".")[0], blueprint["final_prompt"])
        self.assertIn("no text", blueprint["final_prompt"])


class TestSEOEngine(SceneBase):
    def test_seo_package_counts(self):
        run_until_direction(self.project_path)
        SceneScriptEngine().create_dummy_scene_script(self.project_path)
        engine = SEOEngine()
        package = engine.create_seo_package(self.project_path)
        self.assertTrue(engine.validate_seo_package(self.project_path))
        self.assertEqual(package["seo_mode"], "formula_v2_triggers")
        self.assertEqual(len(package["title_candidates_ko"]), 20)
        self.assertEqual(len(package["title_candidates_en"]), 20)
        for key in ("title_candidates_ko", "title_candidates_en"):
            axes = {candidate["trigger"] for candidate in package[key]}
            self.assertEqual(axes, set(TRIGGER_AXES))
            for candidate in package[key]:
                self.assertNotIn("{topic", candidate["text"])  # 변수 치환 완료
        self.assertGreaterEqual(len(package["thumbnail_text_candidates"]), 5)
        self.assertGreaterEqual(len(package["tags"]), 10)
        self.assertGreaterEqual(len(package["chapters"]), 3)
        self.assertIn("[챕터]", package["description"])

    def test_ab_test_sets_pair_different_axes(self):
        run_until_direction(self.project_path)
        package = SEOEngine().create_seo_package(self.project_path)
        sets = package["ab_test_sets"]
        self.assertEqual(len(sets), 3)
        self.assertEqual([s["set_id"] for s in sets], ["AB1", "AB2", "AB3"])
        for ab_set in sets:
            self.assertNotEqual(ab_set["a"]["trigger"], ab_set["b"]["trigger"])
            self.assertTrue(ab_set["a"]["text"] and ab_set["b"]["text"])

    def test_seo_without_scene_script_has_minimal_chapters(self):
        run_until_direction(self.project_path)
        engine = SEOEngine()
        package = engine.create_seo_package(self.project_path)
        self.assertEqual(package["chapters"][0]["timestamp"], "00:00")

    def test_load_seo_templates_axes(self):
        triggers = load_seo_templates(self.project_path)
        self.assertEqual(set(triggers), set(TRIGGER_AXES))
        for axis in TRIGGER_AXES:
            self.assertGreaterEqual(len(triggers[axis]["ko_titles"]), 4)
            self.assertGreaterEqual(len(triggers[axis]["en_titles"]), 4)
            self.assertGreaterEqual(len(triggers[axis]["thumbnail_texts"]), 1)

    def test_seo_requires_templates_config(self):
        run_until_direction(self.project_path)
        (self.root / "config" / "seo_templates.yaml").unlink()
        with self.assertRaises(ADOSFileNotFoundError):
            load_seo_templates(self.project_path)


class TestSceneLayerReviewRegressions(SceneBase):
    """코드 리뷰에서 확인된 시나리오 회귀 테스트."""

    def test_units_budget_never_negative_and_sums_exactly(self):
        # 장면 스케일 ≫ 프로젝트 길이일 때 음수 예산이 나오던 버그
        run_until_direction(self.project_path)
        script_path = self.project_path / "story" / "scene_script.json"
        SceneScriptEngine().create_dummy_scene_script(self.project_path)
        script = load_json(script_path)
        base = script["scenes"][0]
        script["scenes"] = [
            {**base, "scene_id": f"SCN{i:03d}", "duration_seconds": 10.0}
            for i in range(1, 31)
        ]
        write_json(script_path, script)
        units = DocumentaryShotPlanner._units_from_scene_script(script["scenes"], 100)
        budgets = [unit["budget"] for unit in units]
        self.assertEqual(sum(budgets), 100)
        self.assertTrue(all(budget >= 2 for budget in budgets), budgets)

    def test_units_raise_when_duration_too_short_for_scenes(self):
        scenes = [
            {"scene_id": f"SCN{i:03d}", "section": "development", "duration_seconds": 10.0,
             "year": 2100, "location": "도시", "time_of_day": "dawn", "action": "걷는다",
             "visual_focus": "city"}
            for i in range(1, 31)
        ]
        with self.assertRaises(ADOSValidationError):
            DocumentaryShotPlanner._units_from_scene_script(scenes, 45)

    def test_sentences_distributed_without_duplication_or_loss(self):
        # 문장이 장면 수보다 많을 때 중복·유실되던 버그
        run_until_direction(self.project_path)
        draft_path = self.project_path / "story" / "script_draft.json"
        draft = load_json(draft_path)
        draft["narration_blocks"] = [
            {
                "block_id": "NB001",
                "section": "hook",
                "text": "첫 문장입니다. 둘째 문장입니다. 셋째 문장입니다. 넷째 문장입니다. 다섯째 문장입니다.",
                "estimated_duration_seconds": 31,
            }
        ]
        write_json(draft_path, draft)
        script = SceneScriptEngine().create_dummy_scene_script(self.project_path)
        narrations = [scene["narration_text"] for scene in script["scenes"]]
        joined = " ".join(narrations)
        for word in ("첫", "둘째", "셋째", "넷째", "다섯째"):
            self.assertEqual(joined.count(word), 1, f"{word} 문장이 중복/유실됨: {narrations}")

    def test_block_duration_defaults_from_script_total(self):
        # 블록별 길이가 없으면 대본 전체 길이/블록 수로 배분 (블록당 10초 고정 금지)
        run_until_direction(self.project_path)
        script = SceneScriptEngine().create_dummy_scene_script(self.project_path)
        # 1500초 / 5블록 = 300초 → 블록당 최대 분할(3장면)이 일어나야 한다
        self.assertGreater(script["total_scenes"], 5)
        self.assertGreater(script["total_duration_seconds"], 100)

    def test_anchor_ignores_plain_counts(self):
        engine = WorldBibleEngine()
        engine.create_channel_world_bible(self.channel_path)
        # "3가지"가 연도를 하이잭하면 안 된다 — "100만 년"이 이긴다
        anchor = engine.resolve_episode_anchor(
            self.channel_path, "3가지 시나리오: 100만 년 후 인간"
        )
        self.assertEqual(anchor["year"], 1000000)
        # 수량("1000개")만 있으면 연도 없음 → 마지막 연표 시점
        fallback = engine.resolve_episode_anchor(
            self.channel_path, "화성에 1000개의 도시가 생긴다면"
        )
        self.assertEqual(fallback["year"], 1000000)


class TestSceneLayerSafety(SceneBase):
    def test_no_media_files_created(self):
        WorldBibleEngine().create_channel_world_bible(self.channel_path)
        run_until_direction(self.project_path)
        SceneScriptEngine().create_dummy_scene_script(self.project_path)
        AssetMixPlanner().create_asset_mix_plan(self.project_path, duration_minutes=25)
        DocumentaryShotPlanner().create_documentary_shot_list(self.project_path)
        PromptBlueprintEngine().create_midjourney_prompt_blueprints(self.project_path)
        MotionPromptEngine().create_motion_prompt_blueprints(self.project_path)
        SEOEngine().create_seo_package(self.project_path)
        media = [
            str(p) for p in self.root.rglob("*")
            if p.is_file() and p.suffix.lower() in MEDIA_EXTENSIONS
        ]
        self.assertEqual(media, [], f"미디어 파일이 생성됨: {media}")


class TestZDocsUntouched(unittest.TestCase):
    def test_docs_not_modified(self):
        snapshot = sorted(
            (p.name, p.stat().st_size, p.stat().st_mtime_ns)
            for p in DOCS_DIR.rglob("*.md")
        )
        self.assertEqual(snapshot, _DOCS_SNAPSHOT, "테스트가 docs/*.md를 변경함")


if __name__ == "__main__":
    unittest.main(verbosity=2)
