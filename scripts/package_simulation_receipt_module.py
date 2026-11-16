#!/usr/bin/env python3
"""Build the standalone receipt engineering module, not the full DGSI toolkit."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "src/dgsi/simulation_run_receipt.py",
    "skills/dgsi-simulation-to-sft/schemas/simulation_run_receipt.schema.json",
    "skills/dgsi-simulation-to-sft/references/SIMULATION_RUN_RECEIPT.md",
    "scripts/audit_simulation_run_receipt.py",
    "scripts/create_simulation_receipt_fixture.py",
    "scripts/package_simulation_receipt_module.py",
    "tests/test_simulation_run_receipt.py",
)


def build_package(output: Path) -> dict:
    selected = {}
    for name in FILES:
        path = ROOT / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("PACKAGE_REQUIRED_FILE_UNAVAILABLE")
        selected[name] = path.read_bytes()
    selected["src/dgsi/__init__.py"] = b"\"\"\"Standalone DGSI receipt module subset.\"\"\"\n"
    selected["requirements-validation.txt"] = b"jsonschema>=4.22,<5\n"
    selected["START_HERE_zh.md"] = selected[FILES[2]]
    manifest = {"package": "DGSI simulation run receipt engineering module", "version": "0.1.0", "standalone_subset": True,
                "training_authorized": False, "gold_authorized": False,
                "files": [{"path": name, "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()} for name, data in sorted(selected.items())]}
    selected["PACKAGE_MANIFEST.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(selected.items()):
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return {"file_count": len(selected), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "training_authorized": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="dist/dgsi-run-receipt-module-v0.1.0.zip")
    args = parser.parse_args()
    try:
        out = build_package(Path(args.output))
    except (OSError, ValueError):
        print(json.dumps({"error_code": "PACKAGE_BUILD_FAILED"}))
        return 2
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
