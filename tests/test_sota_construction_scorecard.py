from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dgsi.sota_construction_scorecard import ARMS, DIMENSIONS, ScorecardError, scorecard_file, summarize_construction_trials


def trial(arm="M0", group="G1", track="LITERATURE_DERIVED_SYNTHETIC", status="PENDING"):
    item = {
        "trial_id": f"{arm}-{group}", "source_group": group, "event_family": group,
        "arm": arm, "track": track, "attempts": 1, "accepted_candidates": 1,
        "generation_tokens": 900, "token_budget": 1000,
        "critical_failures": [], "review_status": status,
        "reviewer_tokens": [], "scores": {},
    }
    if status == "ADJUDICATED":
        item.update(reviewer_tokens=["R1", "R2"], scores={d: 2 for d in DIMENSIONS}, review_receipt_sha256="a" * 64)
    return item


def doc(rows):
    return {"schema_version": "dgsi-sota-construction-scorecard.v1", "purpose": "CONSTRUCTION_ONLY", "trials": rows}


class ScorecardTests(unittest.TestCase):
    def reject(self, code, document):
        with self.assertRaisesRegex(ScorecardError, "^" + code + "$"):
            summarize_construction_trials(document)

    def test_empty_returns_not_run(self):
        r = summarize_construction_trials(doc([]))
        self.assertEqual(r["comparison_status"], "NOT_COMPARABLE_OR_NOT_RUN")
        self.assertEqual(r["arms"]["M4"]["status"], "NOT_RUN")
        self.assertFalse(r["training_authorized"])

    def test_five_arms_matched_but_not_human_reviewed(self):
        r = summarize_construction_trials(doc([trial(a) for a in ARMS]))
        self.assertTrue(r["source_group_budget_matched"])
        self.assertEqual(r["comparison_status"], "MATCHED_UNREVIEWED")
        self.assertIsNone(r["arms"]["M4"]["reviewer_reported_dimension_means"])

    def test_valid_adjudicated_inputs_never_authorize_sft(self):
        r = summarize_construction_trials(doc([trial(a, status="ADJUDICATED") for a in ARMS]))
        self.assertEqual(r["comparison_status"], "REVIEWED_COMPARABLE_INPUT")
        self.assertEqual(r["arms"]["M0"]["reviewer_reported_dimension_means"]["source_fidelity"], 2)
        self.assertEqual(r["downstream_sft_result"], "NOT_RUN")
        self.assertFalse(r["gold_authorized"])

    def test_partial_source_and_token_budget_cannot_claim_comparison(self):
        rows = [trial(a) for a in ARMS]
        rows[-1]["source_group"] = "OTHER"
        self.assertFalse(summarize_construction_trials(doc(rows))["source_group_budget_matched"])
        rows = [trial(a) for a in ARMS]
        rows[-1]["token_budget"] = 999
        self.assertFalse(summarize_construction_trials(doc(rows))["source_group_budget_matched"])

    def test_reject_duplicate_and_cross_track_identity(self):
        self.reject("SOTA_DUPLICATE_TRIAL", doc([trial(), trial()]))
        real = trial("M1", track="REAL_GOLD")
        real["gold_admitted"] = True
        self.reject("SOTA_SOURCE_TRACK_COLLISION", doc([trial(), real]))

    def test_real_gold_must_be_explicitly_admitted(self):
        self.reject("SOTA_REAL_GOLD_NOT_ADMITTED", doc([trial(track="REAL_GOLD")]))

    def test_critical_failures_cannot_be_accepted(self):
        r = trial()
        r["critical_failures"] = ["FABRICATED_ML_OR_LOG"]
        self.reject("SOTA_CRITICAL_CANDIDATE_ACCEPTED", doc([r]))

    def test_no_fake_independent_reviews_or_partial_rubric(self):
        r = trial(status="ADJUDICATED")
        r["reviewer_tokens"] = ["R1", "R1"]
        self.reject("SOTA_REVIEWERS_NOT_INDEPENDENT", doc([r]))
        r = trial(status="ADJUDICATED")
        del r["scores"][DIMENSIONS[0]]
        self.reject("SOTA_SCORE_DIMENSIONS", doc([r]))

    def test_no_pending_scores(self):
        r = trial()
        r["scores"] = {"source_fidelity": 2}
        self.reject("SOTA_PENDING_HAS_SCORES", doc([r]))

    def test_aggregate_does_not_disclose_reviewers_or_trial_ids(self):
        r = summarize_construction_trials(doc([trial(a, status="ADJUDICATED") for a in ARMS]))
        s = json.dumps(r)
        self.assertNotIn("R1", s)
        self.assertNotIn("M0-G1", s)

    def test_io_no_clobber(self):
        with tempfile.TemporaryDirectory() as temp:
            inp = Path(temp) / "in.json"
            out = Path(temp) / "out.json"
            inp.write_text(json.dumps(doc([trial("M4")])), encoding="utf-8")
            scorecard_file(inp, out)
            self.assertEqual(json.loads(out.read_text())["arms"]["M4"]["status"], "REVIEW_PENDING")
            with self.assertRaisesRegex(ScorecardError, "SOTA_OUTPUT_EXISTS"):
                scorecard_file(inp, out)
            with self.assertRaisesRegex(ScorecardError, "SOTA_NO_INPUT_OVERWRITE"):
                scorecard_file(inp, inp)


if __name__ == "__main__":
    unittest.main()
