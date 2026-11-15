"""Validate the published diagnostic Case/SFT JSON Schemas at runtime.

JSON Schema validation complements (does not replace) semantic safety gates.
Errors deliberately omit case contents and identifiers, which may be restricted.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

_SCHEMA_FILES = {
    "case": "diagnostic_case.schema.json",
    "sft": "diagnostic_sft.schema.json",
    "source_fact_card": "source_fact_card.schema.json",
    "l1_task_packet": "l1_task_packet.schema.json",
    "l1_task_packet_collection": "l1_task_packet_collection.schema.json",
}
_SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "resources"


class SchemaContractError(ValueError):
    """Schema violation with a payload-free error code."""


@lru_cache(maxsize=2)
def _validator(kind: str) -> Draft202012Validator:
    try:
        name = _SCHEMA_FILES[kind]
    except KeyError as exc:
        raise SchemaContractError("UNKNOWN_SCHEMA_KIND") from exc
    with (_SCHEMA_ROOT / name).open(encoding="utf-8") as handle:
        schema = json.load(handle)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())



@lru_cache(maxsize=1)
def _diagnostic_input_validator() -> Draft202012Validator:
    """Reuse the published Case input contract for standalone SFT prompts."""
    source_schema = _validator("case").schema
    input_schema = source_schema["properties"]["input"]
    return Draft202012Validator(input_schema, format_checker=FormatChecker())


def validate_diagnostic_input_schema(payload: Any) -> None:
    """Check the complete nested input without requiring a target or review.

    In isolation this validates structure only. It does not certify upstream
    results, logs, event timestamps relative to the cutoff, or source rights.
    Rejection errors deliberately never include the supplied payload.
    """
    error = next(_diagnostic_input_validator().iter_errors(payload), None)
    if error is not None:
        raise SchemaContractError(f"JSON_SCHEMA_INPUT_{str(error.validator).upper()}")



@lru_cache(maxsize=1)
def _diagnostic_report_validator() -> Draft202012Validator:
    """Use the same report contract as a source Case expected_output."""
    report_schema = _validator("case").schema["properties"]["expected_output"]
    return Draft202012Validator(report_schema, format_checker=FormatChecker())


def validate_diagnostic_report_schema(payload: Any) -> None:
    """Validate a standalone SFT assistant target without source-case text."""
    error = next(_diagnostic_report_validator().iter_errors(payload), None)
    if error is not None:
        raise SchemaContractError(f"JSON_SCHEMA_TARGET_{str(error.validator).upper()}")


def validate_payload_schema(kind: str, payload: Any) -> None:
    """Enforce the complete Draft 2020-12 contract, including nested properties.

    Do not expose jsonschema's raw error message: it may contain sensitive
    instance values, field names, or file paths from restricted cases.
    """
    error = next(_validator(kind).iter_errors(payload), None)
    if error is not None:
        # The path contains schema property names and array indexes only; it
        # never echoes the offending value or any source text/identifier.
        path = ".".join(str(part) for part in error.absolute_path) or "ROOT"
        raise SchemaContractError(
            f"JSON_SCHEMA_{str(error.validator).upper()}_AT_{path}"
        )
