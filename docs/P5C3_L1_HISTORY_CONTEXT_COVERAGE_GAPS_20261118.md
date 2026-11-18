# P5-C3 | Current 21-task historical Context coverage gap audit (2026-11-18)

## Product boundary
The only downstream product is satellite fault-diagnosis SFT from upstream ML findings, diagnostic logs, spacecraft/mission context and qualified retrieved history. Raw telemetry is not a default LLM input. REAL Gold and literature-derived SYNTHETIC remain separate.

## Implementation
`src/dgsi/l1_context_coverage_gap.py` first validates the entire L1 collection and referenced L0 cards, then counts **nonexclusive per-packet metadata scenarios**. Counts are not scientific correct-answer rates, expert approval, or independent holdout size. Outputs contain aggregate labels only, never original case IDs, source refs, ML/log content or formal targets.

Current corrected 21-task fixture (same nine event families):
- NO_HIT: 18 packets.
- HIT: three packets, two REJECTED and one PARTIALLY_CONFIRMED, all with UNKNOWN hardware compatibility and mandatory transfer limitations.
- Confirmed/compatible: 0; unresolved: 0; incompatible hardware: 0; multiple conflicting hits: 0.
- External time-cutoff, same-family, missing-time and vote-on-current-root-cause cases are **negative validator controls**, not valid L1 training data; do not bypass the gate merely to increase coverage.
- Whether logs contradict historical precedent or a history citation is scientifically transferable **cannot be inferred from metadata**. Requires content-bound independent review.

## Evidence and limits
Run `python -m unittest tests.test_l1_context_coverage_gap -v` (zero network). Tests include the current 21-task cohort, mixed/multiple-hit classification, fail-closed future-time and track/packet-integrity guards. Existing PRs #151 and #154 provide conservative holdout linkage and the 21-task expert handoff, respectively; this report supplements, not replaces, either.

Next meaningful science work: an independently sourced confirmed-and-compatible historical case, a hardware-mismatched negative-transfer example, and a clearly unresolved/multi-history conflict scenario, each with source and as-of evidence, without fabricating real ML/logs or historical timestamps. Source rights and two independent domain reviews remain blocked; no Gold, official split, export or fine-tuning.

## Development experience
- **Changed:** a validated, redacted task-scenario coverage matrix and nine synthetic tests.
- **Why:** collection sizes/CI passes masked 18/21 NO_HIT cases and the absence of confirmed-transfer coverage.
- **Trap avoided:** scoring expired/future or same-event-family history as admissible training examples; validator rejection tests are not positive SFT samples. Multi-label counts must not be summed into case counts.
