"""SYNTHETIC_TEST_ONLY: source-bound review dossier must never be SFT output."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from dgsi.l1_c2_scientific_dossier import build_c2_scientific_dossier
from dgsi.l1_c2_expert_handoff import build_c2_expert_handoff

ROOT = Path(__file__).resolve().parents[1]
COLLECTION_PATH = ROOT / "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"
SOURCE_PATH = ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"
CLI = ROOT / "scripts/create_l1_c2_scientific_dossier.py"
COLLECTION = json.loads(COLLECTION_PATH.read_text(encoding="utf-8"))
SOURCES = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))["cards"]


class C2ScientificDossierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dossier = build_c2_scientific_dossier(
            COLLECTION, source_fact_cards=SOURCES
        )

    def test_15_real_candidate_tasks_match_blank_scorecard_hashes(self):
        handoff = build_c2_expert_handoff(
            COLLECTION, source_fact_cards=SOURCES, reviewer_slot="A"
        )
        dossier = self.dossier
        self.assertEqual(dossier["packet_count"], 15)
        self.assertEqual(dossier["event_family_count"], 9)
        self.assertEqual(dossier["collection_projection_sha256"],
                         handoff["collection_projection_sha256"])
        forms = {t["task_id"]: t for t in handoff["tasks"]}
        self.assertEqual(len(dossier["items"]), len(forms))
        for item in dossier["items"]:
            form = forms[item["task_id"]]
            self.assertEqual(item["packet_sha256"], form["packet_sha256"])
            self.assertEqual(item["source_public_sha256"], form["source_public_sha256"])

    def test_l0_current_and_historical_sources_are_present_but_internal_excluded(self):
        originals = {p["task_id"]: p for p in COLLECTION["packets"]}
        for item in self.dossier["items"]:
            refs = {f["case_id"] for f in item["l0_public_source_context"]}
            bindings = {b["source_fact_ref"] for b in item["source_fact_bindings"]}
            self.assertEqual(refs, bindings)
            self.assertTrue(set(originals[item["task_id"]]["source_fact_refs"]) <= refs)
            for fact in item["l0_public_source_context"]:
                self.assertIn("source_reference", fact)
                self.assertIn("domain_review_status", fact)
                self.assertIn("domain_review_evidence_sha256", fact)
                self.assertIn("sft_eligible", fact)
                self.assertEqual(
                    fact["domain_review_status"],
                    next(c["domain_review_status"] for c in SOURCES
                         if c["case_id"] == fact["case_id"]),
                )
                self.assertNotIn("internal_review", fact)

    def test_bound_l0_review_status_counts_do_not_imply_approval(self):
        dossier = self.dossier
        all_bound_ids = {
            fact["case_id"]
            for item in dossier["items"]
            for fact in item["l0_public_source_context"]
        }
        self.assertEqual(dossier["l0_bound_fact_card_count"], len(all_bound_ids))
        self.assertEqual(
            sum(dossier["l0_domain_review_status_counts"].values()), len(all_bound_ids)
        )
        self.assertEqual(
            dossier["l0_domain_review_status_counts"], {
                "AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION": len(all_bound_ids)
            },
        )
        self.assertFalse(dossier["expert_review_complete"])
        self.assertFalse(dossier["source_rights_verified"])

    def test_review_only_full_synthetic_input_and_formal_target(self):
        self.assertTrue(self.dossier["not_for_sft"])
        self.assertFalse(self.dossier["training_authorized"])
        self.assertFalse(self.dossier["source_rights_verified"])
        self.assertFalse(self.dossier["gold_eligible"])
        self.assertEqual(self.dossier["sft_records_emitted"], 0)
        for item in self.dossier["items"]:
            self.assertIs(item["synthetic_input"]["raw_telemetry_included"], False)
            self.assertEqual(item["synthetic_provenance"]["classification"], "SYNTHETIC")
            self.assertTrue(item["synthetic_provenance"]["generated_fields"])
            self.assertTrue(item["formal_target_for_expert_review"])
            self.assertNotIn("messages", item)

    def test_internal_curator_and_reviewer_fields_never_leak(self):
        serialized = json.dumps(self.dossier, ensure_ascii=False)
        for key in ("internal_review", "curator_prompts", "reviewer_questions",
                    "quality_flags", "reviewer_token", "reviewer_id", "reviewed_at"):
            self.assertNotIn('"' + key + '"', serialized)

    def test_l0_public_fact_change_must_change_cohort_fingerprint(self):
        altered = copy.deepcopy(SOURCES)
        altered[0]["phenomenon_analysis"] += " (source-review correction)"
        next_dossier = build_c2_scientific_dossier(
            COLLECTION, source_fact_cards=altered
        )
        self.assertNotEqual(next_dossier["collection_projection_sha256"],
                            self.dossier["collection_projection_sha256"])

    def test_formal_target_mirror_divergence_fails_closed(self):
        changed = copy.deepcopy(COLLECTION)
        changed["packets"][0]["case"]["expected_output"]["disposal_status"] = "EXECUTED"
        with self.assertRaises(ValueError):
            build_c2_scientific_dossier(changed, source_fact_cards=SOURCES)

    def test_cli_generates_local_json_html_without_clobbering(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "new-review-annex"
            command = [
                sys.executable, str(CLI), "--collection", str(COLLECTION_PATH),
                "--source-facts", str(SOURCE_PATH), "--output-dir", str(out),
            ]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertEqual(len(list(out.iterdir())), 2)
            json_path = out / "C2_SYNTHETIC_SCIENTIFIC_REVIEW_ONLY.json"
            html_path = out / "C2_SYNTHETIC_SCIENTIFIC_REVIEW_ONLY.html"
            content = json_path.read_text(encoding="utf-8")
            page = html_path.read_text(encoding="utf-8")
            self.assertEqual(len(json.loads(content)["items"]), 15)
            self.assertIn("SYNTHETIC", page)
            self.assertIn("当前合成事件", page)
            self.assertIn("L0 领域审核状态", page)
            self.assertIn("AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION", page)
            self.assertNotIn("<script", page)
            self.assertNotIn('"internal_review"', page)
            second = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(second.returncode, 2)
            self.assertIn("REJECTED", second.stdout)
            self.assertEqual(json_path.read_text(encoding="utf-8"), content)


if __name__ == "__main__":
    unittest.main()
