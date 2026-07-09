# -*- coding: utf-8 -*-
"""Walking skeleton 데모 테스트.

규칙: 실제 저장소에 채널/프로젝트를 만들지 않는다. 임시 루트에서만 생성한다.
실행: 프로젝트 루트에서  python -m unittest tests.test_walking_skeleton_demo -v
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from core import ADOSPathManager  # noqa: E402
from engines.template import TemplateLoader  # noqa: E402
from create_sample_channel import channel_exists, create_sample_channel  # noqa: E402
from create_sample_project import SAMPLE_PROJECT_REQUEST, create_sample_project  # noqa: E402
from run_walking_skeleton_demo import SAMPLE_TEMPLATE_ID, run_demo  # noqa: E402

DOCS_DIR = PROJECT_ROOT / "docs"
_DOCS_SNAPSHOT = sorted(
    (p.name, p.stat().st_size, p.stat().st_mtime_ns)
    for p in DOCS_DIR.rglob("*.md")
)

REAL_TEMPLATE_YAML = (
    PROJECT_ROOT / "templates" / SAMPLE_TEMPLATE_ID / "template.yaml"
)


def make_temp_root(tmp: Path) -> ADOSPathManager:
    """임시 ADOS 루트 구성 + 실제 샘플 템플릿 복사."""
    for d in ("docs", "config", "templates", "channels", "projects", "logs"):
        (tmp / d).mkdir(parents=True, exist_ok=True)
    dst = tmp / "templates" / SAMPLE_TEMPLATE_ID
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy(REAL_TEMPLATE_YAML, dst / "template.yaml")
    return ADOSPathManager(tmp)


class TestSampleTemplate(unittest.TestCase):
    def test_real_template_exists_and_loads(self):
        """실제 저장소의 샘플 템플릿이 로드된다 (읽기 전용)."""
        self.assertTrue(REAL_TEMPLATE_YAML.is_file())
        data = TemplateLoader(ADOSPathManager(PROJECT_ROOT)).load(SAMPLE_TEMPLATE_ID)
        self.assertEqual(data["template_id"], "future_documentary_template")
        self.assertEqual(data["status"], "ACTIVE")
        self.assertEqual(data["default_language"], "ko")
        self.assertEqual(data["supported_languages"], ["ko", "en"])


class TestSampleScriptsInTempRoot(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pm = make_temp_root(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_sample_channel(self):
        self.assertFalse(channel_exists(self.pm))
        result = create_sample_channel(self.pm)
        self.assertTrue(channel_exists(self.pm))
        self.assertEqual(result["channel"]["channel_name"], "Future Lab")
        self.assertEqual(result["channel"]["template_id"], SAMPLE_TEMPLATE_ID)

    def test_create_sample_project(self):
        create_sample_channel(self.pm)
        result = create_sample_project(self.pm)
        folder = Path(result["path"])
        self.assertTrue((folder / "project.json").is_file())
        self.assertTrue((folder / "topic.json").is_file())
        self.assertTrue(str(folder).startswith(str(self.pm.projects)))

    def test_sample_project_uses_english_slug(self):
        """한국어 topic이어도 topic_slug(million-year-human)로 project_id가 생성된다."""
        self.assertEqual(SAMPLE_PROJECT_REQUEST["topic_slug"], "million-year-human")
        create_sample_channel(self.pm)
        result = create_sample_project(self.pm)
        self.assertRegex(
            result["project_id"], r"^\d{8}-\d{6}-future-million-year-human$"
        )

    def test_demo_end_to_end(self):
        result = run_demo(self.pm)
        self.assertTrue(result["channel_created"])
        self.assertTrue(Path(result["project_path"]).is_dir())
        # 두 번째 실행: 기존 채널 재사용 + 새 프로젝트
        result2 = run_demo(self.pm)
        self.assertFalse(result2["channel_created"])
        self.assertNotEqual(result["project_id"], result2["project_id"])


class TestZRepoUntouched(unittest.TestCase):
    def test_docs_not_modified(self):
        current = sorted(
            (p.name, p.stat().st_size, p.stat().st_mtime_ns)
            for p in DOCS_DIR.rglob("*.md")
        )
        self.assertEqual(current, _DOCS_SNAPSHOT)

    def test_runtime_outputs_ignored_by_git(self):
        """channels/*, projects/* 런타임 산출물이 git에서 무시되는지 확인."""
        import shutil as _shutil
        import subprocess
        if not _shutil.which("git"):
            self.skipTest("git 없음")
        for target in ("channels/future", "projects/future"):
            rc = subprocess.run(
                ["git", "check-ignore", "-q", target],
                cwd=PROJECT_ROOT,
            ).returncode
            self.assertEqual(rc, 0, f"{target}가 gitignore되지 않음")
        # .gitkeep은 계속 추적되어야 한다
        tracked = subprocess.run(
            ["git", "ls-files", "channels/.gitkeep", "projects/.gitkeep"],
            cwd=PROJECT_ROOT, capture_output=True, text=True,
        ).stdout.split()
        self.assertEqual(len(tracked), 2, ".gitkeep 추적이 풀렸음")


if __name__ == "__main__":
    unittest.main(verbosity=2)
