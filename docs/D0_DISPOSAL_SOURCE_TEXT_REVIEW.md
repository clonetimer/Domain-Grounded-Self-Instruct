# D0/P3 — Local human adjudication of disposal source text (2026-11-15)

## Scope and precedence

Product scope is LLM **secondary diagnosis** from upstream ML findings, diagnostic logs, spacecraft/mission context, and historical experience. Raw telemetry remains upstream. This is an optional **local, fail-closed review gate** following the Case/SFT structural disposal-reference checks in PR #36. It is **not** an automated language-semantic proof or Gold approval.

PR #36 checked that a disposal measure cited an existing log or knowledge passage. However, a valid citation may refer to an alarm or background narrative that never documents the claimed action. A log ID alone is therefore insufficient for expert sign-off.

## Review packet (local-only, NOT for SFT)

The review packet lives outside the Case and SFT prompt/target. It is a human-attestation **claim**, not the source of truth. Set `not_for_sft=true`. It contains:

- `schema_version=dgsi-disposal-source-review.v1`, `case_ref`, `reviewer_id`, `reviewer_role=INDEPENDENT_DOMAIN_EXPERT`, `reviewed_at`, `attestations`.
- Exactly one attestation per source-documented disposal measure, indexed by `measure_index`.
- `measure_sha256` computed over the exact UTF-8 bytes of the Case's `measure` string, binding the adjudication to unchanged wording.
- `evidence_ref` from that measure's recorded source references; `verbatim_excerpt` must be a literal substring of the cited log content or supplied knowledge-evidence excerpt.
- `source_action_type` equal to `EXECUTED`, `PLANNED`, or `RECOMMENDED`, matching the Case.
- `verdict=SUPPORTED` for expert acceptance; other verdicts block the gate.
- For a knowledge passage, a separately verified `source_published_at` time. Logs use their recorded timestamp; unknown-time execution logs fail closed.

The validator checks literal excerpt binding, index uniqueness, measure-digest identity, source type, source timing as of the diagnostic decision cutoff, and explicit expert sign-off. It rejects unreviewed, mismatched or future-source actions.

**Caution:** Exact passage inclusion is a necessary but insufficient condition for factual semantic support. The reviewer must confirm that the excerpt explicitly documents the same action, modality (executed vs planned vs recommended), subject, and event. The tool cannot verify credentials, permissions, authenticity of original logs, source publication dates, or reviewer independence. A self-declared reviewer role does not establish identity. This gate never automatically sets Case/SFT review status to `APPROVED` or Gold.

## Use on authorized workstation

```bash
PYTHONPATH=src python scripts/audit_disposal_source_review.py \
    --case /authorized/local/case.json \
    --review /authorized/local/disposal_review.json
```

Only fixed error codes or aggregate counts are printed. Neither input content, local paths, document excerpts, hashes nor case IDs are emitted. Keep the case data, review packet, and expert identity records within their authorized storage; **do not commit them** to the public repository.

When a record does not mention any historical disposal, preserve `disposal_status=NOT_RECORDED`, `disposal_measures=[]`, and use an empty attestation list. Any new check proposed by the LLM belongs exclusively in `follow_up_actions`.

## Required human-source workflow

1. Preserve user-supplied 5 cases and public literature cases as L0 source fact cards, distinctly labelled as real flight incident, ground test, engineering simulation, literature synthesis, or synthetic test.
2. Check source authenticity/IP permission/redaction, whether the literal original source supports each phenomenon, fault-source localization and affected component, action and its time, and whether the expert review is independently evidenced.
3. For any L0 record lacking upsteam ML result, logs, mission context or confirmed source cause, leave these fields missing/blocked. Do not hallucinate a run, score, score calibration, flight log or expert target.
4. If a true case has a source-documented disposal, review each cited passage locally, bind digest and evidence, and record an independently supported source-action status; otherwise mark `NOT_RECORDED`.
5. Only after a complete and authorized Case passes all other provenance, as-of, run-lineage, split-isolation and expert review gates may its SFT eligibility be considered. This tool's PASS is not approval.

All committed examples and tests in this stage are explicitly **SYNTHETIC_TEST_ONLY**. No restricted R21 data, private user-case notes or expert excerpts were added.
