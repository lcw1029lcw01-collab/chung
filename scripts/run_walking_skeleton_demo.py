# -*- coding: utf-8 -*-
"""ADOS walking skeleton 데모: Template → Channel → Project.

실행: 프로젝트 루트에서  python scripts/run_walking_skeleton_demo.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from core import ADOSPathManager  # noqa: E402
from engines.template import TemplateLoader  # noqa: E402
from create_sample_channel import (  # noqa: E402
    SAMPLE_CHANNEL_REQUEST,
    channel_exists,
    create_sample_channel,
)
from create_sample_project import create_sample_project  # noqa: E402

SAMPLE_TEMPLATE_ID = SAMPLE_CHANNEL_REQUEST["template_id"]


def run_demo(path_manager: ADOSPathManager | None = None) -> dict:
    pm = path_manager or ADOSPathManager()

    template = TemplateLoader(pm).load(SAMPLE_TEMPLATE_ID)

    channel_created = False
    if not channel_exists(pm):
        create_sample_channel(pm)
        channel_created = True

    project = create_sample_project(pm)

    return {
        "template": template,
        "channel_created": channel_created,
        "project_id": project["project_id"],
        "project_path": project["path"],
    }


def main() -> int:
    result = run_demo()
    print(f"template loaded : {result['template']['template_id']} (v{result['template']['version']})")
    channel_note = "새로 생성됨" if result["channel_created"] else "기존 채널 사용"
    print(f"channel ready   : {SAMPLE_CHANNEL_REQUEST['channel_id']} ({channel_note})")
    print("project created : OK")
    print(f"project path    : {result['project_path']}")
    print(f"project_id      : {result['project_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
