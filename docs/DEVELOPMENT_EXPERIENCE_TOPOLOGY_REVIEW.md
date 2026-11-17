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


## P5-C2 specialized L1 target review (2026-11-17)

Reviewed the five one-example specialized task types: Pathfinder conflict reconciliation, FUSE/Cassini history reuse, Pathfinder evidence sufficiency, Cassini next-step recommendation and S-band TWTA handover. Found two concrete data-quality defects and several positive source-logic checks.

69. **Keep source-grounding context separate from current-scenario supporting evidence.** A literature L0 passage can establish what the historical source reported and constrain certainty/mechanism; it does not become direct evidence for the current synthetic diagnostic scenario. Do not place a context-only L0 knowledge-evidence ID in current-event `supporting_refs`. Keep it in a separately bounded source/context field; keep current synthetic ML/log refs explicitly labeled synthetic.

70. **Hardware compatibility is not implied by shared equipment/interface labels.** If the history record itself says hardware differs or the exact design is unknown, do not mark COMPATIBLE merely because the broad equipment_scope string matches. Use UNKNOWN and preserve transfer limitations until component design, materials, interfaces and operating envelope are compared.

71. **A specialized task's one example is a template demonstration, not competence evidence.** Maintain separate counts for task-type presence, event-family diversity and independent reviewed target count. Do not create paraphrases to make a sparse task type appear statistically supported.

72. **Preserve distinct failure episodes and vendor/source attribution in history-reuse targets.** FUSE 2000 pitch-wheel Kapton-liner hypothesis, 2001 yaw-wheel similar event, later thermal-distortion failures and Cassini low-speed lubricant redistribution must remain distinct mechanisms/episodes with their original certainty and compatibility limitations.

73. **Review target report semantics against the structured target, not only JSON equality.** A report_text field may be a task-specific concise handover/recommendation rather than a literal concatenation of every structured field. Check that it preserves all material conclusions and does not introduce claims, while allowing intentional task-specific compression.

74. **Use immutable review-candidate collections for bounded corrections.** Keep the prior packet snapshot unchanged, create a versioned candidate collection, record exactly which fields changed, and run the existing validator plus targeted tests. Do not overwrite the baseline or imply approval from structural validation.

The v0.2 review candidate removes context-only L0 refs from current supporting refs in five specialized tasks and changes rejected Pathfinder history hardware compatibility from COMPATIBLE to UNKNOWN. It does not alter source facts, synthetic scenario values, conclusions, certainty, disposal, event families or task count. All packets remain REVIEW_REQUIRED and training-disabled.
