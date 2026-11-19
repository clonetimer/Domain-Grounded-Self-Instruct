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
| IMAGE 2005 loss of communications / transponder power path | IMAGE Failure Review Board Final Report, 2006-09-19, NASA/GSFC-hosted report: https://spdf.gsfc.nasa.gov/pub/data/image/documents/website/image.gsfc.nasa.gov/publication/document/IMAGE_FRB_Final_Report.pdf | Report states likely SEU-induced instant trip of transponder SSPC; several less likely causes cannot be eliminated. It describes nominal telemetry before loss, unsuccessful recovery attempts, and a design issue where instant trips were not reflected in status telemetry. | NASA-hosted public report found; exact reuse terms for derivative dataset still require confirmation. Do not infer blanket license solely from hosting. | Not listed among the explicit PR #188 exclusions, but repository-wide and retrieval-exposure checks remain required. | HOLD — rights and exposure review |
| ISS US solar-array Beta Gimbal Assembly rising motor-current anomaly (2000–2001) | NASA NTRS 20030014592, NASA/TM-2003-212012: https://ntrs.nasa.gov/citations/20030014592 | NTRS abstract reports higher-than-expected BGA drive-motor currents increasing over time on both assemblies; EPS analyses supported operational workarounds to reduce BGA use while maintaining adequate solar-array power. | NTRS record explicitly states “Public Use Permitted” and distribution limits “Public”. Verify any third-party material embedded in the full PDF before reuse. | Not listed among explicit PR #188 exclusions; still requires repository-wide and retrieval-exposure check. Event family is distinct from IMAGE. | CONDITIONAL CANDIDATE — rights evidence present; exposure and full-text audit pending |
| MethaneSAT 2025-06-20 loss of communications | New Zealand MBIE-hosted Appendix 9 anomaly investigation report: https://www.mbie.govt.nz/dmsdocument/31529-appendix-9-methanesat-anomaly-investigation-report | Report says last received data were nominal; no post-anomaly telemetry was available; the investigation narrowed the direct event to flight avionics or EPS but could not identify the specific failure. It lists three possible contributors without ranking their relative likelihood. | Government-hosted appendix, but underlying report is authored by MethaneSAT LLC and partners; derivative reuse/IP permission is not established. | Not listed among explicit PR #188 exclusions; full exposure check remains required. | HOLD — rights and exposure review |

## Source-fidelity constraints

- IMAGE: preserve “likely” for the SEU/SSPC explanation; do not promote it to certain root cause. Distinguish source report findings from any later synthetic upstream ML candidate.
- ISS BGA: the source abstract supports increasing motor current and EPS workaround analyses; do not infer a confirmed motor mechanical root cause from the abstract. Full report review is required before an L0 fact card.
- MethaneSAT: retain the investigation's unresolved distinction between flight avionics and EPS and the explicit statement that relative likelihood among the three possible contributors could not be stated. Do not choose one contributor.
- None of these public reports supplies an actual upstream ML model output/run, structured diagnostic log, or current LLM-ready task input. Such fields must remain absent in L0 and, if later needed for an L1 synthetic experiment, be labeled SYNTHETIC with field-level generation provenance.

## Current gate result

- Candidate documents screened: 3.
- Rights fully cleared for derivative DGSI use: 0.
- Event/source clusters admitted to confirmatory holdout: 0.
- L0 fact cards created: 0.
- L1 tasks created: 0.
- Official holdout manifest changed: false.
- Existing holdout cases or scores changed: false.
- Model calls / generation / fine-tuning: not performed.

## Next actions

1. Obtain explicit reuse/IP determination for IMAGE and MethaneSAT; verify third-party content in the ISS NTRS PDF.
2. Run repository-wide source-hash, event-family, prior-chat/retrieval exposure and excluded-lead checks for all three candidates.
3. Read the full ISS NTRS report before deciding whether its abstract has enough detail; do not treat an abstract as a complete engineering fact card.
4. Only after rights and exposure gates pass, draft L0 fact cards with page/section locators and explicit missing-material fields for independent review.
5. If fewer than the preregistered minimum of independent clusters pass, keep the 2×2 experiment at NOT_RUN. Do not substitute familiar or exposed cases.

