# -*- coding: utf-8 -*-
"""수동 자산 등록 데모.

샘플 프로젝트를 만들고 자산 요구사항·제작 자산 manifest를 생성한 뒤,
placeholder 경로로 예시 자산 메타데이터를 등록한다 (파일 복사 없음).

실행: 프로젝트 루트에서  python scripts/run_manual_asset_registration_demo.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.assets import AssetRegistry  # noqa: E402
from engines.pipeline import FullPipelineRunner  # noqa: E402

EXAMPLE_ASSETS = [
    ("image", "C:/manual_assets/SC001_hero.png", "SC001_hero.png"),
    ("audio", "C:/manual_assets/narration_ko.wav", "narration_ko.wav"),
    ("video", "C:/manual_assets/final_video.mp4", "final_video.mp4"),
]


def main() -> int:
    runner = FullPipelineRunner()
    project = runner.create_sample_project()
    project_path = Path(project["path"])

    registry = AssetRegistry()
    registry.create_asset_requirements(project_path)
    registry.create_production_asset_manifest(project_path)

    for asset_type, source, target in EXAMPLE_ASSETS:
        item = registry.register_asset(
            project_path, asset_type, source, target,
            metadata={"note": "placeholder 경로 — 실제 파일 아님"},
        )
        print(f"registered: {item['asset_id']} ({asset_type}) exists={item['exists']} copied={item['copied']}")

    readiness = registry.create_asset_readiness_report(project_path)
    manifest = registry.load_production_asset_manifest(project_path)

    print()
    print(f"project_id                : {project['project_id']}")
    print(f"production_asset_manifest : {registry.manifest_path(project_path)}")
    print(f"asset_readiness_report    : {registry.readiness_path(project_path)}")
    print(f"registered asset count    : {len(manifest['assets'])}")
    print(f"real_assets_present       : {readiness['real_assets_present']}")
    print("upload_ready              : False (실자산 없음·검토 미승인 — 최종 게이트 미통과)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
