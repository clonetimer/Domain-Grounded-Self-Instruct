# P5-C1: initial public-source precheck (not domain approval)

Date: 2026-11-17  
Status: preliminary source-navigation and consistency check. All 12 L0 cards remain pending independent domain-expert review and source-rights review. This note does not approve any card or authorize SFT use.

## 1. SEASAT slip-ring failure

L0 card: LIT-SEASAT-SLIPRING-001  
Source: NASA, Report of the Seasat Failure Review Board, Document ID 20040171604.  
Source: https://ntrs.nasa.gov/archive/nasa/casi.ntrs.gov/20040171604.pdf

Precheck observations:
- The report summary attributes the spacecraft power loss to a massive, progressive short in a slip-ring assembly connecting rotating solar arrays to the power subsystem.
- It describes an arc between adjacent slip-ring brush assemblies as the most likely cause.
- The trigger remains a set of alternatives: wire-to-brush contact, brush-to-brush contact, or a contaminant bridging opposite-polarity components.

Review consequence: retain the board's MOST_LIKELY certainty and preserve the trigger alternatives. Do not collapse the event to one proven trigger mechanism. The cited NASA source metadata states public use is permitted; retain the source's own report identity and exact summary/page locator.

## 2. TROPICS slip-ring event family

L0 cards:
- LIT-TROPICS-SLIPRING-TVAC-002
- LIT-TROPICS-FLIGHT-CRC-003-A
- LIT-TROPICS-FLIGHT-CRC-003-B
- LIT-TROPICS-PATHFINDER-CROSSSHORT-004

Source: Cunningham et al., Lessons Learned from the NASA TROPICS CubeSat Constellation Mission, NASA NTRS 20240011771, Section 6, PDF pp. 3–5.  
Source: https://ntrs.nasa.gov/api/citations/20240011771/downloads/IEEEAero_TROPICS_2025_for_approval.pdf

Precheck observations:
- During TVAC calibration of the first flight payload, UART CRC errors were observed; oscilloscope observations indicated a discontinuity likely in the slip ring. A wire-bundle/brush-misalignment theory was considered, but CRC errors remained after routing modifications.
- Later CRC errors were observed on two payloads. Reverse rotation was a successful mitigation for one; the other worsened and became non-operational.
- The Pathfinder event is a distinct episode: a later anomaly affected SADA drive, star tracker and payload. The paper states excessive slip-ring debris could have shorted the 12 V bus and serial line, and considered this more likely than three simultaneous destructive SEL events.

Review consequence:
- Preserve the four cards as distinct episodes/event classes; do not merge TVAC qualification/flight-payload testing, two separate payload CRC histories, and Pathfinder's cross-interface damage into one fault episode.
- Preserve uncertainty: the Pathfinder slip-ring-debris explanation is presented as more likely, not as a direct physical confirmation in the cited passage.
- Keep the two payload outcomes and mitigation difference separate; do not transfer the reverse-spin mitigation from one payload to the other.

**Source-rights blocker:** the PDF states © 2025 Massachusetts Institute of Technology and describes U.S. Government unlimited rights, while also warning that uses other than specifically authorized by the U.S. Government may violate copyright. Public NTRS accessibility does not establish unrestricted third-party model-training rights. Keep these four cards pending until the responsible rights authority confirms the permitted use for the intended DGSI training/derivation purpose. Do not copy substantial source text into generated tasks or training data while this is unresolved.

## 3. Lunar Orbiter III TWTA cases

L0 cards:
- LIT-LUNAR-ORBITER-HELIX-005
- LIT-LUNAR-ORBITER-POWER-MONITOR-006

Source: NASA-CR-66461, Lunar Orbiter III Mission System Performance, NASA NTRS Document ID 19670027946.  
Source: https://ntrs.nasa.gov/api/citations/19670027946/downloads/19670027946.pdf

Precheck observations:
- The first-turn-on helix-current anomaly is not uniquely explained. The report preserves two candidate explanations: mechanical stresses induced by launch and later relieved by temperature cycles, or slow internal pressure decay/outgassing.
- The CE02 TWTA output-power indication is a separate measurement-chain issue. The report describes the indication as excessively temperature-sensitive and identifies a diode power monitor in the filter/monitor assembly; the summary attributes the variation to temperature-dependent diode rectification characteristics.

Review consequence:
- Keep first-turn-on helix-current anomaly and CE02 output-power measurement variation as separate episodes/diagnostic tasks within the same report family.
- Do not interpret the CE02 indication as proof that actual RF output changed by the same amount. Preserve the distinction between measured telemetry indication and physical TWTA output.
- Preserve both competing explanations for the first-turn-on helix-current anomaly; do not choose one without discriminating evidence.

## 4. NASA 22-N hydrazine life-test cases

L0 cards:
- LIT-NASA-HYDRAZINE-INJECTOR-009
- LIT-NASA-HYDRAZINE-CATALYST-010

Source: NASA-TM-100232, A Life Test of a 22-Newton (5-lbf) Hydrazine Rocket, NASA NTRS Document ID 19880002368.  
Source: https://ntrs.nasa.gov/api/citations/19880002368/downloads/19880002368.pdf

Precheck observations:
- The test ended at 60.2 hours after residual hydrazine in the propellant valve autodecomposed during heat-lamp heating; the resulting valve pressure caused a violent valve event and Teflon valve-seat material was ejected into and plugged the injector tube.
- Separately, analysis found iron/nickel contamination in the catalyst; the source traces the metal contamination to a contaminated "pink" hydrazine barrel and describes catalyst poisoning/washout.
- The source explicitly distinguishes the injector blockage from the catalyst contamination; the test did not reach the predetermined end-of-life roughness criterion.

Review consequence:
- Preserve injector blockage and catalyst poisoning as separate mechanisms/episodes within the same test/report family.
- Do not say the metal contamination caused the Teflon injector blockage, or that the catalyst reached its planned end-of-life criterion.
- Retain the actual sequence and distinguish the test termination event from catalyst degradation evidence.

## 5. Gate decisions

These observations are preliminary consistency checks, not domain-expert approvals. For every card, the expert reviewer must still inspect the cited passage and confirm source statement, certainty, event class, event-family/episode grouping, fault source versus affected components, recorded disposal, migration constraints and missing evidence.

For the TROPICS cards, rights clearance is an additional independent blocker. Do not mark any of these cards DOMAIN_EXPERT_CONFIRMED or authorize L1/SFT use based on this note.

All generated L1 scenarios remain LITERATURE_DERIVED_SYNTHETIC, REVIEW_REQUIRED, not Gold, and training-disabled.
