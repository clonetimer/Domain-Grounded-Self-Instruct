# DGSI L0 source-fact domain review matrix

**Review state:** `AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION`

All 13 cards are source-curation candidates, not domain-expert-confirmed facts and not SFT examples. `internal_review.not_for_sft=true` and `sft_eligible=false` remain mandatory. The 12 event cards used by the 15 L1 pilot and the one knowledge-only card are listed separately.

## Review rules

- Verify the cited source, exact page/section or passage, event type, and wording against the original public document.
- Preserve `certainty_in_source`; do not strengthen MOST_LIKELY, CANDIDATE, or NOT_STATED into CONFIRMED.
- Verify event family and episode boundaries; related episodes must not be merged.
- Verify fault-source versus affected-component separation.
- Verify disposal status against source text: executed, conditional, planned, not recorded, or not applicable.
- Review migration tier and every transfer constraint for the intended L1 task. A mechanism analogy is not a diagnosis of the user's case.
- Do not copy `curator_prompts`, `reviewer_questions`, or internal cautions into model-facing assistant targets.
- Record the expert decision and a digest of the separately retained authorized review record. The digest binds data; it does not authenticate identity by itself.

## Event source cards

### LIT-SEASAT-SLIPRING-001
- **Source:** Report of the Seasat Failure Review Board (NASA-NTRS-20040171604; NASA NTRS report summary)
- **Event:** FLIGHT_EVENT / PUBLIC_FLIGHT_REPORT; family `SEASAT-SLIPRING-1978`; episode `LIT-SEASAT-SLIPRING-001-EPISODE`
- **Phenomenon:** SEASAT在轨运行105天后失效，Agena母线电源丢失；调查报告将失效与连接旋转太阳翼和电源分系统的滑环组件发生渐进性短路联系起来。
- **Source cause statement:** 调查报告认为相邻滑环电刷组件间起弧是最可能原因；触发方式可能包括导线与电刷接触、电刷间接触或污染物跨接相反极性部件。
- **Source certainty:** `EXPLICIT_MOST_LIKELY`
- **Fault source:** 太阳翼旋转接口滑环组件内相邻电刷组件之间的电弧/短路路径
- **Affected components:** Agena母线电源；旋转太阳翼电源连接通路
- **Disposal:** `NOT_RECORDED`
- **Migration assessment:** 可用于SADA滑环/电刷风险识别；不能据此确证用户案例的碎屑起弧路径。
- **Transfer constraints:** 核实电刷极性、滑环几何、绝缘结构及短路时序。；用户案例须有碎屑、弧光或短路路径直接证据。
- **Materials absent from L0 source card:** upstream_ml_result, diagnostic_logs, spacecraft_context, operational_context, historical_cases, expert_adjudicated_target
- **Expert decision:** □ CONFIRM  □ REVISE  □ REJECT
- **Evidence/decision record:** ______________________________________________

### LIT-TROPICS-SLIPRING-TVAC-002
- **Source:** Lessons Learned from the NASA TROPICS CubeSat Constellation Mission (MITLL-TROPICS-LESSONS-2025; NASA NTRS 20240011771, Section 6, pp.3–4)
- **Event:** GROUND_TEST_EVENT / PUBLIC_GROUND_TEST_REPORT; family `TROPICS-SLIPRING-QUALIFICATION`; episode `TROPICS-FIRST-FLIGHT-PAYLOAD-TVAC`
- **Phenomenon:** 首个飞行载荷在热真空校准期间出现UART CRC错误；线束走线调整后问题仍存在，旋转状态下接触电阻在不同湿度环境中差异明显。
- **Source cause statement:** 调查认为间断可能发生在滑环，讨论了stick-slip及接触电阻波动。
- **Source certainty:** `EXPLICIT_MOST_LIKELY`
- **Fault source:** TROPICS载荷滑环旋转接触界面
- **Affected components:** 载荷UART串行通信链路
- **Disposal:** `SOURCE_RECORDS_MEASURE`; 来源随后记录了针对飞行载荷滑环的项目级筛选与返工流程（选择并润滑电刷/轴件、跑合、温度范围内电阻监测、拆检碎屑、必要时清洁重装及复测）；论文称返工后六台飞行载荷在载荷与飞行器测试中未再检测到CRC错误。
- **Scope qualification:** 该措施是后续项目级/批次级纠正流程；来源没有明确说明其中每一项均作为首个TVAC受影响载荷的单机处置执行。不得将项目级后续结果写成该episode已完成的单机修复记录。
- **Migration assessment:** 仅迁移接触可靠性与地面资格测试诊断方法。
- **Transfer constraints:** 不得迁移地面重工、润滑和清洁动作作为在轨处置。；CRC接触间断与SADA功率短路不是同一现象。
- **Materials absent from L0 source card:** upstream_ml_result, diagnostic_logs, spacecraft_context, operational_context, historical_cases, expert_adjudicated_target
- **Expert decision:** □ CONFIRM  □ REVISE  □ REJECT
- **Evidence/decision record:** ______________________________________________

### LIT-TROPICS-FLIGHT-CRC-003-A
- **Source:** Lessons Learned from the NASA TROPICS CubeSat Constellation Mission (MITLL-TROPICS-LESSONS-2025; NASA NTRS 20240011771, Section 6, p.4)
- **Event:** FLIGHT_EVENT / PUBLIC_FLIGHT_REPORT; family `TROPICS-SLIPRING-FLIGHT-2023`; episode `TROPICS-FLIGHT-PAYLOAD-A`
- **Phenomenon:** 2023年7月，TROPICS其中一台载荷出现CRC错误；通过反向旋转载荷获得成功缓解并继续工作。
- **Source cause statement:** 论文将CRC错误与前述滑环问题联系，但该飞行单元的具体失效机理未完全解决。
- **Source certainty:** `EXPLICIT_CANDIDATE`
- **Fault source:** TROPICS载荷滑环/旋转接触界面（候选）
- **Affected components:** 该载荷串行通信链路
- **Disposal:** `SOURCE_RECORDS_MEASURE`; 该台载荷通过反向旋转获得缓解并继续工作。
- **Migration assessment:** 仅限该台载荷的在轨运控经验。
- **Transfer constraints:** 与另一台载荷拆分为独立episode。；反向旋转不能作为SADA或其他卫星通用操作。
- **Materials absent from L0 source card:** upstream_ml_result, diagnostic_logs, spacecraft_context, operational_context, historical_cases, expert_adjudicated_target
- **Expert decision:** □ CONFIRM  □ REVISE  □ REJECT
- **Evidence/decision record:** ______________________________________________

### LIT-TROPICS-FLIGHT-CRC-003-B
- **Source:** Lessons Learned from the NASA TROPICS CubeSat Constellation Mission (MITLL-TROPICS-LESSONS-2025; NASA NTRS 20240011771, Section 6, p.4)
- **Event:** FLIGHT_EVENT / PUBLIC_FLIGHT_REPORT; family `TROPICS-SLIPRING-FLIGHT-2023`; episode `TROPICS-FLIGHT-PAYLOAD-B`
- **Phenomenon:** 2023年7月，另一台TROPICS载荷出现CRC错误；问题持续恶化，最终载荷不再工作。
- **Source cause statement:** 论文将CRC错误与前述滑环问题联系，但该飞行单元的具体失效机理未完全解决。
- **Source certainty:** `EXPLICIT_CANDIDATE`
- **Fault source:** TROPICS载荷滑环/旋转接触界面（候选）
- **Affected components:** 该载荷串行通信链路
- **Disposal:** `NOT_RECORDED`
- **Migration assessment:** 仅记录该台载荷的恶化与停止工作结果。
- **Transfer constraints:** 与另一台载荷共用事件族但独立保存结局。；无来源处置记录则保持NOT_RECORDED。
- **Materials absent from L0 source card:** upstream_ml_result, diagnostic_logs, spacecraft_context, operational_context, historical_cases, expert_adjudicated_target
- **Expert decision:** □ CONFIRM  □ REVISE  □ REJECT
- **Evidence/decision record:** ______________________________________________

### LIT-TROPICS-PATHFINDER-CROSSSHORT-004
- **Source:** Lessons Learned from the NASA TROPICS CubeSat Constellation Mission (MITLL-TROPICS-LESSONS-2025; NASA NTRS 20240011771, Section 6, p.4)
- **Event:** FLIGHT_EVENT / PUBLIC_FLIGHT_REPORT; family `TROPICS-PATHFINDER-SLIPRING-2023`; episode `TROPICS-PATHFINDER-SPACECRAFT`
- **Phenomenon:** Pathfinder在轨运行两年多后先出现少量CRC错误；数周后异常导致SADA驱动、星敏感器和载荷出现功能异常。
- **Source cause statement:** 作者认为滑环碎屑造成12V母线与串行线短接，比三个独立破坏性SEL事件同时发生更可能。
- **Source certainty:** `EXPLICIT_MOST_LIKELY`
- **Fault source:** 滑环碎屑可能引起12V母线与串行通信线之间跨网短接
- **Affected components:** 载荷LVDS接收器；总线FPGA I/O bank；载荷接口；星敏感器接口；SADA驱动接口
- **Disposal:** `NOT_RECORDED`
- **Migration assessment:** 条件迁移：用于跨分系统共因分析，不回填为用户SADA确诊根因。
- **Transfer constraints:** 须核对电路拓扑、极性及时间共因关系。；不能把所有受影响部件写成故障源。
- **Materials absent from L0 source card:** upstream_ml_result, diagnostic_logs, spacecraft_context, operational_context, historical_cases, expert_adjudicated_target
- **Expert decision:** □ CONFIRM  □ REVISE  □ REJECT
- **Evidence/decision record:** ______________________________________________

### LIT-LUNAR-ORBITER-HELIX-005
- **Source:** Lunar Orbiter III Mission System Performance (NASA-CR-66461; NASA CR-66461, PDF p.173 (printed p.165), High TWTA Helix Current at First Turn-On)
- **Event:** FLIGHT_EVENT / PUBLIC_FLIGHT_REPORT; family `LUNAR-ORBITER-III-TWTA-1967`; episode `LUNAR-ORBITER-III-TWTA-FIRST-TURNON`
- **Phenomenon:** Lunar Orbiter III首次启动TWTA时，螺旋线电流遥测指示为8.8 mA，约1.5分钟后下降至5.1 mA并保持；正常启动值约5.75 mA。
- **Source cause statement:** 报告保留发射机械应力经温度循环释放，或发射后内部压力缓慢衰减两种解释。
- **Source certainty:** `NOT_STATED`
- **Fault source:** 首次启动高螺旋线电流的成因未唯一确定
- **Affected components:** TWTA启动运行状态
- **Disposal:** `SOURCE_RECORDS_PLANNED_PROCEDURE`; 报告提出将制定发射后TWTA启动时间约束，以留出内部放气时间；未说明已经实施。
- **Migration assessment:** 不直接迁移为Ku-TWTA EPDF根因或已实施处置。
- **Transfer constraints:** 首次开机短时异常与运行数分钟后自动关机不同。；核对螺流定义及保护逻辑。
- **Materials absent from L0 source card:** upstream_ml_result, diagnostic_logs, spacecraft_context, operational_context, historical_cases, expert_adjudicated_target
- **Expert decision:** □ CONFIRM  □ REVISE  □ REJECT
- **Evidence/decision record:** ______________________________________________

### LIT-LUNAR-ORBITER-POWER-MONITOR-006
- **Source:** Lunar Orbiter III Mission System Performance (NASA-CR-66461; detailed telemetry discussion PDF pp.118–119 / printed pp.110–111; anomaly summary PDF p.173 / printed p.165)
- **Event:** FLIGHT_EVENT / PUBLIC_FLIGHT_REPORT; family `LUNAR-ORBITER-III-TWTA-1967`; episode `LUNAR-ORBITER-III-POWER-MONITOR-TELEMETRY`
- **Phenomenon:** CE02功率遥测随温度升高而上升，但深空站接收信号强度基本恒定，报告据此判断真实TWTA输出未显著变化。
- **Source cause statement:** 报告判断异常位于CE02遥测电路；监测二极管整流特性随温度偏移是其提出的可能机理。
- **Source certainty:** `EXPLICIT_MOST_LIKELY`
- **Fault source:** TWTA内部滤波/监测组件的CE02功率遥测测量链（可能涉及温度敏感的二极管整流特性）
- **Affected components:** CE02 TWTA输出功率遥测指示链
- **Disposal:** `NOT_RECORDED`
- **Migration assessment:** 作为测量链与真实功率链的鉴别反例。
- **Transfer constraints:** 先确认用户功率数据来自内部遥测还是独立RF测量。；需要独立功率计或地面复测。
- **Materials absent from L0 source card:** upstream_ml_result, diagnostic_logs, spacecraft_context, operational_context, historical_cases, expert_adjudicated_target
- **Expert decision:** □ CONFIRM  □ REVISE  □ REJECT
- **Evidence/decision record:** ______________________________________________

### LIT-CASSINI-RWA-DRAG-007
- **Source:** Cassini RWA Flight Anomaly Due to Extended Use at Slow Speed (2001) (NASA-LLIS-1416; NASA Lessons Learned 1416, Driving Event / Lessons Learned)
- **Event:** FLIGHT_EVENT / PUBLIC_FLIGHT_REPORT; family `CASSINI-RWA-LOW-SPEED-2001`; episode `LIT-CASSINI-RWA-DRAG-007-EPISODE`
- **Phenomenon:** Cassini发射约三年后，一只反作用轮检测到高于正常水平的拖曳/阻力；相关科学观测暂停约9天。
- **Source cause statement:** 过量摩擦被认为与长期近零转速运行导致润滑剂分布变化有关，速度在零附近频繁振荡也可能有贡献。
- **Source certainty:** `EXPLICIT_MOST_LIKELY`
- **Fault source:** 反作用轮轴承润滑状态退化/润滑剂分布变化
- **Affected components:** 反作用轮组件；姿态控制指向性能
- **Disposal:** `SOURCE_RECORDS_MEASURE`; 提高轮速后润滑剂分布似乎恢复并消除拖曳异常；团队制定避免长期低速运行程序。
- **Migration assessment:** 仅限润滑/拖曳机理条件迁移。
- **Transfer constraints:** 需比较轮型、润滑结构、速度区间和运行历史。；升速方案不可直接用于用户动量轮。
- **Materials absent from L0 source card:** upstream_ml_result, diagnostic_logs, spacecraft_context, operational_context, historical_cases, expert_adjudicated_target
- **Expert decision:** □ CONFIRM  □ REVISE  □ REJECT
- **Evidence/decision record:** ______________________________________________

### LIT-NASA-HYDRAZINE-INJECTOR-009
- **Source:** A Life Test of a 22-Newton (5-lbf) Hydrazine Rocket (NASA-TM-100232; NASA-TM-100232, pp.1, 5–6)
- **Event:** GROUND_TEST_EVENT / PUBLIC_GROUND_TEST_REPORT; family `NASA-22N-HYDRAZINE-LIFE-TEST-1987`; episode `NASA-22N-INJECTOR-PLUGGING`
- **Phenomenon:** 22 N肼推进器地面寿命试验运行约40小时后出现燃烧室压力振荡；60.2小时后试验因喷注管堵塞而终止。
- **Source cause statement:** 推进剂阀门Teflon阀座材料在试验加热过程后脱落并堵塞喷注管。
- **Source certainty:** `EXPLICIT_CONFIRMED`
- **Fault source:** 推进剂阀门Teflon阀座材料脱落并堵塞喷注管
- **Affected components:** 推进剂喷注管；推进剂供给通路
- **Disposal:** `NOT_APPLICABLE`
- **Migration assessment:** 不适合迁移为用户2#推力器直接根因；保留为特定地面试验堵塞反例。
- **Transfer constraints:** 不得将试验终止写成在轨恢复措施。；需比较阀门、喷注器结构及推进剂供给路径。
- **Materials absent from L0 source card:** upstream_ml_result, diagnostic_logs, spacecraft_context, operational_context, historical_cases, expert_adjudicated_target
- **Expert decision:** □ CONFIRM  □ REVISE  □ REJECT
- **Evidence/decision record:** ______________________________________________

### LIT-NASA-HYDRAZINE-CATALYST-010
- **Source:** A Life Test of a 22-Newton (5-lbf) Hydrazine Rocket (NASA-TM-100232; NASA-TM-100232, pp.4–6)
- **Event:** GROUND_TEST_EVENT / PUBLIC_GROUND_TEST_REPORT; family `NASA-22N-HYDRAZINE-LIFE-TEST-1987`; episode `NASA-22N-CATALYST-CONTAMINATION`
- **Phenomenon:** 推进器拆解后的催化剂化学分析发现铁、镍金属污染；报告将污染追溯到受污染肼推进剂批次。
- **Source cause statement:** 化学分析确认催化剂中铁、镍污染，报告追溯至误混入试验罐的受污染肼推进剂。
- **Source certainty:** `EXPLICIT_CONFIRMED`
- **Fault source:** 受污染肼推进剂中的金属杂质导致催化剂中毒
- **Affected components:** 肼推进器催化床
- **Disposal:** `NOT_APPLICABLE`
- **Migration assessment:** 仅作推进剂污染替代机制参考；用户案例没有推进剂污染证据。
- **Transfer constraints:** 不得把催化剂中毒和喷注堵塞合并为单一根因。；不能用于用户案例确诊。
- **Materials absent from L0 source card:** upstream_ml_result, diagnostic_logs, spacecraft_context, operational_context, historical_cases, expert_adjudicated_target
- **Expert decision:** □ CONFIRM  □ REVISE  □ REJECT
- **Evidence/decision record:** ______________________________________________

### LIT-SPACEBORNE-TWTA-HYDROGEN-011
- **Source:** 某星载S频段线性化行波管放大器输出功率下降问题研究 (JOURNAL-2026-TWTA-SBAND-POWER-DROP; Article abstract, journal page)
- **Event:** GROUND_TEST_EVENT / PUBLIC_GROUND_TEST_REPORT; family `SPACEBORNE-SBAND-TWTA-GROUND-TEST`; episode `SPACEBORNE-SBAND-LNA-HYDROGEN`
- **Phenomenon:** 某卫星整星转发器性能测试中，一台S频段行波管放大器输出功率下降约4 dB。
- **Source cause statement:** 地面排查将原因定位到线性化通道放大器两个微波模块内部的低噪声放大器芯片氢中毒。
- **Source certainty:** `EXPLICIT_CONFIRMED`
- **Fault source:** 线性化通道放大器两个微波模块中的低噪声放大器芯片
- **Affected components:** S频段TWTA输出功率链路；转发器性能
- **Disposal:** `SOURCE_RECORDS_MEASURE`; 更换为氢含量合格批次的同型号模块，地面试验验证后整机恢复正常。
- **Migration assessment:** 不适合迁移为用户电缆/隔离器故障根因；可借鉴RF链路故障树覆盖方法。
- **Transfer constraints:** 功率下降幅度接近不代表机理相同。；不得推定用户案例氢中毒或迁移地面换件方案。
- **Materials absent from L0 source card:** upstream_ml_result, diagnostic_logs, spacecraft_context, operational_context, historical_cases, expert_adjudicated_target
- **Expert decision:** □ CONFIRM  □ REVISE  □ REJECT
- **Evidence/decision record:** ______________________________________________

### LIT-FUSE-RWA-KAPTON-001
- **Source:** FUSE In-Orbit Attitude Control with Two Reaction Wheels and No Gyroscopes (FUSE-SPIE-2002-RWA; Section 3, Reaction Wheel Failures: Magnetic Torquer Bar Control)
- **Event:** FLIGHT_EVENT / PUBLIC_FLIGHT_REPORT; family `FUSE-RWA-2000-2001`; episode `FUSE-PITCH-RWA-2000-08-04`
- **Phenomenon:** 2000年8月4日，FUSE姿态控制飞行软件因俯仰轴反作用轮拖曳增大而将其关闭。重新启动后，异常拖曳持续数分钟，随后消失。
- **Source cause statement:** 供应商分析认为，轮组件内壳体衬层Kapton胶带中的小气泡可能导致局部凸起并接触转子；胶带逐渐磨损后，异常拖曳消失。该解释为供应商给出的可能原因。
- **Source certainty:** `EXPLICIT_MOST_LIKELY`
- **Fault source:** FUSE俯仰轴反作用轮组件内壳体Kapton胶带局部起泡并与转子接触
- **Affected components:** FUSE俯仰轴反作用轮组件；ADCS俯仰轴控制能力
- **Disposal:** `SOURCE_RECORDS_MEASURE`; 重新启动该反作用轮；异常拖曳持续数分钟后消失。
- **Migration assessment:** 可作为反作用轮拖曳异常的历史对照，但不能据此把Cassini低速润滑剂重新分布机理迁移到FUSE，也不能直接复制其他型号的轮速管理措施。
- **Transfer constraints:** 核实轮组件壳体衬层、转子间隙、材料和热环境后再讨论机理迁移。；FUSE 2000年俯仰轴事件与2001年其他轮组件失效必须保持不同episode。；供应商给出的Kapton起泡解释保留为最可能原因，不升级为独立确诊。
- **Materials absent from L0 source card:** upstream_ml_result, diagnostic_logs, spacecraft_context, operational_context, historical_cases, expert_adjudicated_target
- **Expert decision:** □ CONFIRM  □ REVISE  □ REJECT
- **Evidence/decision record:** ______________________________________________

## Knowledge-only source (not a fault episode)
### LIT-ISEE-HPS-EXPERT-SYSTEM-008
- **Source:** Satellite Operations Support Expert System Final Report (NASA-CR-180709)
- **Classification:** `KNOWLEDGE_SOURCE_NOT_EVENT`; this is a knowledge/feasibility demonstration, not a real flight incident.
- **Source statement:** 报告指出过滤器堵塞与催化床失效等不同故障可能产生相似症状。
- **Migration assessment:** 排除作为真实故障episode；保留为知识规则和症状重叠诊断来源。
- **Required treatment:** retain as a knowledge-source candidate only; do not count as an event, real fault case or event SFT example.
- **Expert decision:** □ CONFIRM KNOWLEDGE-ONLY  □ REVISE  □ REJECT

## Collection decision

- Current state: **13/13 pending domain-expert confirmation**.
- L1 pilot references: **12 unique event source cards**; ISEE/IUE expert-system card is not used as an event source.
- L1 experiment approval remains blocked until every source card referenced by that L1 packet is domain-expert-confirmed with a review-evidence digest.
- A changed L0 fact card or review status changes its fingerprint and invalidates any earlier L1 review receipt.

Overall decision: □ CONFIRM SOURCE SET  □ REVISE SELECTED CARDS  □ REJECT

Authorized review record reference: ______________________________
