# -*- coding: utf-8 -*-
"""ADOS Foundation Utilities 테스트.

실행: 프로젝트 루트에서  python -m unittest tests.test_foundation -v
"""
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import (  # noqa: E402
    ADOSConfigLoader,
    ADOSError,
    ADOSFileNotFoundError,
    ADOSLogger,
    ADOSPathManager,
    ADOSValidationError,
    ADOSValidator,
    ADOSErrorReporter,
    ProjectStatus,
    ProviderMode,
    QualityGateResult,
    load_json,
    load_yaml,
    write_json,
    write_yaml,
)


class TestPathManager(unittest.TestCase):
    def setUp(self):
        self.pm = ADOSPathManager(PROJECT_ROOT)

    def test_root_detection(self):
        self.assertEqual(self.pm.root, PROJECT_ROOT)
        found = ADOSPathManager.find_project_root(PROJECT_ROOT / "docs")
        self.assertEqual(found, PROJECT_ROOT)

    def test_expected_folders(self):
        self.assertEqual(self.pm.docs, PROJECT_ROOT / "docs")
        self.assertEqual(self.pm.templates, PROJECT_ROOT / "templates")
        self.assertEqual(self.pm.channels, PROJECT_ROOT / "channels")
        self.assertEqual(self.pm.projects, PROJECT_ROOT / "projects")
        self.assertEqual(self.pm.engines, PROJECT_ROOT / "engines")
        self.assertEqual(self.pm.providers, PROJECT_ROOT / "providers")
        self.assertEqual(self.pm.memory, PROJECT_ROOT / "memory")
        self.assertEqual(self.pm.config, PROJECT_ROOT / "config")
        self.assertEqual(self.pm.prompts, PROJECT_ROOT / "prompts")
        self.assertEqual(self.pm.logs, PROJECT_ROOT / "logs")
        self.assertEqual(self.pm.reports, PROJECT_ROOT / "reports")
        self.assertEqual(self.pm.outputs, PROJECT_ROOT / "outputs")

    def test_safe_join(self):
        p = self.pm.join("projects", "sample", "project.json")
        self.assertTrue(str(p).startswith(str(self.pm.root)))

    def test_join_escape_blocked(self):
        with self.assertRaises(ADOSValidationError):
            self.pm.join("..", "outside.txt")


class TestFileLoader(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_json_roundtrip(self):
        data = {"channel_id": "future", "quality_score": 95, "이름": "충컴퍼니"}
        path = self.dir / "sub" / "data.json"
        write_json(path, data)
        self.assertEqual(load_json(path), data)

    def test_yaml_roundtrip(self):
        data = {"system_name": "ADOS", "supported_languages": ["ko", "en"]}
        path = self.dir / "data.yaml"
        write_yaml(path, data)
        self.assertEqual(load_yaml(path), data)

    def test_missing_file_error(self):
        with self.assertRaises(ADOSFileNotFoundError):
            load_json(self.dir / "no_such_file.json")


class TestLogger(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.logs_dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_logger_writes_files(self):
        logger = ADOSLogger("TestComponent", self.logs_dir)
        event = logger.info("테스트 메시지", metadata={"project_id": "p1"})
        text = logger.text_log_path.read_text(encoding="utf-8")
        self.assertIn("테스트 메시지", text)
        self.assertIn("[INFO]", text)
        self.assertIn("TestComponent", text)
        events = logger.event_log_path.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(events), 1)
        for key in ("timestamp", "level", "component", "message", "metadata"):
            self.assertIn(key, event)


class TestValidator(unittest.TestCase):
    def test_missing_required_fields(self):
        with self.assertRaises(ADOSValidationError) as ctx:
            ADOSValidator.require_fields({"a": 1}, ["a", "b", "c"], location="test")
        self.assertIn("b", str(ctx.exception))
        self.assertIn("c", str(ctx.exception))

    def test_enum_validation(self):
        ADOSValidator.validate_enum("manual", ProviderMode)
        with self.assertRaises(ADOSValidationError):
            ADOSValidator.validate_enum("turbo", ProviderMode, field="mode")

    def test_schema_validation(self):
        schema = {
            "channel_id": str,
            "quality_score": int,
            "status": {"type": str, "enum": list(ProjectStatus)},
            "note": {"type": str, "required": False},
        }
        ADOSValidator.validate_schema(
            {"channel_id": "future", "quality_score": 95, "status": "NEW"}, schema
        )
        with self.assertRaises(ADOSValidationError):
            ADOSValidator.validate_schema(
                {"channel_id": 123, "quality_score": "high", "status": "FLYING"},
                schema,
            )


class TestErrors(unittest.TestCase):
    def test_structured_error_dict(self):
        err = ADOSError(
            "문제 발생",
            location="tests",
            project_id="p1",
            stage="STORY",
            cause="원인",
            suggested_fix="수정 방법",
        )
        d = err.to_dict()
        for key in (
            "error_type", "message", "location", "project_id",
            "stage", "cause", "suggested_fix", "created_at",
        ):
            self.assertIn(key, d)
        self.assertEqual(d["error_type"], "ADOSError")
        self.assertEqual(d["stage"], "STORY")

    def test_reporter_handles_any_exception(self):
        reporter = ADOSErrorReporter()
        d = reporter.report(ValueError("plain error"))
        self.assertEqual(d["error_type"], "ValueError")
        self.assertEqual(d["message"], "plain error")


class TestConfigLoader(unittest.TestCase):
    def setUp(self):
        self.cfg = ADOSConfigLoader(ADOSPathManager(PROJECT_ROOT))

    def test_ados_config(self):
        self.assertEqual(self.cfg.company_name, "CHUNG COMPANY")
        self.assertEqual(self.cfg.system_name, "ADOS")
        self.assertEqual(self.cfg.default_language, "ko")
        self.assertEqual(self.cfg.supported_languages, ["ko", "en"])
        self.assertEqual(self.cfg.default_run_mode, "auto_until_package")
        self.assertTrue(self.cfg.human_review_required)

    def test_providers_config(self):
        for role, name in [
            ("visual", "midjourney"),
            ("motion", "midjourney_video"),
            ("voice", "typecast"),
            ("subtitle", "internal_subtitle"),
            ("editing", "internal_editing"),
        ]:
            provider = self.cfg.get_provider(role)
            self.assertEqual(provider["provider_name"], name)
            ADOSValidator.validate_enum(provider["mode"], ProviderMode)

    def test_quality_thresholds(self):
        self.assertEqual(self.cfg.get_quality_threshold("pass"), 95)
        self.assertEqual(self.cfg.get_quality_threshold("human_review_recommended"), 90)
        self.assertEqual(self.cfg.get_quality_threshold("auto_fix_required"), 80)
        self.assertEqual(self.cfg.get_quality_threshold("partial_regeneration_required"), 70)
        self.assertEqual(self.cfg.get_quality_threshold("fail"), 70)

    def test_quality_gate_values_exist(self):
        self.assertEqual(len(QualityGateResult), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
