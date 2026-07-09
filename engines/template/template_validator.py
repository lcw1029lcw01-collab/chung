# -*- coding: utf-8 -*-
"""Template validator (walking skeleton).

Template Status: docs/08_TEMPLATE_SYSTEM.md (DRAFT/ACTIVE/DEPRECATED/ARCHIVED/ERROR)
"""
from core import ADOSValidator

TEMPLATE_REQUIRED_FIELDS = ["template_id", "name", "version", "status"]

TEMPLATE_STATUSES = ["DRAFT", "ACTIVE", "DEPRECATED", "ARCHIVED", "ERROR"]


class TemplateValidator:
    @staticmethod
    def validate(data: dict, location: str = "template.yaml") -> None:
        ADOSValidator.require_fields(data, TEMPLATE_REQUIRED_FIELDS, location=location)
        ADOSValidator.validate_enum(
            data["status"], TEMPLATE_STATUSES, field="status", location=location
        )
