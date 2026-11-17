# Development experience: topology evidence review

Continuation of DEVELOPMENT_EXPERIENCE_OPTIONAL_PYTHON_DEPENDENCIES.md.
Scope: P5-B4.3c and B4.4, plus cross-track CI review, 2026-11-17.

## Baseline attribution

P5-B4.3c head 9ce3c387a7edfc646e39c3d40337383a6b782fd5 (PR #110): PR workflow 44018907359 and Push workflow 44018860199; Ubuntu and Windows SUCCESS, 881 tests each. PR jobs tested synthetic merge bfe6f92d895a889e5faff2b0509a61cf67e7e37d, not a direct checkout of the feature head.

P4 history direct-evidence fix PR #109, head 330a132bf004ce0c19fc43b1fa063087cb51c9f3, workflow 44018120012: Ubuntu and Windows SUCCESS, 876 tests each. This is a separate P4 branch, not automatically integrated into P5.

## Reusable rules

33. **Bind evidence to the individual claim and object.** A drawn connector does not establish direction or engineering medium. Port label, direction, medium, unit, connector existence, edge direction and relation type require separate subject/field-bound evidence.
34. **Unknown direction must not become a directed graph edge.** Keep direction-unknown links in an unresolved sidecar.
35. **Preserve typed evidence through conversion.** Keep complete receipts and canonical hashes; do not promote receipt consistency to authenticated inspection or engineering truth.
36. **Test actual CLI failure paths.** Exercise invalid UTF-8, duplicate keys, non-finite values, oversized inputs, missing output directories, overwrite refusal and payload-free errors.
37. **Regex validation must consume the entire identifier.** A pattern ending in $ may accept a trailing newline; explicitly prohibit CR/LF.
38. **Distinguish isolated tests from full repository integration.** A local subset is not a full regression. Run actual toolkit ZIP/detached execution and both OS full suites on the feature branch.
39. **Inspect both PR and Push workflows.** Attribute each run to event, exact SHA, branch and PR, then inspect both matrix jobs.
40. **Verify test signatures and counts on both platforms.** Inspect logs for newly added test names and detached package integration; a green badge alone is insufficient.
41. **Keep cross-track fixes separate until integration is proven.** PR #109 forbids retrieved history refs, history source refs and prior verification refs from directly supporting/contradicting current-fault diagnosis. Preserve historical relevance only in its dedicated context field. Its 876-test CI does not prove the guard exists in P5.
42. **Freeze dependency snapshots; never silently refresh old receipts.** Each derived diagram artifact binds exact parent hashes. A changed upstream artifact invalidates descendants; regenerate downstream artifacts and issue new immutable review records.
43. **Make invalidation directional and test unaffected branches.** Source mutation invalidates descendants; leaf mutation does not invalidate ancestors; middle mutation invalidates only its downstream subgraph.
44. **A consistent manifest is not proof of semantic derivation.** A dependency DAG verifies bytes and declared snapshots, not whether a child was truly derived from those parents or whether a human reviewed the source.

## P5-B4.3c CI interpretation

The 881-test suite includes 43 new feature/CLI tests plus a full-toolkit ZIP test that verifies package manifest hashes, extracts the archive, removes repository PYTHONPATH, and executes the dedicated tests from the detached package. Both platforms ran the full suite. Fixtures are synthetic and establish structural, evidence-binding, CLI and packaging contracts only.

P4 #109 separately passed 876/876 on both platforms. Its historical-context guard is not presumed integrated into P5. Candidate smoke remained structural-only; blind pressure/holdout runners remained DRY_RUN with zero model calls.

## P5-B4.4 verification boundary

The artifact dependency snapshot auditor verifies declared file bytes, dependency graph structure, frozen dependency digests, safe relative paths and directional invalidation. It does not inspect image pixels, authenticate reviewers, prove child derivation or authorize Gold/SFT/training. Fixtures are SYNTHETIC_TEST_ONLY.

## P5-B4.4 first CI failure: schema gate masked the semantic duplicate-dependency code

The first B4.4 exact-head CI ran 906 tests on Ubuntu and Windows; both platforms failed the same two tests. The root failure was test_duplicate_dependency: JSON Schema rejected the repeated dependency earlier via uniqueItems and returned ARTIFACT_LINEAGE_MANIFEST_INVALID, while the semantic test expected ARTIFACT_LINEAGE_DUPLICATE_DEPENDENCY. The portable detached-package test failed only because it reran this same failing unit test; it was not a separate packaging defect.

Correction:
- Remove uniqueItems from the schema-level depends_on array constraint so the semantic validator owns the stable duplicate-dependency error code.
- Add semantic rejection for duplicate artifact paths, preventing two artifact IDs from aliasing one local file.
- Explicitly reject CR/LF in local artifact paths; JSON Schema regex end anchors can accept a trailing newline in some regex engines.
- Add direct regressions for duplicate paths and trailing-newline paths, then rerun both platform suites and detached package execution.

Reusable rule 45:
**Do not let schema and semantic validators compete for the same error contract.** If callers/tests require a stable semantic error code, keep the schema permissive enough to pass that shape to the semantic layer, or explicitly assert the schema-level error. Test the intended rejecting layer, not merely that malformed input is rejected.
