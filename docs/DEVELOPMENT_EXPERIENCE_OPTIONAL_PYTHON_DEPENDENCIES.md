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

## CI failure: test method placed after the module entry point

During P5-B4.1 review, the new OCR preflight regression was appended after:

```python
if __name__ == "__main__":
    unittest.main()
```

The method retained class-method indentation, so Python encountered an unexpected indent at module scope during test-module import. This is a test-file structure/syntax defect, not a production OCR failure.

Correction:
- Move the regression method back inside `OcrCandidateTests`.
- Keep the `unittest.main()` guard as the final module-level statement.
- Verify the exact file tail and ensure CI discovers the test by its full test name.

Reusable rule:

19. **Insert tests at the correct syntactic scope.** When extending compact test modules, inspect the class boundary and module entry-point guard before appending. Run compile/import or a focused test command before launching full cross-platform CI; verify newly added test names appear in the CI log.

The failure reinforces that a passing prior workflow cannot validate code added afterward. Exact-head CI must run after every test-source change.

## P5-B4.1 exact-head CI: nested OCR geometry and source-level failure propagation

The corrected provenance implementation completed exact-head cross-platform CI:

- Exact head: `d91b6e4bf8023e2060f69af5ace2729bd5b554dd`
- PR workflow: `43904056941`
- Ubuntu: 798/798 PASS
- Windows: 798/798 PASS
- Both logs contain the two new provenance regressions:
  - `test_empty_ocr_line_id_rejected`
  - `test_ocr_word_boxes_must_fit_inside_parent_line`

The additional checks close two distinct geometry gaps:
1. A whitespace-only OCR line ID is not a usable evidence identity, even if it is technically a non-empty string.
2. A word box can be inside the image but outside its declared parent line box. Image-bound checks alone are insufficient; nested geometry must be validated.

A subsequent review also identified a source-level state propagation gap: a document manifest marked `BLOCKED` must not become admissible merely because a separately extracted asset and OCR record have matching hashes. PR #95 adds an explicit fail-closed check before asset processing. A source-level rejection status takes precedence over child artifact consistency.

Reusable rules:

20. **Validate geometry at every containment level.** Check image bounds, line bounds, and word-within-line bounds independently; a child can be image-valid but parent-invalid.
21. **Reject semantically blank identifiers.** Whitespace-only IDs pass basic non-empty string checks but cannot provide stable evidence identity.
22. **Propagate parent failure states to child workflows.** A matching child hash cannot override a source/document manifest marked BLOCKED. Validate parent admission status before expensive or downstream processing.
23. **Do not stop at one green workflow when later commits extend the same PR.** Re-verify the latest head, exact new test names and both platform logs; earlier green commits do not validate later geometry or source-state changes.

These tests prove structural consistency and fail-closed behavior only. They do not prove OCR accuracy, diagram semantics, source authenticity or training eligibility.

## P5-B4 source-state regression: BLOCKED parent cannot be rescued by matching child hashes

PR #95's exact-head workflow `43908433433` completed successfully:
- Ubuntu: 800/800 PASS
- Windows: both matrix jobs SUCCESS (same exact head)
- Ubuntu log explicitly contains `test_blocked_source_manifest_cannot_pass_even_with_matching_asset_hashes`.

The regression confirms that a source manifest marked `BLOCKED` remains blocked even when the separately extracted image bytes and OCR record have matching SHA-256 values. The source-level extraction state is authoritative for downstream admission.

Reusable rule 24:

24. **Keep integrity and admissibility separate.** Matching hashes prove byte identity between referenced artifacts; they do not reverse a parent source's rejection state, grant processing permission, or establish source validity. Every downstream stage must enforce upstream admission status before using child artifacts.

## P5-B4.2a exact-head CI: local text-region CLI and portable bundle

Exact head `412f327545c47b5ffd07397bb6ba596a696fb18b` completed workflow `43991124346`:
- Ubuntu: 812/812 PASS
- Windows: 812/812 PASS
- Both logs contain all three new CLI regressions:
  - `test_writes_local_review_required_output_without_echoing_ocr_text`
  - `test_refuses_to_overwrite_existing_output`
  - `test_blocked_source_emits_payload_free_error`
- Both logs contain `test_full_toolkit_zip_contains_run_receipt_module_and_is_not_user_data` and `test_required_portable_files_exist`.
- Candidate smoke is explicitly `PASS_STRUCTURAL_ONLY`; blind pressure and holdout runners remain `DRY_RUN`, with no external model calls.

Reusable rule 25:

25. **Test the user-facing CLI and detached package, not only the Python function.** A pure-function test cannot catch argument wiring, output overwrite, stdout leakage or missing portable files. Add subprocess tests for exit codes, payload-free stdout and filesystem effects, and a ZIP-level regression that opens the generated archive, checks the allowlist and verifies every manifest hash.

The 812-test result confirms the code and packaging contracts on these two CI platforms. It does not establish OCR recognition accuracy or engineering-semantic correctness.

## P5-B4.2b implementation note: preserve actual line boundaries in grouped OCR text

While reviewing the new two-line grouping implementation before CI, a source-generation escaping issue was found: the join expression initially used a literal backslash-plus-`n` rather than an actual newline separator. The implementation and regression expectation were corrected before the CI run.

Reusable rule 26:

26. **Test serialized text semantics, not just candidate membership.** For multi-line OCR hypotheses, assert the exact separator and ordering in the emitted text, alongside source line IDs and geometry. Escaping mistakes can preserve candidate counts and IDs while silently corrupting the reviewer's displayed label.

The pair grouping remains a geometric hypothesis only. The original single-line candidates are retained, and no component semantics are inferred.

## P5-B4.2b CI failure: stale recipe assertion after versioned behavior change

Workflow `43997986946` failed on both Ubuntu and Windows at the same single assertion:
`test_candidates_are_exact_unresolved_ocr_text_only` expected `isolated-ocr-line-v1`, while the implementation and JSON Schema correctly emitted `isolated-lines-plus-pair-hypotheses-v2`.

The four new pair-hypothesis tests were not the cause. The failure was a stale test expectation left behind when the generation recipe was deliberately versioned to include the new two-line hypothesis behavior. The implementation, schema and test contract must advance atomically when a behavior-affecting recipe version changes.

Correction:
- Update the expected recipe assertion to `isolated-lines-plus-pair-hypotheses-v2`.
- Keep schema and runtime recipe constants aligned.
- Retain explicit tests for singleton preservation, pair generation, distance/overlap rejection, order independence and exact newline serialization.

Reusable rule 27:

27. **Versioned behavior changes require atomic contract updates.** When a generator recipe/version changes, update runtime constants, JSON Schema, golden fixtures, test assertions, documentation and package manifest in one change set. Add a test that asserts the runtime recipe equals the schema contract; do not rely only on a hand-maintained expected string in one test.

The failure is a regression-test synchronization issue, not a cross-platform implementation difference: both operating systems failed identically at the same stale assertion.

## P5-B4.2b CI follow-up: adversarial geometry fixture violated its own image bounds

After the stale recipe assertion was corrected, the next exact-head run failed on one new adversarial test on both platforms: `test_pair_hypothesis_only_uses_adjacent_vertical_lines`. The fixture placed a 120-pixel-wide synthetic word/line box at x=150 in a 200-pixel image, so the provenance validator correctly rejected it with `DIAGRAM_OCR_BOX_OUT_OF_BOUNDS` before the adjacency algorithm was reached.

This was a test-fixture construction defect, not a production grouping failure. The fixture now narrows the unrelated middle line to 40 pixels, keeping it within the image while preserving the intended horizontal separation.

Reusable rule 28:

28. **Make adversarial fixtures valid up to the invariant under test.** A test intended to exercise grouping order or adjacency must first satisfy source hash, image bounds, parent-child geometry and schema invariants. Otherwise an earlier fail-closed gate masks the behavior being tested. Add fixture self-checks or comments showing why each geometry is valid.

## P5-B4.2b final exact-head CI and fixture correction

The corrected P5-B4.2b head `9299ccfb0f9e8b9aeb855c653de5ed6f5cf2d261` completed workflow `44005948905`:
- Ubuntu: 818/818 PASS
- Windows: 818/818 PASS
- Both logs contain the new recipe/schema parity and adjacent-line grouping tests.
- Both logs contain portable ZIP and required-file regression checks.

The first failure was a stale v1 recipe assertion; the second was an out-of-bounds synthetic test fixture. Both were corrected and independently re-run. This confirms why a failure must be diagnosed at the first rejecting layer: the second failure was caught by the provenance gate before the adjacency behavior under test could execute.

Reusable rule 29:

29. **Make the review receipt's trust level explicit in the result vocabulary.** A locally supplied reviewer alias and timestamp can be bound to a candidate record, but cannot authenticate identity, role, signature or actual inspection. Report `REVIEW_RECEIPT_BOUND_NOT_AUTHENTICATED`; do not emit `HUMAN_APPROVED`, `VERIFIED`, Gold eligibility or SFT authorization from metadata binding alone.
