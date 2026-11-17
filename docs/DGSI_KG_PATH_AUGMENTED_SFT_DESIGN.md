# DGSI: KG- and reasoning-path-augmented SFT data design

Status: research/design proposal; no training-data schema or training pipeline is changed by this document.

## 1. Decision summary

DGSI should support a graph-structured evidence representation in addition to the existing diagnostic-example fields. It should not replace the existing sample format with a flat list of triples, nor should every sample carry a copy of the entire domain KG.

Recommended representation is a **hybrid evidence package**:
1. a versioned domain KG reference (ontology/graph snapshot ID and hash);
2. a case-specific evidence subgraph (typed nodes and directed, typed edges);
3. one or more explicit connected reasoning paths through that subgraph;
4. source/evidence locators and epistemic status for every node/edge/claim;
5. the existing structured diagnosis report as the supervised target.

The KG is the knowledge representation; triples are one possible edge serialization. A reasoning path is an ordered, connected sequence of edges. These concepts are complementary, not competing formats.

## 2. What PoG actually establishes

PoG is a training-free, prompting-based KG reasoning framework, not a fine-tuning data-format study. It represents the source KG as entities, relations and triples, but changes the LLM retrieval/conditioning unit from independently selected triples to connected reasoning paths that preserve relationships among multiple topic entities.

Its pipeline:
- identifies topic entities and constructs a query-relevant subgraph;
- decomposes the question and generates an LLM indicator / predicted reasoning depth;
- explores topic-entity paths, LLM-supplemented paths and node expansions;
- prunes paths using graph structure, semantic similarity and LLM selection;
- summarizes selected paths and asks the LLM to answer from them.

The paper reports that graph-structure-aware pruning reduces irrelevant information and that path summarization improves answer quality/token efficiency in its KGQA experiments. These are results for its inference-time KGQA setting; they do **not** prove that encoding DGSI SFT examples as KG JSON will itself improve fine-tuning.

## 3. DGSI target architecture

### 3.1 Separate three graph layers

**A. Domain ontology / reference KG (shared, versioned)**
- Spacecraft, subsystem, unit, component, telemetry parameter, operating mode, symptom, fault mode, failure mechanism, effect, diagnostic method, corrective action.
- Typed relations such as PART_OF, MEASURED_BY, OBSERVES, INDICATES, CAN_CAUSE, AFFECTS, MITIGATED_BY, VALID_IN_MODE.
- Each relation has definition, direction, domain/range, cardinality where applicable, and provenance/source references.
- Do not place case-specific observations or unverified hypotheses into the shared ontology.

**B. Case evidence graph (per example)**
- Nodes reference upstream ML outputs, diagnostic-log statements, spacecraft/mission context, historical experience, symptoms, candidate causes and actions.
- Edges record only supported relations, such as ML_RESULT_SUPPORTS, LOG_RECORDS, OBSERVED_DURING, COMPONENT_BELONGS_TO, SYMPTOM_CONSISTENT_WITH, CAUSE_CANDIDATE_FOR.
- Each node/edge carries provenance, source hash, source locator, timestamp/scope, confidence where meaningful, and epistemic status.

**C. Reasoning-path set (per task)**
- Ordered connected paths through the case graph.
- Preserve branch alternatives and contradictions; do not force all evidence into one linear chain.
- Distinguish supporting, contradicting, missing and context-only paths.
- A path is an evidence organization, not proof of causality by itself.

### 3.2 Epistemic status vocabulary

Use explicit values:
- OBSERVED: directly present in an admitted source record.
- UPSTREAM_MODEL_OUTPUT: produced by the upstream ML system; preserve model/run identity and score semantics.
- INFERRED: derived by a documented rule from cited evidence.
- HYPOTHESIS: plausible candidate not established by evidence.
- CONTRADICTED: conflicts with cited evidence.
- UNKNOWN: insufficient evidence.
- HISTORICAL_CONTEXT: prior experience; informative but not current-case observation.

Never promote HYPOTHESIS or HISTORICAL_CONTEXT to OBSERVED. AI-generated graph edges are proposals until reviewed. Preserve rejected alternatives and the reason for rejection.

## 4. SFT example serialization (proposed)

The training example remains a task-level JSON object. Add optional graph fields rather than replacing the current input contract:

- domain_kg_ref: ontology version, graph snapshot ID and SHA-256.
- case_evidence_graph: nodes[] and edges[]; each has stable IDs, typed labels, source refs and epistemic status.
- reasoning_paths[]: path ID, ordered node/edge IDs, role (SUPPORTING, CONTRADICTING, CONTEXT_ONLY, INCOMPLETE), and completeness status.
- graph_retrieval_receipt: retrieval query/entity anchors, graph snapshot, depth/beam/pruning recipe, and retrieved candidate IDs.
- upstream_diagnosis, diagnostic_log, spacecraft_context, history_context: retain the established source-specific input separation.
- target.diagnosis_report: the existing structured diagnostic output, with evidence references into the graph.

Do not duplicate full source documents, raw telemetry, or the entire global KG into every SFT sample. The default LLM input remains upstream ML results, diagnostic logs and spacecraft/mission context; raw telemetry remains upstream input unless a separately approved task requires otherwise.

## 5. Graph/path retrieval design inspired by PoG

At example construction or inference time:
1. Resolve entities from the upstream diagnosis, log and mission context against the versioned domain KG.
2. Build a bounded case subgraph around those anchors.
3. Search for connected paths linking the observed symptom / ML result to candidate components, fault modes, mechanisms and actions.
4. Retain paths that contain the required anchors in the task-defined order; preserve direction and edge types.
5. Prune irrelevant paths with deterministic graph constraints first, then optional semantic ranking.
6. Serialize both the compact subgraph and the selected paths; retain IDs so every path edge can be traced to the graph and source.
7. If no supported path exists, explicitly return an incomplete/unknown path state rather than inventing a bridge.

PoG's dynamic depth, multi-entity path exploration and three-stage pruning are useful design references. DGSI should initially use bounded, deterministic graph traversal and transparent ranking, not copy PoG's KGQA prompts or rely on LLM-generated graph edges.

## 6. Example (illustrative only; not a real case)

A case graph could connect:
- an upstream ML anomaly result for a wheel-current residual;
- a diagnostic-log statement recording intermittent current excursions;
- spacecraft context identifying the active attitude-control mode;
- a reaction-wheel assembly node;
- candidate mechanisms such as bearing friction or driver-current limitation.

The graph must keep the two mechanisms as separate hypotheses unless evidence distinguishes them. A path may show that the ML result and log statement are consistent with a wheel-drive anomaly; it must not assert a bearing fault merely because that is a known failure mode.

## 7. Evaluation plan: test whether KG structure helps SFT

Do not assume a performance gain. Run a controlled ablation with identical cases, target reports, model, token budget, optimizer, training steps and data split:

- A — Text baseline: current separated diagnostic context in text/JSON, no graph fields.
- B — Triple list: relevant facts serialized as independent triples.
- C — Case subgraph: typed nodes and edges serialized as graph JSON, without explicit paths.
- D — Reasoning paths: connected paths serialized with edge IDs and evidence references.
- E — Hybrid (recommended candidate): compact case subgraph plus selected connected paths.

Keep source-event families disjoint across train/validation/test. Include unseen components, unseen fault mechanisms and cross-subsystem cases where data allow. Compare:
- fault correctness and root-cause localization;
- evidence citation precision/recall and unsupported-claim rate;
- multi-hop relation/path validity;
- contradiction handling and abstention calibration;
- structured report completeness and actionability;
- token cost, latency and robustness to graph noise / missing edges.

Use paired evaluation and expert adjudication. Report confidence intervals and per-scenario results. A graph-format claim is accepted only if E or D improves relevant metrics over A and B without increasing unsupported causal claims or unacceptable token/latency cost.

## 8. Rollout gates

1. Freeze ontology vocabulary and relation direction/domain/range.
2. Build a small, manually reviewed graph set from already admitted examples.
3. Validate graph schema, referential integrity, provenance and epistemic-state transitions.
4. Generate paired A–E representations from the same cases.
5. Run structural tests and expert review before any SFT use.
6. Conduct the controlled ablation; only then decide whether graph/path fields become mandatory.

All generated graph records remain non-Gold and training-disabled until source admission, expert review, split audit and DGSI's existing authorization gates pass.

## 9. Recommendation

Adopt the **KG + case subgraph + connected reasoning paths + evidence references** as an optional parallel representation for DGSI examples. Keep the existing task-level SFT format and diagnosis report target. Do not replace the dataset with isolated triples, and do not claim a fine-tuning benefit before the A–E ablation.

This is a design proposal only; implementation should begin with schema and validators after the current P5-B4.3a review-receipt CI is green.
