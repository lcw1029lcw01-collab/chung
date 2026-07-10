# -*- coding: utf-8 -*-
"""ADOS v0.3 실제 수동 트라이얼 최종화.

검증·실자산 준비도·최종 게이트·업로드 패키지 전체를 재실행한다.
업로드하지 않는다 — 업로드는 manual_upload_instructions에 따라
사람이 직접 수행한다. upload_ready는 게이트가 실제로 통과할 때만 true다.

실행: 프로젝트 루트에서
  python scripts/run_real_manual_trial_finalize.py {project_path}
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import load_json  # noqa: E402
from engines.manual_trial import ManualTrialRunner  # noqa: E402

USAGE = """사용법: python scripts/run_real_manual_trial_finalize.py {project_path}

  project_path: 최종화할 프로젝트 폴더 경로
    예) projects/future/2026/07/20260710-120000-future-million-year-human

validate 스크립트로 검증을 통과하고 검토 승인을 마친 뒤 실행하세요."""


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(USAGE)
        return 1
    project_path = Path(argv[0])
    if not (project_path / "project.json").is_file():
        print(f"project.json이 없는 경로입니다: {project_path}")
        print()
        print(USAGE)
        return 1

    runner = ManualTrialRunner()
    upload_ready = runner.finalize_real_manual_trial(project_path)
    project = load_json(project_path / "project.json")
    gate = load_json(project_path / "reports" / "final_upload_gate.json")
    preparer = runner.loop.preparer

    print(f"project_id                : {project['project_id']}")
    print(f"youtube_metadata_package  : {preparer.metadata_path(project_path)}")
    print(f"upload_readiness_checklist: {preparer.checklist_path(project_path)}")
    print(f"manual_upload_instructions: {preparer.instructions_path(project_path)}")
    print(f"operation_report          : {project_path / 'reports' / 'operation_report.json'}")
    print(f"upload_ready              : {upload_ready}")
    print(f"blockers                  : {gate['blockers']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
