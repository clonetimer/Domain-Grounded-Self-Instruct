# P5-C1: remaining L0 source precheck — Cassini, FUSE and S-band TWTA

Date: 2026-11-17  
Status: public-source precheck only. This is not independent domain-expert approval, source-rights clearance or SFT admission.

## 1. Cassini reaction-wheel low-speed anomaly

L0 card: `LIT-CASSINI-RWA-DRAG-007`  
Primary source: NASA/JPL LLIS Lesson 1416, “Cassini RWA Flight Anomaly Due to Extended Use at Slow Speed (2001)”. https://llis.nasa.gov/lesson/1416  
Corroborating contemporaneous source: NASA Cassini Significant Event Report, week ending 2001-01-05. https://science.nasa.gov/missions/cassini/significant-event-report-for-week-ending-152001/

Source-supported facts:
- Higher-than-normal drag was detected after prolonged operation at very low speed approaching zero rpm.
- Reduced lubricant dispersal is described as the likely cause; frequent speed oscillations around zero rpm may also have contributed.
- The anomaly interrupted science observations for nine days. Operating at higher speeds apparently restored lubricant distribution and eliminated the drag.
- The LLIS distinguishes zero-speed dwell, described as benign, from prolonged residence in the low-rpm region, which may contribute to bearing/lubricant failure mechanisms.
- The contemporaneous report says manufacturer/JPL discussions considered inadequate bearing lubrication distribution due to extended low-speed operation the likely cause; it documents return to reaction-wheel control on Dec. 21 followed by six days of monitoring without recurrence.

Review decisions:
- Preserve “likely” and “apparently”; do not upgrade the cause to physically confirmed root cause.
- Distinguish prolonged low-speed operation from stationary zero rpm.
- Separate anomaly onset, nine-day science interruption, Dec. 21 return to RWA control and subsequent six-day monitoring.
- Preserve both candidate contributing mechanisms: lubricant distribution reduction and frequent speed oscillations around zero.
- Verify the L0 card's episode dates and ISA Z70706/Z70716 references against the original incident records; LLIS lists Jan. 4 and Jan. 8, 2001 as references, while the precursor operational history spans December 2000.

## 2. FUSE reaction-wheel failures

L0 card: `LIT-FUSE-RWA-KAPTON-001`  
Primary source: “FUSE In-Orbit Attitude Control with Two Reaction Wheels and No Gyroscopes”, SPIE 4854-72, Section 3. https://archive.stsci.edu/fuse/papers/spie4854/spie_4854-72.pdf  
Corroborating source: FUSE Archival Instrument Handbook, Chapter 7, §7.3 and Table 7.3-1. https://archive.stsci.edu/fuse/fuse_ihb_090616_final.pdf

Source-supported facts:
- On Aug. 4, 2000 the ACS flight software shut down the pitch-axis reaction wheel after increased drag.
- Vendor analysis identified growth of small bubbles in Kapton tape lining the inner wheel housing as the likely cause. The tape was used to absorb launch-vibration loads while maintaining a close rotor-to-housing clearance.
- After restart, above-normal drag persisted for several minutes and then disappeared; the paper attributes this to gradual wearing-away of Kapton in contact with the rotor, consistent with the bubble hypothesis.
- The yaw wheel experienced a similar shutdown on Feb. 16, 2001 and required nearly three days of operation before increased drag disappeared.
- The paper separately states that wheel failures were ascribed by the vendor to thermally induced housing distortion causing rotor contact. Do not conflate this broad attribution with the specific Aug. 2000 Kapton-bubble hypothesis without further evidence.
- The handbook lists the Aug. 4, 2000 pitch-wheel stop and restart on day 258 (Sep. 14, 2000), plus later distinct wheel events and final failures.

Review decisions:
- The L0 card uses one event episode ID for the Aug. 2000 pitch-wheel event but its locator mentions later events and broad vendor attribution. Decide whether the Feb. 2001 yaw-wheel event is a separate L0 episode or linked related episode; do not collapse both into one occurrence.
- Keep the Kapton-bubble explanation as vendor-attributed likely cause, not a directly verified teardown result unless evidence supports it.
- Separate the initial recoverable shutdown from later final wheel failures.
- Preserve the handbook's approximately 40-day restart interval and distinguish it from the SPIE paper's initial high-drag behavior.
- Give the broader thermal-distortion statement its own claim-level locator and attribution.

## 3. Spaceborne S-band linearized TWTA output-power decline

L0 card: `LIT-SPACEBORNE-TWTA-HYDROGEN-011`  
Source: Wang Jun, Yu Xumin and Xu Lei, “Research on the output power decline problem of a spaceborne S-band linearized traveling wave tube amplifier”, Space Electronic Technology, 2026, 23(2):46–53, DOI 10.3969/j.issn.1674-7135.2026.02.007.  
Article: https://kjdzjs.spacejournal.cn/article/doi/10.3969/j.issn.1674-7135.2026.02.007  
Issue listing: https://kjdzjs.spacejournal.cn/article/2026/2

Publisher abstract supports:
- During whole-spacecraft transponder performance testing, one S-band TWTA showed an output-power decline of approximately 4 dB.
- Fault-tree analysis and multiple ground troubleshooting tests were conducted.
- The paper attributes the problem to hydrogen poisoning of low-noise amplifier chips inside two microwave modules in the linearized channel amplifier.
- Corrective action was replacement with same-model modules from another batch with qualified hydrogen content; the paper reports the unit returned to normal after experimental verification.

Review decisions:
- Classify as GROUND_TEST_EVENT, not an in-orbit flight anomaly.
- Distinguish the TWTA output symptom from the cause localized to two LNA chips in the linearized-channel microwave modules.
- Do not attribute the fault to the TWTA electron gun, cathode or helix; the abstract localizes it to LNA chips.
- The detailed FGM/ALC, Z2/Z6, hydrogen-content and EMMI evidence in the L0 locator must be checked against the full article before expert approval.
- The journal article's copyright/licensing terms are not established by public accessibility. Obtain rights review before training or substantial derivative reuse.

## 4. Cross-case corrections and source-use gate

- Cassini and FUSE are separate missions, wheel designs and mechanisms.
- FUSE's Aug. 2000 pitch-wheel recovery and later yaw-wheel event should be separated or explicitly linked as related episodes.
- Cassini's low-speed lubricant-distribution hypothesis is not the same as FUSE's Kapton tape / rotor-housing interference hypothesis.
- The S-band TWTA case is a ground test and concerns LNA hydrogen poisoning; it is not a TWTA electron-gun/helix failure.
- NASA/JPL public availability and journal abstract accessibility do not themselves grant third-party training rights.

All three L0 cards remain AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION. This is a preliminary source cross-check, not expert approval, Gold admission, split assignment or SFT authorization.
