---
name: adcs-gold-seed-curation
description: Use when drafting or reviewing Self-Instruct seed tasks for spacecraft ADCS fault diagnosis, especially when AI outputs contain invented technical terms, unsupported causal inferences, self-certifying claims, fabricated telemetry, or uncertain source provenance.
---

# ADCS Gold Seed Curation (DRAFT, P1)

Generate **candidate** tasks, never self-authorize Gold. A citation, catalog entry, or syntactically valid trace is not physical proof. Human-domain review decides final status.

## Procedure

1. Choose an ADCS task from an admitted source passage or telemetry receipt. Inspect `resources/sources.json`, `source_passages.json`, `terms.json`, `fault_effects.json` and `telemetry_channels.csv` before drafting. Select a registered `passage_id`; read the cited passage and record its applicability, allowed claim types and evidence status. Never invent page/section locators.
2. Create a `dgsi-seed.v1` candidate. Set `input.kind=HYPOTHETICAL` for hypothetical cases, or `TRACE` only when a verified local receipt is available. Keep labels, simulator truth, faults and injection timestamps out of `input`.
3. Break each output into atomic `claims`, with registered `source_ids` and `evidence_ids`. For `MECHANISM` and `CAUSAL` claims, include registered `source_passage_ids`; a free-text locator alone is insufficient. Passage scope must authorize the claim type. Do not turn “observed on channel X” into “component X is the source”.
4. Prefer concise technical prose using admitted `term_ids`. Preserve the alias class: exact alias, alternate translation, informal/contextual short form, broader functional description, or structural subtype. For example, `磁力矩杆` is a structural subtype, not an exact alias for every `磁力矩器`. The compound-term scanner is deliberately narrow and only flags some suspicious constructions; its silence does not certify vocabulary coverage.
5. Apply `PYTHONPATH=src python -m dgsi.cli validate <seed.json> --root .`. Correct blocking findings by revisiting the actual evidence, **not** by simply rewording the claim to evade a detector. Treat `REVIEW_REQUIRED` as an unresolved terminology review, not a pass.
6. When independent evidence is insufficient, use `INSUFFICIENT_EVIDENCE` or `AMBIGUOUS` and state what measurements would resolve the case. A confirmed fault result requires an admitted run receipt and measured evidence.
7. Present original text, source locators, suggested correction and uncertainty to the human curator; preserve each approval/rejection/edit in an independent audit. The validator can check review metadata but cannot authenticate a person or freeze Gold itself.

## Quick reference

| Symptom | Correct response |
|---|---|
| Invented fault name | Reject and map to registry or request terminology review |
| “A therefore caused B” | Check mechanism, independent evidence and causal human approval; otherwise downgrade conclusion |
| “This is proven/validated” | Verify independently; remove self-attestation if unsupported |
| Injected fault label present in question | Remove truth/labels, inspect the inference split, rerun checks |
| Vague sensor anomaly | Preserve uncertainty; request independent channels and operating-mode context |
| Tool reports PASS | Candidate only; request human review before Gold |

**Validation status:** automated gates and fixture tests cover known bad patterns. This draft Skill itself still requires independent blind/pressure evaluation before it can be designated production-ready.
