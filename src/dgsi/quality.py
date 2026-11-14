"""Offline quality gates for ADCS instruction seed *candidates*.

A machine-readable PASS does not certify the truth of natural-language claims,
authenticate a reviewer, or authorize an on-orbit fault diagnosis.
"""
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any, Mapping


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    path: str
    message: str


REQUIRED = (
    "schema_version", "seed_id", "domain", "task_type", "instruction", "input", "answer",
    "evidence", "claims", "term_ids", "provenance", "review",
)
DIAGNOSIS_STATUSES = {
    "DIAGNOSED", "NORMAL", "AMBIGUOUS", "UNKNOWN_FAULT", "INSUFFICIENT_EVIDENCE",
    "DATA_ERROR", "CONFLICTING_EVIDENCE",
}
REVIEW_STATES = {"CANDIDATE", "MACHINE_CHECKED", "HUMAN_REVIEWED", "REJECTED"}
CLAIM_TYPES = {"OBSERVATION", "MECHANISM", "CAUSAL", "UNCERTAINTY"}
SELF_ATTESTATION = re.compile(r"(?:已经过权威验证|经过权威验证|完全证明|绝对证明|百分之百确定|已获专家一致认可|经严格验证.*正确)")
CAUSAL_LANGUAGE = re.compile(r"(?:直接导致|必然导致|证明.*?(?:致使|引起)|根因必然是)")
TRUTH_KEYS = {"fault_id", "fault_type", "fault_mode", "effect_id", "onset_s", "target_role", "split", "group", "truth", "label", "labels", "source_sha256"}


def _load_json(path: Path) -> dict[str, Any]:
    content = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(content, dict):
        raise ValueError(f"not a JSON object: {path}")
    return content


def _index_unique(rows: list[dict[str, Any]], field: str, name: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        item_id = row.get(field)
        if not isinstance(item_id, str) or not item_id.strip() or item_id in result:
            raise ValueError(f"blank or duplicate {field} in {name}: {item_id!r}")
        result[item_id] = row
    return result


def load_registry(root: str | Path) -> dict[str, Any]:
    """Read and cross-check only the public source/metadata catalogs."""
    resources = Path(root) / "resources"
    sources_file = _load_json(resources / "sources.json")
    terms_file = _load_json(resources / "terms.json")
    effects_file = _load_json(resources / "fault_effects.json")
    simulation_truth = _load_json(resources / "simulation_truth.json")
    with (resources / "telemetry_channels.csv").open(encoding="utf-8-sig", newline="") as f:
        channels_rows = list(csv.DictReader(f))
    sources = _index_unique(sources_file["sources"], "source_id", "sources")
    terms = _index_unique(terms_file["terms"], "term_id", "terms")
    effects = _index_unique(effects_file["effects"], "effect_id", "effects")
    channels = _index_unique(channels_rows, "channel_id", "telemetry_channels")
    runs = _index_unique(simulation_truth.get("runs", []), "run_id", "simulation_truth")
    for name, records, property_name in (
        ("terms", terms.values(), "source_ids"),
        ("effects", effects.values(), "source_id"),
        ("channels", channels.values(), "source_id"),
    ):
        for row in records:
            ref = row.get(property_name)
            refs = ref if isinstance(ref, list) else [ref]
            if not refs or any(x not in sources for x in refs):
                raise ValueError(f"{name}: unregistered source ref in {row!r}")
    for effect in effects.values():
        for channel in effect.get("declared_observation_channels", []):
            if channel not in channels:
                raise ValueError(f"effect {effect['effect_id']}: channel {channel} not registered")
    for run in runs.values():
        if run.get("effect_id") not in effects:
            raise ValueError(f"run {run['run_id']}: unknown effect_id")
    return {
        "sources": sources, "terms": terms, "effects": effects, "channels": channels,
        "simulation_truth": simulation_truth, "runs": runs,
        "forbidden_phrases": [item["phrase"] for item in terms_file.get("forbidden_phrases", [])],
    }


def _text_fields(seed: dict[str, Any]) -> list[tuple[str, str]]:
    fields: list[tuple[str, str]] = []
    for path, content in (
        ("instruction", seed.get("instruction")),
        ("answer.summary", (seed.get("answer") or {}).get("summary") if isinstance(seed.get("answer"), dict) else None),
    ):
        if isinstance(content, str):
            fields.append((path, content))
    answer = seed.get("answer")
    if isinstance(answer, dict):
        for i, lim in enumerate(answer.get("limitations", [])):
            if isinstance(lim, str):
                fields.append((f"answer.limitations[{i}]", lim))
    inp = seed.get("input")
    if isinstance(inp, dict):
        if isinstance(inp.get("context"), str):
            fields.append(("input.context", inp["context"]))
        for i, obs in enumerate(inp.get("observations", [])):
            if isinstance(obs, dict) and isinstance(obs.get("note"), str):
                fields.append((f"input.observations[{i}].note", obs["note"]))
    for coll in ("claims", "evidence"):
        for i, item in enumerate(seed.get(coll, [])):
            if isinstance(item, dict):
                key = "text" if coll == "claims" else "statement"
                if isinstance(item.get(key), str):
                    fields.append((f"{coll}[{i}].{key}", item[key]))
    return fields


def _truth_paths(value: object, path: str = "input") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            k = str(key).casefold()
            current = f"{path}.{key}"
            if k in TRUTH_KEYS or k.startswith(("label_", "truth_", "fault_label", "injected_fault")):
                paths.append(current)
            paths.extend(_truth_paths(child, current))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            paths.extend(_truth_paths(child, f"{path}[{i}]"))
    return paths


def _valid_iso_utc(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None
    except ValueError:
        return False


def validate_seed(seed: object, registry: Mapping[str, Any]) -> list[Finding]:
    """Deterministic preflight. It cannot itself establish scientific truth."""
    findings: list[Finding] = []

    def add(code: str, path: str, message: str, severity: str = "BLOCK") -> None:
        findings.append(Finding(code, severity, path, message))

    if not isinstance(seed, dict):
        add("INVALID_SEED_SHAPE", "$", "seed must be an object")
        return findings
    for key in REQUIRED:
        if key not in seed:
            add("REQUIRED_FIELD_MISSING", key, "required field absent")
    if seed.get("schema_version") != "dgsi-seed.v1":
        add("SCHEMA_VERSION_MISMATCH", "schema_version", "expected dgsi-seed.v1")
    if seed.get("domain") != "adcs":
        add("DOMAIN_NOT_ADMITTED", "domain", "v1 pilot supports adcs only")
    for key in ("seed_id", "instruction", "task_type"):
        if not isinstance(seed.get(key), str) or not seed[key].strip():
            add("INVALID_REQUIRED_TEXT", key, "must be a nonempty string")
    for key in ("input", "answer", "review", "provenance"):
        if not isinstance(seed.get(key), dict):
            add("INVALID_SECTION", key, "must be an object")
    for key in ("claims", "evidence", "term_ids"):
        if not isinstance(seed.get(key), list):
            add("INVALID_SECTION", key, "must be an array")
    if any(f.code == "INVALID_SECTION" for f in findings):
        return findings

    inp, answer, review, provenance = (seed.get(key, {}) for key in ("input", "answer", "review", "provenance"))
    term_ids, claims, evidence = (seed.get(key, []) for key in ("term_ids", "claims", "evidence"))
    if inp.get("kind") not in {"HYPOTHETICAL", "TRACE"}:
        add("INPUT_KIND_INVALID", "input.kind", "HYPOTHETICAL or TRACE required")
    for path in _truth_paths(inp):
        add("INPUT_TRUTH_LEAKAGE", path, "label, fault type or simulator truth must not appear in inference input")
    obs = inp.get("observations", [])
    if not isinstance(obs, list):
        add("INVALID_SECTION", "input.observations", "must be an array")
        obs = []
    for i, row in enumerate(obs):
        if not isinstance(row, dict) or row.get("channel_id") not in registry["channels"]:
            add("UNKNOWN_CHANNEL", f"input.observations[{i}].channel_id", "channel must exist in curated public catalog")
    for i, term in enumerate(term_ids):
        if not isinstance(term, str) or term not in registry["terms"]:
            add("UNKNOWN_TERM", f"term_ids[{i}]", "unknown technical term: require terminology curation")
    for path, value in _text_fields(seed):
        for phrase in registry["forbidden_phrases"]:
            if phrase in value:
                add("FORBIDDEN_PHRASE", path, f"known coined/non-domain phrase detected: {phrase}")
        if SELF_ATTESTATION.search(value):
            add("SELF_ATTESTATION", path, "unverified self-certifying language requires rewriting and independent evidence")
        if path == "answer.summary" and CAUSAL_LANGUAGE.search(value):
            causal_claims = [c for c in claims if isinstance(c, dict) and c.get("claim_type") == "CAUSAL" and c.get("causal_review") == "HUMAN_REVIEWED"]
            if not causal_claims:
                add("UNDECLARED_CAUSAL_CONCLUSION", path, "answer uses causal language without a reviewed causal claim")

    evidence_by_id: dict[str, dict[str, Any]] = {}
    for i, item in enumerate(evidence):
        if not isinstance(item, dict) or not isinstance(item.get("evidence_id"), str) or not item["evidence_id"].strip():
            add("INVALID_EVIDENCE", f"evidence[{i}]", "evidence must have a stable nonempty ID")
            continue
        eid = item["evidence_id"]
        if eid in evidence_by_id:
            add("DUPLICATE_EVIDENCE", f"evidence[{i}].evidence_id", "duplicate evidence ID")
        evidence_by_id[eid] = item
        if item.get("source_id") not in registry["sources"]:
            add("UNKNOWN_SOURCE", f"evidence[{i}].source_id", "source must be registered")
        channel = item.get("channel_id")
        if channel is not None and channel not in registry["channels"]:
            add("UNKNOWN_CHANNEL", f"evidence[{i}].channel_id", "unknown telemetry channel")
        if item.get("origin") not in {"HYPOTHETICAL", "MEASURED", "DOCUMENT_EXCERPT"}:
            add("UNKNOWN_EVIDENCE_ORIGIN", f"evidence[{i}].origin", "origin must be explicit")
        if item.get("origin") == "MEASURED" and inp.get("kind") != "TRACE":
            add("MEASUREMENT_ORIGIN_MISMATCH", f"evidence[{i}].origin", "a hypothetical prompt cannot claim measured evidence")
        if item.get("origin") == "DOCUMENT_EXCERPT":
            if not item.get("locator"):
                add("SOURCE_LOCATOR_MISSING", f"evidence[{i}].locator", "document evidence requires a section/page locator")
            source = registry["sources"].get(item.get("source_id"), {})
            if source.get("kind") not in {"OFFICIAL_DOMAIN_REFERENCE", "RESEARCH_PAPER", "USER_LIBRARY_REFERENCE", "SIMULATOR_DOCUMENTATION", "RESEARCH_DATASET_REFERENCE"}:
                add("DOCUMENT_SOURCE_NOT_ADMITTED", f"evidence[{i}].source_id", "catalog/interface metadata is not document evidence")
    claim_ids: set[str] = set()
    for i, claim in enumerate(claims):
        path = f"claims[{i}]"
        if not isinstance(claim, dict):
            add("INVALID_CLAIM", path, "claim must be an object")
            continue
        cid = claim.get("claim_id")
        if not isinstance(cid, str) or not cid or cid in claim_ids:
            add("INVALID_CLAIM_ID", f"{path}.claim_id", "claim ID must be unique and nonempty")
        claim_ids.add(cid)
        kind = claim.get("claim_type")
        if kind not in CLAIM_TYPES:
            add("UNKNOWN_CLAIM_TYPE", f"{path}.claim_type", "claim type must be structured")
        refs = claim.get("evidence_ids", [])
        if not isinstance(refs, list):
            add("INVALID_CLAIM_EVIDENCE", f"{path}.evidence_ids", "must be a list")
            refs = []
        for eid in refs:
            if eid not in evidence_by_id:
                add("UNKNOWN_EVIDENCE", f"{path}.evidence_ids", f"reference {eid!r} does not exist")
        sources = claim.get("source_ids", [])
        if not isinstance(sources, list):
            add("INVALID_CLAIM_SOURCE", f"{path}.source_ids", "must be a list")
            sources = []
        for source_id in sources:
            if source_id not in registry["sources"]:
                add("UNKNOWN_SOURCE", f"{path}.source_ids", f"source {source_id!r} not registered")
        has_mechanism_source = any(
            "MECHANISM" in registry["sources"][sid].get("scopes", [])
            for sid in sources if sid in registry["sources"]
        )
        if kind in {"MECHANISM", "CAUSAL"} and not has_mechanism_source:
            add("CAUSAL_SOURCE_NOT_ADMITTED" if kind == "CAUSAL" else "MECHANISM_SOURCE_NOT_ADMITTED",
                f"{path}.source_ids", "physical/causal claim needs an approved-scope domain reference")
        if kind in {"MECHANISM", "CAUSAL"}:
            locators = claim.get("source_locators")
            if not isinstance(locators, dict) or not any(isinstance(locators.get(sid), str) and locators[sid].strip() for sid in sources):
                add("CLAIM_SOURCE_LOCATOR_MISSING", f"{path}.source_locators", "mechanism/causal claim requires precise source section or page")
        if kind == "CAUSAL":
            if claim.get("causal_review") != "HUMAN_REVIEWED":
                add("UNREVIEWED_CAUSAL_CLAIM", f"{path}.causal_review", "causal relation requires an explicit human-reviewed record")
            groups = {evidence_by_id[eid].get("independence_group") for eid in refs if eid in evidence_by_id and evidence_by_id[eid].get("independence_group")}
            if len(groups) < 2:
                add("CAUSAL_NEEDS_INDEPENDENT_EVIDENCE", f"{path}.evidence_ids", "at least two genuinely independent evidence groups must be reviewed")
        if kind != "CAUSAL" and CAUSAL_LANGUAGE.search(str(claim.get("text", ""))):
            add("CAUSAL_LANGUAGE_MISMATCH", f"{path}.text", "causal certainty expressed as non-causal claim")

    if answer.get("status") not in DIAGNOSIS_STATUSES:
        add("UNKNOWN_DIAGNOSIS_STATUS", "answer.status", "use the declared diagnosis status taxonomy")
    if not isinstance(answer.get("summary"), str) or not answer["summary"].strip():
        add("INVALID_ANSWER_SUMMARY", "answer.summary", "nonempty answer required")
    answer_refs = answer.get("evidence_ids", [])
    if not isinstance(answer_refs, list):
        add("INVALID_ANSWER_EVIDENCE", "answer.evidence_ids", "must be a list")
    else:
        for eid in answer_refs:
            if eid not in evidence_by_id:
                add("UNKNOWN_EVIDENCE", "answer.evidence_ids", "answer cites unregistered evidence")
    status = answer.get("status")
    if status in {"DIAGNOSED", "NORMAL"}:
        effect_id = answer.get("effect_id")
        if status == "DIAGNOSED" and (effect_id not in registry["effects"] or registry["effects"].get(effect_id, {}).get("effect_kind") != "FAULT"):
            add("UNKNOWN_DIAGNOSTIC_EFFECT", "answer.effect_id", "a diagnosis must refer to a registered fault effect")
        run = registry["runs"].get(provenance.get("run_id"))
        if status == "DIAGNOSED" and run is not None and run.get("effect_id") != effect_id:
            add("RUN_EFFECT_MISMATCH", "answer.effect_id", "claimed fault differs from admitted run's registered effect")
        if inp.get("kind") != "TRACE" or run is None or not all(
            run.get(key) is True for key in ("trace_verified", "event_window_reviewed", "physical_effect_verified", "split_admitted")
        ):
            add("DIAGNOSIS_NEEDS_ADMITTED_RUN", "provenance.run_id", "no verified run receipt with reviewed event/window and dataset admission")
        if not any(isinstance(e, dict) and e.get("origin") == "MEASURED" for e in evidence):
            add("DIAGNOSIS_NEEDS_MEASURED_EVIDENCE", "evidence", "definitive result needs measured evidence")
    elif status in {"UNKNOWN_FAULT", "INSUFFICIENT_EVIDENCE", "AMBIGUOUS", "CONFLICTING_EVIDENCE", "DATA_ERROR"}:
        if answer.get("effect_id") is not None:
            add("UNSAFE_CONCLUSION", "answer.effect_id", "non-definitive status must not assert a single fault source")

    if provenance.get("truth_in_prompt") is not False:
        add("TRUTH_PROMPT_FLAG", "provenance.truth_in_prompt", "training input must be truth-free")
    if provenance.get("trace_used") is True and inp.get("kind") != "TRACE":
        add("TRACE_PROVENANCE_MISMATCH", "provenance.trace_used", "trace_used conflicts with hypothetical input")
    if review.get("status") not in REVIEW_STATES:
        add("INVALID_REVIEW_STATUS", "review.status", "must use a declared review status")
    if review.get("status") == "HUMAN_REVIEWED":
        if not (
            review.get("review_mode") == "HUMAN"
            and isinstance(review.get("reviewer_id"), str) and review["reviewer_id"].strip()
            and _valid_iso_utc(review.get("reviewed_at"))
            and review.get("decision") == "APPROVE"
        ):
            add("GOLD_REVIEW_RECEIPT_MISSING", "review", "human approval metadata required; machine review never upgrades a seed")
    return findings


def report(seed: object, registry: Mapping[str, Any]) -> dict[str, Any]:
    findings = validate_seed(seed, registry)
    blocked = any(f.severity == "BLOCK" for f in findings)
    review_status = seed.get("review", {}).get("status") if isinstance(seed, dict) and isinstance(seed.get("review"), dict) else None
    gold_eligible = not blocked and review_status == "HUMAN_REVIEWED"
    if blocked:
        decision = "BLOCKED"
    elif gold_eligible:
        decision = "GOLD_METADATA_ELIGIBLE_MANUAL_AUTHENTICATION_REQUIRED"
    elif review_status == "REJECTED":
        decision = "REJECTED"
    else:
        decision = "CANDIDATE_CHECKS_PASSED"
    return {
        "seed_id": seed.get("seed_id") if isinstance(seed, dict) else None,
        "decision": decision,
        "gold_eligible": gold_eligible,
        "gold_identity_authenticated": False,
        "findings": [asdict(item) for item in findings],
        "claim_boundary": "Deterministic metadata checks only; no factual correctness, causal proof, observed trace verification or human identity authentication is implied.",
    }
