"""DEV_ONLY exact-marker guard for current-event L0 answers in retrieved history.

Reviewer-identified leaked phrases belong to a coordinator-only ledger, never
the model-visible input. This is a targeted check, NOT semantic certification,
a scientific adjudication, or permission to export training data.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile


class HistorySourceBoundaryError(ValueError):
    """Emit fixed codes only, not potentially sensitive source text."""


def _fail(code: str) -> None:
    raise HistorySourceBoundaryError(code)


def audit_history_source_boundary(archive: str | Path) -> dict:
    """Reject current-event source-answer clues inside historical_cases."""
    with ZipFile(archive) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or len(names) > 256 or any(
            n.startswith("/") or "\\" in n or ".." in n.split("/") for n in names
        ):
            _fail("SOURCE_BOUNDARY_INVALID_ARCHIVE")
        required = {
            "coordinator_ONLY_pairing_manifest.json",
            "coordinator_ONLY_current_source_sanitization.json",
        }
        if not required.issubset(names):
            _fail("SOURCE_BOUNDARY_LEDGER_MISSING")

        def read_json(name):
            if name not in names or z.getinfo(name).file_size > 1_000_000:
                _fail("SOURCE_BOUNDARY_INVALID_MEMBER")
            try:
                return json.loads(z.read(name))
            except (ValueError, UnicodeError):
                _fail("SOURCE_BOUNDARY_INVALID_MEMBER")

        manifest = read_json("coordinator_ONLY_pairing_manifest.json")
        ledger = read_json("coordinator_ONLY_current_source_sanitization.json")
        if (not isinstance(manifest, dict) or not isinstance(ledger, dict)
                or ledger.get("not_for_sft") is not True
                or ledger.get("coordinator_only") is not True
                or ledger.get("review_state") != "PENDING_INDEPENDENT_REVIEW"
                or manifest.get("training_authorized") is not False
                or manifest.get("expert_review_complete") is not False
                or manifest.get("source_rights_verified") is not False):
            _fail("SOURCE_BOUNDARY_RELEASE_OR_REVIEW_GUARD")

        entries, pairs = ledger.get("redactions"), manifest.get("pairs")
        if not isinstance(entries, list) or not isinstance(pairs, list):
            _fail("SOURCE_BOUNDARY_LEDGER_INVALID")
        redactions = {}
        for e in entries:
            if not isinstance(e, dict) or not isinstance(e.get("task_id"), str):
                _fail("SOURCE_BOUNDARY_LEDGER_INVALID")
            if e["task_id"] in redactions:
                _fail("SOURCE_BOUNDARY_LEDGER_INVALID")
            terms = e.get("forbidden_current_source_substrings")
            source = e.get("source_field_utf8")
            replacement = e.get("replacement_field_utf8")
            if (not isinstance(terms, list) or not terms
                    or any(not isinstance(t, str) or len(t) < 8 for t in terms)
                    or len(set(terms)) != len(terms)
                    or e.get("field_path") !=
                    "input.historical_cases[*].applicability_limitations"
                    or not isinstance(source, str)
                    or e.get("source_field_sha256") !=
                    sha256(source.encode("utf-8")).hexdigest()
                    or not isinstance(replacement, str) or not replacement):
                _fail("SOURCE_BOUNDARY_LEDGER_INVALID")
            if not all(t in source for t in terms):
                _fail("SOURCE_BOUNDARY_NOT_AN_ACTUAL_REDACTION")
            if any(t in replacement for t in terms):
                _fail("SOURCE_BOUNDARY_RESIDUAL_HINT")
            redactions[e["task_id"]] = e
        if not redactions:
            _fail("SOURCE_BOUNDARY_LEDGER_INVALID")

        matched = set()
        for pair in pairs:
            if not isinstance(pair, dict):
                _fail("SOURCE_BOUNDARY_LEDGER_INVALID")
            task = pair.get("task_id")
            if not isinstance(task, str) or "/" in task or "\\" in task:
                _fail("SOURCE_BOUNDARY_LEDGER_INVALID")
            if task not in redactions:
                continue
            entry = redactions[task]
            side = "A" if pair.get("arm_A") == "HISTORY" else "B"
            if pair.get("arm_" + side) != "HISTORY":
                _fail("SOURCE_BOUNDARY_ARM_INVALID")
            record = read_json(f"model_visible_inputs/{task}/arm_{side}.json")
            priors = record.get("input", {}).get("historical_cases", [])
            matches = [
                prior for prior in priors
                if prior.get("case_ref") == entry.get("history_case_ref")
            ]
            if len(matches) != 1:
                _fail("SOURCE_BOUNDARY_PRIOR_BINDING_INVALID")
            limitations = matches[0].get("applicability_limitations")
            if (not isinstance(limitations, list)
                    or entry["replacement_field_utf8"] not in limitations):
                _fail("SOURCE_BOUNDARY_REPLACEMENT_MISMATCH")
            history_text = json.dumps(priors, ensure_ascii=False)
            if any(t in history_text for t in
                   entry["forbidden_current_source_substrings"]):
                _fail("SOURCE_BOUNDARY_RESIDUAL_HINT")
            matched.add(task)
        if matched != set(redactions):
            _fail("SOURCE_BOUNDARY_UNBOUND_REDACTION")
        return {
            "decision": "DEV_ONLY_NOT_RELEASED",
            "audited_redactions": len(matched),
            "historical_context_source_answer_sidechannel":
                "REVIEWER_IDENTIFIED_SUBSTRINGS_BLOCKED",
            "semantic_completeness": "NOT_CERTIFIED",
            "expert_review_complete": False,
            "source_rights_verified": False,
            "training_authorized": False,
            "model_scoring": "NOT_RUN",
        }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Audit DEV_ONLY history source hints")
    p.add_argument("archive", type=Path)
    print(json.dumps(audit_history_source_boundary(p.parse_args().archive),
                     indent=2, ensure_ascii=False))
