# DGSI 2×2 新留出来源筛查总表 — 2026-11-20

**用途：** 为 PR #191 的预注册 2×2 对比实验筛选未暴露、权利清晰且适合 DGSI 诊断任务的独立来源簇。  
**性质：** 来源筛查记录，`not_for_sft=true`。不是 L0/L1 案例，不是正式留出清单，也不授权模型生成、评审或训练。  
**冻结原则：** 不改变既有评测集、案例、rubric、评分阈值或历史成绩；不因候选不足而降低来源权利、独立性或任务适配要求。

| 候选 | 来源 | 版权状态 | 历史暴露 | 准入决定 |
|---|---|---|---|---|
| **IMAGE：2005 通信丢失 / 转发器 SSPC** | [IMAGE Failure Review Board Final Report](https://spdf.gsfc.nasa.gov/pub/data/image/documents/website/image.gsfc.nasa.gov/publication/document/IMAGE_FRB_Final_Report.pdf) | NASA 报告；报告内第三方材料仍需逐项核验 | **已确认泄漏**：该报告及“likely SEU-induced instant trip of transponder SSPC”机制已进入 EPS seed-curation skill、source registry、source passages、pressure-test cases、domain review checklist 和探索性模型预试验 | **排除**。保留原文“likely”，不把 SEU 提升为确定根因；明确标记为已暴露，不得进入确认性留出 |
| ISS Beta Gimbal Assembly 电机电流升高 | [NASA/TM-2003-212012, NTRS 20030014592](https://ntrs.nasa.gov/citations/20030014592) | NTRS 标注 Public / Work of US Gov. Public Use Permitted；PDF 中第三方图表待检查 | GitHub 默认分支精确检索未命中；历史对话、PR、资料包及检索索引独立性尚未证实 | **条件候选，不准入**；须完成全文页码核查、第三方材料核验及完整暴露审计 |
| MethaneSAT 2025-06-20 通信丢失 | [MBIE Appendix 9 anomaly investigation](https://www.mbie.govt.nz/dmsdocument/31529-appendix-9-methanesat-anomaly-investigation-report)；[MBIE–MethaneSAT MOU](https://www.mbie.govt.nz/dmsdocument/31526-appendix-1-memorandum-of-understanding-methanesat) | 政府网站可访问不等于企业报告可自由衍生；MOU 的 IP / 分发条款未提供本数据集所需的明确许可 | 尚未完成跨 PR、历史资料包、对话及检索索引的完整暴露审计 | **版权与暴露双重 HOLD**；根因仍须保留 flight avionics / EPS 未决，不得自行选定 |
| IUS 1983 固体火箭发动机喷管故障 | [NASA-TM-86513, NTRS 19860000811](https://ntrs.nasa.gov/citations/19860000811) | NTRS 标注 Public / Work of US Gov. Public Use Permitted | 本轮筛查已向协调上下文暴露；仓库及历史材料仍需检查 | **不准入**；上面级推进事件与当前卫星总线/分系统任务范围不一致，须先正式界定范围 |
| Seasat 故障 | [Seasat Failure Review Board Report](https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19930015504.pdf) | NASA 公共使用标记 | 已在现有 P5-C17 来源中出现 | **排除**；已有来源暴露，不得作为新独立簇 |
| ISS SARJ 轴承 / 旋转关节故障 | [NASA/TP-2011-217116, NTRS 20110015384](https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20110015384.pdf) | NTRS 公共使用标记；需核查报告中 Boeing 等第三方材料 | 本轮已向协调上下文暴露；与 ISS BGA 同平台，完整独立性未证实 | **不准入**；仅为开发候选，不能将同平台/关联事件自动计作独立簇 |
| Lucy 太阳翼部分展开 | [NASA NTRS 20250002257](https://ntrs.nasa.gov/citations/20250002257) | NASA 会议演示材料；IEEE 会议内容及嵌入图像的衍生使用权未确认 | 本轮已向协调上下文暴露；历史仓库与 PR 暴露待查 | **版权 HOLD / 不准入**；无部署状态传感器，需严格区分观测与模型推断 |
| Galileo 航天器异常与 safing 恢复 | [NASA NTRS 19940019391](https://ntrs.nasa.gov/search.jsp?R=19940019391) | NTRS 标注 Public / Work of US Gov. Public Use Permitted | 本轮已向协调上下文暴露；历史资料暴露待查 | **不准入**；摘要未给出足够明确的单一故障根因和有界事件输入 |
| NASA RP-1390 空间环境异常综述 | [NTRS 19960050463](https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19960050463.pdf) | NASA 公共使用标记；含 USRA / CSC 等贡献，逐事件权利需查 | 本轮已向协调上下文暴露 | **仅作来源索引**；综述本身不等于多个独立原始事件簇 |
| SAMPEX 反作用飞轮故障 | [NASA NTRS 20080039634](https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20080039634.pdf) | NASA 公共使用标记 | PR #184 已明确列为既有来源线索 | **排除**；已有开发暴露，不得重命名为新留出 |
| Apollo 13 氧气罐故障 | [NASA NTRS 19710010479](https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19710010479.pdf) | NASA 公共使用标记 | 本轮已向协调上下文暴露 | **当前范围排除**；载人指令舱/服务舱事故，不属于当前卫星分系统 SFT 样本范围 |
| UARS 在轨动力学 / 太阳翼驱动振动 | [NASA-TM-110325, NTRS 19970019258](https://ntrs.nasa.gov/citations/19970019258) | NTRS 标注 Public / Work of US Gov. Public Use Permitted | 本轮已向协调上下文暴露 | **不准入**；属于动力学表征，缺少边界清楚的故障事件及确证根因 |
| BurstCube 反作用轮 / 太阳翼 / 星敏异常 | [NASA-associated SSC25-III-02 proceedings](https://ntrs.nasa.gov/api/citations/20250007104/downloads/Tian%20-%20SSC25%20Paper.pdf) | 会议论文，作者及嵌入内容的衍生使用许可未确认 | 本轮已向协调上下文暴露 | **不准入**；多个异常交织、根因边界不清，不能拆成多个独立样本 |
| Lunar Trailblazer 失联 | [Earth and Space Science, DOI 10.1029/2025EA004734](https://doi.org/10.1029/2025EA004734) | 出版页面虽开放访问，但 AI training / text-data mining 权利保留，未验证许可 | 本轮已向协调上下文暴露 | **版权 HOLD / 不准入**；不能以可下载替代衍生训练授权 |
| Anik-E2 1991 天线展开 / 1994 姿态控制异常 | [1993 recovery paper](https://www.sciencedirect.com/science/article/abs/pii/009457659390162P)；[1994 space-weather analysis](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2012SW000811) | 出版商版权控制；本轮未确认衍生数据集许可 | 本轮已向协调上下文暴露 | **不准入**；1991 与 1994 是不同事件；1994 Anik-E1/E2 属同一空间天气事件簇，不能拆成两个独立样本 |
| Nimbus I 太阳翼驱动电机停转 | [GE report scan, NASA NTRS 19680019353](https://ntrs.nasa.gov/api/citations/19680019353/downloads/19680019353.pdf) | 原件醒目标注 “FOR USE OF G.E. EMPLOYEES ONLY”；未获权利人衍生使用许可 | 本轮已向协调上下文暴露 | **版权排除**；技术证据丰富不能覆盖来源限制，不得制作 L0 / L1 |
| GOES-13 Sounder / Imager 关联异常 | [NOAA/NESDIS 2012-10-17 presentation](https://satepsanone.nesdis.noaa.gov/pub/Presentations/Joint_NWS-NESDIS_Quarterly/20121017/20121017%20NWS%20Quarterly%20Presentation.pdf) | 政府演示文稿可访问；底层调查报告及衍生许可未核实 | 本轮已向协调上下文暴露 | **开发线索，不准入**；Sounder 与 Imager 是同一关联事件簇，不能算两个独立样本 |

| NOAA-10 ERBE 扫描仪内部地址译码电路故障 | [NASA-TM-102661, NTRS 19900016012](https://ntrs.nasa.gov/citations/19900016012) | NTRS 标注 Public / Work of US Gov. Public Use Permitted；作者列表含 ST Systems Corp. 合作者，图表/第三方材料待核验 | GitHub 精确检索本轮未命中该文档 ID 或 NOAA-10 ERBE 组合；但本轮协调检索已暴露该来源，完整历史资料包/PR/检索暴露仍未审计 | **仅作开发候选，不准入本轮盲留出**；摘要提供明确仪器异常与测试分析，适合后续证据角色任务，但需全文核查、第三方材料权利审查及独立性审计 |
| NOAA-13 太阳阵列母线对地短路 / 电池充电故障 | [NASA Lessons Learned #387](https://llis.nasa.gov/lesson/387)；NASA Release 94-157；NASA SP-2012-4012 | NASA Lesson / NASA 历史材料公开可访问；具体报告及附件的再利用边界仍须按原件确认 | **已确认深度暴露**：已进入 resources/sources.json、resources/source_passages.json、EPS seed-curation skill、pressure cases、domain review checklist 等开发资产 | **排除**；不得将该来源重新包装为新留出；保留“surmised/possible”而非确定根因的原始不确定性 |

| ATS-6 姿态控制 / Roll Wheel / Earth Sensor Assembly 异常 | [NASA-RP-1080-VOL-2, NTRS 19820008275](https://ntrs.nasa.gov/citations/19820008275)；[ATS-6 Final Engineering Performance Report PDF](https://ntrs.nasa.gov/api/citations/19820008275/downloads/19820008275.pdf) | NTRS 标注 Public / Work of US Gov. Public Use Permitted；具体页内第三方材料仍需核查 | 本轮公开检索和报告内容已向协调模型暴露；历史仓库/PR/资料包审计尚未完成 | **仅作开发候选，不准入本轮盲留**；报告包含 Roll Wheel drive electronics 诊断、ESA 温度相关异常及若干候选元件，但部分根因仍是候选；同一 ATS-6 报告内多个异常不可拆成多个独立来源簇 |
| Sentinel-1B CAPS 28V regulated bus anomaly | [ESA Sentinel-1B In-Flight Anomaly Summary Report](https://sentinels.copernicus.eu/documents/247904/4819394/Sentinel-1B%2BIn-Flight%2BAnomaly%2BSummary%2BReport.pdf) | 封面标注 “ESA unclassified - for public release”；本轮未找到明确允许抽取、改写并用于衍生研究数据集/模型训练的许可条款 | 本轮已向协调模型暴露报告及根因摘要；完整历史仓库、PR、资料包审计未完成 | **版权 HOLD，且本轮暴露，不准入盲留**；报告指出主/冗余 CAPS 28V 调节器异常关闭，陶瓷电容修复焊接工艺为 most probable common cause，但独立双故障等其他模式仍未排除；不得把 most probable 改写成确定根因，也不得将 S1A/S1B 关联监测当作两个独立簇 |
| TDRS 环境诱发异常（ACS control processor / SEU） | [NASA NTRS 19900032665](https://ntrs.nasa.gov/citations/19900032665) | NTRS 标注 Distribution Limits: Public，但 Copyright: Other；无可用下载 | 本轮检索已向协调模型暴露摘要；完整历史暴露审计未完成 | **版权 HOLD，不准入**；摘要称 ACS 控制处理器 checksum errors 最终追溯至高能粒子诱发 RAM SEU；同一论文概述多类异常，不能把一篇综述/会议论文拆成多个独立来源簇 |
| Voyager 2 scan platform azimuth slew anomaly | [NASA NTRS 19830062955](https://ntrs.nasa.gov/search.jsp?R=19830062955) | NTRS 标注 Distribution Limits: Public，但 Copyright: Other；无可用下载 | 本轮检索已向协调模型暴露摘要；历史仓库/PR/资料包审计未完成 | **版权 HOLD，不准入**；1981 年 Voyager 2 方位轴未完成 slew，Voyager 1 曾有相似事件，但两者不能未经事件/来源独立性审查就视为独立簇 |

**本轮公开文献侦察说明（2026-11-20）：**以上四条均已被本轮协调模型检索/阅读，因此即使某份文件标注 Public Use Permitted，也不能作为本轮生成模型的未暴露确认性留出。ATS-6 可作为最有价值的开发型材料候选；Sentinel-1B 具有较好的证据链与不确定性表达价值，但衍生数据使用权尚未确认。TDRS 与 Voyager 2 的 NTRS 元数据明确显示 Copyright: Other，当前不能据公开可访问性推定可再利用。四条均不增加准入簇数。

## 统一来源与证据规则

- **历史暴露**包括仓库、PR、历史资料包、既往对话、连接检索源以及本轮协调上下文。仅在 GitHub 默认分支搜索未命中，不足以证明独立。
- **版权状态**必须针对具体文件及拟进行的事实卡提取、改写、合成任务和再分发用途核验；网页公开可访问、NASA NTRS 托管或政府网站托管均不自动等于所有衍生用途获许可。
- **证据忠实度**：不生成不存在的上游 ML 输出、结构化日志、时间戳、故障机理或处置记录。缺失字段保持缺失；如未来制作合成字段，必须逐字段标记 SYNTHETIC 和生成来源。
- **来源簇独立性**按事件、任务、报告及共享故障机制审查；同平台关联故障、同一空间天气事件或同一报告的多个案例，不得简单计为多个独立来源簇。
- **IMAGE SSPC**的原文仅支持 “likely SEU-induced instant trip”；它已深度进入既有 DGSI 开发材料，属于明确泄漏排除，不得转入确认性留出。

## 最终准入计数

**准入簇数 = 0，实验仍 NOT_RUN。**

- 新准入来源簇：0
- 新 L0 fact cards：0
- 新 L1 tasks：0
- 新正式生成答案 / 盲审：0 / 0
- 既有留出案例、rubric、阈值、权重及历史成绩变更：0
- 模型调用 / 训练：0

本表为 PR #191 的来源筛查汇总，不是对外发布的法律意见，也不构成生成或训练授权。
