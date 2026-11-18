"""Bind a C2 offline rights submission to the CURRENT L0/L1 source snapshot.

The structural rights audit alone checks a submission against a supplied blank
worksheet, but an old worksheet can remain internally self-consistent after a
task or L0 source changes. This extra gate independently regenerates the
blank from current public source artifacts before the structural audit.
Neither gate verifies copyright permission or authorizes SFT.
"""
from __future__ import annotations

from typing import Any

from dgsi.l1_c2_rights_intake_audit import (
    C2SourceRightsIntakeError,
    audit_c2_source_rights_intake,
)
from dgsi.l1_c2_scientific_dossier import build_c2_scientific_dossier
from dgsi.l1_c2_source_rights_queue import build_c2_source_rights_queue


def audit_c2_rights_intake_against_current_sources(
    trusted_blank: dict[str, Any],
    submitted_queue: dict[str, Any],
    current_l1_collection: dict[str, Any],
    current_l0_fact_cards: list[dict[str, Any]],
) -> dict[str, Any]:
    """Fail closed if a saved rights worksheet is not today's source-bound one.

    The L1 collection and L0 fact cards must be loaded independently from the
    current authorized, local, version-controlled data snapshot. It is NOT
    sufficient to take these objects from the same editable rights worksheet.
    The resulting report contains aggregate statuses, never rights evidence.
    """
    try:
        if not isinstance(current_l1_collection, dict):
            raise TypeError("invalid collection type")
        if not isinstance(current_l0_fact_cards, list):
            raise TypeError("invalid L0 source type")
        current_dossier = build_c2_scientific_dossier(
            current_l1_collection, source_fact_cards=current_l0_fact_cards
        )
        regenerated_blank = build_c2_source_rights_queue(current_dossier)
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise C2SourceRightsIntakeError(
            "C2_RIGHTS_CURRENT_SOURCE_SNAPSHOT_INVALID"
        ) from exc

    if not isinstance(trusted_blank, dict) or trusted_blank != regenerated_blank:
        raise C2SourceRightsIntakeError(
            "C2_RIGHTS_INTAKE_STALE_OR_TAMPERED_BLANK"
        )

    result = audit_c2_source_rights_intake(regenerated_blank, submitted_queue)
    # A snapshot match does not authenticate the source claims or rights.
    return {**result, "current_public_source_snapshot_matched": True}
