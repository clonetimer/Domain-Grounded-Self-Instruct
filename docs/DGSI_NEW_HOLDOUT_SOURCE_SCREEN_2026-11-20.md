# New holdout source screening — 2026-11-20

**Purpose:** identify possible untouched public source-document clusters for a future confirmatory 2×2 strategy comparison.  
**Classification:** source-screening notes only; `not_for_sft=true`.  
**Status:** NOT ADMITTED. No L0 card, L1 task, synthetic ML output, training split, or model call is created by this document.

## Screening rules

A candidate is not eligible for the confirmatory holdout until all checks pass:
1. Exact source document and event/episode boundaries are recorded.
2. Rights/reuse scope is explicitly verified for the intended derivative fact-card and synthetic-task use.
3. It is independent of all development and retrieval exposures, including PR #183/#184 and the 2026-11-19 four-case bundle.
4. It contains enough source-grounded facts for a bounded L0 card without inventing ML findings, logs, timestamps, or root-cause certainty.
5. Missing upstream ML outputs, mission context, logs, or disposition details remain missing; synthetic fields may only be introduced later with explicit field-level provenance.
6. Holdout identity and reference conclusions are escrowed from prompt authors/generators before any arm is run.

## Candidate register

| Candidate event family | Primary source | Source-supported facts | Rights status | Exposure/independence status | Decision |
|---|---|---|---|---|---|
| IMAGE 2005 loss of communications / transponder power path | IMAGE Failure Review Board Final Report, 2006-09-19, NASA/GSFC-hosted report: https://spdf.gsfc.nasa.gov/pub/data/image/documents/website/image.gsfc.nasa.gov/publication/document/IMAGE_FRB_Final_Report.pdf | Report states likely SEU-induced instant trip of transponder SSPC; several less likely causes cannot be eliminated. It describes nominal telemetry before loss, unsuccessful recovery attempts, and a design issue where instant trips were not reflected in status telemetry. | NASA content is generally reusable for factual/informational purposes subject to NASA media guidelines, but report-specific third-party material must still be checked: https://www.nasa.gov/nasa-brand-center/images-and-media/ | **EXPOSED / INELIGIBLE** — repository search found this exact source and its fault mechanism already used in EPS seed-curation skill, source registry, source passages, pressure-test cases, domain review checklist and exploratory model pretest. | EXCLUDE from confirmatory holdout; retain only as development material |
| ISS US solar-array Beta Gimbal Assembly rising motor-current anomaly (2000–2001) | NASA NTRS 20030014592, NASA/TM-2003-212012: https://ntrs.nasa.gov/citations/20030014592 | NTRS abstract reports higher-than-expected BGA drive-motor currents increasing over time on both assemblies; EPS analyses supported operational workarounds to reduce BGA use while maintaining adequate solar-array power. | NTRS record explicitly states “Public Use Permitted” and distribution limits “Public” (NTRS record metadata, checked 2026-11-20). Verify any third-party material embedded in the full PDF before reuse. | GitHub default-branch search for “Beta Gimbal Assembly” and “20030014592” returned no matches. This is only a limited repository-index check, not proof of no exposure in prior chats, connected retrieval or non-indexed PRs. | CONDITIONAL CANDIDATE — rights metadata verified; independence NOT YET ESTABLISHED |
| MethaneSAT 2025-06-20 loss of communications | New Zealand MBIE-hosted Appendix 9 anomaly investigation report: https://www.mbie.govt.nz/dmsdocument/31529-appendix-9-methanesat-anomaly-investigation-report | Report says last received data were nominal; no post-anomaly telemetry was available; the investigation narrowed the direct event to flight avionics or EPS but could not identify the specific failure. It lists three possible contributors without ranking their relative likelihood. | Government-hosted appendix, but underlying report is authored by MethaneSAT LLC and partners; derivative reuse/IP permission is not established. | Not listed among explicit PR #188 exclusions; full exposure check remains required. | HOLD — rights and exposure review |

## Source-fidelity constraints

- IMAGE: preserve “likely” for the SEU/SSPC explanation; do not promote it to certain root cause. Distinguish source report findings from any later synthetic upstream ML candidate.
- ISS BGA: the source abstract supports increasing motor current and EPS workaround analyses; do not infer a confirmed motor mechanical root cause from the abstract. Full report review is required before an L0 fact card.
- MethaneSAT: retain the investigation's unresolved distinction between flight avionics and EPS and the explicit statement that relative likelihood among the three possible contributors could not be stated. Do not choose one contributor.
- None of these public reports supplies an actual upstream ML model output/run, structured diagnostic log, or current LLM-ready task input. Such fields must remain absent in L0 and, if later needed for an L1 synthetic experiment, be labeled SYNTHETIC with field-level generation provenance.

## Current gate result

- Candidate documents screened: 3.
- Rights metadata explicitly supporting public reuse: 1 (ISS NTRS 20030014592; third-party embedded material still to be checked).
- Candidate disqualified for prior development exposure: 1 (IMAGE).
- Candidates still held for rights/exposure review: 2 (ISS independence; MethaneSAT rights and independence).
- Event/source clusters admitted to confirmatory holdout: 0.
- L0 fact cards created: 0.
- L1 tasks created: 0.
- Official holdout manifest changed: false.
- Existing holdout cases or scores changed: false.
- Model calls / generation / fine-tuning: not performed.

## Next actions

1. Do not reconsider IMAGE for confirmatory holdout: its source and mechanism are already deeply exposed in the DGSI repository and development work.
2. Verify third-party content and permitted derivative reuse in the full ISS NTRS PDF; obtain the full document and exact page/section locators.
3. Obtain explicit reuse/IP determination for MethaneSAT; a government-hosted appendix is not by itself proof that the underlying corporate-authored report may be republished or transformed.
4. Extend exposure screening beyond GitHub code search to prior development bundles, issue/PR history and retrieval indexes before admitting ISS or MethaneSAT.
5. Only after rights and exposure gates pass, draft L0 fact cards with page/section locators and explicit missing-material fields for independent review.
6. If fewer than the preregistered minimum of independent clusters pass, keep the 2×2 experiment at NOT_RUN. Do not substitute familiar or exposed cases.



## Additional primary-source screening — 2026-11-20 (follow-up)

This follow-up adds public-source verification only. It does not admit any source, create a fact card/task, or alter the preregistered holdout manifest.

### ISS Beta Gimbal Assembly — rights metadata confirmed; independence still open

The exact NASA NTRS record for NASA/TM-2003-212012 (Document ID 20030014592) was opened and checked. NTRS identifies the document as a Technical Memorandum, marks Distribution Limits **Public**, and Copyright **Work of the US Gov. Public Use Permitted**; the full 17-page PDF is downloadable from the record. Its abstract supports increasing drive-motor currents on both Beta Gimbal Assemblies and EPS analyses/workarounds to reduce BGA use while maintaining adequate solar-array power. It does not, by itself, establish a confirmed mechanical root cause. The report lists a NASA Glenn author and a Boeing co-author; inspect the full PDF for any third-party figures/material before derivative reuse.

Primary record: https://ntrs.nasa.gov/citations/20030014592  
PDF: https://ntrs.nasa.gov/api/citations/20030014592/downloads/20030014592.pdf  
Checked: 2026-11-20.

**Decision remains CONDITIONAL / NOT ADMITTED.** Public-use metadata now passes the initial document-level rights screen, subject to third-party-material review. The unresolved gate is exposure independence across prior conversations, development bundles, PR history and retrieval indexes. A default-branch code-search miss is insufficient to prove independence.

### MethaneSAT — rights caution strengthened; still not a legal determination

The MBIE-hosted Appendix 9 report is publicly accessible and states that the last received telemetry was nominal, no post-anomaly spacecraft data were available, and the investigation narrowed the direct cause to either flight avionics or EPS while leaving the specific failure reason unknown. It lists three possible contributors and explicitly says their relative likelihood cannot be stated. Preserve that uncertainty; do not choose or rank one contributor.

The publicly posted 2020 MBIE–MethaneSAT MOU states that Work Product IP is owned by the producing participant (or jointly if jointly produced), that neither participant may distribute another participant's Work Product without prior written consent, and that MBIE's license to MethaneSAT IP is non-sublicensable/non-assignable and limited to performing the MOU services. The MOU also says it is not intended to be legally binding. These clauses do **not** establish the current copyright status of Appendix 9 or settle rights for derivative dataset use; public release by MBIE is not itself an explicit license for all transformations. Keep on HOLD pending source-specific permission/rights determination.

Sources: https://www.mbie.govt.nz/dmsdocument/31529-appendix-9-methanesat-anomaly-investigation-report and https://www.mbie.govt.nz/dmsdocument/31526-appendix-1-memorandum-of-understanding-methanesat (sections 3 and 4; checked 2026-11-20).

### New scope-sensitive lead: Inertial Upper Stage (IUS) nozzle failure

NASA NTRS record 19860000811, *Analytical investigation of solid rocket nozzle failure* (NASA-TM-86513), describes an April 5, 1983 IUS loss-of-control event during the second solid-rocket-motor burn. The record says the investigation attributed the anomaly to a solid-rocket-motor malfunction and describes failure analysis, thermal testing, modeling, and design changes. NTRS marks Distribution Limits **Public** and Copyright **Work of the US Gov. Public Use Permitted**; a full PDF is available.

Primary record: https://ntrs.nasa.gov/citations/19860000811  
PDF: https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19860000811.pdf  
Checked: 2026-11-20.

**Decision: SCREENING LEAD ONLY / NOT ADMITTED.** This is an upper-stage propulsion event, not an ordinary satellite bus/subsystem anomaly. Before considering it, determine whether the project scope includes launch/transfer upper-stage spacecraft and whether its source facts support the same diagnostic task contract. It must also pass repository and prior-work exposure checks. Do not count it as an independent eligible cluster yet.

### Explicit exclusion: Seasat

NASA's *Report of the Seasat Failure Review Board* (NTRS 19930015504) has public-use metadata and a useful failure narrative, but Seasat is already named among the existing P5-C17 holdout sources. It is therefore **EXPOSED / INELIGIBLE** for this new confirmatory experiment, regardless of its source quality. Do not reuse it as a fresh cluster.

Primary record: https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19930015504.pdf (checked 2026-11-20).

### Follow-up gate status

- Additional records checked: 3 (ISS BGA, MethaneSAT MOU/report, IUS); Seasat explicitly screened out due existing holdout exposure.
- Document-level public-use metadata confirmed: ISS BGA and IUS.
- Candidates admitted to confirmatory holdout: **0**.
- Candidates requiring exposure/scope checks: ISS BGA and IUS.
- Candidate requiring source-specific rights determination: MethaneSAT.
- Existing holdout manifest, cases, references, scores and rubric: unchanged.
- Generation/model calls/training: not performed.

No candidate is to be promoted merely to meet a quota. The 2×2 remains NOT_RUN until the required number of independent, rights-cleared, scope-compatible source clusters are actually established and frozen.


## Additional candidate discovery — 2026-11-20 (NASA NTRS)

This search round is a discovery screen, not admission. Search-result metadata and abstracts are insufficient to establish full-source fidelity, prior-work independence, or rights for third-party content. No L0/L1 records were created.

| Candidate | Primary-source evidence found | Initial relevance | Current decision |
|---|---|---|---|
| ISS Starboard Solar Alpha Rotary Joint (SARJ) anomaly, NTRS 20090034477 | NTRS abstract describes high current draw beginning ~83 days after installation, EVA inspection, damaged race ring, metallurgical/traction/thermal analyses, and a conclusion involving inadequate lubrication and high bearing edge stress. Record marks Distribution Public / Public Use Permitted. Authors include NASA and Boeing personnel. | Strong mechanical/actuator subsystem diagnostic case with observable current anomaly and later physical inspection. | **LEAD ONLY / NOT ADMITTED**. Same ISS platform as BGA, but distinct mechanism and document; do not assume cluster independence. Review full PDF for Boeing/third-party rights and compare exposure against BGA and all prior DGSI materials. |
| Lucy solar-array partial deployment, NTRS 20250002257 | NTRS abstract reports SAPY wing incomplete deployment after separation; no deployed-state sensor; response team used current-based mathematical models, ADAMS modeling, tests and risk assessment; mistracked lanyard identified as likely proximate cause; incremental redeployment actions. Record marks Distribution Public / Public Use Permitted and NASA Peer Committee review. | Strong contemporary deployment/mechanism case; useful for evidence limitations and distinguishing model inference from physical confirmation. | **LEAD ONLY / NOT ADMITTED**. Download is a PowerPoint presentation associated with an IEEE conference; verify third-party slide/image content and derivative-use boundaries. Search prior repository/chat/retrieval exposure before admission. |
| Galileo spacecraft anomaly and safing recovery, NTRS 19940019391 | NTRS abstract says four in-flight anomalies triggered safing routines and recovery plans were refined; describes operational recovery and constraints. Record marks Distribution Public / Work of US Gov. Public Use Permitted. | Relevant to fault-protection, safe mode and operational recovery, but the abstract is high-level and does not identify specific root causes for each event. | **LEAD ONLY / LOW INPUT SUFFICIENCY**. Full paper needed to identify whether it contains a bounded, source-supported event with enough facts for the DGSI task contract. |
| NASA RP-1390, *Spacecraft System Failures and Anomalies Attributed to the Natural Space Environment*, NTRS 19960050463 | Public-use NASA reference publication cataloguing representative space-environment-related failures/anomalies across subsystems. Authors include USRA and Computer Sciences Corp. contributors. | Potential index to multiple events and subsystem categories. | **SOURCE INDEX ONLY / NOT AN INDEPENDENT CASE**. Must identify individual primary event reports and check each source separately; do not treat this synthesis as several independent clusters. |
| SAMPEX reaction-wheel failure, NTRS 20080039634 | NASA abstract describes reaction-wheel failure after >15 years, transition to magnetic-torquer-only spin-stabilized mode, and recovery using flight-data analysis and dynamics simulation. | Technically strong ADCS case. | **EXPOSED / INELIGIBLE**. SAMPEX NTRS 20080039634 is explicitly named among PR #184's prior source leads and therefore cannot serve as a fresh holdout. |
| Apollo 13 oxygen-tank failure, NTRS 19710010479 | NASA investigation report; NTRS marks Public / Work of US Gov. Public Use Permitted. | Detailed spacecraft incident investigation. | **OUT OF CURRENT SCOPE** for the present satellite subsystem SFT cohort (crewed command/service module and human-spaceflight incident). Do not add unless scope is formally expanded in a separate study. |

Primary records checked 2026-11-20:
- SARJ: https://ntrs.nasa.gov/citations/20090034477
- Lucy: https://ntrs.nasa.gov/citations/20250002257
- Galileo: https://ntrs.nasa.gov/search.jsp?R=19940019391
- NASA RP-1390: https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19960050463.pdf
- SAMPEX (excluded as exposed): https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20080039634.pdf
- Apollo 13 (excluded by scope): https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19710010479.pdf

### Discovery round result

- Additional candidate documents/indexes screened: 6.
- New potentially useful case leads: 3 (SARJ, Lucy, Galileo).
- Source index only: 1 (NASA RP-1390).
- Explicitly exposed and excluded: 1 (SAMPEX).
- Excluded by current scope: 1 (Apollo 13).
- New admitted confirmatory clusters: **0**.
- New L0 fact cards / L1 tasks: **0 / 0**.
- Existing holdout manifest, source membership, rubric, references and scores: unchanged.
- This round's measurable benefit: expanded the candidate queue with three plausible leads and identified two exclusions; it did not yet increase the eligible holdout count.

The next valid work is full-document and prior-exposure screening of SARJ, Lucy and Galileo. No candidate is to be counted as eligible until both gates pass.


## Follow-up source screen — additional mission cases and leakage checks (2026-11-20)

This round reviewed primary/near-primary sources for SARJ, UARS, BurstCube, Lunar Trailblazer and Anik-E2. GitHub code search on the repository default branch returned no matches for the exact mission names/IDs checked (SARJ, UARS, BurstCube, Lunar Trailblazer, Anik E2 / Anik-E2). This is a **limited repository-default-branch search only**; it does not establish absence from PRs, historical bundles, chats, connected retrieval, or model pretraining. Because the sources have now been read in this coordinator workflow, they are not treated as hidden from this coordinator/model context.

| Mission/source | Verified source facts | Rights / source quality | Decision for this experiment |
|---|---|---|---|
| ISS SARJ bearing anomaly, NASA/TP-2011-217116, NTRS 20110015384 | Starboard SARJ drive current exceeded safety limits shortly after installation; investigation used EVAs, sample collection, structural/thermal analyses and build-record review; root cause described as kinematic design vulnerability combined with inadequate lubrication and manufacturing flaws; recovery included component replacement and grease application. | NTRS marks Public / Work of US Gov. Public Use Permitted. Three NASA authors listed. Full primary report is available. | **Strong development candidate, NOT admitted to blind holdout.** Technically rich and traceable, but same ISS platform as BGA and full independent source-cluster relation must be assessed. It has now been exposed to the coordinator/model in this workflow; do not silently use it as a hidden holdout for this context. |
| UARS in-flight dynamics, NASA-TM-110325, NTRS 19970019258 | Flight data over 737 days used to investigate thermal snap at terminator crossings and solar-array/harmonic-drive excitation; report describes excessive vibration amplitude and modal response, not a clearly bounded fault event or confirmed failure. | NTRS marks Public / Work of US Gov. Public Use Permitted; single NASA author. | **Not admitted.** Useful engineering context, but the source abstract describes dynamics characterization rather than a discrete spacecraft fault-diagnosis case; weak fit to the current case target. |
| BurstCube 2024 mission, SSC25-III-02 | The paper describes COTS reaction-wheel issues, improper deployment of one solar-array wing covering the star tracker, attitude-knowledge issues and command-sequence logic changes. It states the exact root cause of the reaction-wheel anomaly is not established in the cited narrative; the instrument remained healthy and the mission ended amid low altitude, attitude-control difficulty and spotty communications. | Public conference paper accessible through NASA-associated proceedings; author list includes non-NASA affiliations and NASA credits. A clear derivative-reuse license was not established in this screen. | **Not admitted.** Rich chronology but multiple interacting anomalies and unresolved causal boundaries; a single diagnosis target risks collapsing separate events. Rights review also remains open. |
| Lunar Trailblazer 2025 loss of contact, Earth and Space Science (first published 2026-08-17), DOI 10.1029/2025EA004734 | Paper reports post-launch software anomalies, solar panels pointed away from Sun, radio restart in off-nominal configuration, battery depletion, short telemetry receipt and unsuccessful recovery. The paper distinguishes observed events from inferred state and recovery constraints. | Publisher page identifies Open Access, but footer reserves text/data mining and AI training rights to AGU/Wiley; no permissive license for derivative training use was verified here. | **Rights HOLD / not admitted.** Scientifically excellent, particularly for separating observed telemetry, software behavior and inferred state; however publisher's rights notice makes it unsuitable for this confirmatory dataset without explicit permission. |
| Anik-E2 1991 antenna deployment anomaly / 1994 attitude-control anomaly | Public abstracts and historical summaries describe two different event families: 1991 C-band antenna deployment failure and 1994 momentum-wheel control failure after a space-weather event. A peer-reviewed public article describes telemetry/diagnostic-test elimination of alternatives and an ESD-related control-circuit mechanism; recovery involved ground-loop attitude control. | Sources include an Elsevier paper with rights-controlled access and public historical/agency summaries. No source-specific derivative-use permission was established. | **Not admitted.** This coordinator has now read the source material; it is no longer hidden from this context. The 1991 and 1994 events must not be merged as one case. 1994 Anik-E1/E2 failures are one shared space-weather episode and should be one event cluster, not two independent samples. |

Primary sources checked:
- SARJ NTRS record: https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20110015384.pdf
- UARS NTRS record: https://ntrs.nasa.gov/citations/19970019258
- BurstCube paper: https://ntrs.nasa.gov/api/citations/20250007104/downloads/Tian%20-%20SSC25%20Paper.pdf
- Lunar Trailblazer paper: https://doi.org/10.1029/2025EA004734
- Anik-E2 recovery mission: https://www.sciencedirect.com/science/article/abs/pii/009457659390162P
- Anik-E1/E2 1994 analysis: https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2012SW000811

### Measured result of this screening round

- Five mission/source families reviewed.
- Three have technically useful source material (SARJ, Lunar Trailblazer, Anik-E2), but each is blocked by exposure or rights/cluster gates.
- UARS is a poor task-contract fit; BurstCube is causally ambiguous for a single target and has unresolved reuse scope.
- Repository default-branch search matches: 0 for the exact strings checked. This is not a complete exposure audit.
- New independent confirmatory clusters admitted: **0**.
- New task packets, generated answers, reviews, model calls: **0**.
- No holdout, rubric, threshold, weights, or prior scores changed.

**No performance gain can be claimed from this round.** Its value is improved source triage and explicit exclusion reasons. The 2×2 remains NOT_RUN.


## Additional archival primary-source check — Nimbus I solar-array drive failure (2026-11-20)

A potentially strong historical case was located in a 69-page scan served through NASA NTRS (accession N68-28825; internal General Electric report dated 1966-08-06, *Final Report - Failure Analysis and Design Report of Nimbus I Solar Array Drive Failure*). The source gives a rich, bounded sequence: after 26 days of operation, solar-array drive control-phase voltage rose over successive orbits, saturated, intermittently recovered, then stalled permanently; the report's conclusion attributes the failure to high motor-bearing temperature, grease deterioration, increased friction and motor stall. It describes flight-data analysis, failure-mode analysis, verification testing, and design changes. It would be technically useful for evidence-role separation and distinguishing telemetry symptoms from post-flight physical cause.

However, the scanned document itself carries the prominent restriction **“FOR USE OF G.E. EMPLOYEES ONLY”** and identifies General Electric Technical Information Series No. 66SD281. NASA NTRS hosting/accessibility and a US Government scan do not override this source-specific restriction or establish a derivative dataset/AI-training license. The current search did not establish permission from GE or its successor rights holder.

Primary source inspected: https://ntrs.nasa.gov/api/citations/19680019353/downloads/19680019353.pdf (especially scanned title page and pp. 1–6; checked 2026-11-20).

**Decision: RIGHTS BLOCK / DO NOT USE.** Do not create an L0 card, quote/republish its contents in the dataset, or include Nimbus I as a confirmatory holdout unless explicit rights clearance is obtained. This is a deliberate exclusion despite its strong technical fit.

### Measured outcome

- One technically strong case found and source-level evidence inspected.
- One candidate rejected on explicit source-document restriction.
- New eligible independent clusters: **0**.
- L0/L1 tasks, generated answers, reviews: **0**.
- Holdout, rubric, weights, thresholds and previous scores: unchanged.
- No model calls or training.

This search round improved the quality of the exclusion decision but produced no increase in usable evaluation data and no performance evidence.
