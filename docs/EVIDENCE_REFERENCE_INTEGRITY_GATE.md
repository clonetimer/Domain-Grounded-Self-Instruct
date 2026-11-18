# Case-level citation integrity gate

The runtime case validator now checks that citations in the target report
resolve to identifiers declared in the LLM-facing case packet. It rejects:

- invented supporting/contradicting evidence references;
- candidate claims citing absent machine/log/knowledge evidence;
- duplicated machine findings, knowledge IDs and historical case references;
- identifier collisions between finding, machine evidence, logs, knowledge and
  history (ambiguous source namespace);
- historical-experience conclusions and provenance referencing a case that
  was not supplied.

Evidence identifiers under an upstream finding's
`supporting_evidence_ids` are **declarations**, not verified source artifacts.
This check verifies the **join**, not the scientific authenticity, timestamp,
citation permissions or physical meaning of the upstream evidence. Those
conditions still require immutable artifacts, authorized review and expert
adjudication before Gold export.

Current tests only mutate the public hypothetical illustrative case; no
restricted logs, R21 telemetry or real engineering data were committed.
No source content or evidence identifier is emitted on validation failure.
Run both Ubuntu and Windows CI; keep this PR draft and stacked on #12.
