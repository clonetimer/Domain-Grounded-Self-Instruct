# DGSI development experience: optional Python dependencies and cross-platform CI

Date: 2026-11-16
Incident: OCR candidate extraction PR #88 / correction PR #89
Scope: reusable engineering lessons; no user-specific source material.

## Incident summary

The first OCR candidate implementation passed neither Ubuntu nor Windows CI. Both platforms ran 771 tests and failed the same test:
`test_ocr_records_words_boxes_hash_and_review_boundary`.

The production extractor used normal package imports:

```python
import pytesseract
from PIL import Image
from pytesseract import Output
```

The test double registered `pytesseract.Output` as a separate `sys.modules` entry and represented `pytesseract` / `PIL` with `SimpleNamespace`. This did not reproduce Python's package import semantics: `from pytesseract import Output` resolves an attribute from the imported package, not an independently registered dotted module. The import failed, and the production code correctly returned its optional-dependency error. The failure was in the test harness, not evidence that OCR runtime dependencies were missing on the CI workers.

## Corrective change

PR #89 uses `types.ModuleType` package/module doubles:
- `pytesseract` is a module with `image_to_data`, `get_tesseract_version`, and an `Output` attribute.
- `PIL` is a package module with an `Image` submodule/attribute.
- The test asserts the `Output.DICT` value is actually passed to `image_to_data`.
- The explicit missing-dependency test remains, so optional dependency failure is still fail-closed.

Exact-head PR CI then passed on both operating systems: Ubuntu 771/771 and Windows 771/771.

## Reusable engineering rules

1. **Mock import semantics, not just object shape.** If production uses `import package`, `from package import symbol`, or `from package.submodule import symbol`, tests must model the corresponding package/module hierarchy and attributes.
2. **Do not make optional runtime dependencies mandatory just to satisfy a unit test.** Test the adapter with realistic package doubles; separately test the explicit missing-dependency path.
3. **Separate three validation layers:** dependency import, adapter invocation/argument contract, and output semantics/schema. A test should identify which layer failed.
4. **Treat cross-platform parity as evidence, not assumption.** The same failing test on Ubuntu and Windows often indicates a shared test fixture or contract error; inspect both logs before changing platform-specific code.
5. **Keep failure codes stable and payload-free.** Dependency absence should have one explicit code; do not silently fall back to fabricated OCR text.
6. **Test the adapter boundary with observable calls.** Assert the expected image, language, page segmentation mode and output type were passed to the OCR library.
7. **Do not infer OCR or visual understanding quality from mocked tests.** Mock tests establish integration contract only. Real image accuracy requires a labeled figure benchmark with word/line metrics and engineering-term error analysis.

## DGSI-specific safeguards

- OCR output is a text/geometry candidate, never a verified node, port, arrow or physical relation.
- OCR lines remain `MANUAL_REVIEW_REQUIRED`.
- Asset SHA-256 binds OCR output to the exact image bytes.
- The generation AI does not receive hidden simulator truth or QA-only injection labels.
- No OCR output is Gold or SFT-ready without source review and independent engineering adjudication.

## Verification record

- Failing head: `a3c195ce3b2fca062e6bd54efd0e4d901fdbfc2f`
- Corrected head: `d99c3a09e176c04feb08b09a79e030c7c582d6b2`
- PR workflow: `43877926706`
- Ubuntu: 771/771 PASS
- Windows: 771/771 PASS
- Original push workflow on corrected head: `43877896425`, both platforms PASS

This record documents the cause and repair. It does not claim a real Tesseract OCR benchmark or validate diagram interpretation.

## Follow-up: deterministic OCR input preflight (P5-B3)

The OCR adapter's next hardening step validates caller-controlled inputs before importing optional OCR packages or invoking the Tesseract executable.

The accepted boundary is explicit:
- reject empty image files and files larger than the configured 40 MiB limit;
- reject boolean values where an integer PSM is required (Python's `bool` is an `int` subclass);
- constrain PSM to the documented 0–13 range;
- accept only explicitly supported language codes;
- bound decoded image dimensions to 100 million pixels.

Reusable rules:

8. **Validate before side effects.** Cheap, deterministic file and option checks should run before optional imports, image decoding where possible, or external executable calls.
9. **Account for Python's type hierarchy.** Use exact-type checks when booleans must not pass integer validation; `isinstance(value, int)` alone accepts `True` and `False`.
10. **Bound both compressed input and decoded work.** A byte-size limit does not prevent decompression or image-dimension resource exhaustion; enforce decoded-pixel limits as a separate control.
11. **Use allowlists for external-tool options.** Language identifiers and mode ranges should be explicit contracts, not arbitrary strings passed through to a local executable.
12. **Test rejection before invocation.** For every invalid input, assert the OCR engine was not called; otherwise the test proves only that an error was eventually returned.

These checks establish input-contract and resource-boundary behavior only. They do not establish OCR accuracy, diagram topology, node/port/arrow recognition, or engineering semantics. Keep extracted OCR text and geometry as review-required proposals; preserve source-image hashes and human adjudication requirements.

## Verification update: development-experience record CI

The follow-up documentation commit `13bd95556178d258b4dd52d69cf17c75fb6f5cc9` completed the repository's cross-platform quality workflow:

- Workflow: `43885131789`
- Windows: 771/771 tests, PASS
- Ubuntu: 771/771 tests, PASS
- Both jobs also completed the candidate smoke checks successfully.
- The blind Skill pressure and holdout runners executed in dry-run mode: 13/13 and 8/8 cases enumerated respectively, with zero network calls and no model/API credentials configured.

Interpretation:
- The 771-test suite confirms repository regression integrity for this documentation update; it is not an OCR image-accuracy benchmark.
- Candidate smoke output `CANDIDATE_CHECKS_PASSED` remains structural/rule-based only and does not imply factual correctness, causal proof, authenticated review or Gold eligibility.
- Dry-run enumeration confirms local protocol/configuration readiness only; it is not a live cross-model evaluation.

Additional reusable rule:

13. **Separate CI health from product evidence.** A green full suite, a passing candidate smoke, and a dry-run evaluation each establish different claims. Report their scopes separately; never combine them into an accuracy, expert-acceptance, or model-performance claim.

## Integration incident: green sibling CI does not prove stacked lineage coverage

On 2026-11-16, P5-B4 integration review identified that the P5 OCR/diagram stack did not contain all previously validated P4 cross-collection lineage guards. The P4 sibling changes had passed independently, but the P5 branch lineage module was older. This is a branch-integration defect, not a failure of the individual P4 implementations.

PR #93 carries the tested lineage guards into the P5 stack and adds 15 `SYNTHETIC_TEST_ONLY` regressions. The integrated guards bind:
- one upstream run reference to one immutable diagnostic-log snapshot;
- one upstream run reference to one spacecraft/mission context snapshot;
- one Case ID to one real/synthetic track;
- one diagnosis-run reference to one real/synthetic track.

The context fingerprint intentionally excludes historical Context, review notes, task targets and analysis-cutoff variants; those may legitimately vary without rewriting the current run's physical/operational snapshot.

Exact workflow evidence:
- Workflow: `43888738459`
- Ubuntu: 771/771 PASS
- Windows: 771/771 PASS
- Both jobs completed the adversarial test and candidate smoke step successfully.

Reusable integration rules:

14. **Test the assembled branch, not just its component PRs.** A passing sibling PR cannot establish that its guard is present in the active feature stack. Recheck ancestry and exact file content at every integration boundary.
15. **Fingerprint identity at the correct scope.** Run-scoped fingerprints should bind immutable ML output, diagnostic logs and physical/operational context; task-specific target and time-safe historical Context should remain outside that fingerprint.
16. **Separate case identity from event-family identity and run identity.** A shared source event family can support distinct tasks, but Case IDs and run references must not be reused across real/synthetic tracks.
17. **Exercise order independence.** Adversarial lineage tests should reverse collection order to ensure the result does not depend on which conflicting record is processed first.

Scope: these are structural lineage protections. They do not authenticate source provenance, establish physical truth, validate IP rights or grant Gold/SFT authorization. The 771-test CI is not evidence of OCR/diagram extraction accuracy.

## CI attribution correction: require test-signature evidence for the exact PR head

A subsequent successful workflow, `43888738459`, reported Ubuntu and Windows 771/771. Log inspection showed that it contained neither of the new P5 integration test modules (`test_l1_global_run_log_snapshot`, `test_l1_global_run_context_snapshot`, `test_l1_global_track_identity`). Its test count also remained identical to the earlier 771-test workflow. Therefore it cannot be used as evidence that PR #93's 15 new lineage regressions ran, even though the workflow itself was green.

Reusable rule:

18. **Attribute CI by exact head and test signature, not by time proximity or green badge.** Verify the workflow's tested commit/head, expected newly added test names, and expected test-count delta. If any is absent, report the workflow as green but the PR acceptance as unverified; trigger or await exact-head CI rather than inferring coverage.

This correction is intentional: do not overstate PR #93 acceptance from workflow `43888738459`. The new P5-B4.1 branch includes the P4 guards and their tests in its source tree; its own exact-head CI remains the acceptance gate.
