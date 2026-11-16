"""Fail-closed, non-release gate for design-derived diagnostic hypotheticals.

A design declaration is not an observed episode, simulator run, ML result,
expert decision, or literature-derived L1 training packet. This module never
creates SFT records and never upgrades review or training permissions.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "dgsi-simulation-to-sft"
    / "schemas"
    / "design_derived_batch.schema.json"
)


class DesignDerivedIntakeError(ValueError):
    """Stable failure code; never reproduce source material or case identifiers."""


def _reject(code: str) -> None:
    raise DesignDerivedIntakeError(code)


def validate_design_derived_batch(
    batch: dict[str, Any],
    *,
    expected_source_sha256: str | None = None,
) -> dict[str, Any]:
    """Validate a hypothetical intake batch, returning metadata-only counts.

    The optional SHA-256 parameter must be independently established from
    authorized source bytes. Its presence does not establish source usage
    rights, review approval, actual execution, or training authorization.
    """
    if not isinstance(batch, dict):
        _reject("DESIGN_INTAKE_INVALID_STRUCTURE")
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    if not Draft202012Validator(schema).is_valid(batch):
        _reject("DESIGN_INTAKE_SCHEMA_INVALID")

    if expected_source_sha256 is not None and (
        not isinstance(expected_source_sha256, str)
        or batch["source"]["sha256"] != expected_source_sha256
    ):
        _reject("DESIGN_INTAKE_SOURCE_FINGERPRINT_MISMATCH")

    facts = batch["source_facts"]
    candidates = batch["candidates"]
    fact_ids = [fact["fact_id"] for fact in facts]
    candidate_ids = [candidate["case_id"] for candidate in candidates]
    if len(fact_ids) != len(set(fact_ids)):
        _reject("DESIGN_INTAKE_DUPLICATE_FACT_ID")
    if len(candidate_ids) != len(set(candidate_ids)):
        _reject("DESIGN_INTAKE_DUPLICATE_CANDIDATE_ID")

    if (
        batch["counts"]["source_facts"] != len(facts)
        or batch["counts"]["design_derived_candidates"] != len(candidates)
        or batch["counts"]["review_required"] != len(candidates)
    ):
        _reject("DESIGN_INTAKE_COUNT_MISMATCH")

    available_facts = set(fact_ids)
    for candidate in candidates:
        linked_facts = set(candidate["source_fact_refs"])
        input_facts = set(candidate["model_visible_input"]["available_evidence_ids"])
        if not linked_facts <= available_facts or not input_facts <= linked_facts:
            _reject("DESIGN_INTAKE_UNBOUND_SOURCE_FACT")
        if len(candidate["source_fact_refs"]) != len(linked_facts):
            _reject("DESIGN_INTAKE_DUPLICATE_SOURCE_REF")

    return {
        "decision": "NON_SFT_INTAKE_ONLY",
        "source_fact_count": len(facts),
        "hypothetical_candidate_count": len(candidates),
        "observed_event_count": 0,
        "upstream_ml_bundle_count": 0,
        "sft_records_emitted": 0,
        "training_authorized": False,
        "gold_eligible_count": 0,
    }
