"""SYNTHETIC_TEST_ONLY: local read-only global L1 audit launcher hardening.

No real or private flight case is read. All paths point to public repository
synthetic fixtures; adversarial plans never become official split assignments.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "audit_l1_global_lineage.py"
L1 = ROOT / "examples" / "l1_literature_synthetic_task_packets_v0.1.json"
L0 = ROOT / "examples" / "l0_public_literature_fact_cards_2026-11-15.json"


def _invoke(manifest_text, *, other=None):
    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        manifest = folder / "manifest.json"
        manifest.write_text(manifest_text, encoding="utf-8")
        cmd = [sys.executable, str(CLI), "--manifest", str(manifest)]
        if other:
            flag, value = other
            aux = folder / "other.json"
            aux.write_text(value, encoding="utf-8")
            cmd += [flag, str(aux)]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=30)
        return result.returncode, json.loads(result.stdout), result.stderr


def _manifest(**overrides):
    payload = {
        "schema_version": "dgsi-l1-global-audit-manifest.v1",
        "batches": [{
            "collection_path": str(L1),
            "source_fact_cards_path": str(L0),
        }],
    }
    payload.update(overrides)
    return json.dumps(payload)


class LocalL1GlobalAuditTests(unittest.TestCase):
    def test_pilot_is_a_structural_preflight_not_training(self):
        code, report, stderr = _invoke(_manifest())
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertEqual(report["task_count"], 15)
        self.assertEqual(report["decision"], "STRUCTURAL_PREFLIGHT_ONLY")
        self.assertEqual(report["gold_eligible_count"], 0)
        self.assertFalse(report["training_authorized"])

    def test_duplicate_json_key_is_rejected_without_source_echo(self):
        code, report, stderr = _invoke('{"schema_version":"a","schema_version":"b","batches":[]}')
        self.assertEqual(code, 2)
        self.assertEqual(report["error_code"], "LOCAL_DUPLICATE_JSON_KEY")
        self.assertNotIn("schema_version", stderr)

    def test_nonfinite_number_is_rejected(self):
        code, report, _ = _invoke('{"schema_version":"dgsi-l1-global-audit-manifest.v1","batches":NaN}')
        self.assertEqual(code, 2)
        self.assertEqual(report["error_code"], "LOCAL_NONFINITE_JSON_NUMBER")

    def test_missing_local_batch_file_is_rejected(self):
        code, report, _ = _invoke(_manifest(batches=[{
            "collection_path": "intentionally-nonexistent.json",
            "source_fact_cards_path": str(L0),
        }]))
        self.assertEqual(code, 2)
        self.assertEqual(report["error_code"], "LOCAL_FILE_INVALID")
        self.assertNotIn("intentionally-nonexistent", json.dumps(report))

    def test_empty_manifest_is_blocked(self):
        code, report, _ = _invoke(_manifest(batches=[]))
        self.assertEqual(code, 2)
        self.assertEqual(report["error_code"], "LOCAL_BATCH_COUNT_INVALID")

    def test_unreviewed_alias_claim_cannot_be_imported(self):
        aliases = json.dumps([{
            "alias_family_id": "invented-source-A",
            "canonical_family_id": "invented-source-B",
            "source_fact_refs": ["A", "B"],
            "review_status": "REVIEW_REQUIRED",
        }])
        code, report, _ = _invoke(_manifest(), other=("--aliases", aliases))
        self.assertEqual(code, 2)
        self.assertEqual(report["decision"], "BLOCKED")
        self.assertFalse(report["training_authorized"])

    def test_hypothetical_split_missing_collection_is_blocked(self):
        code, report, _ = _invoke(
            _manifest(),
            other=("--hypothetical-splits", json.dumps({"WRONG-COLLECTION": {}})),
        )
        self.assertEqual(code, 2)
        self.assertEqual(report["error_code"], "GLOBAL_HYPOTHETICAL_COLLECTION_COVERAGE_INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
