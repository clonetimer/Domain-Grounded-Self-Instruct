"""Conservative, payload-free lineage audit for diagnosis-context SFT exports.

A source_group MUST describe the entire physical incident/episode family, not
an arbitrary row or prompt variant. This audit cannot infer semantic identity
between different incidents; that requires an authorized expert manifest.
"""
from __future__ import annotations

import hashlib
import re
from collections import Counter
from datetime import datetime
from typing import Any

from .diagnostic_context import validate_sft_example


class SftLineageAuditError(ValueError):
    """An SFT batch contains a duplicate, unsafe approval or split leak."""


def _fail(code: str) -> None:
    # Deliberately do not echo potentially sensitive case IDs, file paths or text.
    raise SftLineageAuditError(code)


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _synthetic_marker(example: dict[str, Any]) -> bool:
    refs = [
        example["case_ref"],
        example["source_group"],
        *example["provenance"]["diagnosis_result_refs"],
    ]
    return any(
        ref.casefold().startswith(("synthetic://", "synth-", "illustrative", "dgsi-adcs-illustrative"))
        for ref in refs
    )


def audit_sft_lineage(examples: list[dict[str, Any]]) -> dict[str, Any]:
    """Reject cross-split incident/source duplicates and identical prompt reuse.

    Episode identity comes from `source_group`; case IDs, upstream diagnosis
    references, byte-identical source artifact hashes and normalized prompts
    form independent safety nets against incorrect episode grouping.

    Global knowledge passages and generic spacecraft context are deliberately
    not split keys: reusing a manual across incidents is not incident leakage.
    Unscoped log IDs (e.g. LOG-01) are also not global identifiers.

    No input payload, identifier, digest or private path is returned.
    A passing audit is NOT expert approval or permission to export Gold data.
    """
    if not isinstance(examples, list):
        _fail("INVALID_EXAMPLE_BATCH")

    first_split: dict[tuple[str, str], str] = {}
    seen_example_ids: set[str] = set()
    same_task_prompt: dict[str, tuple[str, str]] = {}
    split_counts: Counter[str] = Counter()
    task_counts: Counter[str] = Counter()
    no_hash_count = 0
    no_diagnosis_ref_count = 0
    synthetic_count = 0

    def register(kind: str, identifier: str, split: str) -> None:
        key = (kind, identifier)
        earlier = first_split.setdefault(key, split)
        if earlier != split:
            _fail("CROSS_SPLIT_" + kind.upper())

    for example in examples:
        # Reject malformed/target-leaking inputs before comparing lineage.
        validate_sft_example(example)
        example_id = example["example_id"]
        if example_id in seen_example_ids:
            _fail("DUPLICATE_EXAMPLE_ID")
        seen_example_ids.add(example_id)
        split = example["split"]
        task = example["task_type"]
        prov = example["provenance"]
        split_counts[split] += 1
        task_counts[task] += 1

        register("source_group", example["source_group"], split)
        register("case_ref", example["case_ref"], split)
        for ref in prov["diagnosis_result_refs"]:
            register("diagnosis_result_ref", ref, split)
        for sha256 in prov["source_artifact_hashes"]:
            register("source_artifact_hash", sha256, split)

        if not prov["source_artifact_hashes"]:
            no_hash_count += 1
        if not prov["diagnosis_result_refs"]:
            no_diagnosis_ref_count += 1

        # Only compare same-task inputs. Ignore harmless formatting variance.
        user = re.sub(r"\\s+", " ", example["messages"][1]["content"]).strip()
        assistant = re.sub(r"\\s+", " ", example["messages"][2]["content"]).strip()
        prompt_digest = _digest(task + "\\x00" + user)
        target_digest = _digest(assistant)
        if prompt_digest in same_task_prompt:
            previous_split, previous_target = same_task_prompt[prompt_digest]
            if previous_split != split:
                _fail("CROSS_SPLIT_USER_PROMPT")
            if previous_target != target_digest:
                _fail("CONFLICTING_TARGETS_FOR_IDENTICAL_PROMPT")
            _fail("DUPLICATE_IDENTICAL_SFT_EXAMPLE")
        same_task_prompt[prompt_digest] = (split, target_digest)

        if _synthetic_marker(example):
            synthetic_count += 1
            if example["review"]["status"] == "APPROVED":
                _fail("SYNTHETIC_FIXTURE_CANNOT_BE_EXPERT_APPROVED")
        if example["review"]["status"] == "APPROVED":
            review = example["review"]
            if not isinstance(review.get("reviewer_id"), str) or not review["reviewer_id"].strip():
                _fail("APPROVED_WITHOUT_REVIEWER_ID")
            try:
                reviewed = datetime.fromisoformat(str(review["reviewed_at"]).replace("Z", "+00:00"))
            except (TypeError, ValueError):
                _fail("APPROVED_WITHOUT_VALID_REVIEW_TIME")
            if reviewed.tzinfo is None or reviewed.utcoffset() is None:
                _fail("APPROVED_WITHOUT_TIMEZONE")

    return {
        "schema_version": "dgsi-sft-lineage-audit.v1",
        "decision": "PASS_STRUCTURAL_ONLY",
        "example_count": len(examples),
        "split_counts": {key: split_counts[key] for key in ("train", "validation", "test")},
        "task_counts": dict(sorted(task_counts.items())),
        "synthetic_or_illustrative_count": synthetic_count,
        "missing_diagnosis_ref_count": no_diagnosis_ref_count,
        "missing_source_hash_count": no_hash_count,
        "gold_eligible": False,
        "expert_event_family_review_required": True,
        "limitations": [
            "Source-group correctness and semantic duplicates require human adjudication.",
            "Source hashes are treated conservatively as episode-specific; globally shared artifacts require explicit role separation.",
            "This gate cannot establish IP permission, real-flight provenance or independent expert correctness.",
        ],
    }
