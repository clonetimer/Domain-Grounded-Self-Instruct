# AAS RUN-03F integration fixture — field mapping correction

Date: 2026-11-18

## Correction

The first DGSI integration demonstration incorrectly mapped the AAS score vector into a field named `threshold_array`. Inspection of the exact `score_only_execution_result.json.gz` shows the source chart trace has distinct fields:

- `decision_threshold = 2.5`
- `decision_thresholds = [2.5] × 24`
- `scores = [49.555320595684975, 50.05064161991172, 50.54596264413846, ...]`

The 49.56–50.55 values are **scores**, not thresholds. Their business interpretation and relationship to the decision threshold are not explained by the evidence package, so the corrected DGSI input preserves them as `scores` and marks their semantics as requiring interface/source-code verification. No interpretation of them as probabilities is made.

## Corrected artifact

- Corrected ZIP: `DGSI_AAS_RUN03F_score_only_integration_demo_corrected_20261118.zip`
- SHA-256: `ef0ca966d5b9f762945bd20502f35971f1ae87ec48a69bc3ccd4e7bdb10c5c44`
- Inner manifest entries verified: 14
- Original ZIP is retained as historical evidence; use the corrected ZIP for future demonstrations.

## Diagnostic conclusion remains unchanged

The AAS run is `SYNTHETIC_TEST_ONLY`, has 24/24 anomaly predictions, no ground truth and empty evaluation metrics. The correct second-stage output still avoids physical fault localization. It flags the mismatch between the training min-max fit range (0.0–0.6) and current input values (10.3–10.5 rad/s) for investigation, without asserting that this proves hardware failure or model malfunction.

## Release boundary

This fixture remains an integration/abstention test only. It is not REAL, not a complete L1 case, not Gold and not SFT-authorized.
