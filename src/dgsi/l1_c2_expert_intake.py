"""Bind returned C2 expert forms to independently supplied current sources."""
from __future__ import annotations

import json

from .l1_c2_expert_handoff import build_c2_expert_handoff
from .l1_c2_scored_review import audit_c2_scored_review
from .l1_coverage_review import DECISIONS, FINDING_CODES, REVIEW_DIMENSIONS, validate_blind_l1_review


class C2ExpertIntakeError(ValueError):
    """Fixed-code rejection safe to show to the operator."""


_PENDING = "PENDING_REVIEW_COMPLETION"
_AUTH = "PENDING_REVIEWER_AUTHENTICATION"
_ADJ = "PENDING_SECURE_ADJUDICATION"
_BINDINGS = ("task_id", "collection_projection_sha256", "packet_sha256", "source_public_sha256")
_NEXT = {
    _PENDING: ("REVIEW_PAIR_INCOMPLETE", "COMPLETE_MISSING_SCORECARDS"),
    _AUTH: ("REVIEWER_AUTHENTICATION_REQUIRED", "VERIFY_REVIEWER_IDENTITIES_PRIVATELY"),
    _ADJ: ("SECURE_ADJUDICATION_REQUIRED", "ROUTE_FOR_SECURE_ADJUDICATION"),
}


def _metadata(document, editable):
    return json.dumps({key: value for key, value in document.items() if key != editable},
                      sort_keys=True, allow_nan=False)


def _scorecard_complete(card):
    invalid = "C2_EXPERT_SCORECARD_INVALID"
    if not isinstance(card, dict) or set(card) != {"scores", "reviewer_token", "finding_codes", "decision"}:
        raise C2ExpertIntakeError(invalid)
    scores, codes = card["scores"], card["finding_codes"]
    decision, token = card["decision"], card["reviewer_token"]
    if not isinstance(scores, dict) or set(scores) != set(REVIEW_DIMENSIONS):
        raise C2ExpertIntakeError(invalid)
    if any(s is not None and (type(s) is not int or not 1 <= s <= 5) for s in scores.values()):
        raise C2ExpertIntakeError(invalid)
    if token is not None and (not isinstance(token, str) or not token.strip()):
        raise C2ExpertIntakeError(invalid)
    if decision is not None and (not isinstance(decision, str) or decision not in DECISIONS):
        raise C2ExpertIntakeError(invalid)
    if (not isinstance(codes, list) or any(not isinstance(c, str) or c not in FINDING_CODES for c in codes)
            or len(set(codes)) != len(codes)):
        raise C2ExpertIntakeError(invalid)
    return token is not None and decision is not None and bool(codes) and None not in scores.values()


def _check_form(form, blank):
    if not isinstance(form, dict) or _metadata(form, "tasks") != _metadata(blank, "tasks"):
        raise C2ExpertIntakeError("C2_EXPERT_HANDOFF_METADATA_INVALID")
    rows = form.get("tasks")
    expected = {row["task_id"]: row for row in blank["tasks"]}
    if not isinstance(rows, list) or len(rows) != len(expected):
        raise C2ExpertIntakeError("C2_EXPERT_TASK_COVERAGE_INVALID")
    cards, tokens = {}, set()
    for row in rows:
        task = row.get("task_id") if isinstance(row, dict) else None
        if not isinstance(task, str) or task not in expected or task in cards:
            raise C2ExpertIntakeError("C2_EXPERT_TASK_COVERAGE_INVALID")
        if _metadata(row, "scorecard") != _metadata(expected[task], "scorecard"):
            raise C2ExpertIntakeError("C2_EXPERT_HANDOFF_METADATA_INVALID")
        card = row.get("scorecard")
        cards[task] = (card, _scorecard_complete(card))
        if card["reviewer_token"] is not None:
            tokens.add(card["reviewer_token"].strip())
    if len(tokens) > 1:
        raise C2ExpertIntakeError("C2_EXPERT_REVIEWER_SLOT_INCONSISTENT")
    return cards, tokens


def _paired_outcome(row, a, b):
    form = {"schema_version": "dgsi-l1-blind-review.v1", "assessments": [a, b],
            "blinded_packet_ref": row["blinded_packet_ref"]}
    try:
        result = validate_blind_l1_review(form)
        state = _ADJ if result["decision"] == "NEEDS_SECURE_ADJUDICATION" else _AUTH
        audited = audit_c2_scored_review(row, {
            **{key: row[key] for key in _BINDINGS},
            "schema_version": "dgsi-c2-scored-blind-review-submission.v1",
            "blind_review": form, "adjudication_status": state,
        })
    except ValueError:
        raise C2ExpertIntakeError("C2_EXPERT_COMPLETE_PAIR_INVALID") from None
    state = audited["adjudication_status"]
    if state == _AUTH:
        return state, [_NEXT[_AUTH][0]]

    # Describe the original rubric's verdict only after both validations pass.
    decisions = {a["decision"], b["decision"]}
    reasons = []
    if "REVISE" in decisions:
        reasons.append("REVIEWER_REQUESTED_REVISION")
    if "REJECT" in decisions:
        reasons.append("REVIEWER_REJECTED")
    if len(decisions) > 1:
        reasons.append("RECOMMENDATION_DISAGREEMENT")
    if audited["disagreement_dimension_count"]:
        reasons.append("SCORE_GAP")
    if any(code != "NO_ISSUE" for card in (a, b) for code in card["finding_codes"]):
        reasons.append("MATERIAL_FINDING_PRESENT")
    return state, reasons


def audit_c2_expert_intake_against_current_sources(
    reviewer_a: dict, reviewer_b: dict, current_l1_collection: dict, current_l0_fact_cards: list,
) -> dict:
    """Return a private pending queue. Partial assessments receive no rubric verdict."""
    try:
        if not isinstance(current_l1_collection, dict) or not isinstance(current_l0_fact_cards, list):
            raise TypeError
        blanks = [build_c2_expert_handoff(current_l1_collection, source_fact_cards=current_l0_fact_cards,
                                          reviewer_slot=slot) for slot in ("A", "B")]
    except (ValueError, TypeError, KeyError, IndexError, AttributeError, RecursionError):
        raise C2ExpertIntakeError("C2_EXPERT_CURRENT_SNAPSHOT_INVALID") from None
    try:
        a, tokens_a = _check_form(reviewer_a, blanks[0])
        b, tokens_b = _check_form(reviewer_b, blanks[1])
    except C2ExpertIntakeError:
        raise
    except (ValueError, TypeError, RecursionError):
        raise C2ExpertIntakeError("C2_EXPERT_HANDOFF_METADATA_INVALID") from None
    if tokens_a & tokens_b:
        raise C2ExpertIntakeError("C2_EXPERT_REVIEWER_SLOTS_MUST_DIFFER")

    counts = dict.fromkeys(_NEXT, 0)
    queue = []
    complete = 0
    for row in blanks[0]["tasks"]:
        task = row["task_id"]
        card_a, complete_a = a[task]
        card_b, complete_b = b[task]
        complete += complete_a + complete_b
        if complete_a and complete_b:
            state, reasons = _paired_outcome(row, card_a, card_b)
        else:
            state, reasons = _PENDING, [_NEXT[_PENDING][0]]
        counts[state] += 1
        reason, action = _NEXT[state]
        queue.append({**{key: row[key] for key in _BINDINGS}, "adjudication_status": state,
                      "reason_code": reason, "reason_codes": reasons, "next_action": action,
                      "incomplete_slots": [slot for slot, done in (("A", complete_a), ("B", complete_b)) if not done]})
    paired = counts[_AUTH] + counts[_ADJ]
    return {
        "schema_version": "dgsi-c2-current-expert-intake.v1",
        "decision": "CURRENT_EXPERT_INTAKE_REVIEW_ONLY",
        "current_public_source_snapshot_matched": True,
        "packet_count": len(queue), "complete_scorecard_count": complete,
        "incomplete_scorecard_count": 2 * len(queue) - complete, "paired_review_count": paired,
        "ten_dimension_rubric_validated_count": paired, "pending_completion_count": counts[_PENDING],
        "adjudication_status_counts": counts, "identity_authenticated": False,
        "source_rights_verified": False, "expert_adjudicated_count": 0, "rights_cleared_count": 0,
        "official_splits_assigned": False, "sft_records_emitted": 0,
        "gold_eligible": False, "training_authorized": False, "task_queue": queue,
    }
