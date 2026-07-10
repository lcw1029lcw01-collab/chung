# -*- coding: utf-8 -*-
"""ADOS v0.2 수동 제작 루프 데모.

전체 dummy 파이프라인 + 업로드 준비를 완주한 뒤:
수동 워크스페이스 생성 → asset intake manifest 생성 →
최종 준비도 재실행 → 수동 제작 루프 보고서 생성.

가짜 실물 미디어 파일을 만들지 않고, 사람 검토도 자동 승인하지 않는다.
따라서 upload_ready는 false가 정상이다.

실행: 프로젝트 루트에서  python scripts/run_manual_production_loop_demo.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.manual_production import ManualProductionLoop  # noqa: E402
from engines.pipeline import FullPipelineRunner  # noqa: E402


def main() -> int:
    runner = FullPipelineRunner()
    summary = runner.run_full_dummy_pipeline_with_upload_preparation()
    project_path = Path(summary["project_path"])

    loop = ManualProductionLoop()
    prep = loop.prepare_manual_loop(project_path)

    # 실물 파일 배치·검토 승인 없이 준비도만 재계산 → BLOCKED가 정상
    upload_ready = loop.rerun_final_readiness(project_path)
    loop.create_manual_loop_report(project_path)

    print(f"project_id                : {summary['project_id']}")
    print(f"project path              : {project_path}")
    print(f"manual workspace path     : {prep['workspace_path']}")
    print(f"asset intake manifest     : {prep['intake_manifest_path']}")
    print(f"production asset manifest : {loop.registry.manifest_path(project_path)}")
    print(f"final quality report      : {loop.final_gate.report_path(project_path)}")
    print(f"upload readiness checklist: {loop.preparer.checklist_path(project_path)}")
    print(f"manual loop report        : {loop.loop_report_path(project_path)}")
    print(f"upload_ready              : {upload_ready}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
