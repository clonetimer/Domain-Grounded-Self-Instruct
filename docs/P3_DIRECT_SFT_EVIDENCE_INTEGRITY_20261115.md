# P3: Direct SFT evidence-reference and prompt identity gate (2026-11-15)

## Verified bypass and fix

PR #24 validated the standalone SFT target report JSON against the published
report schema, but did not cross-check cited evidence or historical case
references against the *supplied* user-prompt packet. Source Case validation
already had this check; standalone SFT validation and batch lineage audit could
still accept syntactically valid reports citing nonexistent evidence IDs.

This change reuses the same source Case evidence-reference checker for direct
SFT exports. It rejects:

- Assistant cited ML evidence/log/candidate support IDs absent from the prompt.
- Historical-case references not supplied to the model.
- Duplicate finding/log/knowledge/history IDs and ambiguous cross-namespace IDs.
- Case or task identity in the JSON prompt differing from the SFT metadata.
- Attempts to bypass these checks through batch lineage audit.

**Test data:** 12 new adversarial tests, all explicitly SYNTHETIC.
No real case data or raw telemetry was introduced.

## Limits

This gate proves only *reference consistency*. A citation ID that exists does
not prove the content is authentic, relevant, available as of the decision
cutoff, or legally usable. Candidate-level evidence attribution and
independent expert Gold approval remain separate requirements. This does not
infer posterior fault probability from uncalibrated ML ranking scores.
A Case-to-SFT binding check is still required for exact source/target lineage;
an approved SFT flag by itself is never Gold certification.

Do not publish restricted R21 inputs, operator logs, non-public reports, or
any content-based case inventory. Keep local restricted intake and human
review in the authorized workspace. No main merge, paid-model call, training,
or automatic promotion is authorized.
