# DGSI instruction refinement: bounded design and execution record

## Design frozen before forward generation

The user requested borrowing Evol-Instruct and Auto-Instruct-style mechanisms
to improve the existing DGSI skill. This change adds an optional instruction
recipe, not another dataset-admission process. Existing v0.2.0 artifacts remain
immutable. The old four cases are development evidence, never a fresh test set.

Three alternatives were considered: expand the baseline prompt, evolve one
instruction, or evolve several instructions then select before answering.
We implement the third as an optional recipe and retain the first two components
as ablations. This is an engineering choice, not a user assertion of superiority.

Evol-Instruct motivates constrained instruction evolution
<https://arxiv.org/abs/2304.12244>. Auto-Instruct motivates diverse instruction
generation and selection <https://aclanthology.org/2023.findings-emnlp.659/>.
The latter paper uses a trained ranking model; this adaptation uses recorded
GPT instruction scores and deterministic selection, not that trained ranker.

### Invariants and stop condition

- Freeze the projected input; never evolve ML outputs, logs, scores, timestamps,
  hardware, historical cases, literature facts or task type.
- Check source scope and comparability only to the extent recorded. Missing
  same-path/time/configuration evidence stays missing.
- Distinguish direct observations, ML inference, independently supplied evidence,
  contradictions and unavailable referenced artifacts.
- Select instructions before generating one answer. Never select among answers
  using final judges or tune on forward-test feedback.
- Construction records are curator-side, not_for_sft=true; when attached to a
  Case, place them only at Case.internal_review. Formal targets stay unchanged.
- Run one frozen forward comparison: existing Evol-style, Auto-style, DGSI;
  DGSI+evolution; DGSI+selection; DGSI+both. Two fresh method-blind GPT judges.
- Reuse existing authorized public SYNTHETIC packets from source groups unused
  in the four-case development comparison. Report connected source-cluster
  counts; these are development holdouts, not formal train/test assignments.
- Report every arm and rejection. Stop after the locked run regardless of rank.
  A tie is a tie, not proof of superiority. No significance or downstream-SFT
  claim from four cases, no exact-token/compute-match claim without telemetry.
- Real Gold, human review, official splits, paid API calls and training remain
  zero/not authorized. The paused continuous automation stays paused.

## Implementation plan

Goal: make the hybrid recipe reusable and test its incremental behavior.
Architecture: an optional authoring sidecar on the existing prepare entry,
strict binding/selection checks, and an additional immutable replay bundle.
Tech stack: existing Python/jsonschema/unittest; no new service or dependency.

1. Add failing tests for recipe isolation, input/hash binding, ranking validity,
   deterministic ties and all-rejected behavior; implement the smallest recipe
   module and optional CLI flag. Run focused tests.
2. Freeze case membership, source groups, prompts, schema, review rubric, budget
   and decision rule before generation. Save all six arms' actual raw outputs.
3. Obtain two separate GPT reviews with randomized opaque item IDs. Aggregate
   original outputs once; keep any invalid outputs visible. Run replay/tests,
   independent code review, full suite and exact-head Ubuntu/Windows CI.

Review focus: changed evidence hashes, accidental authoring-policy leakage into
SFT messages, malformed model scores, incompletely populated comparison matrices,
and source-connected cases falsely counted as independent.

## Execution record

- Initial exact-head audit: all 140 open PRs have both required platforms PASS;
  starting release head bfa94a343f8567d6419764546b1dc689c277151e.
- Old comparison numerical audit: DGSI 158/160, Evol/Auto-style 159/160; each has
  3/4 paired accepts. One reviewer's two DGSI deductions concern omitted
  comparability and mixed evidence roles. The other reviewer scores all three
  arms 20/20 on every case. This is not established population inferiority.
- Input manifest frozen before generation: `d36cacfb898ca249cd199abd634fb23acad961d3ced946c8360abf6aaad10368`.
  The same bytes were verified after both blind review sessions.

## Observed forward results

Six fresh generator sessions produced 24 candidates. Two separate configured
`gpt-6.2-sol` sessions reviewed all 24, without method labels or reference targets.
All 48 reviews bind the frozen visible input, emitted instruction and target.
No generation was repaired, regenerated, discarded or rescored after review.

| Method | Mean / 20, equal cases | Mean / 20, equal source clusters | Paired accepts | Critical-failure candidates |
|---|---:|---:|---:|---:|
| M1 Evol-style | 18.625 | 18.250 | 0/4 | 0 |
| M3 Auto-Instruct-style | 19.500 | 19.333 | 2/4 | 0 |
| M4 original DGSI | 19.750 | 19.500 | 3/4 | 0 |
| M5 DGSI + evolve | 19.875 | 19.750 | 3/4 | 0 |
| M6 DGSI + select | **20.000** | **20.000** | **4/4** | **0** |
| M7 DGSI + evolve-select | 19.625 | 19.417 | 2/4 | 0 |

M6 is the single observed top arm under the frozen ranking rule. This supports
offering `prepare --recipe select` as the recommended optional configuration for
the next development use. The baseline remains the default for compatibility.
The combined M7 recipe did not outperform M6 and remains an optional experiment.
There is no claim of a global optimum, statistical superiority or SFT gain.

### What the reviews actually found

- M1 lost eight raw rubric points across its eight reviews in disposal fidelity:
  reviewer findings concern new recommendations written into disposal fields.
- M3's deductions concern evidence attribution and disposal scope. M4's concern
  phenomenon chronology and evidence attribution; M5 retains one attribution
  deduction. These are visible-input judgments, not external-source findings.
- M7's two unresolved candidates are the NASA test and TROPICS qualification
  cases. One reviewer distinguished log-entry timestamps from the actual start
  of an action and the ML summary's prior catalyst-bed statement from independent
  log evidence. The other issue is wording that could presuppose configuration
  change where the input only records a documentation gap.
- M6 had no material finding under this rubric. A score of 20 means the judges
  found no scored defect in these inputs; it is not engineering certification.
- Five candidates have reviewer disagreement. They remain visible; no score
  override or majority vote changes their status. Fourteen of all 24 candidates
  satisfy the two-reviewer development-accept rule.

All M6 and M7 instruction selections chose I1 under the recorded tie rule. The
run therefore does not demonstrate a gain from selecting a later candidate,
nor isolate a trained-selector effect. The common evidence/scope policy,
instruction style and stochastic generation/review may account for differences.
The old four-case result remains unchanged and is not pooled into this ranking.

### Reproduction and frozen delivery behavior

```bash
python scripts/run_dgsi_skill.py demo --bundle evaluation/refinement_20261119 --output refinement_demo
python evaluation/refinement_20261119/analyze.py --output refinement_analysis.json
```

The first command verifies the replay and preregistration manifests, raw
generation bindings, selected instruction records and paired review hashes. The
second recomputes the case and source-cluster summaries and exact top ties.
Neither calls a model. The recomputed analysis must equal
`evaluation/refinement_20261119/analysis_results.json`.

The protocol preselected M7 as the curated arm. It is deliberately unchanged:
its curated preview has two accepted records. M6's four original candidates are
present in the full 24-candidate replay and `generations/M6.json`. Recommending M6
for subsequent development is explicit and separate from this frozen delivery
selection. All previews remain SYNTHETIC DEV_ONLY, split=null, unauthorized for
training or Gold. Human expert reviews and admitted SFT records are zero.

Fresh generation is stochastic and may not reproduce the scores. To repeat the
procedure, give each fresh generator only its method prompt, shared visible cases
and target schema; give each fresh reviewer only the randomized review input and
rubric. Do not give them coordinator source packets, standard targets, other
methods' outputs or previous scores. Use new source groups for further method
development rather than relabeling these now-observed cases as fresh holdout.

## Implementation and verification scope

- Added three optional recipes and strict input/selection validation; baseline
  preparation messages remain byte-identical.
- Replays also verify the raw generation, frozen recipe and emitted instruction.
  A zero-regeneration protocol rejects delivery revisions. Empty or truncated
  preregistration manifests are blocked before preview output.
- Curator records remain out of user/assistant messages. L1 attachment uses a
  schema-compatible JSON string under root `internal_review.curator_prompts`.
- Independent code review found replay and documentation gaps; each was fixed
  with focused regressions. No frozen prompt, source packet or scored answer was
  changed to address code-review findings.
- The full-suite and exact-head CI evidence are recorded with the dependent
  draft PR. The continuous automation remains paused; this bounded round ends
  here instead of triggering another score-driven optimization cycle.


## Follow-up correction from the two identified review omissions — 2026-11-20

This is an implementation note only. It does not change the frozen four-case results, evaluation set, rubric, reviewer decisions, thresholds, or prior conclusions.

### Changes made

- `src/dgsi/instruction_design.py`: strengthened the shared authoring policy so that a launch/injection-path comparison may be stated as “same launch path, no switch within the window” only when the path identifier, observation-window bounds, and no-switch evidence are explicitly present. Missing path/switch evidence must remain unknown/not recorded; absence of a switch record is not proof that no switch occurred.
- The same policy now requires ML inference, independent observation/counter-evidence, direct telemetry/log observation, and an upstream reference without its original artifact to be recorded as separate evidence items. Independent observations may support or contradict an ML inference but may not be merged into the same support item or relabelled as the ML output itself.
- `tests/test_instruction_design.py`: added two regression checks that ensure the shared policy is present in all three optional recipes (`evolve`, `select`, `evolve-select`).
- `skills/dgsi-simulation-to-sft/references/INSTRUCTION_REFINEMENT.md`: documented the explicit evidence requirements and clarified that missing switch records cannot be treated as proof of continuity.
- Corrected duplicated step numbering in the instruction procedure.

### What this does and does not establish

- Established: the host-authoring instructions now explicitly encode both previously identified requirements; regression tests check that the shared policy reaches every optional recipe.
- Not established: that a model will always obey these instructions; that a generated answer will correctly interpret a real launch-path timeline; or that the two omissions have disappeared from output distributions.
- Not measured: any new generation, blind review, acceptance-rate change, score gain, latency/token cost, or downstream SFT gain. No such experiment was run in this change.

### Verification status

- The new focused tests were committed; exact-head Ubuntu/Windows full-suite and package workflow runs for commit `b8067e7557a84a7f242674c701104d5bdf8ed929` were observed as in progress at the time of this note. They are not marked PASS here.
- The separate 2×2 manifest guard is not a substitute for these implementation tests.
- The PR #186 branch remains a Draft and has a mergeability/conflict issue against its release base; dependent PR #189/#191 have not yet been proven to contain this latest strategy commit.

### Outcome ledger

| Measure | Result |
|---|---:|
| Explicit policy gaps addressed | 2 |
| New regression tests | 2 |
| Evaluation cases changed | 0 |
| Rubric/threshold changes | 0 |
| New generated answers / blind reviews | 0 / 0 |
| New performance evidence | 0 |
| Downstream SFT evidence | 0 |

This change improves specification coverage and test coverage only. It does not demonstrate model-quality improvement.
