# EPS Domain Review Checklist — Public-Literature Pilot

**Status:** REVIEW REQUESTED. No EPS term or source passage is marked expert-approved by this worksheet.

Review the exact source passage and claim boundary, not only the generated summary. Use ACCEPT, EDIT, REJECT or NOT_VERIFIED. An empty cell means not reviewed.

## 1. EPS terminology review

| Term ID | Preferred Chinese | Preferred English | Boundary requiring review | Decision | Reviewer note |
|---|---|---|---|---|---|
| eps | 电源分系统 | Electrical Power Subsystem | generation, storage, management and distribution scope |  |  |
| solar_array | 太阳电池阵 | Solar Array | array vs solar wing/panel |  |  |
| solar_cell | 太阳电池 | Solar Cell | cell vs module/string |  |  |
| solar_array_string | 太阳电池串 | Solar Cell String | series string vs parallel segment |  |  |
| solar_array_circuit | 太阳电池阵电路 | Solar Array Circuit | circuit boundary is mission-specific |  |  |
| solar_array_bus | 太阳电池阵母线 | Solar Array Bus | array output vs regulated spacecraft bus |  |  |
| battery | 蓄电池组 | Spacecraft Battery | battery chemistry and series/parallel topology |  |  |
| battery_cell | 蓄电池单体 | Battery Cell | cell vs common-pressure-vessel cell stack |  |  |
| battery_cell_voltage_collapse | 电池单体电压塌陷 | Battery Cell Voltage Collapse | symptom vs root-cause mechanism |  |  |
| battery_internal_short | 电池单体内部短路 | Battery Cell Internal Short | counterfactual IMAGE analysis, not observed IMAGE fault |  |  |
| battery_open_cell | 电池单体开路 | Battery Cell Open Circuit | counterfactual IMAGE analysis, not observed IMAGE fault |  |  |
| battery_heater_control | 电池加热控制 | Battery Heater Control | heater, HCE, thermostat and thermal response |  |  |
| power_distribution_unit | 配电单元 | Power Distribution Unit | equipment vs function block |  |  |
| solid_state_power_controller | 固态功率控制器 | Solid-State Power Controller | physical output vs status telemetry |  |  |
| power_bus_voltage | 电源母线电压 | Power Bus Voltage | source/storage/regulator/load coupled variable |  |  |
| bus_voltage_limiter | 母线电压限制器 | Bus Voltage Limiter | shunt regulator vs series regulator |  |  |
| parasitic_shunt_current | 寄生分流电流 | Parasitic Shunt Current | unintended static shunt vs commanded regulation |  |  |
| eps_reset_circuit | 电源分系统复位电路 | EPS Reset Circuit | reset path vs main power conversion |  |  |
| schmitt_trigger_inverter | 施密特触发反相器 | Schmitt Trigger Inverter | logic element vs main power switch |  |  |
| single_event_latchup | 单粒子闩锁 | Single-Event Latchup | SEL vs SEU vs destructive burnout |  |  |
| single_event_upset | 单粒子翻转 | Single-Event Upset | SEU vs SEL |  |  |
| electrolyte_bridging | 电解液桥接 | Electrolyte Bridging | WMAP consensus theory, not proven root cause |  |  |
| solar_array_bus_ground_short | 太阳电池阵母线对地短路 | Solar Array Bus-to-Ground Short | NOAA-13 review's surmised mechanism |  |  |
| battery_state_of_charge | 荷电状态 | State of Charge | SOC estimate vs direct cell health measurement |  |  |
| mmod_strike | 微流星体或轨道碎片撞击 | Micrometeoroid or Orbital Debris Impact | TERRA report's likely/suspected cause; not confirmed impact location |  |  |

## 2. Source-passage review

| Passage ID | Source | Review focus | Decision | Reviewer note |
|---|---|---|---|---|
| IMAGE_SSPC_SEU_INSTANT_TRIP | NASA IMAGE FRB | likely SEU-induced instant trip; preserve alternative causes |  |  |
| IMAGE_SSPC_STATUS_TELEMETRY_MISMATCH | NASA IMAGE FRB | physical SSPC output vs stale status bit and FDC response |  |  |
| IMAGE_BATTERY_INTERNAL_SHORT_COUNTERFACTUAL | NASA IMAGE FRB | alternative hypothesis explicitly not observed |  |  |
| IMAGE_BATTERY_OPEN_CELL_COUNTERFACTUAL | NASA IMAGE FRB | counterfactual bus response under sunlight/eclipses |  |  |
| IMAGE_SOLAR_ARRAY_STRING_COUNTERFACTUAL | NASA IMAGE FRB | array architecture and no observed array anomaly |  |  |
| NOAA13_SOLAR_ARRAY_BUS_GROUND_SHORT | NASA Lessons Learned #387 | thermal/mechanical short is surmised, not teardown-confirmed |  |  |
| IDEASSAT_EPS_RESET_CIRCUIT_SEL | IDEASSat 2022 | inverter likely cause; SEL possible mechanism |  |  |
| TERRA_BATTERY_HEATER_CONTROL_ANOMALY | NASA TERRA 2010 paper | simultaneous cell and heater-control anomalies; thermal model and corrective actions |  |  |
| TERRA_MMOD_COMMON_CAUSE_HYPOTHESIS | NASA Terra status summary 2014 | suspected MMOD common cause; no confirmed impact location or recovered debris |  |  |
| TDRS8_SOLAR_ARRAY_CIRCUIT_FAILURES | NASA TDRS-8 2019 | six of 32 circuits failed; physical root cause not specified |  |  |
| TDRS8_BVL_PARASITIC_SHUNT | NASA TDRS-8 2019 | static parasitic shunt vs voltage regulation |  |  |
| TDRS8_BATTERY_UNDERPERFORMING_CELLS | NASA TDRS-8 2019 | underperformance is not a confirmed internal short/open |  |  |
| WMAP_NIH2_CELL_VOLTAGE_COLLAPSE | NASA NESC WMAP 2010 | voltage collapse; root cause unresolved; electrolyte bridge theory |  |  |
| EPS_ON_ORBIT_FAILURE_STATISTICS | Kim et al. 2012 | subsystem statistics, not component-level causal evidence |  |  |
| NASA_SMALLSAT_EPS_ARCHITECTURE | NASA SmallSat Power 2026 | architecture reference, not flight-fault evidence |  |  |

## 3. Cross-cutting review rules

- [ ] A battery cell voltage collapse is not automatically an internal short.
- [ ] A lower solar-array current is not automatically a solar-cell failure.
- [ ] A physical switch state and a telemetry status bit can disagree.
- [ ] An observed symptom, likely cause, hypothesis and counterfactual are represented as different evidence statuses.
- [ ] A simultaneous battery and heater-control anomaly is not automatically a causal chain.
- [ ] SEU, SEL and destructive radiation damage are not synonyms.
- [ ] A component-level failure is not inferred from a subsystem-level performance reduction without localization evidence.
- [ ] A source passage's uncertainty language is preserved in the candidate and final label.

## 4. Review record

- Reviewer identifier:
- Review date:
- Reviewed commit SHA:
- Overall decision: ACCEPT / ACCEPT_WITH_EDITS / REJECT / INCOMPLETE
- Required changes:
- Rationale:

Do not mark EPS terms expert-approved or promote the EPS Skill until decisions and rationales have been incorporated and the revised branch passes CI.
