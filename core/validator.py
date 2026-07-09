# -*- coding: utf-8 -*-
"""ADOS validator.

필수 필드/파일/enum/간단한 스키마 검증. 실패 시 구조화된 에러를 던진다.
"""
from pathlib import Path

from .errors import ADOSFileNotFoundError, ADOSValidationError


class ADOSValidator:
    @staticmethod
    def require_fields(data: dict, fields: list[str], location: str = "") -> None:
        """dict에 필수 필드가 모두 있는지 검사한다. 값이 None이면 누락으로 본다."""
        if not isinstance(data, dict):
            raise ADOSValidationError(
                f"dict가 아닙니다: {type(data).__name__}",
                location=location or "ADOSValidator.require_fields",
            )
        missing = [f for f in fields if f not in data or data[f] is None]
        if missing:
            raise ADOSValidationError(
                f"필수 필드 누락: {', '.join(missing)}",
                location=location or "ADOSValidator.require_fields",
                suggested_fix=f"다음 필드를 추가하세요: {', '.join(missing)}",
            )

    @staticmethod
    def require_files(paths: list[str | Path], location: str = "") -> None:
        missing = [str(p) for p in paths if not Path(p).is_file()]
        if missing:
            raise ADOSFileNotFoundError(
                f"필수 파일 없음: {', '.join(missing)}",
                location=location or "ADOSValidator.require_files",
                suggested_fix="누락된 파일을 먼저 생성하세요.",
            )

    @staticmethod
    def validate_enum(value, allowed, field: str = "", location: str = "") -> None:
        allowed_values = [str(a) for a in allowed]
        if str(value) not in allowed_values:
            raise ADOSValidationError(
                f"허용되지 않는 값: {field or 'value'}={value!r} "
                f"(허용: {', '.join(allowed_values)})",
                location=location or "ADOSValidator.validate_enum",
            )

    @staticmethod
    def validate_schema(data: dict, schema: dict, location: str = "") -> None:
        """간단한 스키마 검증.

        schema 형식: {field_name: expected_type} 또는
                     {field_name: {"type": type, "required": bool, "enum": [...]}}
        """
        loc = location or "ADOSValidator.validate_schema"
        if not isinstance(data, dict):
            raise ADOSValidationError(
                f"dict가 아닙니다: {type(data).__name__}", location=loc
            )
        problems = []
        for field, rule in schema.items():
            if isinstance(rule, dict):
                required = rule.get("required", True)
                expected = rule.get("type")
                enum = rule.get("enum")
            else:
                required, expected, enum = True, rule, None

            if field not in data or data[field] is None:
                if required:
                    problems.append(f"{field}: 누락")
                continue
            value = data[field]
            if expected is not None and not isinstance(value, expected):
                problems.append(
                    f"{field}: 타입 오류 (기대 {getattr(expected, '__name__', expected)}, "
                    f"실제 {type(value).__name__})"
                )
            if enum is not None and str(value) not in [str(e) for e in enum]:
                problems.append(f"{field}: 허용되지 않는 값 {value!r}")
        if problems:
            raise ADOSValidationError(
                f"스키마 검증 실패: {'; '.join(problems)}",
                location=loc,
                suggested_fix="문제 필드를 스키마에 맞게 수정하세요.",
            )
