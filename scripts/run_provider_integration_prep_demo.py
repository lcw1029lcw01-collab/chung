# -*- coding: utf-8 -*-
"""ADOS v0.2 Provider 통합 준비 데모.

전체 dummy 파이프라인 + 업로드 준비를 완주한 뒤:
export pack 3종 생성 → provider job 3건 생성·상태 전환 시뮬레이션
→ placeholder 자산 메타데이터 import → AssetRegistry 연결
→ 준비도·최종 게이트 재계산.

외부 API 호출·업로드·실제 미디어 생성은 없다. upload_ready는 false가 정상.

실행: 프로젝트 루트에서  python scripts/run_provider_integration_prep_demo.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.assets import AssetRegistry  # noqa: E402
from engines.final_quality import FinalQualityGate  # noqa: E402
from engines.pipeline import FullPipelineRunner  # noqa: E402
from engines.provider_jobs import (  # noqa: E402
    ProviderExporter,
    ProviderImporter,
    ProviderJobManager,
)

SAMPLE_JOBS = [
    ("midjourney", "image_generation", "providers/exports/midjourney_prompt_pack.json"),
    ("midjourney_video", "motion_generation", "providers/exports/midjourney_video_prompt_pack.json"),
    ("typecast", "voice_generation", "providers/exports/typecast_script_pack.json"),
]

SAMPLE_IMPORTS = [
    ("midjourney", "image", "C:/manual_assets/SC001_v1.png", "SC001_v1.png"),
    ("midjourney_video", "motion", "C:/manual_assets/SC001_motion.mp4", "SC001_motion.mp4"),
    ("typecast", "audio", "C:/manual_assets/NB001_ko.wav", "NB001_ko.wav"),
]


def main() -> int:
    runner = FullPipelineRunner()
    summary = runner.run_full_dummy_pipeline_with_upload_preparation()
    project_path = Path(summary["project_path"])

    # 1) export pack 3종
    exporter = ProviderExporter()
    exporter.export_all_provider_packs(project_path)

    # 2) job queue + 샘플 job 3건 + 상태 전환 시뮬레이션
    jobs = ProviderJobManager()
    jobs.create_job_queue(project_path)
    for provider, job_type, source_ref in SAMPLE_JOBS:
        job = jobs.create_provider_job(
            project_path, provider, job_type, source_ref,
            payload={"note": "manual work pack 기반 수동 생성 대기"},
        )
        jobs.update_job_status(project_path, job["job_id"], "EXPORTED")
        jobs.update_job_status(
            project_path, job["job_id"], "WAITING_MANUAL_WORK",
            notes="사람이 외부 도구에서 생성 작업을 수행해야 함",
        )

    # 3) placeholder 자산 메타데이터 import + registry 연결
    importer = ProviderImporter()
    for provider, asset_type, source, target in SAMPLE_IMPORTS:
        item = importer.import_provider_asset_metadata(
            project_path, provider, asset_type, source, target,
            metadata={"note": "placeholder 경로 — 실제 파일 아님"},
        )
        importer.link_import_to_asset_registry(project_path, item["import_id"])

    # 4) 준비도·최종 게이트 재계산 (placeholder 경로라 여전히 BLOCKED가 정상)
    registry = AssetRegistry()
    registry.create_asset_readiness_report(project_path)
    final_report = FinalQualityGate().create_final_quality_report(project_path)

    exports = exporter.exports_dir(project_path)
    print(f"project_id                : {summary['project_id']}")
    print(f"project path              : {project_path}")
    print(f"midjourney export pack    : {exports / 'midjourney_prompt_pack.json'}")
    print(f"midjourney video pack     : {exports / 'midjourney_video_prompt_pack.json'}")
    print(f"typecast export pack      : {exports / 'typecast_script_pack.json'}")
    print(f"job_queue                 : {jobs.queue_path(project_path)}")
    print(f"provider_import_manifest  : {importer.manifest_path(project_path)}")
    print(f"production_asset_manifest : {registry.manifest_path(project_path)}")
    print(f"asset_readiness_report    : {registry.readiness_path(project_path)}")
    print(f"upload_ready              : {final_report['upload_ready']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
