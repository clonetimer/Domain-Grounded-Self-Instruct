"""Offline simulation receipt intake; verifies bytes and declarations, not physics.

No simulator execution, prompt export, source authentication or SFT admission.
Error messages and reports deliberately exclude artifact paths and payloads.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "skills/dgsi-simulation-to-sft/schemas/simulation_run_receipt.schema.json"
MAX_RECEIPT_BYTES = 1024 * 1024
MAX_ARTIFACT_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 64 * 1024 * 1024
STAGE_ROLES = {
    "injection_configured": "CONFIGURATION",
    "injection_executed": "EXECUTION_RECORD",
    "physical_effect_observed": "PHYSICS_QA",
    "diagnostic_effect_observed": "DIAGNOSTIC_LOG",
    "upstream_ml_detected": "ML_RESULT",
    "upstream_ml_localized": "ML_EVALUATION",
}
VISIBLE_ROLES = {"DIAGNOSTIC_LOG", "ML_RESULT", "SPACECRAFT_CONTEXT", "OPERATIONAL_CONTEXT", "DESIGN_KNOWLEDGE"}
REQUIRED_INPUT_ROLES = VISIBLE_ROLES - {"DESIGN_KNOWLEDGE"}
# Bounded structural check only: arbitrary text can still leak answers.
TRUTH_KEYS = {"faultid", "injectedfault", "injectedcomponent", "injectiontime", "faulttruth", "groundtruth", "hiddenlabel", "faultlabel", "expectedoutput", "formaltarget", "targetprivate", "splitassignment"}


class SimulationReceiptError(ValueError):
    """Fixed, payload-free validation failure."""


def _reject(code: str) -> None:
    raise SimulationReceiptError(code)


def _pairs(pairs: list) -> dict:
    out = {}
    for key, value in pairs:
        if key in out:
            _reject("SIM_DUPLICATE_JSON_KEY")
        out[key] = value
    return out


def _walk(value: Any, depth: int = 0):
    if depth > 64:
        _reject("SIM_JSON_TOO_DEEP")
    if isinstance(value, float) and not math.isfinite(value):
        _reject("SIM_NONFINITE_JSON")
    if isinstance(value, dict):
        for key, item in value.items():
            yield key, item
            yield from _walk(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item, depth + 1)


def load_receipt_text(text: str) -> Any:
    """Parse bounded strict JSON; also used for individual artifact records."""
    if not isinstance(text, str):
        _reject("SIM_INVALID_JSON")
    try:
        if len(text.encode("utf-8")) > MAX_ARTIFACT_BYTES:
            _reject("SIM_JSON_TOO_LARGE")
        value = json.loads(text, object_pairs_hook=_pairs,
                           parse_constant=lambda _: _reject("SIM_NONFINITE_JSON"))
        for _ in _walk(value):
            pass
        return value
    except (UnicodeError, json.JSONDecodeError, RecursionError, OverflowError):
        _reject("SIM_INVALID_JSON")


def _time(value: str) -> datetime:
    # A deterministic RFC3339 subset avoids jsonschema's optional format
    # plugins and datetime's permissive parsing / sub-microsecond truncation.
    pattern = (r"[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt]"
               r"(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
               r"(?:\.[0-9]{1,6})?(?:[Zz]|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])")
    if not re.fullmatch(pattern, value) or value.endswith("-00:00"):
        _reject("SIM_INVALID_TIMESTAMP")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00").replace("z", "+00:00"))
    except ValueError:
        _reject("SIM_INVALID_TIMESTAMP")
    if parsed.utcoffset() is None:
        _reject("SIM_INVALID_TIMESTAMP")
    return parsed


def _safe_parts(value: str) -> list[str]:
    parts = value.split("/")
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
    if any(c in value for c in '\\:<>"|?*') or any(ord(c) < 32 for c in value):
        _reject("SIM_UNSAFE_ARTIFACT_PATH")
    for part in parts:
        if part in {"", ".", ".."} or part.endswith((".", " ")) or part.split(".")[0].upper() in reserved:
            _reject("SIM_UNSAFE_ARTIFACT_PATH")
    return parts


def _read_artifact(root: Path, artifact: dict) -> bytes:
    try:
        candidate = root
        for part in _safe_parts(artifact["path"]):
            candidate = candidate / part
            if candidate.is_symlink():
                _reject("SIM_SYMLINK_FORBIDDEN")
        if not candidate.resolve().is_relative_to(root):
            _reject("SIM_UNSAFE_ARTIFACT_PATH")
        if not candidate.is_file():
            _reject("SIM_ARTIFACT_NOT_READABLE")
        if candidate.stat().st_size != artifact["size_bytes"]:
            _reject("SIM_ARTIFACT_SIZE_MISMATCH")
        with candidate.open("rb") as stream:
            data = stream.read(MAX_ARTIFACT_BYTES + 1)
        if len(data) != artifact["size_bytes"]:
            _reject("SIM_ARTIFACT_SIZE_MISMATCH")
        if hashlib.sha256(data).hexdigest() != artifact["sha256"]:
            _reject("SIM_ARTIFACT_HASH_MISMATCH")
        return data
    except OSError:
        _reject("SIM_ARTIFACT_NOT_READABLE")


def _check_payload(data: bytes, artifact: dict, origin: str) -> None:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeError:
        _reject("SIM_INVALID_ARTIFACT_JSON")
    records = [text] if artifact["format"] == "json" else [line for line in text.splitlines() if line.strip()]
    if not records:
        _reject("SIM_INVALID_ARTIFACT_JSON")
    for record in records:
        parsed = load_receipt_text(record)
        if not isinstance(parsed, (dict, list)):
            _reject("SIM_INVALID_ARTIFACT_JSON")
        for key, value in _walk(parsed):
            normalized = re.sub(r"[^a-z0-9]", "", key.casefold())
            if artifact["visibility"] == "MODEL_VISIBLE" and normalized in TRUTH_KEYS:
                _reject("SIM_VISIBLE_TRUTH_KEY")
            if origin == "ACTUAL_SIMULATION_RUN" and key == "evidence_origin" and value == "SYNTHETIC_TEST_ONLY":
                _reject("SIM_SYNTHETIC_FIXTURE_MISLABELED")


def validate_simulation_run_receipt(receipt: dict[str, Any], *, artifact_root: Path | str | None = None) -> dict[str, Any]:
    """Check one receipt without mutation. Only local bytes can be verified.

    Reported YES/NO statuses are retained as declarations, not independently
    adjudicated scientific conclusions. No output includes the hidden values.
    """
    if not isinstance(receipt, dict):
        _reject("SIM_SCHEMA_INVALID")
    for _ in _walk(receipt):
        pass
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        _reject("SIM_SCHEMA_UNAVAILABLE")
    if not Draft202012Validator(schema).is_valid(receipt):
        _reject("SIM_SCHEMA_INVALID")
    start, end, cutoff = (_time(receipt[k]) for k in ("started_at", "ended_at", "analysis_cutoff"))
    if end < start:
        _reject("SIM_INVALID_RUN_CHRONOLOGY")
    if cutoff < start:
        _reject("SIM_INVALID_ANALYSIS_CUTOFF")
    origin = receipt["evidence_origin"]
    identities = [receipt[k] for k in ("run_id", "scenario_id", "event_family_id")]
    if origin == "ACTUAL_SIMULATION_RUN" and any(x.upper().startswith("SYNTHETIC-") for x in identities):
        _reject("SIM_SYNTHETIC_FIXTURE_MISLABELED")
    if origin == "SYNTHETIC_TEST_ONLY" and not all(x.upper().startswith("SYNTHETIC-") for x in identities):
        _reject("SIM_FIXTURE_ID_PREFIX_REQUIRED")
    replay = receipt["replay_of"]
    if replay:
        if replay["run_id"] == receipt["run_id"]:
            _reject("SIM_REPLAY_SELF_REFERENCE")
        if any(replay[k] != receipt[k] for k in ("event_family_id", "scenario_id")):
            _reject("SIM_REPLAY_LINEAGE_MISMATCH")
    artifacts = receipt["artifacts"]
    if sum(a["size_bytes"] for a in artifacts) > MAX_TOTAL_BYTES:
        _reject("SIM_ARTIFACT_BUDGET_EXCEEDED")
    by_id, paths, digests = {}, set(), {}
    visible = set()
    visible_roles = set()
    for artifact in artifacts:
        available_at = _time(artifact["available_at"])
        aid = artifact["artifact_id"]
        if aid in by_id:
            _reject("SIM_DUPLICATE_ARTIFACT_ID")
        by_id[aid] = artifact
        if artifact["run_id"] != receipt["run_id"]:
            _reject("SIM_CROSS_RUN_ARTIFACT")
        _safe_parts(artifact["path"])
        normalized = artifact["path"].casefold()
        if normalized in paths:
            _reject("SIM_ARTIFACT_PATH_ALIAS")
        paths.add(normalized)
        previous = digests.setdefault(artifact["sha256"], artifact["visibility"])
        if previous != artifact["visibility"]:
            _reject("SIM_CROSS_VISIBILITY_DIGEST_ALIAS")
        if artifact["visibility"] == "MODEL_VISIBLE":
            if artifact["role"] not in VISIBLE_ROLES:
                _reject("SIM_HIDDEN_ROLE_EXPOSED")
            if available_at > cutoff:
                _reject("SIM_POST_CUTOFF_VISIBLE_ARTIFACT")
            visible.add(aid)
            visible_roles.add(artifact["role"])
    if not any(a["role"] == "CONFIGURATION" and a["sha256"] == receipt["simulator"]["configuration_sha256"] for a in artifacts):
        _reject("SIM_CONFIGURATION_FINGERPRINT_MISMATCH")
    selected = set(receipt["model_visible_artifact_refs"])
    if not selected <= by_id.keys():
        _reject("SIM_UNRESOLVED_ARTIFACT_REF")
    if any(by_id[a]["visibility"] != "MODEL_VISIBLE" for a in selected):
        _reject("SIM_HIDDEN_ARTIFACT_SELECTED")
    if selected != visible:
        _reject("SIM_VISIBLE_SELECTION_MISMATCH")
    for name, stage in receipt["stages"].items():
        refs = stage["evidence_refs"]
        if stage["status"] in {"YES", "NO"} and not refs:
            _reject("SIM_STAGE_EVIDENCE_REQUIRED")
        for ref in refs:
            if ref not in by_id:
                _reject("SIM_UNRESOLVED_ARTIFACT_REF")
            if by_id[ref]["role"] != STAGE_ROLES[name]:
                _reject("SIM_STAGE_EVIDENCE_ROLE_MISMATCH")
    verified = 0
    if artifact_root is not None:
        try:
            root = Path(artifact_root)
            if root.is_symlink():
                _reject("SIM_SYMLINK_FORBIDDEN")
            root = root.resolve(strict=True)
            if not root.is_dir():
                _reject("SIM_INVALID_ARTIFACT_ROOT")
        except SimulationReceiptError:
            raise
        except (OSError, ValueError, TypeError):
            _reject("SIM_INVALID_ARTIFACT_ROOT")
        for artifact in artifacts:
            _check_payload(_read_artifact(root, artifact), artifact, origin)
            verified += 1
    missing = len(REQUIRED_INPUT_ROLES - visible_roles)
    return {
        "decision": "SYNTHETIC_TEST_ONLY" if origin == "SYNTHETIC_TEST_ONLY" else "REVIEW_REQUIRED",
        "verification_scope": "LOCAL_ARTIFACT_BYTES" if artifact_root is not None else "METADATA_ONLY",
        "artifact_count": len(artifacts), "artifact_bytes_verified": verified,
        "model_visible_artifact_count": len(visible), "qa_only_artifact_count": len(artifacts) - len(visible),
        "reported_yes_stage_count": sum(s["status"] == "YES" for s in receipt["stages"].values()),
        "reported_no_stage_count": sum(s["status"] == "NO" for s in receipt["stages"].values()),
        "unknown_stage_count": sum(s["status"] == "UNKNOWN" for s in receipt["stages"].values()),
        "missing_input_role_count": missing, "diagnostic_input_complete": missing == 0,
        "actual_simulation_run_count": 0, "declared_actual_run_count": int(origin == "ACTUAL_SIMULATION_RUN"),
        "input_completeness_scope": "DECLARED_ROLE_COVERAGE_ONLY", "source_authenticity_verified": False,
        "physical_validity_verified": False, "semantic_leakage_review_required": True,
        "sft_records_emitted": 0, "training_authorized": False, "gold_authorized": False,
        "sft_export_authorized": False,
    }
