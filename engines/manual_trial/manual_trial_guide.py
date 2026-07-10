# -*- coding: utf-8 -*-
"""Manual trial guide (v0.3 — real manual trial preparation).

사람이 첫 실제 파일 트라이얼을 수행할 수 있도록 기대 파일명·배치 경로·
작업 단계·안전 경고를 담은 가이드와 체크리스트를 만든다.
실제 미디어 파일은 만들지 않는다.
근거: docs/34_REAL_MANUAL_TRIAL_V0_3.md #5~#7
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSFileNotFoundError,
    ADOSLogger,
    ADOSValidator,
    load_json,
    write_json,
    write_text,
)
from engines.manual_production import ManualIntakeManager, ManualWorkspaceManager

REPORTS_DIR = "reports"
GUIDE_FILE = "manual_trial_guide.json"
CHECKLIST_FILE = "manual_trial_checklist.json"
GUIDE_MD_FILE = "REAL_MANUAL_TRIAL_GUIDE.md"

SOURCE_OF_TRUTH_NOTE = (
    "The intake manifest expected_file_path is the source of truth "
    "for manual asset placement."
)

GUIDE_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "manual_workspace_path",
    "expected_asset_files",
    "source_of_truth_note",
    "provider_export_pack_paths",
    "human_steps",
    "safety_warnings",
    "created_at",
]

PROVIDER_EXPORT_PACKS = [
    "providers/exports/midjourney_prompt_pack.json",
    "providers/exports/midjourney_video_prompt_pack.json",
    "providers/exports/typecast_script_pack.json",
]

HUMAN_STEPS = [
    "1. 아래 expected_asset_files의 기대 경로를 확인한다.",
    "2. provider export pack의 프롬프트/대본으로 외부 도구에서 직접 자산을 생성한다.",
    "3. 생성한 파일을 manual_assets/{project_id}/의 기대 경로에 배치한다.",
    "4. asset_intake_manifest.json의 해당 item에 actual_file_path를 기록한다.",
    "5. scripts/run_real_manual_trial_validate.py {project_path}로 검증한다.",
    "6. FAIL 항목을 수정한 뒤 사람 검토 체크포인트를 승인한다.",
    "7. scripts/run_real_manual_trial_finalize.py {project_path}로 최종화한다.",
    "8. manual_upload_instructions에 따라 직접 업로드한다 (ADOS는 업로드하지 않음).",
]

SAFETY_WARNINGS = [
    "ADOS는 외부 API를 호출하지 않는다 (Midjourney/Typecast 수동 작업 필요).",
    "ADOS는 업로드하지 않는다 — 업로드는 항상 사람이 수동으로 수행한다.",
    "검증은 존재/확장자/최소 크기만 확인한다 — 내용·품질은 사람이 직접 확인한다.",
    "manual_assets/는 gitignore 대상이다 — 커밋하지 않는다.",
    "모든 검토 승인 전에는 upload_ready가 false를 유지한다.",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ManualTrialGuide:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger
        self.workspaces = ManualWorkspaceManager(logger)
        self.intake = ManualIntakeManager(logger)

    def guide_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / REPORTS_DIR / GUIDE_FILE

    def checklist_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / REPORTS_DIR / CHECKLIST_FILE

    def guide_md_path(self, project_path: str | Path) -> Path:
        return self.workspaces.workspace_path(project_path) / GUIDE_MD_FILE

    def _expected_from_intake(self, project_path: Path, workspace: Path) -> list | None:
        """intake manifest가 있으면 그 expected_file_path를 그대로 쓴다 (단일 진실)."""
        if not self.intake.manifest_path(project_path).is_file():
            return None
        manifest = self.intake.load_asset_intake_manifest(project_path)
        prefix = f"{workspace.parent.name}/{workspace.name}/"
        expected = []
        for item in manifest["items"]:
            file = item["expected_file_path"]
            if file.startswith(prefix):
                file = file[len(prefix):]
            expected.append({"asset_type": item["asset_type"], "file": file})
        return expected

    def _expected_asset_files(self, project_path: Path, project: dict) -> list:
        """plan·프로젝트 언어 설정에서 결정적 기대 파일 목록을 만든다 (fallback)."""
        expected = []

        visual_plan_path = project_path / "assets" / "images" / "visual_plan.json"
        if visual_plan_path.is_file():
            for sv in load_json(visual_plan_path)["scene_visuals"]:
                expected.append(
                    {"asset_type": "image", "file": f"images/{sv['scene_id']}.png"}
                )

        motion_plan_path = project_path / "assets" / "motion" / "motion_plan.json"
        if motion_plan_path.is_file():
            for sm in load_json(motion_plan_path)["scene_motions"]:
                expected.append(
                    {"asset_type": "motion", "file": f"motion/{sm['scene_id']}.mp4"}
                )

        master = project["languages"]["master_language"]
        expected.append(
            {"asset_type": "audio", "file": f"audio/voice_{master}.mp3"}
        )
        for lang in project["languages"]["target_languages"]:
            expected.append(
                {"asset_type": "subtitle", "file": f"subtitles/subtitles_{lang}.srt"}
            )
        expected.append({"asset_type": "video", "file": "video/final_video.mp4"})
        expected.append(
            {"asset_type": "thumbnail", "file": "thumbnail/thumbnail.jpg"}
        )
        return expected

    def create_trial_guide(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project = load_json(project_path / "project.json")
        workspace = self.workspaces.workspace_path(project_path)
        # intake manifest가 단일 진실 — 없을 때만 plan 기반 fallback을 쓴다
        expected = self._expected_from_intake(project_path, workspace) \
            or self._expected_asset_files(project_path, project)

        guide = {
            "project_id": project["project_id"],
            "topic": project["topic"]["title"],
            "manual_workspace_path": str(workspace),
            "expected_asset_files": expected,
            "source_of_truth_note": SOURCE_OF_TRUTH_NOTE,
            "provider_export_pack_paths": [
                rel for rel in PROVIDER_EXPORT_PACKS
                if (project_path / rel).is_file()
            ],
            "human_steps": list(HUMAN_STEPS),
            "safety_warnings": list(SAFETY_WARNINGS),
            "created_at": _now_iso(),
        }
        write_json(self.guide_path(project_path), guide)

        checklist_items = [
            {
                "checklist_id": f"CL{n + 1:03d}",
                "description": f"{e['asset_type']} 파일 배치: {e['file']}",
                "done": False,
            }
            for n, e in enumerate(expected)
        ]
        checklist_items += [
            {"checklist_id": f"CL{len(expected) + 1:03d}",
             "description": "validate 스크립트 실행 후 전체 PASS 확인", "done": False},
            {"checklist_id": f"CL{len(expected) + 2:03d}",
             "description": "사람 검토 체크포인트 전체 승인", "done": False},
            {"checklist_id": f"CL{len(expected) + 3:03d}",
             "description": "finalize 스크립트 실행 후 업로드 패키지 확인", "done": False},
        ]
        checklist = {
            "project_id": project["project_id"],
            "items": checklist_items,
            "created_at": _now_iso(),
            "disclaimer": "Human checklist for the real manual trial. No upload is performed by ADOS.",
        }
        write_json(self.checklist_path(project_path), checklist)

        write_text(self.guide_md_path(project_path), self._render_md(guide))
        if self.logger:
            self.logger.info(
                f"수동 트라이얼 가이드 생성: {len(expected)}개 기대 파일",
                metadata={"project_id": project["project_id"]},
            )
        return guide

    @staticmethod
    def _render_md(guide: dict) -> str:
        lines = [
            "# REAL MANUAL TRIAL GUIDE",
            "",
            f"- project_id: {guide['project_id']}",
            f"- topic: {guide['topic']}",
            f"- workspace: {guide['manual_workspace_path']}",
            "",
            "## Expected Files (이 경로에 실제 파일을 배치)",
            "",
            f"> {guide['source_of_truth_note']}",
            "",
        ]
        lines += [
            f"- [{e['asset_type']}] {e['file']}"
            for e in guide["expected_asset_files"]
        ]
        lines += ["", "## Provider Export Packs", ""]
        lines += [f"- {p}" for p in guide["provider_export_pack_paths"]]
        lines += ["", "## Human Steps", ""]
        lines += [f"- {s}" for s in guide["human_steps"]]
        lines += ["", "## Safety Warnings", ""]
        lines += [f"- {w}" for w in guide["safety_warnings"]]
        lines.append("")
        return "\n".join(lines)

    def load_trial_guide(self, project_path: str | Path) -> dict:
        path = self.guide_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"manual_trial_guide.json이 없습니다: {path}",
                location="ManualTrialGuide.load_trial_guide",
                suggested_fix="create_trial_guide를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_trial_guide(self, project_path: str | Path) -> bool:
        guide = self.load_trial_guide(project_path)
        loc = "ManualTrialGuide.validate_trial_guide"
        ADOSValidator.require_fields(guide, GUIDE_REQUIRED_FIELDS, location=loc)
        for entry in guide["expected_asset_files"]:
            ADOSValidator.require_fields(entry, ["asset_type", "file"], location=loc)
        if not self.checklist_path(project_path).is_file():
            raise ADOSFileNotFoundError(
                f"manual_trial_checklist.json이 없습니다: "
                f"{self.checklist_path(project_path)}",
                location=loc,
                suggested_fix="create_trial_guide를 먼저 실행하세요.",
            )
        return True
