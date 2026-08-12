# -*- coding: utf-8 -*-
"""Template loader.

templates/{template_id}/template.yaml을 읽고 최소 필드를 검증해 dict로 반환한다.
production 번들(pipeline/project_form/project_view/roles/quality)은
load_bundle/validate_bundle/snapshot_bundle로 확장 로드한다.
기존 최소 템플릿(template.yaml만)은 계속 load()로 동작한다.
"""
from pathlib import Path

from core import ADOSFileNotFoundError, ADOSPathManager, load_yaml

from .template_bundle import (
    TemplateBundle,
    load_bundle_from_dir,
    raise_if_invalid,
    snapshot_bundle as _snapshot_bundle,
    validate_bundle as _validate_bundle,
)
from .template_validator import TemplateValidator

TEMPLATE_FILENAME = "template.yaml"


class TemplateLoader:
    def __init__(self, path_manager: ADOSPathManager | None = None):
        self.paths = path_manager or ADOSPathManager()

    def template_dir(self, template_id: str):
        return self.paths.templates / template_id

    def exists(self, template_id: str) -> bool:
        return (self.template_dir(template_id) / TEMPLATE_FILENAME).is_file()

    def load(self, template_id: str) -> dict:
        folder = self.template_dir(template_id)
        if not folder.is_dir():
            raise ADOSFileNotFoundError(
                f"Template 폴더가 없습니다: templates/{template_id}",
                location="TemplateLoader.load",
                suggested_fix=f"templates/{template_id}/ 폴더와 {TEMPLATE_FILENAME}을 생성하세요.",
            )
        yaml_path = folder / TEMPLATE_FILENAME
        if not yaml_path.is_file():
            raise ADOSFileNotFoundError(
                f"{TEMPLATE_FILENAME}이 없습니다: templates/{template_id}",
                location="TemplateLoader.load",
                suggested_fix=f"templates/{template_id}/{TEMPLATE_FILENAME}을 생성하세요.",
            )
        data = load_yaml(yaml_path)
        TemplateValidator.validate(data, location=f"templates/{template_id}/{TEMPLATE_FILENAME}")
        return data

    # --- production bundle ---
    def load_metadata(self, template_id: str) -> dict:
        """template.yaml 메타데이터만 로드한다 (load와 동일, 명시적 이름)."""
        return self.load(template_id)

    def load_bundle(self, template_id: str) -> TemplateBundle:
        """template.yaml + 참조된 번들 파일들을 로드한다.

        참조 필드가 없는 최소 템플릿도 로드된다 (번들 파트는 None).
        """
        metadata = self.load(template_id)
        return load_bundle_from_dir(self.template_dir(template_id), metadata)

    def validate_bundle(self, template_id: str) -> list[str]:
        """production 번들 검증. 문제 목록 반환 (빈 목록이면 통과)."""
        from engines.workflow.executor_registry import EXECUTOR_ALLOWLIST

        bundle = self.load_bundle(template_id)
        return _validate_bundle(bundle, EXECUTOR_ALLOWLIST)

    def load_validated_bundle(self, template_id: str) -> TemplateBundle:
        """검증 통과가 필수인 로드. 실패 시 구조화된 에러."""
        from engines.workflow.executor_registry import EXECUTOR_ALLOWLIST

        bundle = self.load_bundle(template_id)
        raise_if_invalid(bundle, EXECUTOR_ALLOWLIST)
        return bundle

    def snapshot_bundle(self, template_id: str, project_path: str | Path) -> dict:
        """검증된 번들을 프로젝트에 snapshot하고 참조 정보를 반환한다."""
        bundle = self.load_validated_bundle(template_id)
        return _snapshot_bundle(bundle, project_path)
