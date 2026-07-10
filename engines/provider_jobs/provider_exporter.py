# -*- coding: utf-8 -*-
"""Provider exporter (v0.2 — manual integration preparation).

Provider별 수동 작업 팩(복사/붙여넣기용)을 내보낸다.
외부에 아무것도 제출하지 않는다.
근거: docs/32_PROVIDER_INTEGRATION_V0_2.md #8
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSFileNotFoundError,
    ADOSLogger,
    load_json,
    write_json,
)

EXPORTS_DIR = Path("providers") / "exports"
MJ_PACK = "midjourney_prompt_pack.json"
MJV_PACK = "midjourney_video_prompt_pack.json"
TYPECAST_PACK = "typecast_script_pack.json"
SUMMARY_FILE = "provider_export_summary.json"

DISCLAIMER = (
    "Manual work pack. Nothing was submitted externally. "
    "external_call_made is always false in v0.2."
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProviderExporter:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def exports_dir(self, project_path: str | Path) -> Path:
        return Path(project_path) / EXPORTS_DIR

    def _require(self, project_path: Path, rel: str, fix: str) -> dict:
        path = project_path / rel
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"{rel}가 없습니다: {path}",
                location="ProviderExporter",
                suggested_fix=f"{fix}를 먼저 실행하세요.",
            )
        return load_json(path)

    def _write_pack(self, project_path: Path, filename: str, provider_name: str,
                    instructions: list, items: list, project_id: str) -> dict:
        pack = {
            "project_id": project_id,
            "provider_name": provider_name,
            "export_mode": "manual",
            "external_call_made": False,
            "instructions": instructions,
            "items": items,
            "created_at": _now_iso(),
            "disclaimer": DISCLAIMER,
        }
        write_json(self.exports_dir(project_path) / filename, pack)
        if self.logger:
            self.logger.info(
                f"export pack 생성: {filename} ({len(items)} items)",
                metadata={"provider": provider_name, "items": len(items)},
            )
        return pack

    def export_midjourney_prompt_pack(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        prompts = self._require(
            project_path, "prompts/visual_prompts.json",
            "VisualEngine.create_dummy_visual_plan",
        )
        visual_plan = self._require(
            project_path, "assets/images/visual_plan.json",
            "VisualEngine.create_dummy_visual_plan",
        )
        counts = {
            sv["scene_id"]: sv["required_image_count"]
            for sv in visual_plan["scene_visuals"]
        }
        items = [
            {
                "scene_id": p["scene_id"],
                "prompt": p["prompt"],
                "required_image_count": counts.get(p["scene_id"], 1),
            }
            for p in prompts["prompts"]
        ]
        return self._write_pack(
            project_path, MJ_PACK, "midjourney",
            [
                "1. 아래 items의 prompt를 Midjourney에 순서대로 붙여넣는다.",
                "2. scene_id별 required_image_count만큼 이미지를 생성·저장한다.",
                "3. 저장한 파일을 ProviderImporter로 메타데이터 등록한다.",
            ],
            items, prompts["project_id"],
        )

    def export_midjourney_video_prompt_pack(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        motion_plan = self._require(
            project_path, "assets/motion/motion_plan.json",
            "MotionEngine.create_dummy_motion_plan",
        )
        items = [
            {
                "scene_id": sm["scene_id"],
                "motion_prompt": sm["motion_prompt"],
                "duration_seconds": sm["duration_seconds"],
            }
            for sm in motion_plan["scene_motions"]
        ]
        return self._write_pack(
            project_path, MJV_PACK, "midjourney_video",
            [
                "1. 해당 scene의 원본 이미지를 준비한다.",
                "2. motion_prompt로 Midjourney Video 클립을 수동 생성한다.",
                "3. duration_seconds를 넘지 않게 저장 후 ProviderImporter로 등록한다.",
            ],
            items, motion_plan["project_id"],
        )

    def export_typecast_script_pack(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        voice_plan = self._require(
            project_path, "assets/audio/voice_plan.json",
            "VoiceEngine.create_dummy_voice_plan",
        )
        self._require(
            project_path, "story/script_draft.json",
            "StoryEngine.create_dummy_story",
        )
        items = [
            {
                "block_id": nb["block_id"],
                "text": nb["text"],
                "voice_style": nb["voice_style"],
                "estimated_duration_seconds": nb["estimated_duration_seconds"],
            }
            for nb in voice_plan["narration_blocks"]
        ]
        return self._write_pack(
            project_path, TYPECAST_PACK, "typecast",
            [
                "1. 아래 items의 text를 Typecast에 블록 단위로 붙여넣는다.",
                "2. voice_style에 맞는 보이스로 블록별 오디오를 생성·저장한다.",
                "3. 저장한 파일을 ProviderImporter로 메타데이터 등록한다.",
            ],
            items, voice_plan["project_id"],
        )

    def export_all_provider_packs(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        packs = {
            "midjourney": self.export_midjourney_prompt_pack(project_path),
            "midjourney_video": self.export_midjourney_video_prompt_pack(project_path),
            "typecast": self.export_typecast_script_pack(project_path),
        }
        summary = {
            "project_id": packs["midjourney"]["project_id"],
            "export_mode": "manual",
            "external_call_made": False,
            "exports": {
                "midjourney": f"providers/exports/{MJ_PACK}",
                "midjourney_video": f"providers/exports/{MJV_PACK}",
                "typecast": f"providers/exports/{TYPECAST_PACK}",
            },
            "item_counts": {name: len(pack["items"]) for name, pack in packs.items()},
            "created_at": _now_iso(),
            "disclaimer": DISCLAIMER,
        }
        write_json(self.exports_dir(project_path) / SUMMARY_FILE, summary)
        return summary
