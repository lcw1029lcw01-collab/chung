# -*- coding: utf-8 -*-
"""ADOS v0.3 실제 수동 트라이얼 검증.

사람이 배치한 파일을 메타데이터로 등록하고 존재/확장자/최소 크기로
검증한 뒤 실자산 준비도·최종 게이트를 재계산한다.

미디어 내용은 검사하지 않는다. 업로드하지 않는다.
필수 파일 배치 + 검토 승인 전에는 upload_ready가 false가 정상이다.

실행: 프로젝트 루트에서
  python scripts/run_real_manual_trial_validate.py {project_path}
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.manual_trial import ManualTrialRunner  # noqa: E402

USAGE = """사용법: python scripts/run_real_manual_trial_validate.py {project_path}

  project_path: 검증할 프로젝트 폴더 경로
    예) projects/future/2026/07/20260710-120000-future-million-year-human

먼저 run_real_manual_trial_prepare.py로 트라이얼을 준비하고,
가이드의 기대 경로에 실제 파일을 배치한 뒤 이 스크립트를 실행하세요."""


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

    summary = ManualTrialRunner().validate_real_manual_trial(project_path)

    print(f"project_id                  : {summary['project_id']}")
    print(f"asset_file_validation_report: {summary['asset_file_validation_report']}")
    print(f"real_asset_readiness_report : {summary['real_asset_readiness_report']}")
    print(f"final_quality_report        : {summary['final_quality_report']}")
    print(f"validation PASS/FAIL        : {summary['validation_pass_count']}"
          f"/{summary['validation_fail_count']}")
    print(f"upload_ready                : {summary['upload_ready']}")
    print(f"blockers                    : {summary['blockers']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
