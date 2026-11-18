"""Offline SOTA construction scorecard. Never grants Gold, split or SFT permission."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ARMS = ("M0", "M1", "M2", "M3", "M4")
TRACKS = ("LITERATURE_DERIVED_SYNTHETIC", "REAL_GOLD")
DIMENSIONS = (
    "source_fidelity", "phenomenon_analysis", "ml_interpretation",
    "fault_source", "affected_components", "evidence_fidelity",
    "uncertainty", "disposal_fidelity", "historical_context_transfer",
    "engineering_actionability",
)
CRITICAL = (
    "FABRICATED_SOURCE", "FABRICATED_ML_OR_LOG", "FABRICATED_DISPOSAL",
    "UNSUPPORTED_CONFIRMED_CAUSE", "HIDDEN_TRUTH_LEAK", "FUTURE_HISTORY_LEAK",
    "HISTORY_AS_CURRENT_EVIDENCE", "FALSE_EXPERT_OR_RIGHTS_CLAIM",
)


class ScorecardError(ValueError):
    pass


def _fail(code: str) -> None:
    raise ScorecardError(code)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def summarize_construction_trials(document: dict[str, Any]) -> dict[str, Any]:
    """Aggregate candidate attempts by arm and source; never invent human scores.

    Each row represents exactly one attempted candidate. Source groups, event
    families, track, attempt counts and allocated budgets must match for a
    comparable five-arm study. Token usage is measured, not artificially equal.
    """
    if not isinstance(document, dict) or document.get("schema_version") != "dgsi-sota-construction-scorecard.v1":
        _fail("SOTA_SCHEMA_VERSION")
    if document.get("purpose") != "CONSTRUCTION_ONLY":
        _fail("SOTA_NOT_CONSTRUCTION_ONLY")
    trials = document.get("trials")
    if not isinstance(trials, list):
        _fail("SOTA_TRIALS_INVALID")
    ids: set[str] = set()
    by_arm: dict[str, list[dict[str, Any]]] = defaultdict(list)
    source_tracks: dict[str, str] = {}
    for trial in trials:
        if not isinstance(trial, dict):
            _fail("SOTA_TRIAL_INVALID")
        if not all(_nonempty(trial.get(k)) for k in ("trial_id", "source_group", "event_family")):
            _fail("SOTA_ID_MISSING")
        if trial["trial_id"] in ids:
            _fail("SOTA_DUPLICATE_TRIAL")
        ids.add(trial["trial_id"])
        arm, track = trial.get("arm"), trial.get("track")
        if arm not in ARMS or track not in TRACKS:
            _fail("SOTA_ARM_OR_TRACK")
        if track == "REAL_GOLD" and trial.get("gold_admitted") is not True:
            _fail("SOTA_REAL_GOLD_NOT_ADMITTED")
        group = trial["source_group"]
        if group in source_tracks and source_tracks[group] != track:
            _fail("SOTA_SOURCE_TRACK_COLLISION")
        source_tracks[group] = track
        attempts, accepted = trial.get("attempts"), trial.get("accepted_candidates")
        used, budget = trial.get("generation_tokens"), trial.get("token_budget")
        if any(type(v) is not int or v < 0 for v in (attempts, accepted, used, budget)):
            _fail("SOTA_COUNTS_INVALID")
        if attempts != 1 or accepted not in (0, 1):
            _fail("SOTA_ONE_CANDIDATE_PER_TRIAL")
        if used > budget:
            _fail("SOTA_TOKEN_BUDGET_EXCEEDED")
        failures = trial.get("critical_failures", [])
        if not isinstance(failures, list) or any(f not in CRITICAL for f in failures):
            _fail("SOTA_CRITICAL_CODE_INVALID")
        if len(failures) != len(set(failures)):
            _fail("SOTA_DUPLICATE_CRITICAL_CODE")
        if failures and accepted:
            _fail("SOTA_CRITICAL_CANDIDATE_ACCEPTED")
        status = trial.get("review_status")
        scores, reviewers = trial.get("scores", {}), trial.get("reviewer_tokens", [])
        if status == "PENDING":
            if scores or reviewers:
                _fail("SOTA_PENDING_HAS_SCORES")
        elif status == "ADJUDICATED":
            if (not isinstance(reviewers, list) or len(reviewers) < 2
                    or any(not _nonempty(t) for t in reviewers)
                    or len(set(reviewers)) != len(reviewers)):
                _fail("SOTA_REVIEWERS_NOT_INDEPENDENT")
            if not isinstance(scores, dict) or set(scores) != set(DIMENSIONS):
                _fail("SOTA_SCORE_DIMENSIONS")
            if any(type(v) is not int or v not in (0, 1, 2) for v in scores.values()):
                _fail("SOTA_SCORE_RANGE")
            receipt = trial.get("review_receipt_sha256")
            if (not isinstance(receipt, str) or len(receipt) != 64
                    or any(c not in "0123456789abcdef" for c in receipt)):
                _fail("SOTA_REVIEW_RECEIPT_HASH")
        else:
            _fail("SOTA_REVIEW_STATUS")
        by_arm[arm].append(trial)

    summaries: dict[str, Any] = {}
    groups: dict[str, set[tuple[str, str, str]]] = {}
    budgets: dict[str, dict[tuple[str, str, str], tuple[int, int]]] = {}
    for arm in ARMS:
        rows = by_arm[arm]
        key_counts: dict[tuple[str, str, str], int] = defaultdict(int)
        budget_by_key: dict[tuple[str, str, str], int] = defaultdict(int)
        for row in rows:
            key = (row["source_group"], row["event_family"], row["track"])
            key_counts[key] += 1
            budget_by_key[key] += row["token_budget"]
        groups[arm] = set(key_counts)
        budgets[arm] = {k: (v, key_counts[k]) for k, v in budget_by_key.items()}
        reviewed = [r for r in rows if r["review_status"] == "ADJUDICATED"]
        attempted = sum(r["attempts"] for r in rows)
        accepted = sum(r["accepted_candidates"] for r in rows)
        by_track_summary = {}
        for track in TRACKS:
            track_rows = [r for r in rows if r["track"] == track]
            track_reviewed = [r for r in track_rows if r["review_status"] == "ADJUDICATED"]
            by_track_summary[track] = {
                "attempts": len(track_rows),
                "filter_accepted_candidates": sum(r["accepted_candidates"] for r in track_rows),
                "critical_failure_trials": sum(bool(r.get("critical_failures")) for r in track_rows),
                "adjudicated_trials": len(track_reviewed),
                "reviewer_reported_dimension_means": (
                    {d: round(sum(r["scores"][d] for r in track_reviewed) / len(track_reviewed), 4)
                     for d in DIMENSIONS} if track_reviewed else None
                ),
            }
        summaries[arm] = {
            "by_track": by_track_summary,
            "status": "NOT_RUN" if not rows else ("REVIEW_PENDING" if len(reviewed) != len(rows) else "ADJUDICATED_INPUT"),
            "trials": len(rows), "source_groups": len(groups[arm]),
            "tokens_used": sum(r["generation_tokens"] for r in rows),
            "token_budget": sum(r["token_budget"] for r in rows),
            "attempts": attempted, "filter_accepted_candidates": accepted,
            "yield_per_100_attempts": round(100 * accepted / attempted, 4) if attempted else None,
            "critical_failure_trials": sum(bool(r.get("critical_failures")) for r in rows),
            "adjudicated_trials": len(reviewed),
            "reviewer_reported_dimension_means": (
                {d: round(sum(r["scores"][d] for r in reviewed) / len(reviewed), 4) for d in DIMENSIONS}
                if reviewed else None
            ),
        }
    comparable = (
        all(by_arm[a] for a in ARMS)
        and all(groups[a] == groups[ARMS[0]] for a in ARMS)
        and all(budgets[a] == budgets[ARMS[0]] for a in ARMS)
    )
    ready = comparable and all(summaries[a]["status"] == "ADJUDICATED_INPUT" for a in ARMS)
    return {
        "schema_version": "dgsi-sota-construction-summary.v1",
        "purpose": "CONSTRUCTION_ONLY",
        "comparison_status": ("REVIEWED_COMPARABLE_INPUT" if ready else
                              "MATCHED_UNREVIEWED" if comparable else "NOT_COMPARABLE_OR_NOT_RUN"),
        "source_group_budget_matched": comparable,
        "tracks": {t: sum(r["track"] == t for rows in by_arm.values() for r in rows) for t in TRACKS},
        "arms": summaries,
        "training_authorized": False,
        "gold_authorized": False,
        "downstream_sft_result": "NOT_RUN",
        "limits": [
            "Human adjudication and permissions are external; receipt hashes do not independently prove reviewer identity",
            "Construction-quality scores do not prove downstream SFT effectiveness",
        ],
    }


def scorecard_file(input_path: Path, output_path: Path) -> None:
    """Read private trial records locally and write only aggregate scores."""
    if input_path.resolve() == output_path.resolve():
        _fail("SOTA_NO_INPUT_OVERWRITE")
    result = summarize_construction_trials(json.loads(input_path.read_text(encoding="utf-8")))
    if output_path.exists():
        _fail("SOTA_OUTPUT_EXISTS")
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
