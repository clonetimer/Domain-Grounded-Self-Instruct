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
