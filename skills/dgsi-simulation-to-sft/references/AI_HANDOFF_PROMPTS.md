# Provider-neutral prompts for delegating work to another AI

Copy these prompts as needed. Attach only authorized, de-identified materials. Do not provide the hidden simulator truth folder to the generation AI.

## Prompt A — INGEST

You are operating under the DGSI Simulation-to-SFT Skill. Read the attached spacecraft simulation design report, model specification, test report and/or run logs. Do not generate diagnosis examples yet.

Tasks:
1. Inventory every source and identify version/date, source hash if available, page/section or log range, permission/confidentiality status and missing material.
2. Extract atomic facts into: design declaration, model assumption, model limitation, test condition, measured result, run event, upstream ML finding, engineering interpretation or historical fact.
3. Separate direct observations from author interpretation and hypothetical/design-level statements.
4. Identify spacecraft → subsystem → unit/component hierarchy, signal/energy/control relationships, units, coordinate frames and operating assumptions.
5. Build an evidence ledger with exact source locators and certainty.
6. List contradictions, missing context and claims that cannot be supported.
7. Return an inventory and proposed L0 fact cards only. Do not invent timestamps, ML outputs, fault labels or physical effects.

Return JSON/CSV/Markdown artifacts and a blocker report. Mark every unsupported field UNKNOWN or NOT_PROVIDED.

## Prompt B — GENERATE

Using the approved source inventory, L0 facts and visible case packet, generate L1 diagnostic candidates under DGSI.

Rules:
- Use only facts present in the model-visible packet and cited sources.
- Never inspect or infer hidden simulator truth, injection labels, QA-only channels or post-cutoff outcomes.
- Do not invent an upstream ML result. If absent, do not claim the case represents the user's actual ML-to-LLM pipeline; mark it as a design-derived hypothetical or incomplete.
- Label every generated scenario value as synthetic and cite its assumption.
- Keep fault-source component separate from affected components.
- Preserve uncertainty and score semantics.
- Do not claim a repair was performed unless a source records it.
- Generate one genuinely distinct task per diagnostic decision, not paraphrases.
- Use the exact DGSI schemas and current supported track values. If the schema cannot represent a simulation candidate, do not force it into a real or literature track; return the candidate in the intake sidecar and flag a schema-extension requirement.

Return L0 candidates, L1 packets, source/evidence ledger, hidden-field exclusion checklist (without exposing hidden values), and review queue. All L1 outputs remain REVIEW_REQUIRED.

## Prompt C — AUDIT (independent reviewer)

You are an independent auditor, not the generator. Re-read the original authorized sources and compare every generated claim to its exact source locator.

Check:
- source and page/line accuracy;
- observed fact versus design declaration versus assumption;
- injected truth leakage and temporal leakage;
- ML result fidelity and score semantics;
- fault source versus affected component;
- physical mechanism and causal direction;
- historical-case date, outcome and hardware compatibility;
- disposal/action status;
- evidence IDs and missing evidence;
- duplicates and event-family grouping.

Do not repair silently. Produce a claim-level table with PASS / CORRECT / REJECT / INSUFFICIENT and proposed corrections with evidence. Identify all critical failures. The generator cannot audit its own outputs as the sole reviewer.

## Prompt D — PREPARE REVIEW HANDOFF

Package only candidates that pass automatic checks into a human review queue. Include source locators, original excerpts where licensed, proposed target, uncertainty, unresolved questions and a diff of changes. Keep hidden truth in a separate reviewer-only package. Do not mark Gold or authorize training.
