# -*- coding: utf-8 -*-
"""Template loader (walking skeleton).

templates/{template_id}/template.yaml을 읽고 최소 필드를 검증해 dict로 반환한다.
전체 Template System(상속/Override/Lock 등)은 docs/08 기준으로 이후에 구현한다.
"""
from core import ADOSFileNotFoundError, ADOSPathManager, load_yaml

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
