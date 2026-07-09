# -*- coding: utf-8 -*-
"""샘플 프로젝트 생성 스크립트 (walking skeleton).

실행: 프로젝트 루트에서  python scripts/create_sample_project.py
사전 조건: channels/future/channel.yaml (scripts/create_sample_channel.py로 생성)
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import ADOSFileNotFoundError, ADOSPathManager  # noqa: E402
from engines.project import ProjectEngine  # noqa: E402

SAMPLE_PROJECT_REQUEST = {
    "channel_id": "future",
    "topic": "100만 년 후 인간은 어떤 모습일까?",
    "topic_slug": "million-year-human",
    "target_languages": ["ko", "en"],
    "duration_seconds": 900,
}


def create_sample_project(path_manager: ADOSPathManager | None = None) -> dict:
    pm = path_manager or ADOSPathManager()
    return ProjectEngine(pm).create_project(dict(SAMPLE_PROJECT_REQUEST))


def main() -> int:
    try:
        result = create_sample_project()
    except ADOSFileNotFoundError:
        print("채널이 없습니다: channels/future/channel.yaml")
        print("먼저 실행하세요:  python scripts/create_sample_channel.py")
        return 1
    print(f"프로젝트 생성 완료: {result['path']}")
    print(f"project_id: {result['project_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
