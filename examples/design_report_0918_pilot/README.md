# DGSI Design Report 0918 Pilot

Source: user-uploaded `航天器自主故障诊断与重构仿真验证平台_方案设计报告_0918.docx` (63 pages; SHA-256 `573765ababd2a370ae838d9c185b855036d8dd904427da14d7bc034e767faf4e`). The original document is not copied into this repository.

## Results
- 20 source-derived design facts with page/section locators.
- 6 design-derived hypothetical diagnostic candidates.
- 0 observed fault episodes, 0 test reports, 0 simulation run logs and 0 upstream ML bundles were supplied.
- All candidates are `REVIEW_REQUIRED`; no Gold or SFT export is authorized.

## Interpretation boundary
These are not real-case records and not simulator-run candidates. Each prompt explicitly labels its scenario as hypothetical. Targets deliberately abstain from root-cause localization and request the missing evidence needed to distinguish fault modes. The 61-entry fault catalogue is a design declaration, not proof that all 61 injection paths were executed or validated.

## Main extracted domains
- ADCS: four-wheel pyramid, gyro/star/sun sensors, wheel telemetry and FDIR/reconfiguration design.
- EPS: solar array, battery, bus, UVLO and load-permission propagation.
- Propulsion: request → supply/autonomy permission → actual thrust/acceleration chain.
- TT&C/communications: geometric visibility is separate from power/autonomy permission and downlink enable.
- Fault injection: 61 configured items across sensor, reaction-wheel, propulsion and EPS domains.

## Quarantined source region
PDF pages 55–57 contain missile/aircraft SDG material inconsistent with the spacecraft report scope. Those claims are excluded pending source-owner clarification.

## Files
- `source_inventory.json`: source identity, hash and limitations.
- `source_facts.json`: atomic source claims with exact locators and certainty boundaries.
- `design_derived_candidates.json`: six hypothetical, truth-free candidate tasks.
- `design_derived_batch.schema.json`: separate intake schema; does not alter the current L1 production schema.

The original report, test reports, logs, hidden simulator truth and any private telemetry are not included.
