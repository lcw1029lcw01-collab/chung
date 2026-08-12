# -*- coding: utf-8 -*-
"""Template bundle 로드/검증 테스트.

실행: 프로젝트 루트에서  python -m unittest tests.test_template_bundle -v
"""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import ADOSFileNotFoundError, ADOSPathManager, write_yaml  # noqa: E402
from engines.template import TemplateLoader, validate_bundle  # noqa: E402
from engines.workflow import EXECUTOR_ALLOWLIST  # noqa: E402
from tests.production_test_utils import (  # noqa: E402
    MINI_TEMPLATE_ID,
    make_temp_root,
    mini_pipeline_stages,
    mini_view,
    write_mini_template,
)


class BundleBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pm = make_temp_root(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def problems_for(self, stages=None, view=None) -> list[str]:
        write_mini_template(self.pm, stages=stages, view=view)
        return TemplateLoader(self.pm).validate_bundle(MINI_TEMPLATE_ID)


class TestRealTemplateBundle(unittest.TestCase):
    """실제 저장소의 future_documentary_template 번들 (읽기 전용)."""

    def setUp(self):
        self.loader = TemplateLoader(ADOSPathManager(PROJECT_ROOT))

    def test_full_bundle_loads_and_validates(self):
        problems = self.loader.validate_bundle("future_documentary_template")
        self.assertEqual(problems, [])
        bundle = self.loader.load_bundle("future_documentary_template")
        self.assertTrue(bundle.is_production_bundle)
        self.assertEqual(bundle.metadata["content_type"], "longform_documentary")
        stage_ids = [s["id"] for s in bundle.pipeline["stages"]]
        self.assertEqual(stage_ids[0], "PROJECT_INTAKE")
        self.assertEqual(stage_ids[-1], "PUBLISH_APPROVAL")
        self.assertEqual(len(stage_ids), 14)

    def test_all_executors_in_allowlist(self):
        bundle = self.loader.load_bundle("future_documentary_template")
        for stage in bundle.pipeline["stages"]:
            self.assertIn(stage["executor"], EXECUTOR_ALLOWLIST)


class TestMinimalTemplateCompat(BundleBase):
    def test_minimal_template_still_loads(self):
        """기존 최소 템플릿(template.yaml만)은 계속 load된다."""
        write_yaml(self.pm.templates / "mini_min" / "template.yaml", {
            "template_id": "mini_min", "name": "Min", "version": "1.0.0", "status": "ACTIVE",
        })
        loader = TemplateLoader(self.pm)
        self.assertEqual(loader.load("mini_min")["template_id"], "mini_min")
        bundle = loader.load_bundle("mini_min")
        self.assertFalse(bundle.is_production_bundle)
        # production 검증은 실패해야 한다 (참조 누락 보고)
        problems = loader.validate_bundle("mini_min")
        self.assertTrue(any("참조 누락" in p for p in problems))


class TestBundleValidation(BundleBase):
    def test_valid_mini_bundle_passes(self):
        self.assertEqual(self.problems_for(), [])

    def test_missing_referenced_file_fails(self):
        write_mini_template(self.pm)
        (self.pm.templates / MINI_TEMPLATE_ID / "roles.yaml").unlink()
        with self.assertRaises(ADOSFileNotFoundError):
            TemplateLoader(self.pm).load_bundle(MINI_TEMPLATE_ID)

    def test_duplicate_stage_id_fails(self):
        stages = mini_pipeline_stages()
        stages[1]["id"] = "T_INTAKE"  # 중복
        stages[1]["depends_on"] = ["T_INTAKE"]
        problems = self.problems_for(stages=stages)
        self.assertTrue(any("stage ID 중복" in p for p in problems))

    def test_dependency_cycle_fails(self):
        stages = mini_pipeline_stages()
        stages[0]["depends_on"] = ["T_ASSETS"]  # 순환
        problems = self.problems_for(stages=stages)
        self.assertTrue(any("순환 dependency" in p for p in problems))

    def test_unknown_executor_fails(self):
        stages = mini_pipeline_stages()
        stages[0]["executor"] = "evil.import_anything"
        problems = self.problems_for(stages=stages)
        self.assertTrue(any("알 수 없는 executor" in p for p in problems))

    def test_unknown_kind_fails(self):
        stages = mini_pipeline_stages()
        stages[0]["kind"] = "magic"
        problems = self.problems_for(stages=stages)
        self.assertTrue(any("알 수 없는 kind" in p for p in problems))

    def test_unknown_role_fails(self):
        stages = mini_pipeline_stages()
        stages[0]["owner_role"] = "ghost_role"
        problems = self.problems_for(stages=stages)
        self.assertTrue(any("존재하지 않는 role" in p for p in problems))

    def test_duplicate_artifact_key_fails(self):
        stages = mini_pipeline_stages()
        stages[1]["produces"] = ["project_intake"]  # 이미 T_INTAKE가 생산
        problems = self.problems_for(stages=stages)
        self.assertTrue(any("artifact key 중복" in p for p in problems))

    def test_requires_without_producer_fails(self):
        stages = mini_pipeline_stages()
        stages[1]["requires"] = ["nonexistent_artifact"]
        problems = self.problems_for(stages=stages)
        self.assertTrue(any("생산하는 앞선 단계가 없습니다" in p for p in problems))

    def test_invalid_view_stage_reference_fails(self):
        view = mini_view()
        view["tabs"][0]["stages"] = ["GHOST_STAGE"]
        problems = self.problems_for(view=view)
        self.assertTrue(any("존재하지 않는 stage 참조" in p for p in problems))

    def test_invalid_view_artifact_reference_fails(self):
        view = mini_view()
        view["tabs"][0]["artifacts"] = ["ghost_artifact"]
        problems = self.problems_for(view=view)
        self.assertTrue(any("존재하지 않는 artifact 참조" in p for p in problems))

    def test_invalid_dependency_reference_fails(self):
        stages = mini_pipeline_stages()
        stages[1]["depends_on"] = ["GHOST"]
        problems = self.problems_for(stages=stages)
        self.assertTrue(any("잘못된 dependency" in p for p in problems))


class TestZDocsUntouched(unittest.TestCase):
    def test_marker(self):
        self.assertTrue((PROJECT_ROOT / "docs").is_dir())


if __name__ == "__main__":
    unittest.main(verbosity=2)
