# DGSI four-case construction pilot — in-session generation report

**Date:** 2026-11-18  
**Status:** 20 candidate drafts generated in the current GPT-6 ChatGPT session. Independent judging NOT RUN.

## Scope
Four frozen literature-derived synthetic evaluation cases: 015 (LNA gain degradation candidate), 016 (monitor-vs-receiver conflict), 020 (recovery without health baseline), 021 (RWA identity/window mismatch).

Five method-inspired arms per case:
- Self-Instruct-style direct seed expansion;
- Evol-Instruct/WizardLM-style depth evolution;
- Auto-Instruct-style candidate plus instruction-quality self-ranking prompt;
- Magpie-style pre-query adaptation;
- DGSI evidence/provenance/context-constrained generation.

Total: 4 cases × 5 arms = 20 candidate drafts. No external API calls; API cost USD 0.

## Important method limitation
All 20 drafts were produced by the same current GPT-6 ChatGPT session using method-inspired prompting. These are not faithful reproductions of the original Self-Instruct, Evol-Instruct, Auto-Instruct or Magpie pipelines. The current session exposes no separately callable judge model or model-switch action. A second pass by the same model would not be an independent judge; therefore blind independent scores, inter-method winner claims and statistical significance are NOT REPORTED.

## Observations from generation
- All four cases can be expressed as structured diagnostic candidates while preserving synthetic-only status.
- 015 retains LNA gain degradation as a candidate and does not assert hydrogen poisoning as the current cause.
- 016 separates onboard monitor indication from independent carrier measurement and does not generalize one carrier result to total RF output.
- 020 distinguishes executed restart and relative improvement from verified recovery.
- 021 treats the wheel/time-window mismatch as DATA_QUALITY_ERROR and does not infer either fault or health for the current wheel.

These are qualitative observations from the generated drafts, not independently scored results.

## Closeout status
- Skill package: existing RC4 candidate package is available; final product release remains subject to PR #159 review/CI.
- Evaluation Suite: inventory manifest prepared.
- Effectiveness report: observed evidence vs. unmeasured metrics documented.
- User/developer handoff: clean-environment guide prepared.
- SOTA comparison: four-case generation pilot drafts produced; independent judging NOT RUN; downstream SFT NOT RUN.

## Next valid step
An independently callable judge model must be made available through an authorized model tool/integration before independent blind scoring. Do not substitute same-model self-review or claim this pilot proves DGSI superiority. Keep all 20 drafts as evaluation-only; no SFT export.
