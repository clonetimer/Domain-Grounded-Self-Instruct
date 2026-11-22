# DGSI confirmatory holdout — independent custodian intake

**Status:** INTAKE TEMPLATE ONLY / NOT A CASE / NOT AUTHORIZATION TO RUN  
**Applies to:** PR #191, preregistered 2×2 experiment  
**Do not place real candidate source identities, source text, gold answers, or confidential rights correspondence in this public template.**

## Purpose

The current source register admits zero eligible independent source clusters. The strategy authors/generators have already seen the sources listed in that register. This template allows an independent custodian to screen new material without sending source identities or reference answers to the prompt authors/generators.

This is a custody procedure, not a way to turn familiar sources into holdout. Any source already exposed to the strategy authors, generator context, repository/PR history, development bundles, or connected retrieval is ineligible for this confirmatory run.

## Role separation

1. **Independent source custodian** obtains and retains the full primary document, rights evidence, source identity, source-cluster mapping, and sealed reference answer.
2. **Independent rights/exposure reviewer** checks derivative-use rights and performs the exposure audit. The custodian cannot self-certify a disputed rights issue.
3. **Case packet author** prepares the visible, source-faithful diagnostic input packet using only documented facts and explicit uncertainty. Do not invent telemetry, ML outputs, logs, timestamps, interventions, or root causes.
4. **Generator / strategy authors** receive only the frozen anonymized input packet, target schema, and preregistered arm configuration. They do not receive source identity, full report, source-to-case key, rights correspondence, or reference answer.
5. **Blind reviewers** receive anonymized outputs and the frozen rubric. They do not receive arm identity, source identity, prompt variants, or other reviewers' decisions.
6. **Data custodian** retains the identity key and gold/reference answer until all four arms and both blinded reviews are complete.

If the same person performs incompatible roles, record the conflict and do not claim independent blinding.

## Custodian screening checklist

A cluster is not eligible unless every item below is supported by retained evidence:

- [ ] Primary source is identified by exact document title, issuing body, document ID, URL and publication date.
- [ ] Original bytes are retained and SHA-256 is calculated from the exact file used.
- [ ] Page/section/paragraph locators support every fact placed in the case packet.
- [ ] Rights reviewer documents the specific legal/licence basis and scope for extracting, paraphrasing, transforming and using the facts in a research dataset/model-training context. Public download alone is insufficient.
- [ ] Exposure audit covers repository and PR history, prior development/evaluation bundles, connected retrieval sources, and prior conversation/model exposure available to the custodian.
- [ ] Event-family and source-cluster independence is assessed against all existing development and holdout clusters. Same mission, same incident, shared causal chain or derivative report must not be counted as independent without a written rationale.
- [ ] Case packet contains no source title, URL, document ID, answer wording, or other avoidable source-identity cue.
- [ ] Reference answer and source-to-case mapping are stored separately with access controls; neither is placed in the generator packet or run manifest.
- [ ] A second reviewer signs the rights, exposure and independence decision.
- [ ] Case IDs, source-cluster IDs, input bytes and target-schema hash are frozen before generation.

Any failed, unknown or unreviewed item means **NOT ADMITTED**. Do not waive a gate to meet a sample quota.

## Per-cluster evidence record required by the validator

The run manifest's `source_evidence_records` must contain exactly one record for each cluster used by the cases. Required keys:

```json
{
  "source_cluster_id": "opaque-custodian-issued-id",
  "primary_source_url": "https://primary-source.example/path",
  "source_document_id": "exact-document-id",
  "source_document_sha256": "64-lowercase-hex-characters",
  "source_locators": ["printed page 4, section 2.1"],
  "rights_basis": "specific licence or written rights determination",
  "rights_scope": "explicitly covers intended extraction/derivative research dataset use",
  "rights_review_ref": "restricted-evidence-record-reference",
  "exposure_audit_scope": [
    "repository_and_pr_history",
    "prior_development_bundles",
    "connected_retrieval_and_prior_conversations"
  ],
  "exposure_audit_ref": "restricted-audit-record-reference",
  "independence_rationale": "why this event/document cluster is independent of all excluded clusters",
  "review_status": "PASS",
  "reviewer_token": "opaque-independent-reviewer-token",
  "reviewed_at": "YYYY-MM-DD"
}
```

This JSON is a **shape example only**. The example URL, document ID, digest, references and reviewer token are placeholders; never copy them into a real run manifest. The validator checks structure and consistency, not the truth of the assertions or the legal merits of the rights determination.

## Visible case packet (generator-visible)

The custodian supplies a separate packet with only:

- opaque case ID;
- visible operational context and time window;
- source-supported telemetry/log excerpts or explicitly marked absence of evidence;
- upstream ML outputs only if they exist in the primary source/context, clearly labelled as ML inference;
- independent observations as separate evidence items;
- target schema and task instruction;
- SHA-256 of exact packet bytes and target schema.

Do not include source identity, source report, gold answer, scoring hints, arm labels, or reviewer notes. Preserve distinctions among direct observations, ML inference, independent observation, hypothesis, and unknown. “No record found” must not be rewritten as “confirmed absent.”

## Freeze and release sequence

1. Custodian completes rights, exposure and independence review before packet authors see the source.
2. Independent reviewer signs the evidence record.
3. Custodian freezes packet bytes, case ID, opaque cluster ID and target-schema hash; records hashes in the manifest.
4. Custodian checks all four arms reference the identical case set and hashes.
5. Custodian keeps source identity and reference answers escrowed.
6. Validate the manifest offline. A passing validator only means the metadata is structurally consistent; it does not authorize model calls.
7. Only after the preregistered source-cluster minimum is actually met and all custody checks pass may a separate run authorization be considered.
8. Run exactly one preregistered round: no retries, regeneration, post-hoc repair, case substitution or rubric changes.
9. Release the sealed key and reference answer only after generation and both blind reviews are complete.

## Current status

As of the latest source-screen register, eligible clusters = **0**. This template creates no cases and does not change that count. The 2×2 experiment remains **NOT_RUN**. Do not run generation or scoring using synthetic test fixtures, previously exposed public leads, or invented source packets.
