# Development experience: topology evidence review

Continuation of `DEVELOPMENT_EXPERIENCE_OPTIONAL_PYTHON_DEPENDENCIES.md`.
Scope: P5-B4.3c implementation and verification boundaries, 2026-11-17.

## Baseline attribution

Pinned P5 head: `fc0f8152057c1ded256084d216d66b041de7b70f` (PR #107).
Push workflow `44011424508`: Ubuntu and Windows jobs SUCCESS. Ubuntu log confirms
837 tests and the exact checkout SHA. A PR-only run-list wrapper would miss this
push run; an empty filtered run list is not proof that CI never ran.
The independent P4 work in PR #108 is not included by this feature branch.

## Reusable rules

33. **Bind evidence to the individual claim and object.** A drawn connector does
not establish its direction or engineering medium. Port label, port direction,
medium, unit, connector existence, edge direction and relation type have separate
subject/field-bound evidence references. Tests reject borrowing another object's
evidence or reusing connector evidence as proof of CONTROL/POWER semantics.

34. **Unknown direction must not become a directed graph edge.** Keep a visible
but direction-unknown connection in an explicit unresolved sidecar. Writing an
arbitrary from/to pair into a directed graph silently introduces unsupported flow.

35. **Preserve typed evidence through conversion.** A generic graph object's
single locator is insufficient for every asserted property. Keep the complete
review receipt and canonical hashes beside the converted graph; do not promote
receipt consistency to authenticated inspection or scientific correctness.

36. **Test actual CLI failure paths before the full matrix.** Tests exercise
invalid UTF-8, duplicate JSON keys, non-finite values, over-limit inputs, missing
output directories, overwrite refusal and payload-free errors. Compile checks
cannot substitute for executing these subprocess paths.

37. **Regex validation must consume the entire identifier.** A negative test
showed that a pattern ending in `$` accepted a final newline. The ID schema now
explicitly prohibits CR/LF as well as restricting characters. The failing test was
observed before the fix; this prevents forged locator fragments in review IDs.

38. **Distinguish an isolated tested subset from full repository integration.**
Container DNS prevented cloning. Inherited validator and schema bytes were
verified against pinned Git blob hashes, then the feature tests were run locally.
This is not a full local repository test. The real toolkit ZIP/detached execution
regression and the full Windows/Ubuntu suite must run on the feature's remote head.
Do not alter files again merely to record a green badge; attach final exact-head
CI evidence to the PR so its tested commit remains identifiable.

## Local evidence

Feature absence and CLI absence were observed as failing tests before implementation.
The identifier-newline regression was also observed failing before correction.
The 43 feature/CLI tests passed locally; compileall passed. The separately built
minimal source bundle is a portability check only, not the full DGSI toolkit.
All fixtures are SYNTHETIC_TEST_ONLY. No image recognition, real fault experiment,
reviewer authentication, KG effectiveness experiment, or training was performed.


## P5-C1 evidence matrix and exact-head CI (2026-11-17)

PR #117 adds a case-specific evidence request matrix for the five user-supplied REAL candidates. Latest head `725b60e230457cf955fe75f99429035376ed2352` passed both Push workflow `44047660415` and PR workflow `44047667106`: Ubuntu 912/912 and Windows 912/912 on each workflow. These runs executed the repository's 912-test suite. No dedicated test signatures for the new matrix were found in the logs; therefore this is a full regression/packaging pass, not a claim that case-specific evidence correctness was automatically validated.

49. **Separate evidence requested, evidence received, and evidence verified.** A case-specific matrix describes what would discriminate hypotheses; it is not proof that those artifacts exist. Track each item through NOT_AVAILABLE / AVAILABLE_NOT_LOCATED / AVAILABLE_AND_LOCATED / NOT_APPLICABLE / PENDING_SOURCE_OWNER. Only after the actual artifact is received in authorized storage, its exact bytes are fingerprinted, its source/time basis is recorded, and a reviewer validates its relevance may it support a claim. A request list must never be counted as evidence completeness.

50. **Evidence completeness is case-relative, not a uniform checklist score.** Common requirements (upstream ML output, logs, spacecraft/mission context) must be combined with case-specific discriminators. For example, cable/isolator contact evidence is relevant to the TWTA case; EPDF protection-state mapping is relevant to the Ku TWTA case; sensor location and thrust-measurement basis are relevant to the thruster case. Do not mark a case complete merely because generic fields are populated.

51. **Keep disposal recommendation, conditional procedure, execution and verified effect as separate states.** The same prose may describe an option, a command, an observed state or a successful recovery. Require command/state evidence and post-action verification before the SFT target states that a measure was executed or effective.

52. **Do not expose raw real-case artifacts to a public repository for convenience.** Keep logs, telemetry, command histories and private reports in authorized storage. Public metadata may contain opaque locators and exact-byte hashes, but hashes do not establish source authenticity, de-identification or training-use rights.

53. **Do not infer dedicated feature coverage from a green full-suite run.** Inspect test names in completed logs. If a newly added data artifact has no dedicated validator/test signature, report that fact and add a targeted contract test only when it protects a real data-integrity boundary; do not present unrelated suite count as feature-specific proof.

PR #117 matrix status remains `EVIDENCE_REQUEST_PREPARATION_ONLY`; no evidence has been received by this artifact, and the five candidates remain zero evidence-complete, zero REAL_GOLD and zero SFT-authorized.


## P5-C1 SADA first-case evidence contract (2026-11-17)

The exact source file `DGSI_用户原始5例_正式结论与内部审核分离_v0.1.docx`, page 2, was reopened. It explicitly separates formal conclusion fields from internal-review questions. The SADA source states three current/main-error-voltage drops, shaft/housing temperature maxima, stall during south-array angle adjustment, disc-ring/brush debris arcing and short circuit, and “停用南太阳翼”. It does not state conclusion certainty or confirm execution/effectiveness of the disposal measure.

54. **Build claim-to-evidence maps from the exact formal source section, not from a prior summary.** Preserve source wording, page/section, source certainty and the fault-source/affected-object distinction. Internal-review questions must remain curator-only and must not leak into the model-visible prompt or assistant target.

55. **Do not invent temporal joins between separately reported observations.** “Three drops”, temperature maxima and a stall in the same case description do not establish simultaneity or causal ordering. Require timestamped, channel-identified, time-basis-aware source records before asserting a sequence or cross-channel causal link.

56. **Keep a source-attributed cause distinct from an independently verified cause.** A source fact card can preserve a stated mechanism while marking certainty NOT_EXPLICITLY_STATED and current evidence NOT_RECEIVED. Do not promote it to expert-confirmed or REAL_GOLD solely because the user regards the general localization as plausible.

57. **Disposal text is not proof of execution or success.** “停用南太阳翼” is recorded as a measure in the source; command/state records and post-action status are still needed before the assistant target can say it was executed and effective.

The SADA claim/evidence map is a source-grounded intake artifact only. No actual ML result, diagnostic log, spacecraft context, private telemetry, expert review or SFT target was added.


## P5-C1 SADA curator-channel isolation defect and repair (2026-11-17)

PR #118 initially placed the exact internal-review question text in a top-level `excluded_internal_review_prompts` field in a public claim/evidence JSON. Although the field was named “excluded”, it still physically published curator-only text. PR #119 removed those strings from the current public artifact and retained only opaque references `SADA-IR-01..03` in a Case-root `internal_review` object marked `not_for_sft=true`, with authorized-private-storage declaration. The audit now rejects prompt text at top level, nested in claims, or in a model-target field; it also blocks source-claim/certainty drift, fabricated evidence/ML receipt, disposal execution escalation, unsupported rights approval and Gold/split/training promotion.

Exact-head PR #119 `0ae077e2e72c13cfcfbf14c79e5fb256ec72c0c7`:
- PR workflow `44053399953`: Ubuntu 929/929 PASS; Windows 929/929 PASS.
- Push workflow `44053363689`: Ubuntu 929/929 PASS; Windows 929/929 PASS.
- Both workflows explicitly executed all 17 new `test_p5c_sada_claim_map.py` adversarial tests, including old inline prompt rejection, curator/model channel separation, target injection, certainty escalation, fabricated evidence, disposal escalation, history role, rights and training-gate checks.

The earlier PR #118 head `7712aa50` had passed 912/912 on both platforms, but that full-suite pass did not detect the curator-text publication issue because no dedicated SADA claim-map contract test existed yet. PR #119 closes this specific current-artifact leak; it does not erase prior Git history. Previously committed inline question text may remain accessible in earlier commits. Do not claim historical erasure or privacy remediation is complete solely from a new commit.

58. **A field named “excluded” is not an access-control boundary.** If sensitive/curator-only text is committed to a public artifact, it is published regardless of whether downstream code intends to exclude it. Store only opaque references in public metadata; keep the actual content in authorized private storage.

59. **Enforce channel separation at the data contract and test adversarial injection.** Curator review prompts, evidence requests and adjudication notes must be structurally disallowed from model input and assistant targets. Reject unexpected keys at the root and nested claim levels, not merely by convention or comments.

60. **A green full-suite run cannot prove an untested data boundary.** The 912-test PR #118 run passed but lacked SADA-specific tests. The 17 targeted tests introduced in PR #119 found and now guard the leak. Add contract tests for data-boundary requirements and inspect test signatures, not just total counts.

61. **A current-branch cleanup does not rewrite historical exposure.** Removing text from the latest file does not remove it from earlier Git commits, forks, caches or clones. Report this limitation accurately and assess history remediation separately with repository owners before any destructive rewrite.

62. **Candidate metadata auditors must fail closed on promotion and source drift.** The SADA auditor fixes the case ID, exact source claim text, source certainty, missing-evidence state, disposal status, history role, rights status and admission gates. A successful audit returns BLOCKED_PENDING_REAL_EVIDENCE; it is not a Gold approval or evidence receipt.

The SADA claim-map audit is structural only. It does not authenticate the source, verify actual evidence, establish reviewer identity, or authorize SFT/training. No actual case evidence has been received.


## P5-C2 structural audit of the 15 L1 packets (2026-11-17)

A read-only audit was run against the exact L1 packet collection and L0 source-card snapshot at `10ad4aba6d50ba4635db969725ed6d100ba29584`. It found 15 synthetic packets across 9 event families, all six task types represented (10 diagnostic_synthesis and one each of five specialized types), all REVIEW_REQUIRED, all with declared synthetic ML/log/context provenance, all source refs resolving, and all target evidence refs resolving to declared input evidence IDs. All 15 contain an internal_review subtree marked not_for_sft. All 15 duplicate the assistant target in `case.expected_output` and `formal_target`, equal in this snapshot. Zero split, authorized SFT, REAL_GOLD or training.

63. **Distinguish task-type presence from task-type competence.** One example in a specialized task type proves only that a template exists. Report per-type counts and event-family diversity; do not claim balanced task capability from a six-type checklist.

64. **A not_for_sft flag is not a model-input projection.** The serializer must use an explicit allowlist of model-facing fields and omit the entire internal_review/reviewer/curator/adjudication subtree. A boolean flag on a retained object does not guarantee that downstream serializers will exclude it.

65. **Count independent source event families, not packet variants.** Multiple tasks from the same report/incident remain one source family for split isolation and coverage. A new task type or paraphrase does not create an independent incident.

66. **Structural evidence-reference closure is not evidence validity.** Resolving every evidence ID proves only that a reference points to an input object. It does not prove that the evidence supports the claim, that its timestamp is coherent, or that the source fact is licensed and correct.

67. **Define one canonical assistant target source.** When `case.expected_output` and `formal_target` coexist, require exact semantic equality and serialize only the designated canonical representation. Reject drift rather than editing both copies independently.

68. **Propagate source-rights and review status to every dependent task.** A source card that is pending expert confirmation or training-use rights cannot yield an admitted L1/SFT packet merely because the generated scenario and schema validate. Public accessibility and a green CI do not establish training rights.

The audit report is `examples/p5c2_l1_pilot_structural_audit_2026-11-17.json`; the review explanation is `docs/P5C2_L1_PILOT_STRUCTURAL_AUDIT_2026-11-17.md`. No packets were modified or newly generated by this audit.


## P5-C2 fail-closed model-facing projection preflight (2026-11-17)

**Lesson — filter by construction, not by naming conventions.** A \`not_for_sft=true\` marker is insufficient if a generic serializer copies the parent case. A future model-facing projection must explicitly reconstruct each allowed field and reject curator/reviewer keys at arbitrary nesting depths. The dry-run projection in \`src/dgsi/l1_model_projection_audit.py\` returns only content digests and a blocked state; it never serializes a sample.

**Lesson — classify synthetic inputs at the actual user boundary.** Merely marking a packet's sidecar provenance SYNTHETIC is insufficient for eventual model-facing prompts. The candidate in-memory user view must visibly say that generated ML/logs are synthetic, not real operations or an authenticated ML run. This preflight proves only structural inclusion of that notice, not source/physics validity.

**Lesson — keep release independent of structure.** Even with a canonical target, reviewed instruction allowlist, 12 adversarial tests, L0 ref closure and SHA-256 consistency, the state remains BLOCKED_PENDING_EXTERNAL_ADMISSION. No external source-use authorization, expert authentication, reviewer agreement, official split, or training permission can be inferred from this pass.

**Integration caveat.** This branch is stacked on #121, while #122 is a sibling packet-quality review. Treat these as independent review tracks; reconcile both against the same source/target snapshot and exact CI head before adopting either in an integrated branch.


**CI regression lesson (PR #123 initial head):** The first Ubuntu/Windows run reached 945 tests but failed one new test with \`KeyError: 'notes'\`. L1 packet-level \`review\` uses \`notes\`, while the nested Diagnostic Case-level \`review\` uses \`review_notes\`. The test fixture incorrectly treated their contracts as identical. Repair the test against the actual declared schemas rather than weakening validators or suppressing the test; only the latest corrected head may count as a PASS.


## P5-C2 whole-collection projection audit: CI error-priority lesson (2026-11-17)

When layering collection validation over a per-packet security preflight, **error priority is part of the security contract**. Initial PR #124 tests correctly inserted a nested curator-only field into a candidate model input; the collection schema rejected the extra property first, producing a generic `L1_PROJECTION_COLLECTION_NOT_VALIDATED` rather than the expected `L1_PROJECTION_CURATOR_FIELD_IN_MODEL_SURFACE`. Both platforms failed the same one regression (952/953 passing). The data remained blocked; no curator material was exported.

Fix: inspect known high-risk model-facing input/target subtrees for curator-only keys **before** invoking general collection JSON-schema validation. Keep generic schema failures for other malformed structures. Do not relax source schema, ignore the failure, or rewrite the test to accept a weaker error code. Exact-head Ubuntu/Windows reruns remain required; older runs are not usable as latest-head proof.


## P5-C2 Integrated Completion execution model (2026-11-17)

The user explicitly approved one integrated completion of C2-B through C2-E rather than four serial mini-projects. The milestone is now defined in `docs/P5C2_INTEGRATED_COMPLETION_2026-11-17.md` and `examples/p5c2_integrated_review_contract_2026-11-17.json`.

75. **Run scientific review, target review, model projection and coverage analysis as coordinated workstreams.** Do not release each as a separate long-running tool milestone. Freeze one baseline, review all packets, apply bounded corrections to a new immutable collection, then run projection/round-trip and coverage checks over the same candidate snapshot.

76. **Keep engineering review, expert adjudication, rights clearance, SFT authorization and actual training as distinct states.** A structurally valid or curator-reviewed synthetic candidate is not Gold. Do not let a successful projection preflight silently grant export or training permission.

77. **Use one canonical Assistant Target throughout the pipeline.** Review `formal_target` as the authoritative target; require `case.expected_output` to remain semantically equal, and serialize only the canonical representation. This prevents dual-source drift during correction and export.

78. **Coverage must be reported at packet and independent event-family levels.** A new task type, paraphrase or second task from the same source family does not create an independent incident. Split isolation must follow event-family and incident lineage, not row count.

79. **Make the final candidate reproducible as one immutable collection snapshot.** Bind collection membership, task/case IDs, L0 public fact-card content, event-family grouping, model-visible input projection and canonical target digest. Any change creates a new candidate version and invalidates the previous review/projection receipts.

80. **Do not fill source-rights or expert-review gaps with engineering assertions.** Public availability, correct schema, source citation and passing CI do not establish permission for third-party training or independent domain correctness. Quarantine unresolved source families and report the resulting coverage gap honestly.

81. **A blocked metadata-only projection can be a valid engineering deliverable.** It can prove allowlist behavior, deterministic serialization, round-trip integrity and zero leakage while intentionally emitting zero SFT rows. This is preferable to relaxing admission gates to create an apparently complete dataset.


## DGSI Skill is a co-equal product deliverable (2026-11-17)

The user clarified that DGSI must deliver both a usable candidate dataset and the reusable generation Skill/toolkit. The Skill cannot be treated as incidental documentation or left behind after dataset work.

82. **Treat the generation Skill and dataset as co-equal release artifacts.** The dataset is one output; the Skill, references, schemas, validators, tests and packaging workflow are the repeatable production capability. A dataset handoff without its matching Skill/toolkit is incomplete.

83. **Package the exact workflow, not just the main Skill entrypoint.** The portable ZIP must include the integrated C2-B/C2-C/C2-D/C2-E reference, pinned contracts, relevant validators and tests. Verify the archive manifest and execute offline tests after extraction without repository PYTHONPATH.

84. **Keep Skill release state independent from dataset admission.** The Skill can be packaged as a draft production tool while source rights, expert adjudication or SFT authorization still block candidate data. Never make the Skill's package build a surrogate for data approval.

The DGSI Skill is being advanced to `0.2.0-rc.1` with an integrated dataset-production workflow. Its package regression now asserts that the integrated workflow reference and manifest contract are included. The dataset remains blocked pending expert/rights admission.


## P5-C2 integrated packet review and candidate correction (2026-11-17)

A curator-level review was applied to all 15 literature-derived synthetic packets. It found the historical L0 evidence-role problem in every packet, not only the five specialized tasks.

86. **Apply evidence-role rules to the whole collection, not only the first failing examples.** A defect discovered in one task family must trigger a collection-wide scan for the same field-role pattern. Fixing only specialized examples leaves the same leakage/attribution defect in the remaining diagnostic-synthesis packets.

87. **Keep source-use status separate from technical source accessibility.** Public NASA/NTRS access, a public abstract or a downloadable paper does not automatically establish third-party derivative or model-training permission. Track rights review per source family and quarantine unresolved sources from SFT authorization.

88. **Do not fill a coverage gap by paraphrasing a blocked source.** When specialized task types are weakly represented but source families are rights-blocked or lack independent episodes, report the gap and defer generation. A valid correct-abstention task must arise from a genuinely underdetermined, source-supported scenario, not an invented incident.

89. **A candidate correction must preserve scenario provenance and change only the intended semantic fields.** For the C2 integrated candidate, only current-vs-historical evidence reference roles, two Pathfinder history compatibility values, collection ID/status and canonical target binding are changed. Preserve source facts, synthetic values/logs, timestamps, task types, event-family IDs, certainty and disposal.

The integrated review candidate is `examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json`; dispositions are in `examples/p5c2_packet_review_dispositions_2026-11-17.json`; coverage decisions are in `examples/p5c2_coverage_gap_report_2026-11-17.json`. All remain curator-reviewed candidates only, with zero expert approvals, zero rights-cleared families and zero SFT records.


90. **Separate a three-message engineering preview from an SFT record.** A C2-D deliverable can expose actual system/user/assistant surfaces for review while keeping `split=null`, `preview_only=true`, `export_authorized=false` and `sft_records_emitted=0`. Do not force a preview through an SFT schema requiring an official split or approval. Validate deterministic round-trip and canonical-target equality; never place preview artifacts in a training directory.

The implementation is `src/dgsi/l1_model_projection_preview.py`, CLI `scripts/create_l1_model_preview.py`, test `tests/test_l1_model_projection_preview.py`.
