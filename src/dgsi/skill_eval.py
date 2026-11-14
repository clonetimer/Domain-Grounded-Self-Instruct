"""Opt-in, stateless OpenAI Responses API runner for blinded Skill evaluation.

No network calls occur at import time. Live execution requires an explicit CLI flag,
a local API key, distinct generator/judge model IDs, and a declared independence note.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


API_URL = "https://api.openai.com/v1/responses"
SCORE_FIELDS = (
    "terminology",
    "evidence_traceability",
    "causal_calibration",
    "self_attestation_control",
    "truth_leakage_control",
    "abstention",
)

CANDIDATE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "instruction": {"type": "string"},
        "input": {"type": "string"},
        "answer": {"type": "string"},
        "diagnostic_status": {
            "type": "string",
            "enum": ["NORMAL", "DIAGNOSED", "AMBIGUOUS", "INSUFFICIENT_EVIDENCE", "UNKNOWN_FAULT"],
        },
        "fault_source_component": {"type": ["string", "null"]},
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim_type": {"type": "string", "enum": ["OBSERVATION", "MECHANISM", "CAUSAL", "UNCERTAINTY"]},
                    "text": {"type": "string"},
                    "source_passage_ids": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["claim_type", "text", "source_passage_ids"],
                "additionalProperties": False,
            },
        },
        "term_mentions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "surface": {"type": "string"},
                    "term_id": {"type": "string"},
                    "relation": {"type": "string", "enum": ["PREFERRED", "EXACT_ALIAS", "CONTEXTUAL_ALIAS", "RELATED_TERM", "UNREGISTERED"]},
                },
                "required": ["surface", "term_id", "relation"],
                "additionalProperties": False,
            },
        },
        "uncertainty": {"type": "string"},
    },
    "required": [
        "instruction", "input", "answer", "diagnostic_status",
        "fault_source_component", "claims", "term_mentions", "uncertainty",
    ],
    "additionalProperties": False,
}

JUDGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "candidate_a": {
            "type": "object",
            "properties": {
                **{field: {"type": "integer", "minimum": 0, "maximum": 2} for field in SCORE_FIELDS},
                "critical_failures": {"type": "array", "items": {"type": "string"}},
            },
            "required": [*SCORE_FIELDS, "critical_failures"],
            "additionalProperties": False,
        },
        "candidate_b": {
            "type": "object",
            "properties": {
                **{field: {"type": "integer", "minimum": 0, "maximum": 2} for field in SCORE_FIELDS},
                "critical_failures": {"type": "array", "items": {"type": "string"}},
            },
            "required": [*SCORE_FIELDS, "critical_failures"],
            "additionalProperties": False,
        },
        "preferred_candidate": {"type": "string", "enum": ["A", "B", "TIE"]},
        "rationale": {"type": "string"},
    },
    "required": ["candidate_a", "candidate_b", "preferred_candidate", "rationale"],
    "additionalProperties": False,
}

BASELINE_SYSTEM = (
    "Create one candidate instruction-data seed for the supplied spacecraft ADCS task. "
    "Follow the task prompt and the required output schema. Return only the requested JSON object."
)

JUDGE_SYSTEM = (
    "You are an independent blind evaluator of two candidate ADCS instruction-data seeds. "
    "The candidates are randomly ordered and their production conditions are hidden. "
    "Score each candidate from 0 to 2 on every rubric dimension. Use the supplied expected "
    "behaviors and source context. Do not reward verbosity. Flag any unsupported definitive "
    "fault-source or causal claim as a critical failure. Return only the requested JSON schema."
)

RUBRIC = {
    "terminology": "0 invented/wrong term; 1 ambiguous or alias scope lost; 2 registered term and alias class used correctly.",
    "evidence_traceability": "0 fabricated/absent support; 1 source name only or weak locator; 2 valid registered passage ID and correct boundary.",
    "causal_calibration": "0 unsupported cause asserted; 1 hedged but still overstates; 2 separates observation, mechanism, affected component and fault source.",
    "self_attestation_control": "0 accepts unsupported self-certification; 1 flags wording only; 2 requires independent evidence and review receipt.",
    "truth_leakage_control": "0 uses hidden labels; 1 notices but continues; 2 excludes or quarantines contaminated input.",
    "abstention": "0 fabricates diagnosis; 1 vague uncertainty; 2 correct non-diagnosis with concrete evidence gaps.",
}


def validate_live_config(
    generator_model: str,
    judge_model: str,
    generator_family: str,
    judge_family: str,
    api_key: str,
    independence_note: str = "",
) -> None:
    if not generator_model.strip() or not judge_model.strip():
        raise ValueError("DGSI_GENERATOR_MODEL and DGSI_JUDGE_MODEL are required")
    if generator_model.strip() == judge_model.strip():
        raise ValueError("generator and judge model IDs must be different")
    if not generator_family.strip() or not judge_family.strip():
        raise ValueError("DGSI_GENERATOR_FAMILY and DGSI_JUDGE_FAMILY are required")
    if generator_family.strip().casefold() == judge_family.strip().casefold():
        raise ValueError("generator and judge model families must be different")
    if not api_key.strip():
        raise ValueError("OPENAI_API_KEY is required for live evaluation")
    if not independence_note.strip():
        raise ValueError("DGSI_JUDGE_INDEPENDENCE_NOTE must describe the independent judge setup")


def build_response_request(
    *,
    model: str,
    system_prompt: str,
    user_prompt: str,
    api_key: str,
    schema_name: str,
    schema: Mapping[str, Any],
    max_output_tokens: int = 2048,
) -> urllib.request.Request:
    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": schema_name,
                "strict": True,
                "schema": dict(schema),
            }
        },
        "max_output_tokens": max_output_tokens,
        "store": False,
    }
    return urllib.request.Request(
        API_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )


def extract_output_text(response: Mapping[str, Any]) -> str:
    status = response.get("status")
    if status != "completed":
        raise ValueError(f"OpenAI response is incomplete or failed: {status!r}")
    chunks: list[str] = []
    for item in response.get("output", []):
        if item.get("type") != "message":
            continue
        for part in item.get("content", []):
            if part.get("type") == "refusal":
                raise ValueError("OpenAI refused an evaluation prompt")
            if part.get("type") == "output_text" and isinstance(part.get("text"), str):
                chunks.append(part["text"])
    if not chunks:
        raise ValueError("OpenAI response contains no output_text")
    return "".join(chunks)


def blind_pair(seed: int, case_id: str, baseline: Any, treatment: Any) -> dict[str, Any]:
    digest = hashlib.sha256(f"{seed}:{case_id}".encode("utf-8")).digest()
    order = ["baseline", "treatment"] if digest[0] % 2 == 0 else ["treatment", "baseline"]
    values = {"baseline": baseline, "treatment": treatment}
    return {
        "order": order,
        "candidates": {"A": values[order[0]], "B": values[order[1]]},
    }


def map_blind_scores(judged: Mapping[str, Any], pair: Mapping[str, Any]) -> dict[str, Any]:
    order = pair["order"]
    if order == ["baseline", "treatment"]:
        return {"baseline": judged["candidate_a"], "treatment": judged["candidate_b"]}
    if order == ["treatment", "baseline"]:
        return {"treatment": judged["candidate_a"], "baseline": judged["candidate_b"]}
    raise ValueError(f"invalid blind order: {order!r}")


def _call_openai(
    *,
    model: str,
    system_prompt: str,
    user_prompt: str,
    api_key: str,
    schema_name: str,
    schema: Mapping[str, Any],
) -> dict[str, Any]:
    request = build_response_request(
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        api_key=api_key,
        schema_name=schema_name,
        schema=schema,
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1200]
        raise RuntimeError(f"OpenAI Responses API HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"OpenAI Responses API connection failed: {exc.reason}") from exc
    text = extract_output_text(payload)
    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"OpenAI returned invalid JSON for {schema_name}") from exc
    if not isinstance(result, dict):
        raise ValueError(f"OpenAI returned a non-object for {schema_name}")
    return result


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _case_context(root: Path, case: Mapping[str, Any]) -> dict[str, Any]:
    passages = _load_json(root / "resources" / "source_passages.json")
    terms = _load_json(root / "resources" / "terms.json")
    passage_index = {item["passage_id"]: item for item in passages["passages"]}
    term_index = {item["term_id"]: item for item in terms["terms"]}
    selected_passages = []
    for passage_id in case["source_passage_ids"]:
        if passage_id not in passage_index:
            raise ValueError(f"{case['case_id']}: unknown source passage {passage_id}")
        item = passage_index[passage_id]
        selected_passages.append({
            "passage_id": item["passage_id"],
            "source_id": item["source_id"],
            "locator": item["locator"],
            "allowed_claim_types": item["allowed_claim_types"],
            "claim_boundary": item["claim_boundary"],
        })
    selected_terms = []
    for term_id in case["term_ids"]:
        if term_id not in term_index:
            raise ValueError(f"{case['case_id']}: unknown term ID {term_id}")
        item = term_index[term_id]
        selected_terms.append({
            "term_id": item["term_id"],
            "preferred_zh": item["preferred_zh"],
            "preferred_en": item["preferred_en"],
            "definition_zh": item["definition_zh"],
            "aliases": item.get("aliases", []),
            "related_terms": item.get("related_terms", []),
        })
    return {"source_passages": selected_passages, "terms": selected_terms}


def _api_call_for_json(
    *,
    model: str,
    system_prompt: str,
    user_prompt: str,
    api_key: str,
    schema_name: str,
    schema: Mapping[str, Any],
) -> dict[str, Any]:
    return _call_openai(
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        api_key=api_key,
        schema_name=schema_name,
        schema=schema,
    )



def validate_output_path(root: Path, output_path: Path) -> Path:
    """Keep generated candidate text outside public source paths."""
    root_resolved = root.resolve()
    output_resolved = output_path.expanduser().resolve()
    try:
        relative = output_resolved.relative_to(root_resolved)
    except ValueError:
        return output_resolved
    if relative.parts[:2] != ("reports", "skill_blind_eval"):
        raise ValueError("live output must be outside the repository or under reports/skill_blind_eval")
    return output_resolved


def run_live_evaluation(
    *,
    root: Path,
    output_path: Path,
    generator_model: str,
    judge_model: str,
    generator_family: str,
    judge_family: str,
    api_key: str,
    independence_note: str,
    seed: int = 20261114,
    limit: int = 10,
) -> dict[str, Any]:
    validate_live_config(generator_model, judge_model, generator_family, judge_family, api_key, independence_note)
    if limit <= 0:
        raise ValueError("limit must be positive")
    output_path = validate_output_path(root, output_path)
    cases_file = root / "resources" / "skill_pressure_cases.json"
    passages_file = root / "resources" / "source_passages.json"
    terms_file = root / "resources" / "terms.json"
    cases_payload = _load_json(cases_file)
    cases = cases_payload["cases"][:limit]
    skill_text = (root / "skills" / "adcs-gold-seed-curation" / "SKILL.md").read_text(encoding="utf-8")
    skill_sha = hashlib.sha256(skill_text.encode("utf-8")).hexdigest()
    cases_sha = hashlib.sha256(cases_file.read_bytes()).hexdigest()

    metadata = {
        "record_type": "run_metadata",
        "schema_version": "dgsi-skill-blind-eval-run.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "generator_model": generator_model,
        "judge_model": judge_model,
        "generator_family": generator_family,
        "judge_family": judge_family,
        "judge_independence_note": independence_note,
        "seed": seed,
        "case_count": len(cases),
        "expected_api_calls": len(cases) * 3,
        "skill_sha256": skill_sha,
        "cases_sha256": cases_sha,
        "source_passages_sha256": hashlib.sha256(passages_file.read_bytes()).hexdigest(),
        "terms_sha256": hashlib.sha256(terms_file.read_bytes()).hexdigest(),
        "responses_store": False,
        "run_status": "IN_PROGRESS",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(metadata, ensure_ascii=False) + "\n")
    try:
        os.chmod(output_path, 0o600)
    except OSError:
        pass
    records: list[dict[str, Any]] = []
    for case in cases:
        context = _case_context(root, case)
        generator_prompt = json.dumps(
            {"task": case["task_prompt"], "registered_context": context},
            ensure_ascii=False,
            sort_keys=True,
        )
        baseline = _api_call_for_json(
            model=generator_model,
            system_prompt=BASELINE_SYSTEM,
            user_prompt=generator_prompt,
            api_key=api_key,
            schema_name="adcs_seed_candidate",
            schema=CANDIDATE_SCHEMA,
        )
        treatment = _api_call_for_json(
            model=generator_model,
            system_prompt=BASELINE_SYSTEM + "\n\nApply this additional domain-grounding Skill:\n" + skill_text,
            user_prompt=generator_prompt,
            api_key=api_key,
            schema_name="adcs_seed_candidate",
            schema=CANDIDATE_SCHEMA,
        )
        pair = blind_pair(seed, case["case_id"], baseline, treatment)
        judge_prompt = json.dumps(
            {
                "case_id": case["case_id"],
                "task": case["task_prompt"],
                "registered_context": context,
                "expected_behaviors": case["expected_behaviors"],
                "rubric": RUBRIC,
                "candidate_A": pair["candidates"]["A"],
                "candidate_B": pair["candidates"]["B"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        judged = _api_call_for_json(
            model=judge_model,
            system_prompt=JUDGE_SYSTEM,
            user_prompt=judge_prompt,
            api_key=api_key,
            schema_name="blind_candidate_scores",
            schema=JUDGE_SCHEMA,
        )
        mapped = map_blind_scores(judged, pair)
        record = {
            "record_type": "case_result",
            "case_id": case["case_id"],
            "blind_order": pair["order"],
            "candidate_A": pair["candidates"]["A"],
            "candidate_B": pair["candidates"]["B"],
            "judge_result_blind": judged,
            "scores_by_condition": mapped,
            "preferred_condition": (
                "baseline" if judged["preferred_candidate"] == "A" and pair["order"][0] == "baseline"
                else "treatment" if judged["preferred_candidate"] == "A" and pair["order"][0] == "treatment"
                else "baseline" if judged["preferred_candidate"] == "B" and pair["order"][1] == "baseline"
                else "treatment" if judged["preferred_candidate"] == "B" and pair["order"][1] == "treatment"
                else "TIE"
            ),
        }
        records.append(record)
        with output_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")

    summary: dict[str, Any] = {
        "case_count": len(records),
        "conditions": {},
        "paired_mean_delta": {},
        "preferred_condition_counts": {"baseline": 0, "treatment": 0, "TIE": 0},
    }
    for condition in ("baseline", "treatment"):
        totals = {field: 0 for field in SCORE_FIELDS}
        failures = 0
        for record in records:
            score = record["scores_by_condition"][condition]
            for field in SCORE_FIELDS:
                totals[field] += score[field]
            failures += len(score["critical_failures"])
        summary["conditions"][condition] = {
            "mean_scores": {field: round(totals[field] / max(len(records), 1), 3) for field in SCORE_FIELDS},
            "critical_failure_count": failures,
        }
    for field in SCORE_FIELDS:
        delta = sum(
            record["scores_by_condition"]["treatment"][field] - record["scores_by_condition"]["baseline"][field]
            for record in records
        )
        summary["paired_mean_delta"][field] = round(delta / max(len(records), 1), 3)
    for record in records:
        preferred = record["preferred_condition"]
        summary["preferred_condition_counts"][preferred] += 1
    summary_record = {"record_type": "run_summary", "run_status": "COMPLETED", "summary": summary}
    with output_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(summary_record, ensure_ascii=False) + "\n")
    metadata["run_status"] = "COMPLETED"
    return {"metadata": metadata, "summary": summary, "output_path": str(output_path)}


__all__ = [
    "API_URL", "CANDIDATE_SCHEMA", "JUDGE_SCHEMA", "SCORE_FIELDS",
    "build_response_request", "extract_output_text", "blind_pair",
    "map_blind_scores", "validate_live_config", "validate_output_path", "run_live_evaluation",
]
