# P5-C3 | REV1 二项实质科学标签修订的专家可执行裁决方案（2026-11-19）

**状态：INTERNAL_REVIEW_ONLY；not_for_sft=true；非专家裁决，非训练材料。** 这是在冻结 REV1 上制作的**供审查的候选差异**，没有自动修改任何 Case、L0、L1、导出投影或审核表。

## 核验基线

- 来源 PR #169 head `261588371259ab2f7d61803bbb7aadcc6436f0f0`，同一 head 的 `ADCS and EPS seed quality gates` 运行 #44403782858 中 `validate (ubuntu-latest)` 与 `validate (windows-latest)` 均已完成 SUCCESS。
- 不可变集合：`examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18_r1.json`，21 个 **LITERATURE_DERIVED_SYNTHETIC** 候选，9 个事件族；collection projection SHA-256 为 `3927c976af6eb46a8842b68926fd893b021df69b034ae8981dc5ed136278521a`。
- 本次核对了候选任务 009、016、017 的**当前正式标签字段**、合成日志文本、ML 候选的证据来源及已交付的 A/B 空白审核包所绑定的 packet SHA-256；引用清单见 `docs/review_only/P5C3_REV1_SCIENTIFIC_REV2_PROPOSAL_OPTIONS_20261119.json`。
- 上述全部当前 ML 输出、评分、日志、时间戳、审核摘要均为场景设定；**没有真实 ML 执行结果、真实运控日志或专家批准**。原始遥测不属于 LLM 默认输入。

## SCI-009 | 先行操作与本事件处置必须分开

- 任务 `L1-NASA-HYDRAZINE-INJECTOR-SYNTH-009`；packet SHA-256 `11f8aefda38a3f34501c59d8419b8d5e02bf9a669690d17e45019abff73df77f`。
- `LOG-91`：对**此前催化床污染疑虑**所实施的合成真空热灯烘烤；`LOG-92`：随后阀门爆裂；`LOG-93`：随后喷注器流量接近中断。
- 当前 `formal_target.disposal_status=RECORDED` 且 `disposal_measures[0]` 将 `LOG-91` 标为 `EXECUTED`，容易让模型学习“当前阀门/喷注器故障发生后实施的处置”这一反向时序。**存在 LOG-91 不是本事件处置的合理风险，不等于直接宣告日志或历史来源错误。**
- **专家选择 A（候选修正）**：当正式诊断事件范围是 LOG-92/93 的后续阀/喷注器故障时，建议 REV2 将本事件 `disposal_status` 改为 `NOT_RECORDED`、`disposal_measures=[]`；同时只在现象分析/事件时序以及报告说明中保留 LOG-91 为此前事件的操作或可能诱发背景。不能删日志、不能编造新的故障处置，也不能把后续建议改为历史已执行操作。
- **专家选择 B**：如审核认定须保存跨 episode 的操作角色，应先明确跨事件动作的类型与范围，不直接沿用当前故障的处置槽位。**选择 C**：需要补充资料，保持任务 `REVIEW_REQUIRED`。
- 与另一个科学问题的区分：LOG-91 在当前候选根因支持链里的**先行操作角色**仍可单独评价；在 `cause_localization` 中保留或移出该引用，应根据因果证据角色独立裁决，而非仅因处置槽位调整就机械删除。

## SCI-016 | 监测证据不得伪装成 RF 物理通路的正证据

- 任务 `L1-LUNAR-ORBITER-POWER-CONFLICT-SYNTH-016`；packet SHA-256 `6e30feb4190b10d4db49548e7c5ecd69d41dd4caeec9308e4bbee5298bbb760d`。
- 合成 `ML-E-016-MONITOR` 与 `LOG-161` 来自**同一个监测源血缘**；仅支持星上功率监测指示变化，不能当成真实发射载波下降的**独立阳性证据**。合成 `LOG-162`、`LOG-163` 则提供特定载波、时间窗及声明可比性下的独立反证。
- 当前 `formal_target.cause_localization.candidates[1].fault_mode=transmitted_carrier_power_decrease_unverified`，其 `supporting_refs=[\"ML-E-016-MONITOR\"]`。正式中文解释已指出这是未经核实的上游推断，但下游结构化训练读取可能将 `supporting_refs` 误作物理原因的正向支持。
- **专家选择 A（候选修正）**：仅针对该**未验证 RF 下降候选**，在 REV2 将 `supporting_refs` 改为 `[]`；保留上游 ML 结果原貌、监测链候选的支持引用、独立反证和不确定性。此字段在其他任务中允许空引用（例如 007 的未证实替代机理）；但仍必须运行 REV2 全量语义与导出测试。
- **专家选择 B**：如果项目规范明确 `supporting_refs` 是“主张来源”而非“正向证据”，则引入有类型的 `claim_provenance_ref`，并与 `positive_evidence_refs` 分开验证；**选择 C**：补证前保持 `REVIEW_REQUIRED`。不得因清空正证据引用就删除相反观测或将监测链故障升级为确诊。

## SCI-017 | 仅复核，无自动修改建议

- 任务 `L1-TROPICS-QUALIFICATION-CONFLICT-SYNTH-017`，packet SHA-256 `1e14342290e190d659a130cc78543ec80cf46ee3b0a7f97d438e3a2e88645cfe`。
- 当前目标已保留合成 18% RH 条件 FAIL、82% RH 条件 PASS，未以一次 PASS 关闭全部资格问题，也未把在空气中的两项地面试验写成 TVAC。请独立审核现有适用范围、测量链差异和原因不确定性；目前没有从当前字段分析得出必须修订的证据。

## 独立审核与版本执行规则

1. 专家 A 和 B **各自独立**核对原始 REV1 task 与文献原始可用范围，选择 A/B/C，报告原因和引用。文档里的推荐路径**不代表专家认可**，两位专家身份/受限意见不进入公开仓库。
2. 仅在裁决完成且来源使用许可满足后，根据批准的精确字段修改创建独立 **REV2**（不是覆盖 REV1），重算每个受影响 packet 的 SHA-256 与 collection projection SHA-256，重新生成版本绑定的 A/B 审核表；不能把原 REV1 回执沿用到 REV2。
3. 检查 JSON 结构、Case→SFT 投影不泄漏 `internal_review`、事件族分组隔离、history as-of 规则、处置来源约束，以及真实/合成分轨统计。独立审核不等于真实 Gold，也不等于训练授权。
4. 如任何任务继续存在解释分歧，则它保持 `REVIEW_REQUIRED`，不以模型打分、GitHub CI 绿灯或开发者意见替代科学签核。

## 开发经验

本轮新增价值不是新 validator，而是提供**精确定位、版本绑定、可选择、可复核**的两项标签修订路线。完整事实和诊断主张可以各自正确，但错配的**处置事件归属**或**证据关系类型**仍会破坏 SFT 的监督信号。正式目标应优先接受人工科学裁决，不能以工程自动化强行“修好”未确认的标签。
