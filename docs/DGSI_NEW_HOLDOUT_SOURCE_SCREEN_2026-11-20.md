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

