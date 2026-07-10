# -*- coding: utf-8 -*-
"""ADOS v0.2 업로드 게이트 시뮬레이션 — **TEST ONLY**.

게이트 로직 증명 전용 스크립트다. gitignore된 manual_assets/{project_id}/
안에 아주 작은 placeholder 파일을 만들어 자산 존재 검사를 통과시키고,
검토를 승인한 뒤 upload_ready가 true로 전이하는지 확인한다.

placeholder는 실제 미디어가 아니며, 이 결과는 실제 제작 준비 완료를
의미하지 않는다. 업로드는 수행하지 않는다.

실행: 프로젝트 루트에서  python scripts/run_test_only_upload_gate_simulation.py
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import load_json, write_json, write_text  # noqa: E402
from engines.manual_production import ManualProductionLoop  # noqa: E402
from engines.pipeline import FullPipelineRunner  # noqa: E402

PLACEHOLDER_TEXT = "TEST ONLY placeholder. Not real media. Do not upload.\n"

TEST_ONLY_WARNING = (
    "TEST ONLY simulation using placeholder files. "
    "Not real production readiness. Do not upload."
)

SIM_REPORT_FILE = "test_only_upload_gate_simulation_report.json"

# TEST ONLY 마커를 심을 보고서들 (존재하는 것만 갱신)
_REPORTS_TO_MARK = [
    "reports/final_quality_report.json",
    "reports/final_upload_gate.json",
    "reports/manual_production_loop_report.json",
]


def mark_reports_test_only(
    project_path: str | Path, placeholder_count: int, upload_ready: bool
) -> Path:
    """생성된 보고서에 TEST ONLY 마커를 남기고 시뮬레이션 보고서를 만든다."""
    project_path = Path(project_path)
    for rel in _REPORTS_TO_MARK:
        path = project_path / rel
        if not path.is_file():
            continue
        report = load_json(path)
        report["test_only_simulation"] = True
        report["test_only_warning"] = TEST_ONLY_WARNING
        report["real_media_verified"] = False
        write_json(path, report)

    project = load_json(project_path / "project.json")
    sim_report_path = project_path / "reports" / SIM_REPORT_FILE
    write_json(sim_report_path, {
        "project_id": project["project_id"],
        "test_only_simulation": True,
        "placeholder_files_created": placeholder_count,
        "upload_ready_result": upload_ready,
        "warning": TEST_ONLY_WARNING,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return sim_report_path

BANNER = """
============================================================
  TEST ONLY — UPLOAD GATE SIMULATION
  - placeholder 파일은 실제 미디어가 아니다.
  - 실제 제작 준비 완료를 의미하지 않는다.
  - 아무것도 업로드하지 않는다.
============================================================
"""


def main() -> int:
    print(BANNER)

    runner = FullPipelineRunner()
    summary = runner.run_full_dummy_pipeline_with_upload_preparation()
    project_path = Path(summary["project_path"])

    loop = ManualProductionLoop()
    loop.prepare_manual_loop(project_path)

    # 1) 모든 intake item에 대해 tiny placeholder 파일 생성·배치 (gitignore 영역)
    manifest = loop.intake.load_asset_intake_manifest(project_path)
    for item in manifest["items"]:
        placeholder = PROJECT_ROOT / item["expected_file_path"]
        write_text(placeholder, PLACEHOLDER_TEXT)
        loop.intake.update_asset_intake_item(
            project_path, item["item_id"],
            file_path=str(placeholder),
            notes="TEST ONLY placeholder — not real media",
        )

    # 2) 메타데이터 등록 (복사 없음) + 검토 승인 + 준비도 재실행
    registered = loop.import_ready_assets(project_path)
    loop.approve_required_reviews(
        project_path, reviewer="human", notes="TEST ONLY simulation"
    )
    upload_ready = loop.rerun_final_readiness(project_path)
    report = loop.create_manual_loop_report(project_path)

    # 3) 생성된 보고서에 TEST ONLY 마커 기록 + 시뮬레이션 보고서 생성
    sim_report_path = mark_reports_test_only(
        project_path, placeholder_count=len(manifest["items"]),
        upload_ready=upload_ready,
    )

    print(f"project_id                  : {summary['project_id']}")
    print(f"registered placeholder count: {registered}")
    print(f"blockers                    : {report['blockers']}")
    print(f"simulation report           : {sim_report_path}")
    print(f"upload_ready (TEST ONLY)    : {upload_ready}")
    print()
    print("이 결과는 게이트 로직 증명용이며, 실제 제작 준비 완료가 아니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
