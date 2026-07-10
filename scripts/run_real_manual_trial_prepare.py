# -*- coding: utf-8 -*-
"""ADOS v0.3 실제 수동 트라이얼 준비.

전체 dummy 파이프라인 + 업로드 준비 완주 후:
provider export pack 3종 → 수동 워크스페이스 + intake manifest →
트라이얼 가이드·체크리스트 생성.

실제 미디어 파일을 만들지 않고, 검토도 자동 승인하지 않는다.
upload_ready는 false가 정상이다. 이후 작업은 사람이 수행한다.

실행: 프로젝트 루트에서  python scripts/run_real_manual_trial_prepare.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.manual_trial import ManualTrialRunner  # noqa: E402


def main() -> int:
    runner = ManualTrialRunner()
    summary = runner.prepare_real_manual_trial()

    print(f"project_id            : {summary['project_id']}")
    print(f"project path          : {summary['project_path']}")
    print(f"manual workspace path : {summary['workspace_path']}")
    print(f"trial guide (json)    : {summary['trial_guide_path']}")
    print(f"trial guide (md)      : {summary['trial_guide_md_path']}")
    print(f"trial checklist       : {summary['trial_checklist_path']}")
    print(f"intake manifest       : {summary['intake_manifest_path']}")
    for name, rel in summary["provider_export_paths"].items():
        print(f"export pack ({name:<16}): {rel}")
    print(f"upload_ready          : {summary['upload_ready']}")
    print()
    print(f"next human action     : {summary['next_human_action']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
