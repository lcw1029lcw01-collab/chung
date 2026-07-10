# -*- coding: utf-8 -*-
"""ADOS v0.2 수동 검토 데모 (검토 전용).

전체 dummy 파이프라인 + 업로드 준비 완주 후 수동 제작 루프를 준비하고,
**이 스크립트에서만** 사람 검토 체크포인트 전체를 승인한 뒤
최종 준비도를 재실행한다.

검토 승인만으로는 부족하다 — 실물 자산과 최종 영상이 없으므로
upload_ready는 여전히 false가 정상이다.

실행: 프로젝트 루트에서  python scripts/run_manual_review_demo.py
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
    loop.prepare_manual_loop(project_path)

    # 검토 전용 데모 — 명시적으로 전체 체크포인트 승인
    loop.approve_required_reviews(
        project_path, reviewer="human", notes="검토 전용 데모 승인"
    )
    upload_ready = loop.rerun_final_readiness(project_path)
    report = loop.create_manual_loop_report(project_path)

    print(f"project_id            : {summary['project_id']}")
    print(f"human_review_summary  : {loop.reviews.summary_path(project_path)}")
    print(f"final_quality_report  : {loop.final_gate.report_path(project_path)}")
    print(f"upload_ready          : {upload_ready}")
    print(f"blockers              : {report['blockers']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
