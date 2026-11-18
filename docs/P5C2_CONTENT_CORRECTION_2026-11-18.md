# P5-C2 现有十五项候选的来源与正式目标修订

本轮继续推进航天器故障诊断数据主线：对现有十五项文献衍生任务逐一检查原始来源、模型实际可见输入和正式目标，修正会影响学习目标的内容差异。新版本仍覆盖九个来源事件族，引用十二张 L0 卡、七个主来源登记项。所有任务继续等待独立领域审核，未生成 SFT 训练行。

## 本轮完整交付

- L1：`examples/l1_literature_synthetic_task_packets_c2_content_corrected_2026-11-18.json`。
- L0：`examples/l0_public_literature_fact_cards_c2_content_corrected_2026-11-18.json`。保留十三张原卡，其中十二张与当前 cohort 绑定，ISEE 知识卡未改动。
- 逐任务处置、字段差异及来源台账：`examples/p5c2_content_correction_review_2026-11-18.json`。
- 实际覆盖：`examples/p5c2_content_corrected_coverage_2026-11-18.json`。
- 整组校验、阻断式投影和空白回填结果：`examples/p5c2_content_corrected_preflight_2026-11-18.json`。

新 cohort 为 `DGSI-L1-LITERATURE-SYNTHETIC-PILOT-C2-CONTENT-CORRECTED-2026-11-18`，投影绑定摘要为 `cb5de1f25d7083c2206d926e5b98a596a9c2a38acd88e12abab08fb5f116a95c`。旧 L0、2026-11-17 L1、旧覆盖报告和已发审核包保持原字节，便于逐项追溯。

## 主要内容判断

**正式目标必须由模型实际看到的材料支持。** 原审核附件含有完整 L0 卡，但模型投影只包含 `case.input` 中的知识片段。Lunar 功率监测、TROPICS 两台在轨载荷、FUSE 后续事件和部分推进/TWTA 目标引用了短片段中没有的历史细节。本版补入必要的压缩历史背景，并继续限制其为 CONTEXT；004 中没有输入依据的 SEASAT 比较被删除。

**已执行尝试与已经恢复是两项判断。** 004 的线束调整、006 的通信重试、009 的热灯烘烤、012 的重启都有当前合成日志。本版把四项列为 `RECORDED`，动作标为 `EXECUTED`，分别引用 LOG-42、LOG-62、LOG-91、LOG-122。日志未证明这些动作完成根因修复或持久恢复，因此没有增加成功处置结论。NASA 两张 L0 卡也补回来源记载的失败恢复尝试，同时与当前合成动作分开。

**现象、上游候选、机理和受影响对象分别评价。** Cassini 的 ML 标签仅给出拖曳增大，不能转述为 ML 已定位润滑退化；FUSE 的局部接触候选不能直接具体化为 Kapton 起泡；高螺流现象也不足以定位供电模块损坏。Pathfinder 的当前受影响接口与历史假设中的 FPGA 损伤分开，飞轮拖曳与尚未证明的姿态性能下降分开。

**合成来源标记不抹去题目已经给出的证据。** 011 已提供模块增益、电流、封装气氛及 EMMI 结果。本版将其视为场景内的支持证据，待补项改为检测质量、样品对应、正常对照和干预效果的核验摘要；不再默认重复全部检测。其场景内不确定性调整为 `MODERATE`，物理机理仍为候选，实际航天器确诊、专家认可及训练授权均未据此增加。默认不向 LLM 索取原始遥测；需要上游对原始材料作校核时，请求其结果摘要和记录索引。

**任务覆盖按实际问题计算。** 003 没有相互冲突的当前诊断结果，已由 `conflict_reconciliation` 改为 `diagnostic_synthesis`。013、014、015 的指令分别明确要求证据充分性判断、下一步检查、交接摘要。它们保留同源任务关系，不增加独立事件计数。

## 十五项任务的具体结果

下表编号对应 task_id 末尾的编号。完整字段路径和更改依据保存在逐任务台账。

| 编号 | 案例与任务 | 本轮结果 |
|---|---|---|
| 001 | SEASAT 诊断综合 | 来源指向实际核查的 NTRS 摘要；保留起弧候选及多种触发解释，明确当前未记录处置。 |
| 002 | Lunar 功率监测 | 补入历史地面接收信号的判别依据；真实 RF 变化与监测链变化均保留未决分支；缺失测量日志不作为阳性证据。 |
| 003 | Pathfinder 综合诊断 | 修正任务分类；当前接口异常与可能的 FPGA 损伤分开；被否决历史假设既不能确诊也不能排除当前原因。 |
| 004 | TROPICS TVAC | 记录已执行但未消除 CRC 的线束调整；去除未提供的跨案例比较。 |
| 005 | TROPICS 飞行单元 A | 补足该历史单元的缓解背景；A 是资料中的区分标签，不是论文给出的飞行器编号。 |
| 006 | TROPICS 飞行单元 B | 历史停机与当前通信不稳分开；记录未恢复稳定链路的重试，不继承另一单元的恢复结果。 |
| 007 | Lunar 首次启动 | 保留两个内部机理假设，故障源未定位；合成第二条日志改为 08:11:30，与已有约 1.5 分钟叙述一致。 |
| 008 | Cassini 拖曳诊断 | 忠实转述拖曳增大标签；润滑解释留作待核实机理，未观察的姿态影响不列为既成事实。 |
| 009 | 肼推进器喷注器 | 区分历史前期 washout 与后期堵塞；记录当前烘烤尝试，不将先后次序直接认定为已经证实的因果。 |
| 010 | 肼推进器催化剂 | 补足独立历史 episode 背景，保留污染归因与取样/批次核验缺口。 |
| 011 | S 频段 TWTA 机理 | 更正期刊来源归属；利用已给出的多项场景检测，准确列出尚未闭合的证据和效果验证。 |
| 012 | FUSE 历史复用 | 区分早期 Kapton 假设和后期热变形归因；记录当前合成重启，拖曳回落不等于恢复健康基线。 |
| 013 | Pathfinder 证据充分性 | 分别判断现象、受影响接口与物理根因的证据是否充分，列出优先补证事项。 |
| 014 | Cassini 下一步检查 | 检查顺序对应实际证据缺口，并说明检查结果如何改变假设优先级；无直接轮速操作命令。 |
| 015 | S 频段 TWTA 交接 | 明确 TWT 与整机 TWTA 层级；交接摘要与结构化字段一致，保留未知责任人、时限和执行结果。 |

## 一手来源及核查范围

本轮核查相关原文段落，不宣称完成每份报告的逐页全文审核。以下七项是 cohort 使用的主 `source_id` 登记组；Cassini 另列三项日期互证资料，不能用主来源计数代替对全部实际使用材料的范围审查。

| 主来源 | 本轮定位 | 核查范围与限制 |
|---|---|---|
| [SEASAT 失效调查](https://ntrs.nasa.gov/citations/20040171604) | NTRS abstract / summary | 仅原始摘要；旧 PDF 链接不可用，备用全文超出当前提取大小限制。 |
| [TROPICS 经验论文](https://ntrs.nasa.gov/api/citations/20240011771/downloads/IEEEAero_TROPICS_2025_for_approval.pdf) | §6，PDF/印刷第 4–5 页 | 修正把零起始页面索引误当页码的定位；分开试验、两个载荷单元与 Pathfinder。 |
| [Lunar Orbiter III 报告](https://ntrs.nasa.gov/api/citations/19670027946/downloads/19670027946.pdf) | PDF 第 119–120、173 页；印刷第 111–112、165 页 | 区分遥测电路判断与所提出的二极管机理；首次启动两种解释保持候选。 |
| [Cassini LLIS 1416](https://llis.nasa.gov/lesson/1416) | Driving Event / Lessons Learned / Recommendations | 使用索引提供的原始正文；事件年份、Lesson Date 和历史运行条件分别处理。 |
| [NASA TM 100232](https://ntrs.nasa.gov/api/citations/19880002368/downloads/19880002368.pdf) | PDF 第 4–7、11 页；印刷第 3–6、10 页 | 区分苯胺污染猜测、金属污染分析、后期堵塞和失败处置。 |
| [S 频段 TWTA 期刊终稿](https://kjdzjs.spacejournal.cn/cn/article/pdf/preview/f2124d75-67bc-4508-b88e-79845ac6f8ce.pdf) | 2026，23(2)：46–53；PDF 第 2–7 页 | 终稿相关段落已可访问和核对；旧预发表卷期页码被更新，数值保留。 |
| [FUSE 飞轮论文](https://archive.stsci.edu/fuse/papers/spie4854/spie_4854-72.pdf) | §3，PDF 第 5 页 | 原 p.3 定位修正；不同年份和轮轴的恢复/完全失效事件分开。 |

Cassini 同期任务报告分别记录 [2000-12-20 周报中的模式切换](https://science.nasa.gov/missions/cassini/significant-event-report-for-week-ending-12202000/) 和 [2001-01-05 周报中的 RWA 控制恢复及后来重启科学序列](https://science.nasa.gov/missions/cassini/significant-event-report-for-week-ending-152001/)；[JPL DESCANSO §2.5.2](https://descanso.jpl.nasa.gov/DPSummary/DESCANSO17_Cassini_RevA.pdf) 的逐日摘要使用另一组日期。本版保留来源口径，不把整个模式恢复区间写成持续异常摩擦，不推定尚未核清的时区转换。DESCANSO 仅完成原始索引摘录核查，完整 PDF 提取受大小限制。

## 覆盖和准入状态

| 任务类型 | 数量 | 状态 |
|---|---:|---|
| 诊断综合 | 11 | 覆盖八个来源事件族，仍明显不均衡 |
| 历史案例复用 | 1 | 同源覆盖有限 |
| 证据充分性 | 1 | 同源覆盖有限 |
| 下一步建议 | 1 | 同源覆盖有限 |
| 交接摘要 | 1 | 同源覆盖有限 |
| 当前冲突协调 | 0 | 明确缺口 |

专门的正确拒答/保留判断任务仍为零；002、007 的未决结论不能直接计成新增专门任务。原事件类别统计的“飞行 8、地面 4”按绑定 L0 卡计数，本版明确该分母，避免误读为十五条 L1 的分布。四条记录处置尝试的任务按 packet 计数。

所有 L0 仍为 `AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION`，所有 L1 仍为 `REVIEW_REQUIRED`。独立专家裁决、权利清理、正式划分、Gold、授权训练行和训练运行均为零。期刊全文相关段落已核对这一进展，不替代科学准入或使用权确认。

## 使用与版本衔接

运行环境的唯一内容适配，是在既有投影允许列表中登记三条专用任务指令。RC3 会拒绝这些新文本，因此运行包升为 `0.2.0-rc.4`；CLI、schema、评分规则和外部准入条件保持既有流程。候选数据作为外部输入交付，不混入通用工具包。

```bash
python scripts/create_l1_c2_complete_review_kit.py \
  --collection examples/l1_literature_synthetic_task_packets_c2_content_corrected_2026-11-18.json \
  --source-facts examples/l0_public_literature_fact_cards_c2_content_corrected_2026-11-18.json \
  --output-file /authorized/output/C2-content-corrected-review-only.zip
```

新 A/B 表与新 cohort、packet、source 摘要绑定。已发旧表仍属于旧快照，不能复制其中的绑定字段来冒充新表。实际回填时，使用同批新 L0/L1 调用既有 current-expert-intake；旧表对新来源应被拒绝。空白新表应得到十五项待补全、三十份未完成 scorecard、零个完整评分对。没有向外部审核者发送材料。

本轮开发经验续记在 `docs/DEVELOPMENT_EXPERIENCE_TOPOLOGY_REVIEW.md` 第 115–120 条。下一步主线是围绕新材料取得独立领域意见，并按真实证据修订；新样本只在来源和证据结构足以支撑明确覆盖缺口时加入。
