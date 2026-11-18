#!/usr/bin/env python3
"""Read-only, redacted inventory of local diagnosis/log/context case folders.

The tool never exports case text or telemetry rows. It writes only aggregate
counts and hashed case identifiers; use it locally on restricted workspaces.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

DIAGNOSIS_NAMES = {"diagnosis_result.json", "diagnosis_results.json"}
LOG_SUFFIXES = {".log", ".csv"}
REFERENCE_SUFFIXES = {".md", ".txt", ".pdf", ".docx"}
CONTEXT_NAMES = {"spacecraft_context.json", "mission_context.json", "context.json"}
HISTORY_NAMES = {"historical_cases.json", "history.json"}
REVIEW_NAMES = {"expert_review.json", "review_record.json", "review.json"}
TIMESTAMP_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\b")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_files(case_dir: Path, root: Path) -> list[Path]:
    files: list[Path] = []
    for path in case_dir.rglob("*"):
        if path.is_symlink():
            continue
        if path.is_file():
            resolved = path.resolve()
            if root == resolved or root in resolved.parents:
                files.append(path)
    return sorted(files)


def _load_diagnosis(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return []
    if isinstance(payload, dict):
        return [payload]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def _csv_profile(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            header = next(csv.reader(stream), [])
    except (OSError, UnicodeError, csv.Error):
        return {"parseable": False, "columns": 0, "kind": "UNKNOWN"}
    normalized = {str(item).strip().lower() for item in header}
    has_time = bool(normalized & {"timestamp", "time", "time_s", "datetime", "date_time"})
    event_fields = bool(normalized & {"severity", "comment", "message", "event", "alarm", "log_type"})
    numeric_signal_fields = bool(normalized & {"signal", "value", "unit"})
    kind = "EVENT_LOG" if has_time and event_fields else (
        "POTENTIAL_TELEMETRY_TABLE" if has_time and numeric_signal_fields else "CSV_UNCLASSIFIED"
    )
    return {"parseable": True, "columns": len(header), "kind": kind}


def inspect_case(case_dir: Path, root: Path) -> dict[str, Any]:
    files = _safe_files(case_dir, root)
    by_name = {path.name.lower(): path for path in files}
    diagnosis_files = [path for path in files if path.name.lower() in DIAGNOSIS_NAMES]
    log_files = [path for path in files if path.suffix.lower() in LOG_SUFFIXES and path.name.lower() not in DIAGNOSIS_NAMES]
    reference_files = [path for path in files if path.suffix.lower() in REFERENCE_SUFFIXES]
    context_files = [path for path in files if path.name.lower() in CONTEXT_NAMES]
    history_files = [path for path in files if path.name.lower() in HISTORY_NAMES]
    review_files = [path for path in files if path.name.lower() in REVIEW_NAMES]

    diagnosis_payloads = [item for path in diagnosis_files for item in _load_diagnosis(path)]
    hidden_truth = any(
        item.get("truth_used") is True or item.get("labels_used") is True
        for item in diagnosis_payloads
    )
    synthetic = any(
        item.get("synthetic") is True
        or str(item.get("case_id", "")).upper().startswith(("SYNTH", "ILLUSTRATIVE"))
        for item in diagnosis_payloads
    )
    candidate_count = sum(
        len(item.get("candidate_faults", [])) if isinstance(item.get("candidate_faults"), list)
        else int(bool(item.get("candidate_fault_id")))
        for item in diagnosis_payloads
    )
    statuses = sorted({str(item.get("status") or item.get("review_status") or "NOT_RECORDED") for item in diagnosis_payloads})
    csv_profiles = [_csv_profile(path) for path in log_files if path.suffix.lower() == ".csv"]
    potential_telemetry = any(profile["kind"] == "POTENTIAL_TELEMETRY_TABLE" for profile in csv_profiles)
    review_payloads = []
    for path in review_files:
        try:
            value = json.loads(path.read_text(encoding="utf-8-sig"))
            if isinstance(value, dict):
                review_payloads.append(value)
        except (OSError, UnicodeError, json.JSONDecodeError):
            pass
    expert_approved = any(
        item.get("status") == "APPROVED"
        and bool(item.get("reviewer_id"))
        and bool(item.get("reviewed_at"))
        for item in review_payloads
    )
    file_hashes = [_sha256(path) for path in files]
    duplicate_hash_count = len(file_hashes) - len(set(file_hashes))

    if not diagnosis_payloads:
        decision = "BLOCKED_NO_UPSTREAM_DIAGNOSIS_RESULT"
    elif hidden_truth:
        decision = "BLOCKED_HIDDEN_TRUTH_OR_LABELS"
    elif synthetic:
        decision = "SYNTHETIC_FIXTURE_ONLY"
    elif not log_files or not context_files:
        decision = "INCOMPLETE_DIAGNOSTIC_CONTEXT"
    elif not reference_files:
        decision = "REVIEW_REQUIRED_NO_KNOWLEDGE_REFERENCE"
    elif not expert_approved:
        decision = "REVIEW_REQUIRED_NO_EXPERT_APPROVAL"
    else:
        decision = "READY_FOR_MANUAL_CONTENT_REVIEW"

    case_digest = hashlib.sha256(case_dir.relative_to(root).as_posix().encode("utf-8")).hexdigest()[:12]
    return {
        "case_ref_hash": case_digest,
        "decision": decision,
        "diagnosis_result_count": len(diagnosis_payloads),
        "log_file_count": len(log_files),
        "reference_file_count": len(reference_files),
        "context_file_count": len(context_files),
        "historical_case_file_count": len(history_files),
        "review_record_count": len(review_files),
        "candidate_count": candidate_count,
        "upstream_statuses": statuses,
        "potential_raw_telemetry_csv": potential_telemetry,
        "duplicate_file_hash_count": duplicate_hash_count,
        "expert_approved": expert_approved,
        "gold_eligible": False,
    }


def build_inventory(root: Path) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"case root does not exist: {root}")
    case_dirs = sorted({
        path.parent for path in root.rglob("diagnosis_result.json")
        if path.is_file() and not path.is_symlink() and root in path.resolve().parents
    } | {
        path.parent for path in root.rglob("diagnosis_results.json")
        if path.is_file() and not path.is_symlink() and root in path.resolve().parents
    })
    if (root / "diagnosis_result.json").is_file():
        case_dirs = [root, *[item for item in case_dirs if item != root]]
    cases = [inspect_case(path, root) for path in case_dirs]
    counts: dict[str, int] = {}
    for item in cases:
        counts[item["decision"]] = counts.get(item["decision"], 0) + 1
    return {
        "schema_version": "dgsi.local-diagnostic-asset-inventory.v1",
        "read_only": True,
        "payload_exported": False,
        "raw_telemetry_exported": False,
        "gold_approval_granted": False,
        "case_count": len(cases),
        "decision_counts": dict(sorted(counts.items())),
        "cases": cases,
        "limitations": [
            "This is metadata/structure preflight only; it does not establish factual correctness.",
            "A hashed case reference is pseudonymous, not an anonymization guarantee.",
            "CSV telemetry detection is heuristic and requires human review.",
            "No case is made Gold or training-eligible by this inventory.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="Local restricted case-store root")
    parser.add_argument("--output", required=True, type=Path, help="Local JSON inventory output path")
    args = parser.parse_args()
    report = build_inventory(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "case_count": report["case_count"],
        "decision_counts": report["decision_counts"],
        "output": str(args.output),
        "payload_exported": False,
        "gold_approval_granted": False,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
