# ADCS Domain Review Checklist — P1-B

**Status:** REVIEW REQUESTED. No term or source passage is marked expert-approved by this worksheet.

This checklist is intended for an ADCS domain reviewer. It is a review aid, not an automatic certification. Record a decision and rationale for every row. Use `ACCEPT`, `EDIT`, `REJECT`, or `NOT_VERIFIED`; an empty cell means not reviewed.

## 1. Terminology review

Review preferred Chinese/English labels, definition boundaries, alias classes and the cited source. Pay particular attention to whether a shorthand is context-dependent and whether a related structure is being incorrectly treated as a synonym.

| Term ID | Preferred Chinese | Preferred English | Alias / related-term issue to check | Decision | Reviewer note |
|---|---|---|---|---|---|
| `adcs` | 姿态确定与控制系统 | attitude determination and control system | “姿态控制系统” may omit determination |  |  |
| `gyro` | 陀螺仪 | gyroscope | “角速度传感器” is broader than gyroscope |  |  |
| `reaction_wheel` | 反作用飞轮 | reaction wheel | “飞轮” is contextual shorthand |  |  |
| `star_tracker` | 星敏感器 | star tracker | “星敏” is informal shorthand |  |  |
| `sun_sensor` | 太阳敏感器 | sun sensor | “太敏” is informal shorthand |  |  |
| `magnetometer` | 磁强计 | magnetometer | Verify consistent use vs. magnetic-field sensor |  |  |
| `magnetorquer` | 磁力矩器 | magnetorquer | “磁力矩杆” is a structural subtype, not a universal synonym |  |  |
| `angular_velocity` | 角速度 | angular velocity | Verify physical quantity vs. sensor output |  |  |
| `gyro_bias` | 陀螺仪零偏 | gyroscope bias | “角速度测量偏置” may refer to a broader measurement chain |  |  |
| `measurement_noise` | 测量噪声 | measurement noise | Distinguish noise, bias, drift and quantization |  |  |
| `fault_mode` | 故障模式 | fault mode | Distinguish failure mode from symptom and injection event |  |  |
| `fault_source` | 故障源部件 | fault-source component | Distinguish originating component from affected component |  |  |
| `affected_component` | 受影响部件 | affected component | Do not infer root cause from impact alone |  |  |
| `telemetry` | 遥测数据 | telemetry data | Catalog schema is not an observed sample |  |  |
| `uncertainty` | 诊断不确定性 | diagnostic uncertainty | Distinguish ambiguity, conflict and insufficient evidence |  |  |
| `evidence` | 诊断证据 | diagnostic evidence | Distinguish evidence source, evidence item and claim |  |  |

## 2. Source-passage review

For each row, open the linked source and verify the locator, applicability and allowed claim boundary. Do not approve a passage solely because its URL resolves.

| Passage ID | Source / locator | Review questions | Decision | Reviewer note |
|---|---|---|---|---|
| `NASA_GNC_ADCS_SCOPE` | [NASA SmallSat GNC §5.1](https://www.nasa.gov/smallsat-institute/sst-soa/guidance-navigation-and-control/) | ADCS scope, sensor/actuator roles |  |  |
| `NASA_REACTION_WHEEL_FUNCTION` | NASA SmallSat GNC §5.2.2 | Torque, momentum storage and saturation scope |  |  |
| `NASA_MAGNETIC_TORQUER_ROD_RESIDUAL_FIELD` | NASA SmallSat GNC §5.2.3 | Residual field and magnetometer interaction; rod subtype boundary |  |  |
| `NASA_STAR_TRACKER_VALIDITY` | NASA SmallSat GNC §5.2.5 | Field of view, angular rate, glare and solution validity |  |  |
| `NASA_MAGNETOMETER_LOCAL_FIELD` | NASA SmallSat GNC §5.2.6 | Multiple local magnetic sources; no unique root-cause signature |  |  |
| `NASA_SUN_SENSOR_ESTIMATION` | NASA SmallSat GNC §5.2.7 | Sun direction measurement, attitude observability and albedo/glint |  |  |
| `NASA_INERTIAL_SENSOR_GYRO_BIAS` | NASA SmallSat GNC §5.2.9 | Gyro/IMU role, bias and bias drift; no universal threshold |  |  |
| `NASA_NESC_BP5` | [NASA/TP-20230005922, printed p.68](https://ntrs.nasa.gov/api/citations/20230005922/downloads/20230005922.pdf?attachment=true) | Independence of fault management from fault-causing/diagnosing elements |  |  |
| `CNSA_ADCS_CLOSED_LOOP` | [CNSA satellite attitude control](https://www.cnsa.gov.cn/n6758968/n6758973/c10578880/content.html) | Chinese terminology and sensor-controller-actuator loop; educational vs normative status |  |  |
| `ASTROGRAPH_PROJECT_SCHEMA_V3` | [AstroGraph schema v3](https://github.com/clonetimer/AstroGraph-LLM/blob/9bdb92e95f1878b7ed057c169fcd116ae29ec83f/src/astrograph/knowledge/schema_v3.py) | Project schema only; do not treat it as physical-domain authority |  |  |
| `BASILISK_2_11_0_RELEASE` | [Basilisk 2.11.0 release notes](https://avslab.github.io/basilisk/Support/bskReleaseNotes/2.11.html) | Version identity only; module-specific behavior needs versioned docs/tests |  |  |

## 3. Cross-cutting diagnostic rules

- [ ] A measured channel anomaly is not automatically a component fault.
- [ ] An affected component is not automatically the fault-source component.
- [ ] A catalogued fault or declared simulation capability is not an observed run.
- [ ] Correlation, temporal coincidence and a graph edge do not automatically establish causality.
- [ ] A causal claim needs a source passage that authorizes the claim type and independent case-level evidence.
- [ ] A shared measurement source is not independent corroboration.
- [ ] If evidence is insufficient, ambiguous or conflicting, preserve that status rather than forcing a diagnosis.
- [ ] A human-review status requires an independently recorded reviewer decision; model-generated text is not a review receipt.

## 4. Review record

- Reviewer identifier (recorded by the project owner, not generated by the model):
- Review date:
- Reviewed commit SHA:
- Overall decision: `ACCEPT` / `ACCEPT_WITH_EDITS` / `REJECT` / `INCOMPLETE`
- Required changes:
- Rationale:

Do not change `resources/terms.json` or promote the Skill to production-ready until the reviewed decisions and rationales have been incorporated and the revised version has passed CI.
