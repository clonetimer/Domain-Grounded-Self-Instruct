#!/usr/bin/env python3
"""Read-only, local, aggregate-only L1 cross-collection lineage preflight.

Only explicit local JSON paths are read. No network calls, no source text,
case identifiers, paths or reviewer identities are included in output.
A passing preflight NEVER authorizes dataset splits, Gold or fine-tuning.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dgsi.l1_global_lineage import (  # noqa: E402
    L1GlobalLineageError,
    audit_l1_cross_collection_lineage,
)

MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_BATCHES = 64
VERSION = "dgsi-l1-global-local-audit.v1"
MANIFEST_VERSION = "dgsi-l1-global-audit-manifest.v1"


class LocalInputError(ValueError):
    """Fixed-code input error; never include source paths or contents."""


def _no_duplicates(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise LocalInputError("LOCAL_DUPLICATE_JSON_KEY")
        out[key] = value
    return out


def _reject_constant(_value):
    raise LocalInputError("LOCAL_NONFINITE_JSON_NUMBER")


def _finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise LocalInputError("LOCAL_NONFINITE_JSON_NUMBER")
    return number


def _read_json(path: Path):
    try:
        if path.is_symlink() or not path.is_file():
            raise LocalInputError("LOCAL_FILE_INVALID")
        if path.stat().st_size > MAX_FILE_BYTES:
            raise LocalInputError("LOCAL_FILE_TOO_LARGE")
        with path.open("r", encoding="utf-8") as handle:
            return json.load(
                handle,
                object_pairs_hook=_no_duplicates,
                parse_constant=_reject_constant,
                parse_float=_finite_float,
            )
    except LocalInputError:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError):
        raise LocalInputError("LOCAL_JSON_UNREADABLE") from None


def _local_path(value, root: Path):
    if not isinstance(value, str) or not value.strip():
        raise LocalInputError("LOCAL_PATH_INVALID")
    path = Path(value)
    return path if path.is_absolute() else root / path


def audit_manifest(manifest_path: Path, aliases_path=None, hypothetical_path=None):
    manifest = _read_json(manifest_path)
    if not isinstance(manifest, dict) or set(manifest) != {"schema_version", "batches"}:
        raise LocalInputError("LOCAL_MANIFEST_SHAPE_INVALID")
    if manifest["schema_version"] != MANIFEST_VERSION:
        raise LocalInputError("LOCAL_MANIFEST_VERSION_UNSUPPORTED")
    entries = manifest["batches"]
    if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_BATCHES:
        raise LocalInputError("LOCAL_BATCH_COUNT_INVALID")

    batches = []
    root = manifest_path.parent
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {
            "collection_path", "source_fact_cards_path"
        }:
            raise LocalInputError("LOCAL_BATCH_ENTRY_INVALID")
        collection = _read_json(_local_path(entry["collection_path"], root))
        fact_input = _read_json(_local_path(entry["source_fact_cards_path"], root))
        cards = fact_input.get("cards") if isinstance(fact_input, dict) else fact_input
        if not isinstance(cards, list):
            raise LocalInputError("LOCAL_SOURCE_FACT_CARDS_INVALID")
        batches.append({"collection": collection, "source_fact_cards": cards})

    aliases = None
    if aliases_path is not None:
        aliases = _read_json(Path(aliases_path))
        if not isinstance(aliases, list):
            raise LocalInputError("LOCAL_ALIASES_INVALID")
    hypothetical = None
    if hypothetical_path is not None:
        hypothetical = _read_json(Path(hypothetical_path))
        if not isinstance(hypothetical, dict):
            raise LocalInputError("LOCAL_HYPOTHETICAL_SPLITS_INVALID")
    return audit_l1_cross_collection_lineage(
        batches, hypothetical_splits=hypothetical, reviewed_aliases=aliases
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Local metadata-only L1 collection lineage audit; no data export"
    )
    parser.add_argument("--manifest", required=True, help="Explicit local manifest JSON")
    parser.add_argument("--aliases", help="Optional local expert alias metadata JSON")
    parser.add_argument(
        "--hypothetical-splits",
        help="Offline adversarial split plan ONLY; never approves a dataset split",
    )
    args = parser.parse_args(argv)
    try:
        result = audit_manifest(
            Path(args.manifest),
            aliases_path=args.aliases,
            hypothetical_path=args.hypothetical_splits,
        )
        success = result["decision"] == "STRUCTURAL_PREFLIGHT_ONLY"
    except (LocalInputError, L1GlobalLineageError) as exc:
        result = {
            "schema_version": VERSION,
            "decision": "BLOCKED",
            "error_code": str(exc),
            "gold_eligible_count": 0,
            "training_authorized": False,
        }
        success = False
    except Exception:
        # Never expose stack traces: local paths and restricted payloads
        # may appear in library exceptions or validator diagnostics.
        result = {
            "schema_version": VERSION,
            "decision": "BLOCKED",
            "error_code": "LOCAL_GLOBAL_LINEAGE_AUDIT_FAILED",
            "gold_eligible_count": 0,
            "training_authorized": False,
        }
        success = False
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0 if success else 2


if __name__ == "__main__":
    raise SystemExit(main())
