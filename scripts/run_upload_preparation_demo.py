# -*- coding: utf-8 -*-
"""ADOS 업로드 준비 데모.

전체 dummy 파이프라인 완주 후 자산 요구사항·사람 검토 체크포인트·
최종 품질 게이트·YouTube 메타데이터 패키지·수동 업로드 안내·운영 보고서를
생성한다. 실자산이 없고 검토가 승인되지 않았으므로 upload_ready는 false가 정상.

실행: 프로젝트 루트에서  python scripts/run_upload_preparation_demo.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.pipeline import FullPipelineRunner  # noqa: E402


def main() -> int:
    runner = FullPipelineRunner()
    summary = runner.run_full_dummy_pipeline_with_upload_preparation()
    prep = summary["upload_preparation"]

    print(f"project_id               : {summary['project_id']}")
    print(f"project path             : {summary['project_path']}")
    print(f"asset_readiness_report   : {prep['asset_readiness_report']}")
    print(f"human_review_summary     : {prep['human_review_summary']}")
    print(f"final_quality_report     : {prep['final_quality_report']}")
    print(f"youtube_metadata_package : {prep['youtube_metadata_package']}")
    print(f"upload_readiness_checklist: {prep['upload_readiness_checklist']}")
    print(f"operation_report         : {prep['operation_report']}")
    print(f"final_decision           : {prep['final_decision']}")
    print(f"upload_ready             : {prep['upload_ready']}")
    if prep["next_manual_actions"]:
        print("next manual actions:")
        for action in prep["next_manual_actions"]:
            print(f"  - {action}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
