# Runtime JSON Schema gate (synthetic-only verification)

Both published Draft 2020-12 contracts are now checked against complete
Case/SFT instances during validation, using `jsonschema` and `FormatChecker`.
This blocks nested unknown properties, missing required fields, invalid enums
and invalid types that the earlier handwritten safety checks did not cover.

The existing semantic validators remain mandatory and run first: no raw telemetry,
truth/target leakage, timezone-naive cutoff, post-cutoff diagnostic logs,
non-finite scores or unsupported diagnosis status. JSON Schema checks complement
rather than replace those protections. Schema errors deliberately expose only the
failed keyword (for example `JSON_SCHEMA_REQUIRED`), not private input values.

Local prerequisite: `python -m pip install -r requirements-validation.txt`.
Run `PYTHONPATH=src python -m unittest discover -s tests -v`.
Ubuntu and Windows CI install the same validation requirement before running the
full adversarial matrix. Do not relax either platform check to accept a PR.

The only committed examples and new tests are synthetic illustrations. A schema
PASS is not authenticity, IP permission, expert review, Gold approval or clearance
for SFT model fine-tuning. Restricted case bundles must remain outside the
public repository.
