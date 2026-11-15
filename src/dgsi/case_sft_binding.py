"""Fail-closed, local-only binding between a source diagnosis case and SFT export.

This prevents plausible but ungrounded SFT prompts/answers from silently
drifting away from the reviewed case. It neither authenticates source
artifacts nor promotes examples to Gold.
"""
from __future__ import annotations

from collections import Counter
import json
from typing import Any

from .diagnostic_context import (
    DiagnosticContextValidationError,
    validate_diagnostic_case,
    validate_sft_example,
)


class CaseSftBindingError(ValueError):
    """Payload-free rejection code; never includes restricted case content."""


def _fail(code: str) -> None:
    raise CaseSftBindingError(code)


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            _fail("DUPLICATE_JSON_KEY")
        value[key] = item
    return value


_DECODER = json.JSONDecoder(
    object_pairs_hook=_no_duplicate_keys,
    parse_constant=lambda _value: _fail("NONFINITE_JSON_NUMBER"),
)


def _decode_json(text: str, *, embedded: bool) -> Any:
    """Decode the entire JSON target, or a single trailing JSON prompt packet.

    The source prompt may contain human instructions before the JSON, but
    the structured portion must be the only JSON object and no suffix text
    is allowed. No private parse errors are ever exposed.
    """
    start = text.find("{") if embedded else 0
    if start < 0:
        _fail("MISSING_JSON_PACKET")
    try:
        value, end = _DECODER.raw_decode(text, start)
    except CaseSftBindingError:
        raise
    except (ValueError, TypeError):
        _fail("MALFORMED_JSON_PACKET")
    if text[end:].strip():
        _fail("TRAILING_JSON_PACKET_CONTENT")
    if not isinstance(value, dict):
        _fail("JSON_PACKET_NOT_OBJECT")
    return value


def _equal_multiset(a: Any, b: Any) -> bool:
    return isinstance(a, list) and isinstance(b, list) and Counter(a) == Counter(b)


def verify_case_sft_binding(case: dict[str, Any], example: dict[str, Any]) -> dict[str, Any]:
    """Verify exact case-to-example input/target/lineage agreement.

    This gate is intentionally strict: an edited/rewritten target requires
    a separately versioned source case with independent expert adjudication.
    Never run it to approve, train on, or publish restricted examples.
    """
    try:
        validate_diagnostic_case(case)
    except (DiagnosticContextValidationError, TypeError, KeyError, ValueError):
        _fail("INVALID_SOURCE_CASE")
    try:
        validate_sft_example(example)
    except (DiagnosticContextValidationError, TypeError, KeyError, ValueError) as exc:
        # Preserve the two existing payload-free template rejection codes for
        # Case/SFT binding callers; all other validator details stay redacted.
        if isinstance(exc, DiagnosticContextValidationError) and str(exc) in {
            "UNAPPROVED_SYSTEM_PROMPT_TEMPLATE",
            "UNAPPROVED_USER_PROMPT_PREAMBLE",
        }:
            _fail(str(exc))
        _fail("INVALID_SFT_EXAMPLE")

    if example["case_ref"] != case["case_id"]:
        _fail("CASE_REFERENCE_MISMATCH")
    if example["task_type"] != case["task_type"]:
        _fail("TASK_TYPE_MISMATCH")
    if example["source_group"] != case["provenance"]["source_group"]:
        _fail("INCIDENT_FAMILY_MISMATCH")

    prompt = _decode_json(example["messages"][1]["content"], embedded=True)
    if set(prompt) != {"case_id", "task_type", "instruction", "input"}:
        _fail("PROMPT_PACKET_FIELDS_MISMATCH")
    if prompt["case_id"] != case["case_id"] or prompt["task_type"] != case["task_type"]:
        _fail("PROMPT_CASE_IDENTITY_MISMATCH")
    if prompt["instruction"] != case.get("instruction"):
        _fail("PROMPT_INSTRUCTION_MISMATCH")
    if prompt["input"] != case["input"]:
        _fail("PROMPT_SOURCE_INPUT_MISMATCH")

    target = _decode_json(example["messages"][2]["content"], embedded=False)
    if target != case["expected_output"]:
        _fail("ASSISTANT_TARGET_MISMATCH")

    case_prov = case["provenance"]
    sft_prov = example["provenance"]
    checks = (
        (sft_prov["diagnosis_result_refs"], case_prov["diagnosis_run_refs"],
         "UPSTREAM_RUN_LINEAGE_MISMATCH"),
        (sft_prov["diagnostic_log_refs"],
         [item["log_id"] for item in case["input"]["diagnostic_logs"]],
         "DIAGNOSTIC_LOG_LINEAGE_MISMATCH"),
        (sft_prov["knowledge_passage_ids"],
         [item["passage_id"] for item in case["input"].get("knowledge_evidence", [])],
         "KNOWLEDGE_PASSAGE_LINEAGE_MISMATCH"),
        (sft_prov["source_artifact_hashes"], case_prov["source_artifact_hashes"],
         "SOURCE_ARTIFACT_HASH_LINEAGE_MISMATCH"),
    )
    for actual, expected, code in checks:
        if not _equal_multiset(actual, expected):
            _fail(code)

    if case["input"]["spacecraft_context"]["spacecraft_id"] not in sft_prov["context_refs"]:
        _fail("SPACECRAFT_CONTEXT_REFERENCE_MISSING")

    # Review state is metadata, not input. Matching reviewer strings alone
    # can never establish that independent expert review really took place.
    if example["review"]["status"] == "APPROVED" and case["review"]["status"] != "APPROVED":
        _fail("SFT_APPROVAL_WITHOUT_SOURCE_CASE_APPROVAL")
    if example["review"]["status"] == "APPROVED":
        method = str(case_prov.get("generation_method") or "").casefold()
        fields = (case["case_id"], example["case_ref"], example["source_group"],
                  *case_prov["diagnosis_run_refs"])
        if any(word in method for word in ("synthetic", "illustrative", "hypothetical")) or any(
            str(field).casefold().startswith(("synthetic://", "synth-", "illustrative", "dgsi-adcs-illustrative"))
            for field in fields
        ):
            _fail("SYNTHETIC_EXAMPLE_CANNOT_BE_APPROVED")

    return {
        "schema_version": "dgsi-case-sft-binding.v1",
        "decision": "PASS_BINDING_ONLY",
        "matched_pair_count": 1,
        "gold_eligible": False,
        "human_source_and_expert_review_required": True,
    }
