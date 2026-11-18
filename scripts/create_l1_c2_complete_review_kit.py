#!/usr/bin/env python3
"""Assemble two separate, source-bound C2 review packs without approving SFT."""
from __future__ import annotations

import argparse
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import sys
import tempfile
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
for directory in (ROOT / "src", ROOT / "scripts"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from create_l1_c2_expert_review_handoff import _word_document
from create_l1_c2_scientific_dossier import _html
from dgsi.l1_c2_expert_handoff import build_c2_expert_handoff
from dgsi.l1_c2_scientific_dossier import build_c2_scientific_dossier

NOTICE = (
    "DGSI C2 SYNTHETIC / INDEPENDENT EXPERT REVIEW ONLY\n"
    "These materials are BLANK or PROPOSED; they are not real ML runs, "
    "flight logs, authenticated expert conclusions, Gold, or SFT.\n"
    "Send reviewer_A.zip and reviewer_B.zip separately through an authorized "
    "channel. Neither reviewer should see the other's completed assessment.\n"
    "Read the cited source publications independently and check permissions. "
    "Literature facts constrain a synthetic scenario; they do not prove its "
    "current fault. No real telemetry is part of the default model input.\n"
    "Do not upload filled reviews or restricted records to GitHub.\n"
    "No official splits, Gold promotion, or training authorization.\n"
)


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True,
                       allow_nan=False) + "\n").encode("utf-8")


def _zip_bytes(files: dict[str, bytes]) -> bytes:
    """Make a reproducible, path-fixed ZIP without file system traversal."""
    memory = BytesIO()
    with ZipFile(memory, mode="w") as archive:
        for name, payload in sorted(files.items()):
            if not name or "/" in name or "\\" in name or name.startswith("."):
                raise ValueError("REVIEW_KIT_INVALID_ARCHIVE_PATH")
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, payload)
    return memory.getvalue()


def build_review_kit(collection: dict, cards: list[dict]) -> tuple[bytes, dict]:
    """Assemble review-only artifacts; fail before publishing on any mismatch."""
    dossier = build_c2_scientific_dossier(collection, source_fact_cards=cards)
    items = {item["task_id"]: item for item in dossier["items"]}
    if len(items) != dossier["packet_count"]:
        raise ValueError("REVIEW_KIT_DUPLICATE_DOSSIER_TASK")
    dossier_json = _json_bytes(dossier)
    dossier_html = _html(dossier).encode("utf-8")
    archives: dict[str, bytes] = {}
    for slot in ("A", "B"):
        form = build_c2_expert_handoff(
            collection, source_fact_cards=cards, reviewer_slot=slot
        )
        if (form["collection_projection_sha256"] !=
                dossier["collection_projection_sha256"]
                or form["packet_count"] != dossier["packet_count"]
                or form["event_family_count"] != dossier["event_family_count"]):
            raise ValueError("REVIEW_KIT_COLLECTION_DRIFT")
        if len(form["tasks"]) != len(items):
            raise ValueError("REVIEW_KIT_COUNT_DRIFT")
        for task in form["tasks"]:
            item = items.get(task["task_id"])
            if item is None or any(
                item[key] != task[key]
                for key in ("collection_projection_sha256", "packet_sha256",
                            "source_public_sha256", "source_fact_bindings")
            ):
                raise ValueError("REVIEW_KIT_TASK_OR_L0_DRIFT")
            if task["scorecard"]["reviewer_token"] is not None or any(
                value is not None for value in task["scorecard"]["scores"].values()
            ) or task["scorecard"]["decision"] is not None:
                raise ValueError("REVIEW_KIT_FORM_NOT_BLANK")
        archives[f"reviewer_{slot}.zip"] = _zip_bytes({
            f"C2_reviewer_{slot}_BLANK.json": _json_bytes(form),
            f"C2_reviewer_{slot}_BLANK.docx": _word_document(form),
            "C2_SYNTHETIC_SCIENTIFIC_REVIEW_ONLY.json": dossier_json,
            "C2_SYNTHETIC_SCIENTIFIC_REVIEW_ONLY.html": dossier_html,
            "README_REVIEW_ONLY.txt": NOTICE.encode("utf-8"),
        })
    manifest = {
        "schema_version": "dgsi-c2-two-reviewer-complete-kit.v1",
        "collection_id": dossier["collection_id"],
        "collection_projection_sha256": dossier["collection_projection_sha256"],
        "packet_count": dossier["packet_count"],
        "event_family_count": dossier["event_family_count"],
        "track": "LITERATURE_DERIVED_SYNTHETIC",
        "reviewer_archives_sha256": {
            name: sha256(data).hexdigest() for name, data in archives.items()
        },
        "reviewer_forms": "BLANK_UNAUTHENTICATED",
        "source_rights_verified": False,
        "expert_review_complete": False,
        "not_for_sft": True,
        "gold_eligible": False,
        "official_splits_assigned": False,
        "training_authorized": False,
        "sft_records_emitted": 0,
    }
    manifest_bytes = _json_bytes(manifest)
    package = _zip_bytes({
        **archives,
        "COORDINATOR_REVIEW_ONLY_MANIFEST.json": manifest_bytes,
        "README_REVIEW_ONLY.txt": NOTICE.encode("utf-8"),
        "SHA256SUMS.txt": (
            "".join(f"{sha256(data).hexdigest()}  {name}\n"
                    for name, data in sorted(archives.items()))
        ).encode("ascii"),
    })
    return package, manifest


def _publish_once(destination: Path, data: bytes) -> None:
    """Atomic no-clobber publication; never follow an existing destination."""
    if destination.suffix.lower() != ".zip":
        raise ValueError("REVIEW_KIT_OUTPUT_MUST_BE_ZIP")
    temporary = None
    try:
        fd, temporary = tempfile.mkstemp(
            prefix=".dgsi-c2-review-kit-", suffix=".tmp",
            dir=destination.parent
        )
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        # os.link() is atomic no-replace across supported Windows/Linux FS;
        # no fallback to overwrite-capable replace/copy.
        os.link(temporary, destination)
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", type=Path, required=True)
    parser.add_argument("--source-facts", type=Path, required=True)
    parser.add_argument("--output-file", type=Path, required=True)
    args = parser.parse_args(argv)
    stage = "READ_INPUT"
    try:
        collection = json.loads(args.collection.read_text(encoding="utf-8"))
        cards = json.loads(args.source_facts.read_text(encoding="utf-8"))["cards"]
        stage = "BUILD_AND_BIND"
        archive, manifest = build_review_kit(collection, cards)
        stage = "ATOMIC_NO_CLOBBER_PUBLICATION"
        _publish_once(args.output_file, archive)
    except FileExistsError:
        error_code = "OUTPUT_EXISTS_NO_OVERWRITE"
    except (KeyError, ValueError, TypeError, OSError, UnicodeError):
        error_code = "REVIEW_KIT_INPUT_OR_OUTPUT_REJECTED"
    else:
        print(json.dumps({
            "decision": "TWO_REVIEWER_KIT_GENERATED_REVIEW_ONLY",
            "packet_count": manifest["packet_count"],
            "event_family_count": manifest["event_family_count"],
            "collection_projection_sha256":
                manifest["collection_projection_sha256"],
            "expert_review_complete": False, "training_authorized": False,
            "sft_records_emitted": 0,
        }))
        return 0
    print(json.dumps({
        "decision": "REJECTED", "stage": stage, "error_code": error_code,
        "training_authorized": False, "sft_records_emitted": 0,
    }))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
