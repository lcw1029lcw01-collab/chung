# -*- coding: utf-8 -*-
"""ADOS production CLI — 템플릿 검증·프로젝트 생성·워크플로우 운영.

기본적으로 외부 호출과 업로드는 금지된다.
외부 호출이 선언된 stage는 config(allow_external_calls)와 --allow-external이
둘 다 있어야 실행된다.

사용:
  python scripts/ados.py template validate future_documentary_template
  python scripts/ados.py project create --channel CHANNEL_ID --topic "주제" --duration 900
  python scripts/ados.py project status PROJECT_PATH
  python scripts/ados.py project next PROJECT_PATH
  python scripts/ados.py project run-until-gate PROJECT_PATH
  python scripts/ados.py project import-result PROJECT_PATH STAGE_ID RESULT_FILE
  python scripts/ados.py project approve PROJECT_PATH STAGE_ID --decision APPROVE --reviewer human
  python scripts/ados.py project retry PROJECT_PATH STAGE_ID [--force]
  python scripts/ados.py project view PROJECT_PATH
"""
import argparse
import io
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from core import ADOSError, ADOSPathManager  # noqa: E402


def _engine(project_path: str):
    from engines.workflow import ProductionWorkflowEngine

    return ProductionWorkflowEngine(project_path)


def _print_status(status: dict) -> None:
    print(f"project : {status['project_id']}")
    print(f"workflow: {status['workflow_status']} "
          f"({status['progress']['completed']}/{status['progress']['total']} 완료)")
    print(f"current : {status['current_stage']}")
    print()
    for stage in status["stages"]:
        marker = {
            "COMPLETED": "[v]", "RUNNING": "[>]", "PENDING": "[ ]", "SKIPPED": "[-]",
            "WAITING_APPROVAL": "[?]", "WAITING_INPUT": "[?]", "WAITING_EXTERNAL": "[?]",
            "FAILED": "[x]", "BLOCKED": "[!]",
        }.get(stage["status"], "[ ]")
        line = f"  {marker} {stage['id']:<22} {stage['status']:<18} ({stage['kind']}, {stage['owner_role']})"
        print(line)
        if stage["blocker"]:
            print(f"        blocker: {stage['blocker']}")
        if stage["error"]:
            print(f"        error  : {stage['error']}")
    if status["blockers"]:
        print()
        print("blockers:")
        for blocker in status["blockers"]:
            print(f"  - {blocker}")
    print()
    print(f"next    : {status['next_action']['description']}")


def cmd_template_validate(args) -> int:
    from engines.template import TemplateLoader

    loader = TemplateLoader(ADOSPathManager(PROJECT_ROOT))
    problems = loader.validate_bundle(args.template_id)
    if problems:
        print(f"검증 실패 ({len(problems)}건):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    bundle = loader.load_bundle(args.template_id)
    stages = (bundle.pipeline or {}).get("stages") or []
    print(f"검증 통과: {args.template_id}")
    print(f"  content_type: {bundle.metadata.get('content_type')}")
    print(f"  pipeline    : {bundle.pipeline.get('pipeline_id')} ({len(stages)} stages)")
    print(f"  roles       : {len((bundle.roles or {}).get('roles') or [])}")
    print(f"  view tabs   : {len((bundle.project_view or {}).get('tabs') or [])}")
    return 0


def cmd_project_create(args) -> int:
    from engines.project import ProjectEngine

    request = {
        "channel_id": args.channel,
        "topic": args.topic,
        "target_languages": args.languages.split(","),
        "duration_seconds": args.duration,
        "production_mode": True,
        "run_mode": args.run_mode,
    }
    result = ProjectEngine(ADOSPathManager(PROJECT_ROOT)).create_project(request)
    print(f"프로젝트 생성: {result['project_id']}")
    print(f"  path: {result['path']}")
    for warning in result.get("input_warnings") or []:
        print(f"  경고: {warning}")
    print()
    print("다음 명령:")
    print(f"  python scripts/ados.py project run-until-gate \"{result['path']}\"")
    return 0


def cmd_project_status(args) -> int:
    _print_status(_engine(args.project_path).status())
    return 0


def cmd_project_next(args) -> int:
    action = _engine(args.project_path).next_action()
    print(f"action: {action['action']}")
    if action.get("stage"):
        print(f"stage : {action['stage']}")
    print(f"설명  : {action['description']}")
    return 0


def cmd_project_run(args) -> int:
    engine = _engine(args.project_path)
    engine.run_until_gate(allow_external=args.allow_external)
    _print_status(engine.status())
    return 0


def cmd_project_import(args) -> int:
    engine = _engine(args.project_path)
    state = engine.import_result(args.stage_id, args.result_file,
                                 allow_external=args.allow_external)
    step = state["step_states"][args.stage_id]
    print(f"{args.stage_id}: {step['status']}")
    if step["error"]:
        print(f"  error: {step['error']}")
        return 1
    _print_status(engine.status())
    return 0


def cmd_project_approve(args) -> int:
    engine = _engine(args.project_path)
    state = engine.approve(args.stage_id, args.decision,
                           reviewer=args.reviewer, notes=args.notes)
    step = state["step_states"][args.stage_id]
    print(f"{args.stage_id}: {args.decision} 기록됨 → {step['status']}")
    _print_status(engine.status())
    return 0


def cmd_project_retry(args) -> int:
    engine = _engine(args.project_path)
    state = engine.retry(args.stage_id, force=args.force,
                         allow_external=args.allow_external)
    step = state["step_states"][args.stage_id]
    print(f"{args.stage_id}: {step['status']}")
    _print_status(engine.status())
    return 0


def cmd_project_view(args) -> int:
    from engines.project import ProjectViewBuilder

    view = ProjectViewBuilder(args.project_path).build()
    print(json.dumps(view, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ados", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    template = sub.add_parser("template", help="템플릿 관리")
    template_sub = template.add_subparsers(dest="subcommand", required=True)
    validate = template_sub.add_parser("validate", help="production 번들 검증")
    validate.add_argument("template_id")
    validate.set_defaults(func=cmd_template_validate)

    project = sub.add_parser("project", help="프로젝트 운영")
    project_sub = project.add_subparsers(dest="subcommand", required=True)

    create = project_sub.add_parser("create", help="production 프로젝트 생성")
    create.add_argument("--channel", required=True)
    create.add_argument("--topic", required=True)
    create.add_argument("--duration", type=int, default=900, help="목표 길이(초)")
    create.add_argument("--languages", default="ko")
    create.add_argument("--run-mode", default="manual",
                        choices=["manual", "semi_auto"])
    create.set_defaults(func=cmd_project_create)

    status = project_sub.add_parser("status", help="진행 상태")
    status.add_argument("project_path")
    status.set_defaults(func=cmd_project_status)

    next_cmd = project_sub.add_parser("next", help="다음 행동")
    next_cmd.add_argument("project_path")
    next_cmd.set_defaults(func=cmd_project_next)

    run = project_sub.add_parser("run-until-gate", help="게이트/대기까지 실행")
    run.add_argument("project_path")
    run.add_argument("--allow-external", action="store_true",
                     help="외부 호출 선언 stage 허용 (config 허용도 필요)")
    run.set_defaults(func=cmd_project_run)

    import_cmd = project_sub.add_parser("import-result", help="작업 결과 import")
    import_cmd.add_argument("project_path")
    import_cmd.add_argument("stage_id")
    import_cmd.add_argument("result_file")
    import_cmd.add_argument("--allow-external", action="store_true")
    import_cmd.set_defaults(func=cmd_project_import)

    approve = project_sub.add_parser("approve", help="사람 승인 기록")
    approve.add_argument("project_path")
    approve.add_argument("stage_id")
    approve.add_argument("--decision", required=True,
                         choices=["APPROVE", "REQUEST_REVISION", "REJECT"])
    approve.add_argument("--reviewer", default="human")
    approve.add_argument("--notes", default=None)
    approve.set_defaults(func=cmd_project_approve)

    retry = project_sub.add_parser("retry", help="실패 단계 재시도")
    retry.add_argument("project_path")
    retry.add_argument("stage_id")
    retry.add_argument("--force", action="store_true",
                       help="완료된 단계 포함 강제 재실행")
    retry.add_argument("--allow-external", action="store_true")
    retry.set_defaults(func=cmd_project_retry)

    view = project_sub.add_parser("view", help="view model 재생성·출력")
    view.add_argument("project_path")
    view.set_defaults(func=cmd_project_view)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ADOSError as e:
        print(f"오류: {e.message}")
        if e.suggested_fix:
            print(f"해결: {e.suggested_fix}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
