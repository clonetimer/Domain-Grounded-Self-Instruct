# D0 / P4: REAL evidence-submission binding preflight (local only)

This is a deliberately narrow **submission** gate, not evidence verification or case admission.
It closes the gap between the v0.5 unverified REAL candidate request queue
(`real_review_queue_preflight.py`) and later independently audited source/ML/expert receipts.

## Usage

Only for explicitly authorized, local, metadata-only JSON inputs:

```bash
PYTHONPATH=src python scripts/audit_real_evidence_submissions.py /path/to/real_queue_v0.5.json /path/to/local_submission_manifest.json
PYTHONPATH=src python -m unittest discover -s tests -p 'test_real_evidence_submission_preflight.py'
```

The tool does not open files referenced by evidence artifacts, access private repositories,
make any network calls, write files, emit sensitive source paths/refs or upload data.
The returned JSON reports **aggregate declared submissions**, never verified evidence.
The original v0.5 queue must first pass its unverified-only preflight.

## Manifest contract: `dgsi.local-real-evidence-submissions.v1`

Required root keys only:

- `schema_version` = `dgsi.local-real-evidence-submissions.v1`
- `classification` = `LOCAL_REVIEW_WORKSPACE_ONLY`
- `candidate_count` = exact length of the v0.5 queue's `cases`
- `not_for_sft=true`, `gold_eligible=false`, `training_authorized=false`,
  `split_assignment_allowed=false`
- `cases`: exact same case IDs and `source_case_sha256` as the queue

Each case has exactly `case_id`, `source_case_sha256`, `not_for_sft=true`, and
`submissions`. The latter contains exactly one entry for each of the nine
`verification_checklist` dimensions used by the v0.5 REAL queue.

Each dimension entry has exactly `check_id`, `status`, `artifacts`,
`not_for_sft=true`. `status` can only be `NOT_SUBMITTED` (empty artifacts) or
`SUBMITTED_FOR_REVIEW` (at least one artifact). No `VERIFIED`, `APPROVED`,
`Gold`, expert adjudication or training authorization is accepted.

Each artifact holds exactly `evidence_ref`, `evidence_sha256` (64 lowercase hex
characters) and `evidence_type`. The type must match the check:

| Check | Allowed evidence_type |
|---|---|
| SOURCE_RIGHTS | SOURCE_PERMISSION_RECORD |
| DEIDENTIFICATION | DEIDENTIFICATION_REPORT |
| EVENT_FAMILY | EVENT_FAMILY_RECORD |
| UPSTREAM_ML | ML_RESULT |
| LOGS_CUTOFF | DIAGNOSTIC_LOG, ANALYSIS_CUTOFF_RECORD |
| MISSION_CONTEXT | MISSION_CONTEXT |
| HISTORY_ASOF | HISTORY_ASOF_RETRIEVAL |
| EVIDENCE_DISPOSAL | EVIDENCE_LINK, DISPOSAL_RECORD |
| BLIND_EXPERT | BLIND_REVIEW_REQUEST |

Evidence refs must resolve consistently to **one claimed digest and one evidence type**
across the bundle. Reusing a ref with another evidence type is rejected, even
if both declarations have the same digest. ML results, diagnostic logs, analysis
cutoff receipts, historical as-of retrievals and blind-review requests are
**case-scoped**: the same ref cannot be claimed by different REAL candidates.
This avoids double-counting a shared run/log or reviewer request as distinct
case-specific evidence. Shared permission records, deidentification reports,
mission context and event-family documents may remain cross-case when
legitimately applicable, pending independent applicability review.
A multi-episode shared run requires separately scoped, attributable receipts
before submission; this guard never infers unique runs from different refs.

**No hash-to-file verification is performed here**. Different digests do not establish
independent sources, events or experts. In particular, a history retrieval submission
does not establish `available_at <= analysis_cutoff`; the downstream as-of validator
must verify original timestamp provenance before any context is eligible.

## Trust boundary and workflow

1. Keep the original intake queue unmodified and entirely `NOT_VERIFIED`.
2. Produce this *separate* local manifest from actual available artifacts. If missing,
   leave the corresponding dimension `NOT_SUBMITTED`; never invent ML run IDs,
   logs, permission receipts, source timestamps, reviewer signatures or decisions.
3. Run both local preflights. Resolve metadata binding failures before forwarding any
   documents or logs to independently authorized reviewers.
4. Preserve source/permission, privacy, diagnosis run, log chronology, task context,
   evidence claims and expert review in separate verifiable receipts. Only later
   validators and human review may assess their substantive validity.

For all submission states, the preflight returns `evidence_verified_count=0`,
`expert_review_ready_count=0`, `real_gold_count=0`,
`split_assignment_allowed=false` and `training_authorized=false`.
A fully populated submission manifest is **not** a ready-to-train dataset.

All tests are `SYNTHETIC_TEST_ONLY`; no private case files, real reviewer identities
or real telemetry are included in this PR.
