"""Append-only, hash-chained human review and delivery ledger.

The ledger records workflow events and candidate hashes only; it does not store candidate
text or authenticate reviewer identity. Use one writer per ledger file.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

GENESIS = "0" * 64
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
DECISIONS = {"APPROVE", "EDIT", "REJECT"}
DELIVERY_STATES = {"DELIVERED", "FAILED"}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def object_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_candidate_sha256(path: str | Path) -> str:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return object_sha256(payload)


def _parse_timestamp(value: str) -> None:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp_utc must include a timezone")


def _event_hash(event: Mapping[str, Any]) -> str:
    payload = {key: value for key, value in event.items() if key != "event_sha256"}
    return object_sha256(payload)


def _validate_event_shape(event: Mapping[str, Any]) -> None:
    if event.get("event_type") not in {"REVIEW_DECISION", "DELIVERY_RESULT"}:
        raise ValueError("unsupported event_type")
    for field in ("seed_id", "domain", "timestamp_utc"):
        if not isinstance(event.get(field), str) or not event[field].strip():
            raise ValueError(f"{field} must be a nonempty string")
    if event["domain"] not in {"adcs", "eps"}:
        raise ValueError("domain must be adcs or eps")
    _parse_timestamp(event["timestamp_utc"])
    if not HASH_RE.fullmatch(str(event.get("candidate_sha256", ""))):
        raise ValueError("candidate_sha256 must be a lowercase SHA-256 hex digest")
    if not HASH_RE.fullmatch(str(event.get("previous_event_sha256", ""))):
        raise ValueError("previous_event_sha256 must be a lowercase SHA-256 hex digest")
    if event["event_type"] == "REVIEW_DECISION":
        if event.get("decision") not in DECISIONS:
            raise ValueError("decision must be APPROVE, EDIT or REJECT")
        if not isinstance(event.get("reviewer_id"), str) or not event["reviewer_id"].strip():
            raise ValueError("reviewer_id must be a nonempty pseudonymous identifier")
        if not isinstance(event.get("round_index"), int) or event["round_index"] < 1:
            raise ValueError("round_index must be a positive integer")
        elapsed = event.get("elapsed_seconds")
        if not isinstance(elapsed, int) or elapsed < 0:
            raise ValueError("elapsed_seconds must be a non-negative integer")
        issues = event.get("issue_categories")
        if not isinstance(issues, list) or any(not isinstance(item, str) or not item.strip() for item in issues):
            raise ValueError("issue_categories must be a list of nonempty strings")
        if event["decision"] == "APPROVE":
            if event.get("accepted_candidate_sha256") != event["candidate_sha256"]:
                raise ValueError("APPROVE must bind accepted_candidate_sha256 to candidate_sha256")
            if event.get("corrected_candidate_sha256") is not None:
                raise ValueError("APPROVE cannot include corrected_candidate_sha256")
        elif event["decision"] == "EDIT":
            if not HASH_RE.fullmatch(str(event.get("corrected_candidate_sha256", ""))):
                raise ValueError("EDIT requires corrected_candidate_sha256 for the next review round")
            if event.get("accepted_candidate_sha256") is not None:
                raise ValueError("EDIT cannot include accepted_candidate_sha256")
        else:
            if event.get("accepted_candidate_sha256") is not None or event.get("corrected_candidate_sha256") is not None:
                raise ValueError("REJECT cannot include accepted or corrected candidate hashes")
    else:
        if event.get("delivery_status") not in DELIVERY_STATES:
            raise ValueError("delivery_status must be DELIVERED or FAILED")
        if not isinstance(event.get("delivery_note", ""), str):
            raise ValueError("delivery_note must be a string")


def verify_ledger(path: str | Path) -> dict[str, Any]:
    ledger_path = Path(path)
    if not ledger_path.exists():
        return {"valid": True, "event_count": 0, "seed_count": 0, "last_event_sha256": GENESIS}
    previous = GENESIS
    states: dict[str, dict[str, Any]] = {}
    count = 0
    for line_number, line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise ValueError(f"blank ledger line at {line_number}")
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON at ledger line {line_number}") from exc
        if not isinstance(event, dict):
            raise ValueError(f"ledger line {line_number} must be an object")
        _validate_event_shape(event)
        if event.get("previous_event_sha256") != previous:
            raise ValueError(f"broken previous-event hash at ledger line {line_number}")
        if event.get("event_sha256") != _event_hash(event):
            raise ValueError(f"event hash mismatch at ledger line {line_number}")
        seed_id = event["seed_id"]
        state = states.setdefault(seed_id, {
            "domain": event["domain"], "review_events": [], "delivery_events": [],
            "next_candidate_sha256": None, "terminal": False,
        })
        if state["domain"] != event["domain"]:
            raise ValueError(f"domain changed within seed {seed_id!r}")
        if event["event_type"] == "REVIEW_DECISION":
            if state["terminal"]:
                raise ValueError(f"review event follows terminal decision for seed {seed_id!r}")
            expected_round = len(state["review_events"]) + 1
            if event["round_index"] != expected_round:
                raise ValueError(f"non-sequential review round for seed {seed_id!r}")
            expected_candidate = state["next_candidate_sha256"]
            if expected_candidate is not None and event["candidate_sha256"] != expected_candidate:
                raise ValueError(f"candidate hash does not match prior EDIT for seed {seed_id!r}")
            if state["delivery_events"]:
                raise ValueError(f"review event follows delivery event for seed {seed_id!r}")
            state["review_events"].append(event)
            if event["decision"] == "EDIT":
                state["next_candidate_sha256"] = event["corrected_candidate_sha256"]
            elif event["decision"] in {"APPROVE", "REJECT"}:
                state["next_candidate_sha256"] = None
                state["terminal"] = True
        else:
            reviews = state["review_events"]
            if not reviews or reviews[-1]["decision"] != "APPROVE":
                raise ValueError(f"delivery event requires an approved candidate for seed {seed_id!r}")
            approved_hash = reviews[-1]["accepted_candidate_sha256"]
            if event["candidate_sha256"] != approved_hash:
                raise ValueError(f"delivery candidate hash does not match approved version for seed {seed_id!r}")
            if state["delivery_events"] and state["delivery_events"][-1]["delivery_status"] == "DELIVERED":
                raise ValueError(f"delivery already succeeded for seed {seed_id!r}")
            state["delivery_events"].append(event)
        previous = event["event_sha256"]
        count += 1
    return {
        "valid": True,
        "event_count": count,
        "seed_count": len(states),
        "last_event_sha256": previous,
    }


def append_event(path: str | Path, event: Mapping[str, Any]) -> dict[str, Any]:
    ledger_path = Path(path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    verification = verify_ledger(ledger_path)
    payload = dict(event)
    payload["previous_event_sha256"] = verification["last_event_sha256"]
    payload.pop("event_sha256", None)
    _validate_event_shape(payload)
    payload["event_sha256"] = _event_hash(payload)
    # Validate the transition before touching the ledger.
    existing = ledger_path.read_text(encoding="utf-8") if ledger_path.exists() else ""
    candidate_text = existing + json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n"
    temp_path = ledger_path.with_suffix(ledger_path.suffix + ".tmp")
    temp_path.write_text(candidate_text, encoding="utf-8")
    try:
        verify_ledger(temp_path)
        temp_path.replace(ledger_path)
    finally:
        if temp_path.exists():
            temp_path.unlink()
    return payload


def build_review_event(
    *,
    seed_id: str,
    domain: str,
    candidate_sha256: str,
    reviewer_id: str,
    round_index: int,
    elapsed_seconds: int,
    decision: str,
    issue_categories: list[str],
    corrected_candidate_sha256: str | None = None,
    timestamp_utc: str | None = None,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "event_type": "REVIEW_DECISION",
        "seed_id": seed_id,
        "domain": domain,
        "candidate_sha256": candidate_sha256,
        "reviewer_id": reviewer_id,
        "round_index": round_index,
        "elapsed_seconds": elapsed_seconds,
        "decision": decision,
        "issue_categories": issue_categories,
        "accepted_candidate_sha256": candidate_sha256 if decision == "APPROVE" else None,
        "corrected_candidate_sha256": corrected_candidate_sha256 if decision == "EDIT" else None,
        "timestamp_utc": timestamp_utc or datetime.now(timezone.utc).isoformat(),
    }
    _validate_event_shape({**event, "previous_event_sha256": GENESIS})
    return event


def build_delivery_event(
    *,
    seed_id: str,
    domain: str,
    candidate_sha256: str,
    delivery_status: str,
    delivery_note: str = "",
    timestamp_utc: str | None = None,
) -> dict[str, Any]:
    event = {
        "event_type": "DELIVERY_RESULT",
        "seed_id": seed_id,
        "domain": domain,
        "candidate_sha256": candidate_sha256,
        "delivery_status": delivery_status,
        "delivery_note": delivery_note,
        "timestamp_utc": timestamp_utc or datetime.now(timezone.utc).isoformat(),
    }
    _validate_event_shape({**event, "previous_event_sha256": GENESIS})
    return event


def summarize_ledger(path: str | Path) -> dict[str, Any]:
    verification = verify_ledger(path)
    events = []
    ledger_path = Path(path)
    if ledger_path.exists():
        events = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    states: dict[str, dict[str, Any]] = {}
    for event in events:
        state = states.setdefault(event["seed_id"], {
            "domain": event["domain"], "reviews": [], "deliveries": [],
        })
        if event["event_type"] == "REVIEW_DECISION":
            state["reviews"].append(event)
        else:
            state["deliveries"].append(event)
    total = len(states)
    reviewed = {key: value for key, value in states.items() if value["reviews"]}
    first_approved = sum(value["reviews"][0]["decision"] == "APPROVE" for value in reviewed.values())
    final_approved = {
        key: value for key, value in reviewed.items() if value["reviews"][-1]["decision"] == "APPROVE"
    }
    corrected_approved = sum(value["reviews"][0]["decision"] != "APPROVE" for value in final_approved.values())
    delivered = {
        key: value for key, value in final_approved.items()
        if value["deliveries"] and value["deliveries"][-1]["delivery_status"] == "DELIVERED"
        and value["deliveries"][-1]["candidate_sha256"] == value["reviews"][-1]["accepted_candidate_sha256"]
    }
    total_review_seconds = sum(event["elapsed_seconds"] for value in reviewed.values() for event in value["reviews"])
    initial_not_approved = sum(value["reviews"][0]["decision"] != "APPROVE" for value in reviewed.values())
    summary: dict[str, Any] = {
        "ledger_integrity": verification,
        "seed_count": total,
        "reviewed_seed_count": len(reviewed),
        "first_pass_approval_count": first_approved,
        "first_pass_approval_rate": round(first_approved / len(reviewed), 4) if reviewed else None,
        "final_review_approval_count": len(final_approved),
        "final_review_approval_rate": round(len(final_approved) / len(reviewed), 4) if reviewed else None,
        "corrected_to_approved_count": corrected_approved,
        "corrected_to_approved_yield": round(corrected_approved / initial_not_approved, 4) if initial_not_approved else None,
        "final_delivery_success_count": len(delivered),
        "final_delivery_success_rate_all_reviewed": round(len(delivered) / len(reviewed), 4) if reviewed else None,
        "delivery_success_rate_among_approved": round(len(delivered) / len(final_approved), 4) if final_approved else None,
        "final_rejection_count": sum(value["reviews"][-1]["decision"] == "REJECT" for value in reviewed.values()),
        "mean_human_review_minutes_per_seed": round(total_review_seconds / 60 / len(reviewed), 3) if reviewed else None,
        "mean_review_rounds_per_seed": round(sum(len(value["reviews"]) for value in reviewed.values()) / len(reviewed), 3) if reviewed else None,
        "by_domain": {},
    }
    for domain in ("adcs", "eps"):
        domain_states = {key: value for key, value in reviewed.items() if value["domain"] == domain}
        count = len(domain_states)
        first = sum(value["reviews"][0]["decision"] == "APPROVE" for value in domain_states.values())
        final = {key: value for key, value in domain_states.items() if value["reviews"][-1]["decision"] == "APPROVE"}
        delivery = {
            key: value for key, value in final.items()
            if value["deliveries"] and value["deliveries"][-1]["delivery_status"] == "DELIVERED"
            and value["deliveries"][-1]["candidate_sha256"] == value["reviews"][-1]["accepted_candidate_sha256"]
        }
        initial_not = sum(value["reviews"][0]["decision"] != "APPROVE" for value in domain_states.values())
        corrected = sum(value["reviews"][0]["decision"] != "APPROVE" for value in final.values())
        seconds = sum(event["elapsed_seconds"] for value in domain_states.values() for event in value["reviews"])
        summary["by_domain"][domain] = {
            "reviewed_seed_count": count,
            "first_pass_approval_rate": round(first / count, 4) if count else None,
            "final_review_approval_rate": round(len(final) / count, 4) if count else None,
            "corrected_to_approved_yield": round(corrected / initial_not, 4) if initial_not else None,
            "final_delivery_success_rate_all_reviewed": round(len(delivery) / count, 4) if count else None,
            "mean_human_review_minutes_per_seed": round(seconds / 60 / count, 3) if count else None,
        }
    return summary
