"""Local, metadata-only attestation of *input* file bytes in a handoff.

Explicitly invoked by an authorized custodian. Streams allow-listed files only;
never opens expert targets, raw telemetry, reference collections or arbitrary
paths. Matching untrusted digests is NOT proof of authentic provenance or rights.
Output is constant codes/counts, never identifiers, file paths or digests.
"""
from __future__ import annotations

import hashlib
import hmac
import os
from pathlib import Path
import stat
from typing import Any

from .real_case_handoff import RealCaseHandoffError, assess_handoff_manifest

MAX_INPUT_FILE_BYTES = 64 * 1024 * 1024
INPUT_FILENAMES = frozenset({
    "diagnosis_result.json",
    "diagnostic_logs.jsonl",
    "diagnostic_logs.csv",
    "spacecraft_context.json",
    "operational_context.json",
    "historical_cases.json",
    "knowledge_refs.json",
})


def _digest_regular_input(directory: Path, filename: str, maximum: int) -> tuple[str | None, str | None]:
    """Hash one fixed-name regular file, rejecting obvious link/path escapes.

    No-follow is enforced at OS-open time where available (Unix). On Windows,
    pre/post path checks are best effort, not protection against a malicious
    concurrent filesystem writer: use a custodian-controlled, quiescent folder.
    """
    path = directory / filename
    try:
        if path.is_symlink() or path.resolve(strict=True).parent != directory:
            return None, "INPUT_FILE_LINK_OR_ESCAPE"
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
        try:
            with os.fdopen(fd, "rb") as stream:
                fd = -1
                details = os.fstat(stream.fileno())
                if not stat.S_ISREG(details.st_mode):
                    return None, "INPUT_NOT_REGULAR_FILE"
                if details.st_size > maximum:
                    return None, "INPUT_FILE_SIZE_LIMIT"
                digest = hashlib.sha256()
                total = 0
                while True:
                    chunk = stream.read(64 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > maximum:
                        return None, "INPUT_FILE_SIZE_LIMIT"
                    digest.update(chunk)
                if path.is_symlink() or path.resolve(strict=True).parent != directory:
                    return None, "INPUT_FILE_LINK_OR_ESCAPE"
                return digest.hexdigest(), None
        finally:
            if fd >= 0:
                os.close(fd)
    except (OSError, ValueError, RuntimeError):
        return None, "INPUT_FILE_UNAVAILABLE"


def assess_local_input_sha256(
    manifest: dict[str, Any], input_directory: str | Path,
    *, max_file_bytes: int = MAX_INPUT_FILE_BYTES,
) -> dict[str, Any]:
    """Cross-check optional manifest SHA-256 declarations with actual local bytes.

    This is an independent *integrity stage*, not a substitute for Case binding,
    upstream ML run authentication, source-owner permission or expert review.
    Any missing declaration, mismatch or failed read blocks this stage.
    """
    assessed = assess_handoff_manifest(manifest)
    if not isinstance(max_file_bytes, int) or isinstance(max_file_bytes, bool) or max_file_bytes < 1:
        raise RealCaseHandoffError("INVALID_LOCAL_HASH_SIZE_LIMIT")

    declared = set(manifest.get("available_files", [])) & INPUT_FILENAMES
    expected = manifest.get("input_file_sha256")
    blockers: set[str] = set()
    verified_count = 0
    if not isinstance(expected, dict) or not expected:
        blockers.add("INPUT_SHA256_DECLARATIONS_MISSING")
        expected = {}
    if declared - set(expected):
        blockers.add("INPUT_SHA256_DECLARATIONS_INCOMPLETE")
    if set(expected) - declared:
        blockers.add("INPUT_SHA256_UNDECLARED_FILE")

    directory: Path | None = None
    try:
        raw_directory = Path(input_directory)
        if raw_directory.is_symlink() or not raw_directory.is_dir():
            blockers.add("INPUT_DIRECTORY_UNAVAILABLE")
        else:
            directory = raw_directory.resolve(strict=True)
    except (OSError, TypeError, ValueError, RuntimeError):
        blockers.add("INPUT_DIRECTORY_UNAVAILABLE")

    # Only declared input files can ever be opened. The expert target is not
    # permitted in input_file_sha256, even when listed in available_files.
    if directory is not None:
        for filename in sorted(declared & set(expected)):
            actual, error_code = _digest_regular_input(directory, filename, max_file_bytes)
            if error_code is not None:
                blockers.add(error_code)
            elif hmac.compare_digest(actual, expected[filename]):
                verified_count += 1
            else:
                blockers.add("INPUT_SHA256_MISMATCH")

    matched = not blockers and len(declared) == verified_count
    if manifest["source_class"] in {"SIMULATION", "SYNTHETIC_FIXTURE"}:
        decision = "SYNTHETIC_TEST_ONLY"
    elif not matched:
        decision = "BLOCKED_INPUT_HASH_AUDIT"
    else:
        decision = "LOCAL_INPUT_BYTES_MATCH_DECLARATIONS"

    return {
        "schema_version": "dgsi-local-input-sha256-audit.v1",
        "decision": decision,
        "blocker_codes": sorted(blockers),
        "manifest_blocker_codes": assessed["blocker_codes"],
        "checked_input_count": verified_count,
        "declared_input_count": len(declared),
        "input_file_sha256_matched": matched,
        "source_artifact_hashes_verified": False,
        "upstream_run_authenticated": False,
        "source_rights_verified": False,
        "expert_target_opened": False,
        "independent_expert_review_verified": False,
        "training_eligible": False,
        "gold_eligible": False,
        "split_assignment_allowed": False,
        "note": (
            "Local bytes agree with manifest-supplied digests only. Source origin, "
            "IP rights, run identity, Case binding, input chronology, target quality "
            "and independent expert review require separate authorized checks."
        ),
    }
