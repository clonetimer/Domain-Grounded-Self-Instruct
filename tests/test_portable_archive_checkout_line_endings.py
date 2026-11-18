"""SYNTHETIC_TEST_ONLY: portable ZIP source-byte canonicalization contract."""
from __future__ import annotations

from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = runpy.run_path(
    str(ROOT / "scripts" / "package_dgsi_simulation_to_sft.py"),
    run_name="dgsi_package_test_import",
)["canonical_checkout_bytes"]


class PortableCheckoutLineEndingTests(unittest.TestCase):
    def test_windows_and_unix_checkout_text_share_exact_bytes(self):
        original = b'print("SYNTHETIC_TEST_ONLY")\nvalue = 1\n'
        windows = original.replace(b"\n", b"\r\n")
        self.assertEqual(original, CANONICAL(original))
        self.assertEqual(original, CANONICAL(windows))

    def test_mixed_and_utf8_text_preserve_semantics(self):
        original = "现象分析\nsource_ref\n".encode("utf-8")
        mixed = original.replace(b"\n", b"\r\n", 1)
        self.assertEqual(original, CANONICAL(mixed))

    def test_binary_with_nul_is_not_rewritten(self):
        binary = b"\x89PNG\r\n\x1a\n\x00\xfe\r\n"
        self.assertEqual(binary, CANONICAL(binary))

    def test_invalid_utf8_is_not_rewritten(self):
        binary = b"\xff\xfe\r\n"
        self.assertEqual(binary, CANONICAL(binary))


if __name__ == "__main__":
    unittest.main()
