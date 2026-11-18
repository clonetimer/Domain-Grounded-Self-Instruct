"""Regression guards: SFT prompts must not disclose target answers or reviews."""
import copy
import json
import unittest
from pathlib import Path

from dgsi.diagnostic_context import DiagnosticContextValidationError, validate_sft_example

ROOT = Path(__file__).resolve().parents[1]


def fixture(name):
    return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))


class SftPromptIsolationTests(unittest.TestCase):
    def test_illustration_exports_only_case_input(self):
        example = fixture("diagnostic_context_sft_illustrative.json")
        case = fixture("diagnostic_context_case_illustrative.json")
        user = example["messages"][1]["content"]
        packet = json.loads(user.split("\n\n", 1)[1])
        self.assertEqual(set(packet), {"case_id", "task_type", "instruction", "input"})
        self.assertEqual(packet["input"], case["input"])
        self.assertNotIn("expected_output", packet)
        self.assertNotIn("review", packet)
        self.assertNotIn("provenance", packet)
        validate_sft_example(example)

    def test_old_full_case_prompt_is_rejected(self):
        example = fixture("diagnostic_context_sft_illustrative.json")
        case = fixture("diagnostic_context_case_illustrative.json")
        example["messages"][1]["content"] += "\n\n" + json.dumps(case, ensure_ascii=False)
        with self.assertRaisesRegex(DiagnosticContextValidationError, "forbidden target"):
            validate_sft_example(example)

    def test_forbidden_json_keys_adversarial(self):
        original = fixture("diagnostic_context_sft_illustrative.json")
        keys = [
            "expected_output", "review", "answer_key", "target_report",
            "gold_answer", "ground_truth", "fault_truth", "injection_truth",
            "hidden_label", "gold_label", "labels_used", "truth_used",
            "raw_telemetry", "telemetry_rows", "waveform", "waveforms",
            "time_series", "timeseries", "raw_signal", "samples",
        ]
        for key in keys:
            with self.subTest(key=key):
                example = copy.deepcopy(original)
                example["messages"][1]["content"] += "\n" + json.dumps({key: {"secret": 1}})
                with self.assertRaisesRegex(DiagnosticContextValidationError, "forbidden target"):
                    validate_sft_example(example)

    def test_case_insensitive_whitespace_variant_is_rejected(self):
        example = fixture("diagnostic_context_sft_illustrative.json")
        example["messages"][1]["content"] += '\n{"ExPeCtEd_OuTpUt"  : {"leak": true}}'
        with self.assertRaisesRegex(DiagnosticContextValidationError, "forbidden target"):
            validate_sft_example(example)

    def test_ordinary_discussion_of_review_is_not_json_field(self):
        example = fixture("diagnostic_context_sft_illustrative.json")
        # Natural discussion of prior review is permitted as source log data,
        # not as an unreviewed instruction appended after the JSON packet.
        user = example["messages"][1]["content"]
        start = user.index("{")
        packet = json.loads(user[start:])
        packet["input"]["diagnostic_logs"][0]["content"] += " Prior review is unresolved."
        example["messages"][1]["content"] = user[:start] + json.dumps(packet, ensure_ascii=False)
        validate_sft_example(example)


if __name__ == "__main__":
    unittest.main()
