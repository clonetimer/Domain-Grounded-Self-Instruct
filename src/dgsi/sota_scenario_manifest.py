"""Verify SOTA input-pairing digests against local canonical scenario data.

Review-only: no Gold, source-rights approval, model calls, or training.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from typing import Any

from .sota_construction_scorecard import ScorecardError, summarize_construction_trials

MANIFEST_SCHEMA = "dgsi-sota-local-scenario-manifest.v1"
ROOT_FIELDS = (
    "comparison_unit_id", "source_group", "event_family", "track",
    "requested_task_type", "shared_input",
)
INPUT_FIELDS = (
    "upstream_ml_result", "diagnostic_logs", "spacecraft_mission_context",
    "analysis_cutoff", "historical_context", "provenance",
)


def _fail(code: str) -> None:
    raise ScorecardError(code)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())



_FORBIDDEN_SHARED_KEYS = frozenset({
    "raw_telemetry", "internal_review", "expert_identity", "expert_signature",
    "reviewer_identity", "curator_prompt", "curator_prompts",
    "formal_target", "assistant_target", "reference_answer", "gold_answer",
    "answer_key", "diagnostic_ground_truth", "system_prompt",
    "developer_prompt", "reviewer_token", "curator_notes",
})


def _reject_nested_private_or_answer_fields(payload: Any) -> None:
    """Fail closed on curator, answer-label, and raw telemetry keys at any depth.

    The shared scenario is common to all generation arms, never a place for
    target answers or restricted curator content. This is a key-name guard,
    not a complete PII scanner or authorization check.
    """
    stack: list[tuple[Any, int]] = [(payload, 0)]
    visited = 0
    while stack:
        value, depth = stack.pop()
        visited += 1
        if depth > 64 or visited > 100_000:
            _fail("SOTA_MANIFEST_NESTING_LIMIT")
        if isinstance(value, dict):
            for key, child in value.items():
                if not isinstance(key, str):
                    _fail("SOTA_MANIFEST_JSON_INVALID")
                normalized = re.sub(r"[\s_-]+", "_", key.strip().casefold()).strip("_")
                if normalized in _FORBIDDEN_SHARED_KEYS:
                    _fail("SOTA_MANIFEST_FORBIDDEN_INPUT")
                stack.append((child, depth + 1))
        elif isinstance(value, list):
            stack.extend((child, depth + 1) for child in value)


def canonical_scenario_sha256(entry: dict[str, Any]) -> str:
    """Fingerprint shared scenario content, excluding method-specific prompt text.

    Input schema is deliberately narrower than L1. It cannot authenticate
    the claimed origin or analyze diagnostic/historical factual correctness.
    """
    if not isinstance(entry, dict):
        _fail("SOTA_MANIFEST_ENTRY_FIELDS")
    _reject_nested_private_or_answer_fields(entry)
    # Unbound root fields would reach downstream prompts without contributing to
    # the canonical hash; do not silently accept extensible scenario entries.
    if set(entry) != set(ROOT_FIELDS):
        _fail("SOTA_MANIFEST_ENTRY_FIELDS")
    if not all(_nonempty(entry[k]) for k in ROOT_FIELDS if k != "shared_input"):
        _fail("SOTA_MANIFEST_ID_MISSING")
    payload = entry["shared_input"]
    if not isinstance(payload, dict) or not all(k in payload for k in INPUT_FIELDS):
        _fail("SOTA_MANIFEST_INPUT_FIELDS")
    if (not isinstance(payload["upstream_ml_result"], dict)
            or not isinstance(payload["diagnostic_logs"], list)
            or not isinstance(payload["spacecraft_mission_context"], dict)
            or not isinstance(payload["historical_context"], list)
            or not isinstance(payload["provenance"], dict)):
        _fail("SOTA_MANIFEST_INPUT_TYPES")
    cutoff = payload["analysis_cutoff"]
    if not _nonempty(cutoff):
        _fail("SOTA_MANIFEST_CUTOFF_INVALID")
    try:
        parsed = datetime.fromisoformat(cutoff.replace("Z", "+00:00"))
    except ValueError:
        _fail("SOTA_MANIFEST_CUTOFF_INVALID")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail("SOTA_MANIFEST_CUTOFF_INVALID")
    prov = payload["provenance"]
    track = entry["track"]
    if track not in ("LITERATURE_DERIVED_SYNTHETIC", "REAL_GOLD"):
        _fail("SOTA_MANIFEST_TRACK_INVALID")
    if track == "LITERATURE_DERIVED_SYNTHETIC":
        if (prov.get("synthetic") is not True or not isinstance(prov.get("source_refs"), list)
                or not prov["source_refs"] or any(not _nonempty(x) for x in prov["source_refs"])):
            _fail("SOTA_MANIFEST_SYNTHETIC_PROVENANCE")
    elif prov.get("synthetic") is not False:
        _fail("SOTA_MANIFEST_REAL_PROVENANCE")
    canon = {k: entry[k] for k in ROOT_FIELDS if k != "comparison_unit_id"}
    try:
        data = json.dumps(canon, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError):
        _fail("SOTA_MANIFEST_JSON_INVALID")
    return hashlib.sha256(data).hexdigest()


def audit_local_sota_scenarios(
    trials_document: dict[str, Any], manifest_document: dict[str, Any],
) -> dict[str, Any]:
    """Check *every* trial against a locally held canonical scenario manifest.

    No case identifiers, hashes, source text, scorecards or reviewers leave
    this function. The returned counts do not establish scientific approval.
    """
    summary = summarize_construction_trials(trials_document)
    if not isinstance(manifest_document, dict):
        _fail("SOTA_MANIFEST_SCHEMA")
    _reject_nested_private_or_answer_fields(manifest_document)
    if (set(manifest_document) != {"schema_version", "scenarios"}
            or manifest_document.get("schema_version") != MANIFEST_SCHEMA
            or not isinstance(manifest_document.get("scenarios"), list)):
        _fail("SOTA_MANIFEST_SCHEMA")
    lookup: dict[str, tuple[dict[str, Any], str]] = {}
    for entry in manifest_document["scenarios"]:
        digest = canonical_scenario_sha256(entry)
        unit = entry["comparison_unit_id"]
        if unit in lookup:
            _fail("SOTA_MANIFEST_DUPLICATE_UNIT")
        lookup[unit] = (entry, digest)
    rows = trials_document["trials"]
    seen: set[str] = set()
    for row in rows:
        unit = row.get("comparison_unit_id")
        if not _nonempty(unit) or not _nonempty(row.get("requested_task_type")):
            _fail("SOTA_MANIFEST_TRIAL_UNIT_MISSING")
        if unit not in lookup:
            _fail("SOTA_MANIFEST_UNIT_NOT_FOUND")
        entry, digest = lookup[unit]
        for key in ("source_group", "event_family", "track", "requested_task_type"):
            if row[key] != entry[key]:
                _fail("SOTA_MANIFEST_METADATA_MISMATCH")
        if row.get("canonical_scenario_sha256") != digest:
            _fail("SOTA_MANIFEST_DIGEST_MISMATCH")
        seen.add(unit)
    if seen != set(lookup):
        _fail("SOTA_MANIFEST_UNUSED_UNIT")
    return {
        "schema_version": "dgsi-sota-local-scenario-audit.v1",
        "manifest_digests_match_local_inputs": True,
        "comparison_status": summary["comparison_status"],
        "source_group_budget_matched": summary["source_group_budget_matched"],
        "comparison_units": len(lookup),
        "trials_checked": len(rows),
        "source_rights_verified": False,
        "expert_identity_verified": False,
        "scientific_facts_verified": False,
        "historical_as_of_verified": False,
        "gold_authorized": False,
        "training_authorized": False,
        "downstream_sft_result": "NOT_RUN",
    }
