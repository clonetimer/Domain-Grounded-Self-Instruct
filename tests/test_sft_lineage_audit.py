"""Adversarial incident/split lineage tests; all examples are synthetic."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

from dgsi.sft_lineage import SftLineageAuditError, audit_sft_lineage

ROOT = Path(__file__).resolve().parents[1]
BASE = json.loads((ROOT / "examples/diagnostic_context_sft_illustrative.json").read_text(encoding="utf-8"))


def make_case(tag, split):
    example = copy.deepcopy(BASE)
    example["example_id"] = "SYNTH-SFT-" + tag
    example["case_ref"] = "SYNTH-CASE-" + tag
    example["source_group"] = "SYNTH-EPISODE-" + tag
    example["split"] = split
    example["messages"][1]["content"] += "\nSynthetic case tag: " + tag
    example["provenance"]["diagnosis_result_refs"] = ["synthetic://diagnosis/" + tag]
    example["provenance"]["source_artifact_hashes"] = [
        hashlib.sha256(("synthetic-artifact:" + tag).encode()).hexdigest()
    ]
    return example


class SftLineageTests(unittest.TestCase):
    def assert_rejected(self, examples, code):
        with self.assertRaisesRegex(SftLineageAuditError, code):
            audit_sft_lineage(examples)

    def test_disjoint_episode_families_pass_structural_only(self):
        report = audit_sft_lineage([make_case("one", "train"), make_case("two", "test")])
        self.assertEqual(report["decision"], "PASS_STRUCTURAL_ONLY")
        self.assertEqual(report["split_counts"]["train"], 1)
        self.assertEqual(report["split_counts"]["test"], 1)
        self.assertEqual(report["synthetic_or_illustrative_count"], 2)
        self.assertFalse(report["gold_eligible"])
        self.assertTrue(report["expert_event_family_review_required"])
        self.assertNotIn("case_ref", report)

    def test_source_group_leak(self):
        a, b = make_case("one", "train"), make_case("two", "test")
        b["source_group"] = a["source_group"]
        self.assert_rejected([a, b], "CROSS_SPLIT_SOURCE_GROUP")

    def test_case_ref_leak_with_different_episode_labels(self):
        a, b = make_case("one", "train"), make_case("two", "validation")
        b["case_ref"] = a["case_ref"]
        self.assert_rejected([a, b], "CROSS_SPLIT_CASE_REF")

    def test_same_upstream_run_with_renamed_case_is_rejected(self):
        a, b = make_case("one", "train"), make_case("two", "test")
        b["provenance"]["diagnosis_result_refs"] = a["provenance"]["diagnosis_result_refs"]
        self.assert_rejected([a, b], "CROSS_SPLIT_DIAGNOSIS_RESULT_REF")

    def test_source_artifact_duplicate_cross_split_is_rejected(self):
        a, b = make_case("one", "train"), make_case("two", "test")
        b["provenance"]["source_artifact_hashes"] = a["provenance"]["source_artifact_hashes"]
        self.assert_rejected([a, b], "CROSS_SPLIT_SOURCE_ARTIFACT_HASH")

    def test_same_prompt_across_splits_without_shared_ids_is_rejected(self):
        a, b = make_case("one", "train"), make_case("two", "test")
        b["messages"][1]["content"] = a["messages"][1]["content"]
        self.assert_rejected([a, b], "CROSS_SPLIT_USER_PROMPT")

    def test_inconsistent_targets_for_identical_prompt_rejected(self):
        a, b = make_case("one", "train"), make_case("two", "train")
        b["messages"][1]["content"] = a["messages"][1]["content"]
        b["messages"][2]["content"] += "\nConflicting answer"
        self.assert_rejected([a, b], "CONFLICTING_TARGETS_FOR_IDENTICAL_PROMPT")

    def test_duplicate_content_different_example_ids_rejected(self):
        a, b = make_case("one", "train"), make_case("two", "train")
        b["messages"][1]["content"] = a["messages"][1]["content"]
        self.assert_rejected([a, b], "DUPLICATE_IDENTICAL_SFT_EXAMPLE")

    def test_duplicate_example_id_even_with_different_prompt_rejected(self):
        a, b = make_case("one", "train"), make_case("two", "train")
        b["example_id"] = a["example_id"]
        self.assert_rejected([a, b], "DUPLICATE_EXAMPLE_ID")

    def test_multiple_tasks_for_same_case_stay_together(self):
        a, b = make_case("one", "train"), make_case("two", "train")
        b["case_ref"] = a["case_ref"]
        b["source_group"] = a["source_group"]
        b["task_type"] = "handover_summary"
        b["messages"][1]["content"] += "\nTask: handover summary"
        report = audit_sft_lineage([a, b])
        self.assertEqual(report["example_count"], 2)

    def test_synthetic_never_expert_approved(self):
        a = make_case("one", "train")
        a["review"]["status"] = "APPROVED"
        a["review"]["reviewer_id"] = "fake-reviewer"
        a["review"]["reviewed_at"] = "2026-11-15T03:00:00+09:00"
        self.assert_rejected([a], "SYNTHETIC_FIXTURE_CANNOT_BE_EXPERT_APPROVED")

    def test_missing_hash_remains_visible_but_not_gold(self):
        a = make_case("one", "train")
        a["provenance"]["source_artifact_hashes"] = []
        report = audit_sft_lineage([a])
        self.assertEqual(report["missing_source_hash_count"], 1)
        self.assertFalse(report["gold_eligible"])


if __name__ == "__main__":
    unittest.main()
