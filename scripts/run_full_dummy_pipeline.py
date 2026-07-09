# -*- coding: utf-8 -*-
"""ADOS 전체 dummy 파이프라인 실행 스크립트.

샘플 채널/프로젝트 생성부터 AI_EVOLUTION까지 전 단계를 완주하고
실행 보고서를 생성한다. 외부 API 호출·업로드·실제 자산 생성은 없다.

실행: 프로젝트 루트에서  python scripts/run_full_dummy_pipeline.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.pipeline import FullPipelineRunner  # noqa: E402
from engines.reporting import RunReportGenerator  # noqa: E402


def main() -> int:
    runner = FullPipelineRunner()
    summary = runner.run_full_dummy_pipeline()
    project_path = Path(summary["project_path"])

    reporter = RunReportGenerator()
    report = reporter.create_run_report(project_path)

    ai_evolution_path = project_path / "ai_evolution" / "ai_evolution_report.json"
    print(f"project_id          : {summary['project_id']}")
    print(f"project path        : {summary['project_path']}")
    print(f"final stage         : {summary['final_stage']} (status: {summary['workflow_status']})")
    print(f"run_report path     : {reporter.report_path(project_path)}")
    print(f"output_inventory    : {reporter.inventory_path(project_path)}")
    print(f"ai_evolution_report : {ai_evolution_path}")
    print(f"production_ready    : {report['production_ready']}")
    print(f"upload_ready        : {report['upload_ready']}")
    print(f"outputs detected    : {report['total_outputs_detected']} / missing: {len(report['missing_expected_outputs'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
