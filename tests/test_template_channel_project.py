# -*- coding: utf-8 -*-
"""Template → Channel → Project 최소 생성 흐름 테스트.

실행: 프로젝트 루트에서  python -m unittest tests.test_template_channel_project -v
"""
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def _seoul_tz_available() -> bool:
    try:
        ZoneInfo("Asia/Seoul")
        return True
    except ZoneInfoNotFoundError:
        return False

from core import (  # noqa: E402
    ADOSFileNotFoundError,
    ADOSPathManager,
    ADOSValidationError,
    write_yaml,
)
from engines.channel import ChannelEngine  # noqa: E402
from engines.project import ProjectEngine, make_topic_slug  # noqa: E402
from engines.template import TemplateLoader  # noqa: E402

# docs 불변 검증용 스냅샷 (모듈 로드 시점)
DOCS_DIR = PROJECT_ROOT / "docs"
_DOCS_SNAPSHOT = sorted(
    (p.name, p.stat().st_size, p.stat().st_mtime_ns)
    for p in DOCS_DIR.rglob("*.md")
)


def make_temp_root(tmp: Path) -> ADOSPathManager:
    """임시 폴더를 ADOS 프로젝트 루트 형태로 구성한다."""
    for d in ("docs", "config", "templates", "channels", "projects", "logs"):
        (tmp / d).mkdir(parents=True, exist_ok=True)
    return ADOSPathManager(tmp)


def make_template(pm: ADOSPathManager, template_id="future", status="ACTIVE") -> None:
    write_yaml(
        pm.templates / template_id / "template.yaml",
        {"template_id": template_id, "name": "Future Template", "version": "1.0.0", "status": status},
    )


class TestTemplateLoader(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pm = make_temp_root(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_load_minimal_template(self):
        make_template(self.pm)
        data = TemplateLoader(self.pm).load("future")
        self.assertEqual(data["template_id"], "future")
        self.assertEqual(data["name"], "Future Template")
        self.assertEqual(str(data["version"]), "1.0.0")
        self.assertEqual(data["status"], "ACTIVE")

    def test_invalid_status_fails(self):
        make_template(self.pm, status="FLYING")
        with self.assertRaises(ADOSValidationError):
            TemplateLoader(self.pm).load("future")

    def test_missing_template_fails(self):
        with self.assertRaises(ADOSFileNotFoundError):
            TemplateLoader(self.pm).load("no_such_template")


class TestChannelEngine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pm = make_temp_root(Path(self.tmp.name))
        make_template(self.pm)
        self.engine = ChannelEngine(self.pm)
        self.request = {
            "channel_id": "future",
            "channel_name": "Beyond Humanity",
            "template_id": "future",
            "language": "ko",
        }

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_channel(self):
        result = self.engine.create_channel(self.request)
        folder = self.pm.channels / "future"
        self.assertTrue((folder / "channel.yaml").is_file())
        self.assertTrue((folder / "memory.yaml").is_file())
        self.assertTrue((folder / "reports").is_dir())
        self.assertTrue((folder / "logs").is_dir())
        self.assertEqual(result["channel"]["channel_name"], "Beyond Humanity")
        self.assertEqual(result["channel"]["template_version"], "1.0.0")
        self.assertEqual(result["channel"]["status"], "ACTIVE")

    def test_duplicate_channel_fails(self):
        self.engine.create_channel(self.request)
        with self.assertRaises(ADOSValidationError):
            self.engine.create_channel(self.request)

    def test_missing_template_fails(self):
        self.request["template_id"] = "ghost"
        with self.assertRaises(ADOSFileNotFoundError):
            self.engine.create_channel(self.request)


class TestProjectEngine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pm = make_temp_root(Path(self.tmp.name))
        make_template(self.pm)
        ChannelEngine(self.pm).create_channel(
            {
                "channel_id": "future",
                "channel_name": "Beyond Humanity",
                "template_id": "future",
                "language": "ko",
            }
        )
        self.engine = ProjectEngine(self.pm)
        self.request = {
            "channel_id": "future",
            "topic": "What will humans look like in one million years",
            "target_languages": ["ko", "en"],
            "duration_seconds": 900,
        }

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_project(self):
        result = self.engine.create_project(self.request)
        folder = Path(result["path"])
        self.assertTrue((folder / "project.json").is_file())
        self.assertTrue((folder / "topic.json").is_file())
        for sub in [
            "research", "knowledge", "story", "direction", "timeline",
            "prompts", "assets/images", "assets/motion", "assets/audio",
            "assets/subtitles", "edit", "reports", "workflow/handoffs",
            "workflow/stage_results", "logs", "package", "analytics",
            "learning", "ai_evolution",
        ]:
            self.assertTrue((folder / sub).is_dir(), f"누락된 폴더: {sub}")
        project = result["project"]
        self.assertEqual(project["status"], "INITIALIZED")
        self.assertEqual(project["current_stage"], "RESEARCH")
        self.assertEqual(project["languages"]["target_languages"], ["ko", "en"])
        self.assertEqual(project["duration"]["target_seconds"], 900)
        # project_id 형식: YYYYMMDD-HHMMSS-{channel_id}-{slug}
        self.assertRegex(
            result["project_id"], r"^\d{8}-\d{6}-future-[a-z0-9-]+$"
        )
        # projects/{channel_id}/{year}/{month}/{project_id}
        self.assertEqual(folder.parent.parent.parent.name, "future")

    def test_missing_channel_fails(self):
        self.request["channel_id"] = "ghost"
        with self.assertRaises(ADOSFileNotFoundError):
            self.engine.create_project(self.request)

    def test_topic_slug(self):
        self.assertEqual(make_topic_slug("Hello  World!"), "hello-world")
        self.assertEqual(
            make_topic_slug("a b c d e f g h i j"), "a-b-c-d-e-f-g-h"
        )
        self.assertEqual(make_topic_slug("한글만 있는 주제"), "topic")

    def test_topic_slug_request_field_used(self):
        """topic_slug를 주면 정제해서 project_id에 사용한다."""
        self.request["topic_slug"] = "Million Year Human!"
        result = self.engine.create_project(self.request)
        self.assertRegex(
            result["project_id"], r"^\d{8}-\d{6}-future-million-year-human$"
        )

    def test_resolve_timezone_fallback_utc(self):
        """config/ados.yaml이 없으면 UTC로 동작한다."""
        self.assertEqual(self.engine._resolve_timezone(), timezone.utc)

    @unittest.skipUnless(_seoul_tz_available(), "tz 데이터 없음 (tzdata 미설치)")
    def test_project_timestamp_uses_configured_timezone(self):
        """config timezone(Asia/Seoul)이 project_id 타임스탬프에 반영된다."""
        from core import write_yaml
        write_yaml(self.pm.config / "ados.yaml", {"timezone": "Asia/Seoul"})
        self.assertEqual(self.engine._resolve_timezone(), ZoneInfo("Asia/Seoul"))
        result = self.engine.create_project(self.request)
        ts = datetime.strptime(result["project_id"][:15], "%Y%m%d-%H%M%S")
        now_kst = datetime.now(ZoneInfo("Asia/Seoul")).replace(tzinfo=None)
        self.assertLess(abs((now_kst - ts).total_seconds()), 120)


class TestZDocsUntouched(unittest.TestCase):
    """모든 테스트가 임시 폴더에서만 동작했는지 — 실제 docs가 그대로인지 확인."""

    def test_docs_not_modified(self):
        current = sorted(
            (p.name, p.stat().st_size, p.stat().st_mtime_ns)
            for p in DOCS_DIR.rglob("*.md")
        )
        self.assertEqual(current, _DOCS_SNAPSHOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
