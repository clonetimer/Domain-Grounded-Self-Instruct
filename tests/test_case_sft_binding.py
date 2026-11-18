"""SYNTHETIC-only case -> SFT export binding adversarial tests."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.case_sft_binding import CaseSftBindingError, verify_case_sft_binding

ROOT = Path(__file__).resolve().parents[1]
CASE = json.loads((ROOT / "examples/diagnostic_context_case_illustrative.json").read_text(encoding="utf-8"))
SFT = json.loads((ROOT / "examples/diagnostic_context_sft_illustrative.json").read_text(encoding="utf-8"))


def pair():
    return copy.deepcopy(CASE), copy.deepcopy(SFT)


def edit_prompt(example, callback):
    text = example["messages"][1]["content"]
    index = text.index("{")
    packet = json.loads(text[index:])
    callback(packet)
    example["messages"][1]["content"] = text[:index] + json.dumps(packet, ensure_ascii=False)


class CaseSftBindingTests(unittest.TestCase):
    def reject(self, case, sft, code):
        with self.assertRaisesRegex(CaseSftBindingError, "^" + code + "$"):
            verify_case_sft_binding(case, sft)

    def test_synthetic_example_binds_but_is_never_gold(self):
        case, sft = pair()
        report = verify_case_sft_binding(case, sft)
        self.assertEqual(report["decision"], "PASS_BINDING_ONLY")
        self.assertEqual(report["matched_pair_count"], 1)
        self.assertFalse(report["gold_eligible"])
        self.assertNotIn("case_ref", report)

    def test_case_id_mismatch(self):
        case, sft = pair()
        sft["case_ref"] = "SYNTH-OTHER"
        self.reject(case, sft, "CASE_REFERENCE_MISMATCH")

    def test_task_type_mismatch(self):
        case, sft = pair()
        sft["task_type"] = "handover_summary"
        self.reject(case, sft, "TASK_TYPE_MISMATCH")

    def test_episode_group_mismatch(self):
        case, sft = pair()
        sft["source_group"] = "synthetic://other"
        self.reject(case, sft, "INCIDENT_FAMILY_MISMATCH")

    def test_prompt_input_score_drift(self):
        case, sft = pair()
        edit_prompt(sft, lambda p: p["input"]["machine_diagnosis"]["findings"][0].update(score=0.99))
        self.reject(case, sft, "PROMPT_SOURCE_INPUT_MISMATCH")

    def test_prompt_input_log_drift(self):
        case, sft = pair()
        edit_prompt(sft, lambda p: p["input"]["diagnostic_logs"][0].update(content="synthetic altered log"))
        self.reject(case, sft, "PROMPT_SOURCE_INPUT_MISMATCH")

    def test_prompt_mission_context_drift(self):
        case, sft = pair()
        edit_prompt(sft, lambda p: p["input"]["operational_context"].update(operating_mode="safe mode"))
        self.reject(case, sft, "PROMPT_SOURCE_INPUT_MISMATCH")

    def test_prompt_instruction_drift(self):
        case, sft = pair()
        edit_prompt(sft, lambda p: p.update(instruction="new unsupported instruction"))
        self.reject(case, sft, "PROMPT_INSTRUCTION_MISMATCH")

    def test_prompt_extra_field_is_rejected(self):
        case, sft = pair()
        edit_prompt(sft, lambda p: p.update(unaudited="extra context"))
        self.reject(case, sft, "PROMPT_PACKET_FIELDS_MISMATCH")

    def test_prompt_json_suffix_is_rejected(self):
        case, sft = pair()
        sft["messages"][1]["content"] += "\nUNREVIEWED_APPENDIX"
        self.reject(case, sft, "TRAILING_JSON_PACKET_CONTENT")

    def test_assistant_target_tampering(self):
        case, sft = pair()
        target = json.loads(sft["messages"][2]["content"])
        target["cause_localization"]["status"] = "SUPPORTED"
        sft["messages"][2]["content"] = json.dumps(target, ensure_ascii=False)
        self.reject(case, sft, "ASSISTANT_TARGET_MISMATCH")

    def test_duplicate_json_field_is_rejected(self):
        case, sft = pair()
        sft["messages"][2]["content"] = '{"disposition":"X","disposition":"Y"}'
        self.reject(case, sft, "DUPLICATE_JSON_KEY")

    def test_nonfinite_json_number_is_rejected(self):
        case, sft = pair()
        sft["messages"][2]["content"] = '{"x": NaN}'
        self.reject(case, sft, "NONFINITE_JSON_NUMBER")

    def test_diagnosis_run_ref_mismatch(self):
        case, sft = pair()
        sft["provenance"]["diagnosis_result_refs"] = ["synthetic://different-run"]
        self.reject(case, sft, "UPSTREAM_RUN_LINEAGE_MISMATCH")

    def test_log_ref_omission(self):
        case, sft = pair()
        sft["provenance"]["diagnostic_log_refs"].pop()
        self.reject(case, sft, "DIAGNOSTIC_LOG_LINEAGE_MISMATCH")

    def test_log_ref_duplication(self):
        case, sft = pair()
        sft["provenance"]["diagnostic_log_refs"].append("LOG-01")
        self.reject(case, sft, "DIAGNOSTIC_LOG_LINEAGE_MISMATCH")

    def test_knowledge_passage_ref_drift(self):
        case, sft = pair()
        sft["provenance"]["knowledge_passage_ids"] = ["phantom-passage"]
        self.reject(case, sft, "KNOWLEDGE_PASSAGE_LINEAGE_MISMATCH")

    def test_source_hash_mismatch(self):
        case, sft = pair()
        sft["provenance"]["source_artifact_hashes"] = ["a" * 64]
        self.reject(case, sft, "SOURCE_ARTIFACT_HASH_LINEAGE_MISMATCH")

    def test_context_ref_missing(self):
        case, sft = pair()
        sft["provenance"]["context_refs"] = ["mission:scheduled attitude slew"]
        self.reject(case, sft, "SPACECRAFT_CONTEXT_REFERENCE_MISSING")

    def test_unapproved_case_cannot_approve_sft(self):
        case, sft = pair()
        sft["review"]["status"] = "APPROVED"
        sft["review"]["reviewer_id"] = "synthetic-reviewer"
        sft["review"]["reviewed_at"] = "2026-11-15T00:00:00Z"
        self.reject(case, sft, "SFT_APPROVAL_WITHOUT_SOURCE_CASE_APPROVAL")

    def test_invalid_source_report_redacts_failure_details(self):
        case, sft = pair()
        case["input"]["diagnostic_logs"][0]["timestamp"] = "2028-01-01T00:00:00Z"
        self.reject(case, sft, "INVALID_SOURCE_CASE")

    def test_invalid_sft_prompt_redacts_failure_details(self):
        case, sft = pair()
        sft["messages"][1]["content"] += '\n"expected_output": {"fault": "secret"}'
        self.reject(case, sft, "INVALID_SFT_EXAMPLE")


if __name__ == "__main__":
    unittest.main()
