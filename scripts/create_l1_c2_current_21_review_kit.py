#!/usr/bin/env python3
"""Generate the frozen 21-task C2 review kit, never a training artifact.

This checkout-only operator entrypoint is intentionally excluded from the
frozen RC4 portable-toolkit allowlist. Output must be outside the repository.
"""
from __future__ import annotations

import argparse
from hashlib import sha1
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from create_l1_c2_complete_review_kit import build_review_kit, _publish_once

# Git blob identities of the explicitly reviewed 21-task candidate and L0 card
# revision. Git checkouts may materialize text as CRLF on Windows; compare
# committed LF content, rather than platform-specific checkout bytes.
_SNAPSHOTS = {
    "collection": (
        "examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18.json",
        "50a3f8f972ea8696ee5dca66dd73304b272998e9",
    ),
    "source_facts": (
        "examples/l0_public_literature_fact_cards_c2_content_corrected_2026-11-18.json",
        "33b831408068e00e366eb6c6c3a0a1751195c685",
    ),
}


class Current21ReviewKitError(ValueError):
    """Fixed-code rejection, never includes actual diagnosis or reviewer data."""


def _read_frozen_json(name: str) -> dict:
    relative, git_blob_sha = _SNAPSHOTS[name]
    content = (ROOT / relative).read_bytes()
    if b"\x00" in content:
        raise Current21ReviewKitError("CURRENT21_INPUT_NOT_TEXT")
    canonical = content.replace(b"\r\n", b"\n")
    actual = sha1(b"blob " + str(len(canonical)).encode("ascii")
                  + b"\x00" + canonical).hexdigest()
    if actual != git_blob_sha:
        raise Current21ReviewKitError("CURRENT21_SOURCE_SNAPSHOT_CHANGED")
    value = json.loads(canonical.decode("utf-8"))
    if not isinstance(value, dict):
        raise Current21ReviewKitError("CURRENT21_INPUT_SHAPE_INVALID")
    return value


def assert_pending_current_21(collection: dict, source_facts: dict) -> None:
    """Reject stale cohorts, approvals, training or split substitutions."""
    if (collection.get("collection_id") !=
            "DGSI-L1-LITERATURE-SYNTHETIC-PILOT-C2-COVERAGE-CANDIDATE-2026-11-18"
            or collection.get("packet_count") != 21
            or len(collection.get("packets", [])) != 21
            or collection.get("track") != "LITERATURE_DERIVED_SYNTHETIC"
            or collection.get("data_status") != "REVIEW_REQUIRED"
            or collection.get("gold_eligible") is not False
            or collection.get("training_authorized") is not False):
        raise Current21ReviewKitError("CURRENT21_COHORT_GATE_BLOCKED")
    if (not isinstance(source_facts.get("cards"), list)
            or len(source_facts["cards"]) != 13
            or any(card.get("domain_review_status") !=
                   "AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION"
                   for card in source_facts["cards"])):
        raise Current21ReviewKitError("CURRENT21_L0_REVIEW_GATE_BLOCKED")
    if any(packet.get("review", {}).get("status") != "REVIEW_REQUIRED"
           or packet.get("track") != "LITERATURE_DERIVED_SYNTHETIC"
           for packet in collection["packets"]):
        raise Current21ReviewKitError("CURRENT21_L1_REVIEW_GATE_BLOCKED")


def build_current_21_review_kit() -> tuple[bytes, dict]:
    collection = _read_frozen_json("collection")
    source = _read_frozen_json("source_facts")
    assert_pending_current_21(collection, source)
    data, manifest = build_review_kit(collection, source["cards"])
    if (manifest["packet_count"] != 21
            or manifest["event_family_count"] != 9
            or manifest["source_rights_document_count"] != 7
            or manifest["source_rights_bound_l0_fact_count"] != 12
            or manifest["expert_review_complete"] is not False
            or manifest["source_rights_verified"] is not False
            or manifest["training_authorized"] is not False
            or manifest["gold_eligible"] is not False
            or manifest["official_splits_assigned"] is not False
            or manifest["sft_records_emitted"] != 0):
        raise Current21ReviewKitError("CURRENT21_KIT_PROJECTION_MISMATCH")
    return data, manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-file", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        destination = args.output_file.resolve(strict=False)
        if destination.is_relative_to(ROOT.resolve()) or destination.suffix.lower() != ".zip":
            raise Current21ReviewKitError("CURRENT21_UNSAFE_OUTPUT")
        data, manifest = build_current_21_review_kit()
        _publish_once(destination, data)
    except FileExistsError:
        code = "OUTPUT_EXISTS_NO_OVERWRITE"
    except (Current21ReviewKitError, ValueError, OSError, KeyError, TypeError, UnicodeError):
        code = "CURRENT21_REVIEW_KIT_REJECTED"
    else:
        print(json.dumps({
            "decision": "CURRENT21_REVIEW_ONLY_KIT_GENERATED",
            "packet_count": manifest["packet_count"],
            "event_family_count": manifest["event_family_count"],
            "source_document_count": manifest["source_rights_document_count"],
            "expert_review_complete": False,
            "source_rights_verified": False,
            "training_authorized": False,
            "sft_records_emitted": 0,
        }))
        return 0
    print(json.dumps({
        "decision": "REJECTED", "error_code": code,
        "training_authorized": False, "sft_records_emitted": 0,
    }))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
