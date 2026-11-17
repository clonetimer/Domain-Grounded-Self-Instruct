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
