"""Full-repository integration: detached B4.3c tests from the real toolkit ZIP."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class TopologyPackageTests(unittest.TestCase):
    def test_full_toolkit_contains_and_executes_detached_topology_tests(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / 'toolkit.zip'
            built = subprocess.run(
                [sys.executable, str(ROOT / 'scripts/package_dgsi_simulation_to_sft.py'),
                 '--output', str(archive_path)], cwd=ROOT, capture_output=True,
                text=True, timeout=60, check=False,
            )
            self.assertEqual(built.returncode, 0, built.stderr)
            detached = root / 'detached'
            with zipfile.ZipFile(archive_path) as archive:
                expected = {
                    'src/dgsi/diagram_topology_review.py',
                    'scripts/audit_diagram_topology_review.py',
                    'tests/test_diagram_topology_review.py',
                    'skills/dgsi-simulation-to-sft/schemas/diagram_topology_review.schema.json',
                    'skills/dgsi-simulation-to-sft/references/DIAGRAM_TOPOLOGY_REVIEW.md',
                    'docs/DEVELOPMENT_EXPERIENCE_TOPOLOGY_REVIEW.md',
                }
                self.assertTrue(expected.issubset(archive.namelist()))
                manifest = json.loads(archive.read('PACKAGE_SHA256_MANIFEST.json'))
                self.assertFalse(manifest['training_authorized'])
                self.assertFalse(manifest['gold_authorized'])
                self.assertFalse(manifest['sft_export_authorized'])
                for item in manifest['files']:
                    self.assertEqual(hashlib.sha256(archive.read(item['path'])).hexdigest(), item['sha256'])
                # Only extract the just-built allowlisted source archive.
                for name in archive.namelist():
                    target = (detached / name).resolve()
                    self.assertTrue(target.is_relative_to(detached.resolve()))
                archive.extractall(detached)
            env = os.environ.copy()
            env.pop('PYTHONPATH', None)
            tested = subprocess.run(
                [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests',
                 '-p', 'test_diagram_topology_review.py', '-v'],
                cwd=detached, env=env, capture_output=True, text=True, timeout=120,
                check=False,
            )
            self.assertEqual(tested.returncode, 0, tested.stderr)
            self.assertIn('test_valid_audit_is_aggregate_only', tested.stderr)
            self.assertIn('OK', tested.stderr)


if __name__ == '__main__':
    unittest.main()
