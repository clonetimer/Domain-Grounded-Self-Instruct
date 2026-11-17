# DGSI Skill: integrated L1 dataset production and release

The DGSI Skill/toolkit and dataset are co-equal deliverables. The Skill is the reusable production system; the dataset is one versioned output. This workflow does not grant source rights, expert approval, Gold status or training permission.

## Inputs and immutable baseline
Require authorized sources and exact locators, source/event-family inventory, L0 cards, L1 collection, pinned schemas/toolkit, source rights/privacy status and analysis cutoff. Freeze hashes and IDs. Corrections create a new immutable candidate; never overwrite reviewed snapshots.

## C2-B — scientific/source review
For every packet check source fidelity, event family versus episode, flight versus ground-test class, phenomenon versus cause, fault source versus affected components, physical mechanism, measurement chain, supported temporal/causal relations, certainty, competing explanations, disposal recommendation/conditional/executed/verified state, and source-use rights. Record RETAIN_CANDIDATE, REVISE_CANDIDATE, QUARANTINE_SOURCE_RIGHTS, REJECT_CANDIDATE or PENDING_EXPERT. Curator review is not expert approval. Preserve NOT_EXPLICITLY_STATED certainty.

## C2-C — formal Assistant Target review
Use one canonical `formal_target`; keep duplicated `case.expected_output` equal and serialize only the canonical target. Review phenomenon, ML interpretation, fault source, affected objects, current evidence, competing causes, uncertainty/abstention, historical transfer/rejection, disposal semantics and report consistency. Historical L0 knowledge constrains historical claims but is not direct evidence for the current synthetic scenario. Curator prompts, reviewer notes, adjudication and hidden truth never enter model input or target.

## C2-D — model projection and deterministic serialization
Build the user projection from an explicit allowlist. Exclude the entire internal_review/reviewer/curator/adjudication/hidden-truth subtrees, regardless of not_for_sft flags. Use three messages: system role/contract; user cutoff-available ML findings, logs, spacecraft/mission context and qualified Context; assistant canonical structured report. Validate against pinned SFT schema, parse back and compare with canonical target. Check leakage, post-cutoff data, unsupported claims and event-family lineage. Bind collection membership, sources, user projections and target digests in a deterministic manifest.

During engineering review produce a blocked preview and metadata-only manifest; emit zero SFT rows until external admission authorizes export.

## C2-E — coverage and bounded additions
Report packet count and independent event-family count separately. Analyze six task types, flight/ground-test strata, domains/components, measurement-chain confounders, cross-subsystem causes, conflicts, evidence insufficiency/abstention, history transfer/mismatch/rejection, and disposal semantics. Classify gaps COVERED, WEAKLY_COVERED, MISSING or NOT_ASSESSABLE. Add tasks only for materially distinct challenges grounded in reviewed source families. Paraphrases do not increase independent event count. Rights/source-diversity blockers remain explicit.

## Unified handoff
Deliver frozen L0/L1 collection, per-packet dispositions, immutable corrected candidate, object-level change log, C2-B/C2-C report, projection specification/leakage report, three-message preview/round-trip report, coverage report, rights/expert blockers, SHA-256 manifest and matching Skill/toolkit ZIP. Extract the ZIP into a clean directory and run documented offline checks without repository PYTHONPATH.

## Release states
ENGINEERING_REVIEWED_CANDIDATE, EXPERT_ADJUDICATED, RIGHTS_CLEARED, SFT_AUTHORIZED and TRAINED are separate. A Skill package can be released while data remains blocked. Never label candidates Gold or training-ready because tests pass.
