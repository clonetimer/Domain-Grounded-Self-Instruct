"""DEV_ONLY history-Context A/B input integrity audit. Never releases training data.

Only structural/temporal checks: it cannot certify source authenticity, rights,
physical cause, expert opinion, or semantic absence of all historical knowledge.
It never prints a model-visible input, reference answer, or reviewer material.
"""
from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile


class HistoryPairAuditError(ValueError):
    """Error codes contain no source text or case identifiers."""


def _fail(code: str) -> None:
    raise HistoryPairAuditError(code)


def _digest(value: Any) -> str:
    try:
        raw = json.dumps(value, sort_keys=True, ensure_ascii=False,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError):
        _fail("PAIR_UNHASHABLE")
    return sha256(raw).hexdigest()


def _date(value: Any) -> datetime:
    if not isinstance(value, str):
        _fail("PAIR_INVALID_TIME")
    try:
        when = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if when.utcoffset() is None:
            _fail("PAIR_INVALID_TIME")
        return when
    except ValueError:
        _fail("PAIR_INVALID_TIME")


def _contains_forbidden_keys(value: Any) -> bool:
    forbidden = {
        "internal_review", "formal_target", "expected_output",
        "curator_prompts", "reviewer_questions", "blind_review",
        "target_answer", "gold_label", "raw_telemetry",
        "reviewer_id", "reviewer_token", "not_for_sft",
    }
    stack, budget = [value], 20000
    while stack:
        budget -= 1
        if budget < 0:
            _fail("PAIR_CONTENT_TOO_COMPLEX")
        node = stack.pop()
        if isinstance(node, dict):
            if forbidden.intersection(node):
                return True
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return False


def audit_pair_zip(path: str | Path) -> dict[str, Any]:
    """Validate paired inputs without releasing their content or claiming effect."""
    try:
        with ZipFile(path) as zf:
            names = zf.namelist()
            if len(names) != len(set(names)) or len(names) > 256:
                _fail("PAIR_ARCHIVE_MEMBERS_INVALID")
            if any(n.startswith("/") or ".." in n.split("/") or "\\" in n for n in names):
                _fail("PAIR_ARCHIVE_MEMBERS_INVALID")
            if sum(zf.getinfo(n).file_size for n in names) > 20_000_000:
                _fail("PAIR_ARCHIVE_TOO_LARGE")

            def load(member: str) -> Any:
                if member not in names or zf.getinfo(member).file_size > 1_000_000:
                    _fail("PAIR_MEMBER_MISSING_OR_TOO_LARGE")
                try:
                    return json.loads(zf.read(member).decode("utf-8"))
                except (ValueError, UnicodeError):
                    _fail("PAIR_MEMBER_JSON_INVALID")

            manifest = load("coordinator_ONLY_pairing_manifest.json")
            if not isinstance(manifest, dict) or manifest.get("purpose") != (
                "DEV_ONLY_HISTORY_SOURCE_ISOLATED_NEGATIVE_TRANSFER_PAIRS_NOT_TRAINING"
            ):
                _fail("PAIR_MANIFEST_NOT_DEV_ONLY")
            for field in ("training_authorized", "gold_eligible",
                          "official_split_assigned", "source_rights_verified",
                          "expert_review_complete"):
                if manifest.get(field) is not False:
                    _fail("PAIR_RELEASE_GUARD_INVALID")
            if (manifest.get("positive_history_evaluation") != "NOT_EVALUABLE"
                    or manifest.get("experiment_execution") != "NOT_RUN"):
                _fail("PAIR_OUTCOME_CLAIM_UNSUPPORTED")
            pairs = manifest.get("pairs")
            if not isinstance(pairs, list) or not 1 <= len(pairs) <= 50:
                _fail("PAIR_LIST_INVALID")

            families, cores, task_ids, expected_members = set(), set(), set(), set()
            hits, missing_verification = 0, 0
            for entry in pairs:
                if not isinstance(entry, dict):
                    _fail("PAIR_ENTRY_INVALID")
                task = entry.get("task_id")
                if not isinstance(task, str) or not task or "/" in task or "\\" in task or task in task_ids:
                    _fail("PAIR_TASK_ID_INVALID")
                task_ids.add(task)
                family = entry.get("event_family")
                if not isinstance(family, str) or not family:
                    _fail("PAIR_FAMILY_MISSING")
                families.add(family)
                assignment = [entry.get("arm_A"), entry.get("arm_B")]
                if sorted(assignment) != ["HISTORY", "NO_HIT"]:
                    _fail("PAIR_ARM_ASSIGNMENT_INVALID")

                arms = {}
                for side, condition in zip(("A", "B"), assignment):
                    member = f"model_visible_inputs/{task}/arm_{side}.json"
                    expected_members.add(member)
                    record = load(member)
                    if not isinstance(record, dict) or set(record) != {
                        "analysis_cutoff", "case_id", "data_classification",
                        "input", "instruction", "task_type",
                    }:
                        _fail("PAIR_VISIBLE_ENVELOPE_INVALID")
                    if (record.get("case_id") != entry.get("case_id")
                            or record.get("task_type") != entry.get("task_type")
                            or record.get("data_classification") !=
                            "LITERATURE_DERIVED_SYNTHETIC_NOT_REAL_RECORD"):
                        _fail("PAIR_VISIBLE_BINDING_INVALID")
                    if record.get("analysis_cutoff") != entry.get("analysis_cutoff"):
                        _fail("PAIR_CUTOFF_MISMATCH")
                    if _contains_forbidden_keys(record):
                        _fail("PAIR_REVIEW_OR_TARGET_LEAK")
                    inp = record.get("input")
                    if (not isinstance(inp, dict)
                            or inp.get("analysis_cutoff") != entry.get("analysis_cutoff")
                            or inp.get("raw_telemetry_included") is not False
                            or not isinstance(inp.get("historical_cases"), list)):
                        _fail("PAIR_INPUT_BOUNDARY_INVALID")
                    arms[condition] = record

                yes, no = arms["HISTORY"], arms["NO_HIT"]
                with_history, without_history = yes["input"], no["input"]
                if not with_history["historical_cases"] or without_history["historical_cases"]:
                    _fail("PAIR_HISTORY_EXPOSURE_INVALID")
                if ({k: v for k, v in yes.items() if k != "input"} !=
                        {k: v for k, v in no.items() if k != "input"}):
                    _fail("PAIR_UNCONTROLLED_ENVELOPE_CHANGE")
                current = {k: v for k, v in with_history.items() if k != "historical_cases"}
                control = {k: v for k, v in without_history.items() if k != "historical_cases"}
                if current != control or _digest(current) != entry.get("core_input_sha256"):
                    _fail("PAIR_UNCONTROLLED_CORE_CHANGE")
                cores.add(_digest(current))
                # Manifest digests bind FULL visible envelopes, not only input.
                if (_digest(yes) != entry.get("with_history_input_sha256")
                        or _digest(no) != entry.get("without_history_input_sha256")):
                    _fail("PAIR_INPUT_HASH_MISMATCH")
                evidence = current.get("knowledge_evidence")
                removed = entry.get("history_only_knowledge_evidence_removed_from_both_arms")
                if not isinstance(evidence, list) or not isinstance(removed, list):
                    _fail("PAIR_SOURCE_REMOVAL_LEDGER_MISSING")
                ids = [v.get("evidence_id") for v in evidence if isinstance(v, dict)]
                if any(v in ids for v in removed) or any(
                    isinstance(v, str) and v.startswith("HIST-") for v in ids
                ):
                    _fail("PAIR_HISTORY_SOURCE_LEAK")
                history = with_history["historical_cases"]
                for key in ("history_refs", "history_outcome_statuses",
                            "history_hardware_compatibilities", "history_available_at"):
                    if not isinstance(entry.get(key), list) or len(entry[key]) != len(history):
                        _fail("PAIR_HISTORY_METADATA_MISMATCH")
                if (sorted(x.get("case_ref") for x in history) != sorted(entry["history_refs"])
                        or sorted(x.get("outcome_status") for x in history) !=
                        sorted(entry["history_outcome_statuses"])
                        or sorted(x.get("hardware_compatibility") for x in history) !=
                        sorted(entry["history_hardware_compatibilities"])):
                    _fail("PAIR_HISTORY_METADATA_MISMATCH")
                if sorted(x.get("available_at") for x in history) != sorted(entry["history_available_at"]):
                    _fail("PAIR_HISTORY_TIME_LEDGER_MISMATCH")
                cutoff = _date(entry["analysis_cutoff"])
                for prior in history:
                    if (prior.get("event_family_id") == family
                            or not prior.get("source_case_refs")
                            or not prior.get("applicability_limitations")):
                        _fail("PAIR_HISTORY_PROVENANCE_INVALID")
                    if _date(prior.get("available_at")) > cutoff:
                        _fail("PAIR_FUTURE_HISTORY_LEAK")
                    if prior.get("verified_at") is None:
                        missing_verification += 1
                    elif _date(prior["verified_at"]) > cutoff:
                        _fail("PAIR_FUTURE_HISTORY_LEAK")
                    if (prior.get("outcome_status") == "CONFIRMED"
                            and prior.get("hardware_compatibility") == "COMPATIBLE"):
                        _fail("PAIR_POSITIVE_TRANSFER_NOT_IN_NEGATIVE_COHORT")
                    hits += 1
                if any(ref in json.dumps(current, ensure_ascii=False)
                       for ref in entry["history_refs"]):
                    _fail("PAIR_HISTORY_REF_IN_COMMON_INPUT")

            if {n for n in names if n.startswith("model_visible_inputs/")} != expected_members:
                _fail("PAIR_MODEL_MEMBER_SET_MISMATCH")
            return {
                "schema_version": "dgsi-history-pair-science-integrity.v1",
                "decision": "DEV_ONLY_NOT_RELEASED",
                "pair_count": len(pairs),
                "model_visible_input_count": len(expected_members),
                "distinct_current_input_cores": len(cores),
                "distinct_event_families": len(families),
                "historical_hit_count": hits,
                "hits_without_verified_at": missing_verification,
                "history_time_trust": "DECLARED_TIMES_ONLY_SOURCE_AUTHENTICITY_UNVERIFIED",
                "negative_transfer_model_scoring": "NOT_RUN",
                "positive_history_transfer": "NOT_EVALUABLE",
                "source_rights_verified": False,
                "expert_review_complete": False,
                "training_authorized": False,
                "records_exported": 0,
            }
    except (OSError, EOFError, KeyError, TypeError, AttributeError,
            OverflowError, BadZipFile, RecursionError):
        _fail("PAIR_ARCHIVE_OR_FIELDS_INVALID")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Inspect a local DEV_ONLY history A/B archive")
    p.add_argument("archive", type=Path)
    print(json.dumps(audit_pair_zip(p.parse_args().archive),
                     sort_keys=True, indent=2, ensure_ascii=False))
