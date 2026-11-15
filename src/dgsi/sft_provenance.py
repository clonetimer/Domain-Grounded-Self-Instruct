"""Check standalone SFT provenance against the evidence actually in its input.

The caller has already validated the nested input schema. This gate checks
ONLY identifiers that can be verified from that packet. In particular, an
upstream run ID or source hash cannot be authenticated from SFT text alone:
Case→SFT binding and local source admission remain mandatory.

Error codes never echo identifiers, log text or other restricted material.
"""
from __future__ import annotations

from collections import Counter
from typing import Any


class SftProvenanceReferenceError(ValueError):
    """Payload-free mismatch between SFT metadata and its prompt evidence."""


def validate_sft_input_provenance(
    inputs: dict[str, Any], provenance: dict[str, Any],
) -> None:
    """Require exact log/passage lineage and a spacecraft context anchor.

    Duplicate or invented provenance references are rejected as well as
    omissions. Order does not matter because these are references, not a
    chronological sequence. A successful check is never evidence of source
    authenticity, permission, diagnostic accuracy or expert Gold approval.
    """
    log_ids = [entry["log_id"] for entry in inputs["diagnostic_logs"]]
    passage_ids = [
        entry["passage_id"] for entry in inputs.get("knowledge_evidence", [])
    ]

    if Counter(provenance["diagnostic_log_refs"]) != Counter(log_ids):
        raise SftProvenanceReferenceError("SFT_DIAGNOSTIC_LOG_PROVENANCE_MISMATCH")
    if Counter(provenance["knowledge_passage_ids"]) != Counter(passage_ids):
        raise SftProvenanceReferenceError("SFT_KNOWLEDGE_PASSAGE_PROVENANCE_MISMATCH")

    spacecraft_id = inputs["spacecraft_context"]["spacecraft_id"]
    if spacecraft_id not in provenance["context_refs"]:
        raise SftProvenanceReferenceError("SFT_SPACECRAFT_CONTEXT_PROVENANCE_MISSING")
