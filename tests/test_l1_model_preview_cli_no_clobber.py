"""SYNTHETIC_TEST_ONLY: L1 preview CLI publishes atomically and never clobbers."""
from __future__ import annotations

import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/create_l1_model_preview.py"
COLLECTION = ROOT / "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"
SOURCES = ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"


def _command(output: Path) -> list[str]:
    return [
        sys.executable, str(SCRIPT),
        "--collection", str(COLLECTION),
        "--source-facts", str(SOURCES),
        "--output", str(output),
    ]


def _run(output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        _command(output), cwd=ROOT, capture_output=True, text=True, check=False
    )


class PreviewCliNoClobberTests(unittest.TestCase):
    def test_real_candidate_preview_is_explicitly_unreleased(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "preview.json"
            result = _run(output)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["packet_count"], 15)
            self.assertEqual(payload["event_family_count"], 9)
            self.assertEqual(payload["sft_records_emitted"], 0)
            self.assertFalse(payload["training_authorized"])
            self.assertFalse(payload["official_splits_assigned"])
            self.assertTrue(all(
                item["preview_only"] and not item["export_authorized"]
                and item["split"] is None for item in payload["preview_records"]
            ))
            self.assertEqual(json.loads(result.stdout)["sft_records_emitted"], 0)

    def test_existing_preview_file_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "preview.json"
            output.write_text("OPERATOR_OWNED", encoding="utf-8")
            result = _run(output)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(
                json.loads(result.stdout)["error_code"], "OUTPUT_ALREADY_EXISTS"
            )
            self.assertEqual(output.read_text(encoding="utf-8"), "OPERATOR_OWNED")

    def test_dangling_symlink_does_not_redirect_preview_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "not_created.json"
            alias = Path(tmp) / "preview.json"
            try:
                alias.symlink_to(target)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink not permitted: {type(exc).__name__}")
            self.assertTrue(alias.is_symlink())
            self.assertFalse(target.exists())
            result = _run(alias)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(
                json.loads(result.stdout)["error_code"], "OUTPUT_ALREADY_EXISTS"
            )
            self.assertTrue(alias.is_symlink())
            self.assertFalse(target.exists())

    def test_two_simultaneous_preview_writers_exactly_one_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "preview.json"
            first = subprocess.Popen(
                _command(output), cwd=ROOT,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            second = subprocess.Popen(
                _command(output), cwd=ROOT,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            first_out, first_err = first.communicate(timeout=90)
            second_out, second_err = second.communicate(timeout=90)
            self.assertEqual(
                sorted([first.returncode, second.returncode]), [0, 2],
                (first_out, first_err, second_out, second_err),
            )
            rejected = first_out if first.returncode == 2 else second_out
            self.assertEqual(
                json.loads(rejected)["error_code"], "OUTPUT_ALREADY_EXISTS"
            )
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["packet_count"], 15)
            self.assertEqual(payload["sft_records_emitted"], 0)
            self.assertFalse(payload["training_authorized"])

    def test_hard_link_unsupported_fails_closed_without_output(self):
        cli = importlib.import_module("scripts.create_l1_model_preview")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "preview.json"
            args = [
                "--collection", str(COLLECTION),
                "--source-facts", str(SOURCES),
                "--output", str(output),
            ]
            with patch.object(cli.os, "link", side_effect=OSError("no hard links")):
                with patch("builtins.print") as mock_print:
                    status = cli.main(args)
            self.assertEqual(status, 2)
            self.assertFalse(output.exists())
            self.assertEqual(
                json.loads(mock_print.call_args.args[0])["error_code"],
                "INPUT_OR_OUTPUT_INVALID",
            )
            self.assertFalse(list(Path(tmp).glob(".dgsi-l1-preview-*.tmp")))


if __name__ == "__main__":
    unittest.main()
