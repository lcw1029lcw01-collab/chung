# -*- coding: utf-8 -*-
"""AI Documentary Engine v1 (연출 계층) 테스트.

규칙: 임시 루트만 사용, 실제 channels/·projects/에 산출물을 만들지 않는다.
실행: 프로젝트 루트에서  python -m unittest tests.test_documentary_engine_v1 -v
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
    load_yaml,
)
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
    shutil.copy(
        PROJECT_ROOT / "config" / "documentary_engine.yaml",
        tmp / "config" / "documentary_engine.yaml",
    )
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
            "topic_slug": "million-year-human-documentary",
            "target_languages": ["ko", "en"],
            "duration_seconds": duration_seconds,
        }
    )
    return Path(result["path"])


def run_until_direction(project_path: Path) -> None:
    """샷 플래너의 사전 조건인 R→K→S→D 더미 산출물을 만든다."""
    ResearchEngine().create_dummy_research(project_path)
    KnowledgeEngine().create_dummy_knowledge(project_path)
    StoryEngine().create_dummy_story(project_path)
    DirectionEngine().create_dummy_direction(project_path)


class DocumentaryBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.project_path = make_project_in_temp_root(self.root)
        self.channel_path = self.root / "channels" / "future"

    def tearDown(self):
        self.tmp.cleanup()

    def run_direction_layer(self) -> dict:
        run_until_direction(self.project_path)
        AssetMixPlanner().create_asset_mix_plan(self.project_path, duration_minutes=25)
        return DocumentaryShotPlanner().create_documentary_shot_list(self.project_path)


class TestDocumentaryEngineConfig(unittest.TestCase):
    def test_config_exists_with_25_minute_mix_defaults(self):
        config_path = PROJECT_ROOT / "config" / "documentary_engine.yaml"
        self.assertTrue(config_path.is_file(), "config/documentary_engine.yaml 누락")
        config = load_yaml(config_path)
        self.assertEqual(config["default_duration_minutes"], 25)
        mix = config["asset_mix"]
        self.assertEqual(mix["ai_video_percent"], 22)
        self.assertEqual(mix["image_camera_movement_percent"], 55)
        self.assertEqual(mix["infographic_percent"], 15)
        self.assertEqual(mix["text_emphasis_percent"], 8)
        self.assertEqual(config["shot_duration_rules"]["ai_video_max_seconds"], 5)
        self.assertEqual(config["style_defaults"]["visual_style"], "netflix_future_documentary")
        self.assertTrue(config["style_defaults"]["no_text_rule"])


class TestDocumentaryBible(DocumentaryBase):
    def test_requires_channel_yaml(self):
        with self.assertRaises(ADOSFileNotFoundError):
            DocumentaryBibleEngine().create_channel_documentary_bible(
                self.root / "channels" / "no_such_channel"
            )

    def test_bible_includes_camera_character_color_bible(self):
        engine = DocumentaryBibleEngine()
        bible = engine.create_channel_documentary_bible(self.channel_path)
        self.assertTrue(engine.bible_path(self.channel_path).is_file())
        self.assertGreaterEqual(len(bible["camera_bible"]), 11)
        self.assertIn("ultra_wide_establishing", bible["camera_bible"])
        self.assertIn("future_human_type_a", bible["character_bible"])
        self.assertEqual(bible["color_bible"]["mars"], "orange")
        self.assertIn("simulation_start_opening", bible["visual_motifs"])
        self.assertTrue(engine.validate_channel_documentary_bible(self.channel_path))

    def test_bible_create_twice_raises(self):
        engine = DocumentaryBibleEngine()
        engine.create_channel_documentary_bible(self.channel_path)
        with self.assertRaises(ADOSValidationError):
            engine.create_channel_documentary_bible(self.channel_path)


class TestAssetMixPlanner(DocumentaryBase):
    def test_mix_uses_target_ratios(self):
        planner = AssetMixPlanner()
        plan = planner.create_asset_mix_plan(self.project_path, duration_minutes=25)
        self.assertTrue(planner.validate_asset_mix_plan(self.project_path))
        total = plan["total_duration_seconds"]
        self.assertEqual(total, 1500)
        planned = plan["planned_seconds_by_asset_type"]
        # AI 영상 20~25%, 이미지 50~60%
        self.assertGreaterEqual(planned["ai_video"] / total, 0.20)
        self.assertLessEqual(planned["ai_video"] / total, 0.25)
        self.assertGreaterEqual(planned["image_camera_movement"] / total, 0.50)
        self.assertLessEqual(planned["image_camera_movement"] / total, 0.60)
        self.assertGreater(planned["image_camera_movement"], planned["ai_video"])
        counts = plan["estimated_counts"]
        for key in ("ai_video_shots", "image_shots", "infographic_shots", "text_emphasis_shots"):
            self.assertGreaterEqual(counts[key], 1, f"누락: {key}")


class TestDocumentaryShotPlanner(DocumentaryBase):
    def test_requires_story_outline(self):
        with self.assertRaises(ADOSFileNotFoundError):
            DocumentaryShotPlanner().create_documentary_shot_list(self.project_path)

    def test_ai_video_shots_do_not_exceed_5_seconds(self):
        shot_list = self.run_direction_layer()
        for shot in shot_list["shots"]:
            if shot["asset_type"] == "ai_video":
                self.assertLessEqual(
                    shot["duration_seconds"], 5,
                    f"{shot['shot_id']} AI 영상이 5초 초과",
                )

    def test_shot_list_has_varied_camera_types(self):
        shot_list = self.run_direction_layer()
        cameras = {shot["camera_type"] for shot in shot_list["shots"]}
        self.assertGreaterEqual(len(cameras), 8, f"카메라 다양성 부족: {sorted(cameras)}")
        # 한 카메라가 전체를 지배하지 않는다
        counts = {}
        for shot in shot_list["shots"]:
            counts[shot["camera_type"]] = counts.get(shot["camera_type"], 0) + 1
        self.assertLess(max(counts.values()), len(shot_list["shots"]) * 0.4)

    def test_shot_list_has_varied_subject_types(self):
        shot_list = self.run_direction_layer()
        subjects = {shot["subject_type"] for shot in shot_list["shots"]}
        self.assertGreaterEqual(len(subjects), 5, f"피사체 다양성 부족: {sorted(subjects)}")

    def test_shot_mix_approximates_target_ratio(self):
        shot_list = self.run_direction_layer()
        seconds_by_type: dict[str, int] = {}
        for shot in shot_list["shots"]:
            seconds_by_type[shot["asset_type"]] = (
                seconds_by_type.get(shot["asset_type"], 0) + shot["duration_seconds"]
            )
        total = sum(seconds_by_type.values())
        self.assertGreaterEqual(seconds_by_type["ai_video"] / total, 0.15)
        self.assertLessEqual(seconds_by_type["ai_video"] / total, 0.30)
        self.assertGreaterEqual(seconds_by_type["image_camera_movement"] / total, 0.45)
        self.assertLessEqual(seconds_by_type["image_camera_movement"] / total, 0.65)

    def test_planned_duration_matches_total(self):
        shot_list = self.run_direction_layer()
        self.assertEqual(shot_list["planned_duration_seconds"], shot_list["total_duration_seconds"])

    def test_validation_passes(self):
        self.run_direction_layer()
        self.assertTrue(
            DocumentaryShotPlanner().validate_documentary_shot_list(self.project_path)
        )

    def test_deterministic_output(self):
        shot_list = self.run_direction_layer()
        again = DocumentaryShotPlanner().create_documentary_shot_list(self.project_path)
        strip = lambda sl: [  # noqa: E731
            {k: v for k, v in shot.items()} for shot in sl["shots"]
        ]
        self.assertEqual(strip(shot_list), strip(again))


class TestPromptBlueprintEngine(DocumentaryBase):
    def test_blueprints_generated_per_shot(self):
        shot_list = self.run_direction_layer()
        engine = PromptBlueprintEngine()
        result = engine.create_midjourney_prompt_blueprints(self.project_path)
        eligible = [
            shot for shot in shot_list["shots"]
            if shot["asset_type"] in ("image_camera_movement", "ai_video")
        ]
        self.assertEqual(result["blueprint_count"], len(eligible))
        self.assertGreater(result["blueprint_count"], 100)  # 씬당 1개가 아니라 샷당 1개
        self.assertTrue(engine.validate_midjourney_prompt_blueprints(self.project_path))

    def test_blueprints_have_structured_fields_and_no_text_safety(self):
        self.run_direction_layer()
        result = PromptBlueprintEngine().create_midjourney_prompt_blueprints(self.project_path)
        blueprint = result["blueprints"][0]
        for field in (
            "subject", "environment", "camera", "lens", "lighting", "atmosphere",
            "mood", "composition", "film_reference", "aspect_ratio",
            "negative_prompt", "no_text_safety_notes", "final_prompt",
        ):
            self.assertIn(field, blueprint, f"누락: {field}")
        self.assertIn("--no", blueprint["final_prompt"])
        self.assertIn("text", blueprint["negative_prompt"])
        self.assertTrue(blueprint["no_text_safety_notes"])
        self.assertEqual(blueprint["aspect_ratio"], "16:9")

    def test_blueprint_prompts_vary_between_shots(self):
        self.run_direction_layer()
        result = PromptBlueprintEngine().create_midjourney_prompt_blueprints(self.project_path)
        prompts = {bp["final_prompt"] for bp in result["blueprints"][:20]}
        self.assertGreater(len(prompts), 5, "프롬프트가 씬당 제네릭 1개 수준으로 반복됨")


class TestFlagshipEpisodePlanner(DocumentaryBase):
    def test_flagship_target_quality_score_is_95(self):
        self.run_direction_layer()
        planner = FlagshipEpisodePlanner()
        blueprint = planner.create_flagship_episode_blueprint(self.project_path)
        self.assertEqual(blueprint["target_quality_score"], 95)
        self.assertTrue(planner.validate_flagship_episode_blueprint(self.project_path))
        self.assertTrue(blueprint["required_human_review_focus"])


class TestShortDurationAndConfigRegressions(unittest.TestCase):
    """코드 리뷰에서 확인된 시나리오 회귀 테스트."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def make_project(self, duration_seconds: int) -> Path:
        project_path = make_project_in_temp_root(self.root, duration_seconds=duration_seconds)
        run_until_direction(project_path)
        return project_path

    def test_short_durations_92_to_108_validate(self):
        # hook 예산 6초(ai 5초 + 잔여 1초)에서 잔여 흡수가 ai 샷을 6초로 늘리던 버그
        planner = DocumentaryShotPlanner()
        for seconds in (92, 100, 108):
            with self.subTest(seconds=seconds):
                tmp = tempfile.TemporaryDirectory()
                try:
                    project_path = make_project_in_temp_root(
                        Path(tmp.name), duration_seconds=seconds
                    )
                    run_until_direction(project_path)
                    shot_list = planner.create_documentary_shot_list(project_path)
                    self.assertTrue(planner.validate_documentary_shot_list(project_path))
                    self.assertEqual(
                        shot_list["planned_duration_seconds"],
                        shot_list["total_duration_seconds"],
                    )
                finally:
                    tmp.cleanup()

    def test_partial_config_backfills_defaults(self):
        # asset_mix에 키 1개만 있는 config — 나머지는 기본값으로 채워져야 한다
        project_path = self.make_project(1500)
        (self.root / "config" / "documentary_engine.yaml").write_text(
            "asset_mix:\n  ai_video_percent: 20\n", encoding="utf-8"
        )
        plan = AssetMixPlanner().create_asset_mix_plan(project_path, duration_minutes=25)
        self.assertEqual(plan["target_mix"]["ai_video"], 20)
        self.assertEqual(plan["target_mix"]["image_camera_movement"], 55)

    def test_empty_config_falls_back_to_defaults(self):
        project_path = self.make_project(1500)
        (self.root / "config" / "documentary_engine.yaml").write_text(
            "# 주석만 있는 config\n", encoding="utf-8"
        )
        plan = AssetMixPlanner().create_asset_mix_plan(project_path, duration_minutes=25)
        self.assertEqual(plan["target_mix"]["ai_video"], 22)

    def test_lowered_ai_video_max_is_respected_by_generation(self):
        # 생성부가 config의 ai_video_max_seconds를 무시하던 버그
        project_path = self.make_project(1500)
        config_path = self.root / "config" / "documentary_engine.yaml"
        config_path.write_text(
            "shot_duration_rules:\n  ai_video_max_seconds: 4\n", encoding="utf-8"
        )
        planner = DocumentaryShotPlanner()
        shot_list = planner.create_documentary_shot_list(project_path)
        self.assertTrue(planner.validate_documentary_shot_list(project_path))
        for shot in shot_list["shots"]:
            if shot["asset_type"] == "ai_video":
                self.assertLessEqual(shot["duration_seconds"], 4, shot["shot_id"])


class TestDocumentaryEngineSafety(DocumentaryBase):
    def test_no_media_files_created(self):
        self.run_direction_layer()
        PromptBlueprintEngine().create_midjourney_prompt_blueprints(self.project_path)
        FlagshipEpisodePlanner().create_flagship_episode_blueprint(self.project_path)
        DocumentaryBibleEngine().create_channel_documentary_bible(self.channel_path)
        media = [
            str(p) for p in self.root.rglob("*")
            if p.is_file() and p.suffix.lower() in MEDIA_EXTENSIONS
        ]
        self.assertEqual(media, [], f"미디어 파일이 생성됨: {media}")

    def test_runtime_outputs_remain_ignored(self):
        gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
        for pattern in ("channels/*", "projects/*", "manual_assets/"):
            self.assertIn(pattern, gitignore, f".gitignore에 {pattern} 누락")


class TestZDocsUntouched(unittest.TestCase):
    def test_docs_not_modified(self):
        snapshot = sorted(
            (p.name, p.stat().st_size, p.stat().st_mtime_ns)
            for p in DOCS_DIR.rglob("*.md")
        )
        self.assertEqual(snapshot, _DOCS_SNAPSHOT, "테스트가 docs/*.md를 변경함")


if __name__ == "__main__":
    unittest.main(verbosity=2)
