# DGSI Batch02 — 第二批生成前冻结与完整性验收（2026-11-21）

**状态：** `PRE_GENERATION_FROZEN_NOT_RUN`  
**分类：** `EXPLORATORY_REPLICATION_NOT_CONFIRMATORY`  
**运行编号：** `DGSI-EXP-2X2-BATCH02-20261121`  
**声明冻结时刻（非可信时间戳）：** `2026-11-21T12:40:18Z`。

## 本轮实际接收和验收

接收用户上传 `DGSI_Batch02_Developer_20261121_v1.zip`，SHA-256：
`3fc7be9eef20b67a609ee7f7466611826408cbaeba6411f117145f26d7911a67`。

- ZIP CRC 通过，12/12 个保管侧文件哈希全部匹配。
- `01_model_inputs.jsonl` 共 5 行，5 个独立标识；对应 5 份 UTF-8 TXT 字节、输入哈希、案例编号、来源簇一致。
- 5 例共 24 条有编号的 E01–E05/E01–E04 证据；全部是来源事实匿名摘编，不是原始遥测或上游真实 ML 结果。
- 保管侧逐例记录为 `material_admission=PASS`，限已经核查的内部科研使用及署名条件；原始 HTML/PDF 完整字节与哈希**未归档**，无法从输入哈希推断源原件完整性。
- 材料保管侧为同一 AI，非两位独立人工专家签章。五个事件簇为已核查的不同事件链，不表示 IID 随机样本。历史核查限定范围，不证明基础模型未预训练见过来源。

## 与首次生成前固定的规则绑定

以下三个既有文件以**原始字节**纳入生成前私有冻结交付包，不修改评分锚点、接受阈值或目标字段。

| 冻结基础 | 原文件/版本 | SHA-256 |
|---|---|---|
| 2×2 实验方案 | `evaluation/refinement_20261120/factorial_preregistration.json` / `dgsi-instruction-2x2-preregistration.v1` | `5d32aa71681d0640da2115bd5e54e28771651753fd84f8a3b8b04ce2d06696a6` |
| 十维 0–2 分细则 | `DGSI_Batch01_八项匿名评审评分细则_v1.0.md` / v1.0 | `8efead9630e565b4778b2cb68916dcf471cea3714555c173cd1a9b9f733b1db1` |
| 目标 JSON Schema | `evaluation/refinement_20261119/target_schema.json` / 文件无独立版本字段，所属协议 `dgsi-refinement-protocol.v1` | `4710df4e9fcbf7d42fcbf3f12ea6f80ce44135c8acae009e3aee1436112243c2` |

**注意十维文件原本针对第一批 2 例/8 项，并在第一批生成后、评分前写成。** 第二批单独记录其在第二批生成前适用于 5 例/20 项的范围声明。所有逐维评分 0/1/2 锚点、缺失 ML/历史信息处理、`accepted`（总分≥16、无0分、无关键失败且 `output_valid=true`）、`output_valid`、`critical_failure_codes`、`evidence_notes` 定义不改。不得反向声称第一批生成前已经有完整细则。

A/B/C/D 四组启用要素、三选一候选数、失败停机规则、目标 Schema 采用原有代码与首批提示中确定的操作。所有组同一条输入的可见事实正文相同，不加研究者参考答案。原 Batch01 提示包 SHA-256：`db509d57edee6d6aef255e1869c29930e703f57d2ceb626f83219f778a29b56f`；仅换运行编号、案例正文与 E 编号、输入哈希，其他规则不随第一批成绩变化。

## 本次材料的五个案号与输入 SHA-256

| 案例 | 来源簇 | 原始输入 SHA-256 |
|---|---|---|
| B02-CASE-001 | B02-CLUSTER-001 | `b9a2bd5148283cc7b7793c1ad156ab9ac592bab745cf8054f4f36881d2de9de5` |
| B02-CASE-002 | B02-CLUSTER-002 | `32ef6355f588d7d38a89e710fbf2c7b58b8ed71d5014b2978d9058d22fe92826` |
| B02-CASE-003 | B02-CLUSTER-003 | `7915d1b82347b11608d6bcb2d098da60f904b3a37b6941961f0d8aaa117ad619` |
| B02-CASE-004 | B02-CLUSTER-004 | `99e6d4ce12f9888a512204a1b75b4db7ee816a762e193f1363cd9a768465c571` |
| B02-CASE-005 | B02-CLUSTER-005 | `90ec283ad29a6cd2db305a40b7aaffd05106a284110746f5fafcc1048a99d880` |

## 生成前包与执行边界

在本次工作容器中创建私有交接文件 `DGSI_BATCH02_PreGeneration_Freeze_20261121.zip`。ZIP SHA-256：
`a59ae02634bf30fee10df2106414d96b8b0772b21c2a8590b5c9e1cbada8db9b`。

其中 `01_pregeneration_freeze_manifest.json` SHA-256：
`b284490d869a743ca84c94a41717b559099ea490f516e760ccba8a36ff79bb70`。
内部 34/34 SHA 校验通过、20/20 方法提示完整，5 份原始输入与所有四组提示中的事实正文逐字一致。

**严格隔离：** 原始输入文本、完整提示包、研究者来源/许可侧册、真实参考答案和事后评分不写入 GitHub 仓库；本文件只记录匿名元数据与完整性指纹。20 次模型生成需要单次独立会话或等效隔离执行；无法独立证明隔离、调用版本或算力时应如实标 `NOT_MEASURED/NOT_ATTESTED`。不准重试、改稿、挑结果；所有失败需原样记录。

**已实际执行：** 材料核验及生成前冻结；**未执行：** 20 次模型调用、原始答案冻结、双盲评分、参考答案核对、微调或 SFT Gold 准入。

**科研判断：** 本批尚缺原源完整 SHA 与满足原确认性证据门禁的材料，因此不升级原 `PREREGISTERED_DESIGN_ONLY_NOT_RUN` 状态，不声称已完成确认性实验或方法优越性。

## 开发经验

- 将材料准入、生成前规则绑定、确认性实验资格拆开登记，避免把 `material_admission=PASS` 误写成所有科学门禁已过。
- 评分锚点和 JSON Schema 坚持复用原字节；面对第一批专用数量说明，仅在第二批开跑前另立适用范围声明，不修改原文件或事后追认。
- 不让生成模型看 `case_manifest`、历史对比成绩、隐藏来源或参考答案；把可见事实正文相同、每条输入哈希相同落实到 20 份提示的自动检查。
- 源原件哈希缺失必须保留为来源归档问题，不用输入文本哈希代替；不能为了快速“完成确认性实验”放宽门禁。
