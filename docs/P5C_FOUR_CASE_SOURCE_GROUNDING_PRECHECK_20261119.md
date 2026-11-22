# P5-C｜四案例 SOTA 开发配对的原始来源—当前证据科学核查（2026-11-19）

**状态：AI 辅助、只读科学预核查；NOT_FOR_SFT / NOT_EXPERT_ADMISSION / NOT_RIGHTS_CLEARANCE。** 本文件是研究核查记录，不是 Case、用户输入、assistant target、专家评分或新的准入规范。不得由生成器、检索器、训练导出器读入本文件。未获得两位独立领域专家回执，不对任务作正式 ACCEPT / REJECT。未授权任何模型生成、训练或数据发布。

## 核查范围和版本边界

- 代码基线：PR #167 head 3e7788b89cd37e78c16cf27697c67ce9455cd0d2；本审查分支仅增加文档，不重写 L0/L1。
- 当前 21 项合成候选：examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18_r1.json（collection DGSI-L1-LITERATURE-SYNTHETIC-PILOT-C2-COVERAGE-CANDIDATE-REV1-2026-11-18）。
- 历史 L0：examples/l0_public_literature_fact_cards_c2_content_corrected_2026-11-18.json。四个任务的 task_id 分别为 001、012、016、019，对应已有四案例 DEV_ONLY 配对计划，非独立测试集，不能与 9 个事件族中同源任务拆分 train/validation/test。
- 核查工作：逐项阅读 L0 的 source_locator、当前 L1 的合成输入/正式 target/历史 Context，另对照三份直接来源（SEASAT NTRS 摘要、FUSE 2002 论文第 3 节、Lunar Orbiter III NASA 报告印刷 p.112）及 2026 S-band TWTA 期刊公开摘要。**核查到的原文范围之外不宣称已核实**。文献版本与可重用权利仍待独立确认。

## 四例事实边界与对照重点

| 配对案例 | 原始来源核查范围与可保留的历史事实 | 当前合成输入可支持的判断 | 禁止升级的判断 / 当前缺口 |
| --- | --- | --- | --- |
| 001 SEASAT 滑环 | NASA NTRS 20040171604 的报告摘要明确：Agena bus 失电与滑环渐进短路有关，相邻电刷起弧为 most likely；导线/电刷接触、刷间接触和污染物跨接均为可选触发方式。**只核验摘要，非完整报告逐页审读。** | 合成 ML 将滑环短路列为候选，LOG-01/02 提供合成母线/驱动异常；排序值不等于校准概率。 | 不得将“历史 most likely 起弧”升级为当前合成样本的确诊、不得选定碎屑为唯一触发物；L0 不提供合成现场的短路实测或拆检。 |
| 012 FUSE ↔ Cassini 历史迁移 | 2002 SPIE 论文 Section 3 / PDF 第 5 页：2000-08-04 俯仰轴轮异常拖曳与供应商提出的 Kapton 起泡/局部接触可能有关，重启后过量拖曳数分钟消退；2001-02-16 偏航轮的消退时长不同；2001 年末不可重启的完全失效属于独立事件。 | 当前 LOG-121/122 仅合成说明拖曳升高、重启后回落。Cassini historical item 为 PARTIALLY_CONFIRMED，硬件兼容性 UNKNOWN，diagnostic_vote_allowed=false。 | 回落不等于回到健康基线，不等于 Kapton 确诊或任务能力恢复；Cassini 的润滑/轮速管理经验不等于 FUSE 的机理或可执行指令。不得把 2001 年末轮失效的热变形解释倒写为 2000-08-04 起因。 |
| 016 Lunar Orbiter III 监测指示与独立接收冲突 | NASA CR-66461 PDF 第 120 页（印刷 p.112）记载历史 CE02 指示功率异常变化，但 DSS 接收信号大体稳定，据此将历史差异归入遥测电路，不能证明所有 TWTA/RF 分量健康。**本轮核对这一印刷页，不宣称全文复审。** | 合成 LOG-161 同窗监测指示约降 3 dB，LOG-162 经声明的独立地面链路处理显示同一载波不超过 0.2 dB 变化，LOG-163 说明已检查的可比性条件。可质疑合成 ML 将监测指示泛化为“同幅度发射载波下降”的判断；可优先检查监测通道。 | 不得把历史 DSS 结果算进当前证据，不得以稳定载波推出总 RF/谐波正常，不得确定某二极管温漂。当前 cause_localization 内 RF 输出候选的 supporting_refs 仍含 ML-E-016-MONITOR；此 ID 代表**监测指示来源**而非独立发射功率证据。虽然 limitations 已说明，仅凭 supporting_refs 字段可能产生正向支撑误读，应列为专家判定的引用语义问题，而非凭本次核查擅自修改已冻结任务及哈希。 |
| 019 S-band TWTA 地面试验证据充分性 | 2026《空间电子技术》对应 DOI 期刊摘要公开陈述：历史整机输出约降 4 dB，经故障树和多种地面排查，历史原因归于 LCAMP 两个微波模块内 LNA 氢中毒，换件及试验验证后历史设备恢复。**本轮仅独立核对公开摘要；Z2/Z6 的细节、测值、气体与 EMMI 原始页码仍须精确文献核对。** | 合成 LOG-019-01/02 为两次同口径整机测量，LOG-019-03 明示缺失分层隔离、模块增益/电流、气体/芯片分析。可以报告整机功率下降，当前具体根因应维持 UNRESOLVED。 | 不得因“同样约 4 dB”直接确认 LCAMP 或 LNA 氢中毒，不得照搬历史 TWT/EPC 排除结论或历史换件成功作为合成场景已执行措施。应维持 disposal_status=NOT_RECORDED、disposal_measures=[]，补证建议仅进入 follow_up_actions。 |

## 这次核查产生的科学工作结论

1. **历史事实与合成当前事实之间的证据边界是四例最有鉴别力的考核点。** 已核对的来源事实支持当前任务结构中的谨慎解释，未出现足以证明应将任何候选自动提升为确诊的证据。
2. **一个具体待裁决的标注语义问题**：016 的“真实 RF 载波下降”候选使用 ML-E-016-MONITOR 作为 supporting_refs，可能把监测链证据在结构层误读为发射功率阳性证据。它在正式文本中已被明确削弱。本轮仅记录此冲突供独立专家审视：若调整结构，应另建版本、重算 task/collection 指纹并重新生成专家回执包，不能静默修改 REV1。
3. **四例不等于四个 Gold，不等于四个真实 ML run，也不是四组独立 holdout。** 四任务共 4 个配对单元，均来自 21 项待审 SYNTHETIC 候选。FUSE–Cassini 必须按历史依赖连通处理；同源多任务不拆分。
4. 五方法（Self-Instruct、Evol-Instruct、Magpie-style、Auto-Instruct-style、DGSI）目前只有 20 个计划单元：生成 0、独立人评 0、真实 Gold 0、正式 split 0、training_authorized=false。计划中的 2048 token/单元是预算上限，不是实际消耗或科学有效性结果。

## 核验来源（原始资料，不代表许可）

- SEASAT，NASA NTRS 报告摘要：https://ntrs.nasa.gov/citations/20040171604
- FUSE，Kruk et al., 2002, SPIE 4854-72，Section 3（PDF 第 5 页）：https://archive.stsci.edu/fuse/papers/spie4854/spie_4854-72.pdf
- Lunar Orbiter III Mission System Performance，NASA CR-66461，通讯分系统 CE02，PDF 第 120 页 / 印刷第 112 页：https://ntrs.nasa.gov/api/citations/19670027946/downloads/19670027946.pdf
- “某星载S频段线性化行波管放大器输出功率下降问题研究”，期刊公开中英文摘要：https://kjdzjs.spacejournal.cn/article/doi/10.3969/j.issn.1674-7135.2026.02.007

这些页面可以读到相关事实，不等于允许本项目训练、复制正文或公开再分发。七份来源组的权利清理保持 0；两位独立专家尚未出具绑定 REV1 的完整、经身份核验的回执。当前不改变审核结果、来源许可状态或 SFT 发布门禁。

## 开发经验

- 本轮不新增又一层 validator；科学增量是拿源文与**当前** 21 任务真实字段逐项对照，区分文献事实、合成观测、模型候选、物理根因、已记录处置及后续建议。
- 源文最易引起的错误不是术语拼写，而是将历史报告中最可能/部分确认的机理升级为当前场景确定根因，以及把监测通道的变化作为真实 RF 输出变化的独立支撑。
- 科研级审计必须记录**核验范围**：摘要核查不能冒充全文核查，截图核查不能冒充专家许可审查；没有完成的实验继续填 NOT_RUN 而不是用测试通过数替代。
