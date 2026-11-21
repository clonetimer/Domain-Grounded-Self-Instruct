# DGSI Batch01 v6 — 原始输出冻结及盲审交接（2026-11-21）

**实验分类：** `EXPLORATORY_NOT_CONFIRMATORY`，2 案例 × 4 组，8 个原始生成文件。  
**材料批次：** `DGSI-BATCH01-20261120-v6`；案例 `CASE-002`、`CASE-004`；来源簇 `CL-002`、`CL-004`。  
**运行编号：** `DGSI-EXP-2X2-BATCH01-20261120`。  
**来源：** 用户在 2026-11-21 上传的八份生成输出 ZIP；只校验文件而不更改答案。

## 文件完整性与机械约束

- 用户原始提交 ZIP SHA-256：`0a8fbb5b1579041a703a09a09f03c38c91db3951ffa77aa22a16b2b845be9c96`。
- 已下发的原始提示包 SHA-256：`db509d57edee6d6aef255e1869c29930e703f57d2ceb626f83219f778a29b56f`。
- ZIP CRC：PASS。八份生成输出文件齐全；A、B、C、D 各有 CASE-002 和 CASE-004 一份。
- JSON 解析：8/8 PASS；`evaluation/refinement_20261119/target_schema.json` 验证：8/8 PASS；baseline/evolve/select/evolve-select 方法记录及指令候选排序规则：8/8 PASS；正式诊断结果引用 `E01–E03`／`E01–E05`：8/8 PASS。
- 八份提示 `prompts/*.md` 与冻结的下发提示包字节相同：8/8 PASS。
- **唯一检测到的包内非答案差异：** 提交者修改 `run_ledger_template.json`，在八行写入自报模型 `gpt-6 sol` 和日期 `2026-11-21`，但行状态仍为 `NOT_STARTED`，原 `SHA256SUMS.txt` 未随之更新，故该账本条目的旧哈希与当前字节不一致。保持原包不变，单独记录这个差异。

### 原始输出哈希（字节级，非标准答案评分）

| 组别 | 案例 | 原始文件 SHA-256 |
|---|---|---|
| A | CASE-002 | `dd8d2743eba021355c60d2c9e5261ce1b936600d2d88b8075cd6dd2a4675549a` |
| A | CASE-004 | `679152687186a95d259e307d6a7508eea7cb6a7f7f304255da95103a47302494` |
| B | CASE-002 | `eab4458866e02da8c85a5a90f89b4efa05f6791a314cf070ce5ad81b915e1326` |
| B | CASE-004 | `19a0490b3bd003ee3372337749cd903c1fd3e15720a63d94bc41d32127b56c5e` |
| C | CASE-002 | `86579e21cfebb1562446290d5a9b79f66061955378d7fe0a94a283fa13362bb1` |
| C | CASE-004 | `1581e51ec69a539dc7fbcd6b78c9724a2f54332145c42c3be41d064f238c9d21` |
| D | CASE-002 | `9819330ce0a3cc891439ede94e6ac33e0e69dc0911c46c6d594fce52c01210d4` |
| D | CASE-004 | `fb67fd8048063f65e2ffe5a363297e4faea6e600119ae343019113a0f0bfad39` |

## 交付及盲态映射隔离

本轮生成内容在模型工作容器中按上传时收到的字节冻结，另分别准备了两个独立文件包：

1. **协调员私有冻结包** `DGSI_BATCH01_Coordinator_Frozen_20261121.zip`，SHA-256 `cacd4fc21dee558c05755ed02f64f2f44bbb1f3b8c52b08daccfc9ddd9f74cc0`：原始提交 ZIP、八份逐字节原始答案、哈希与真实组别对匿名编号的映射。不得发给盲审评审者，也不得以公开代码仓库存储。
2. **评审者匿名包** `DGSI_BATCH01_BlindReview_Packet_20261121.zip`，SHA-256 `e125ec40963f008de0774ea5f2e5c7fedb8c86f5c27a319ee56374f3bc7ee9ec`：仅包括保管方已放行的两份可见输入、八份随机编号的候选指令与 `formal_target` 的无损内容投影、空白评分表，无组别或 `method_record`。投影与原始 JSON 中对应的 `instruction`、`formal_target` 比对通过 8/8。

**盲审风险：** 评审者即便看不到 A/B/C/D，也可能从指令措辞猜测策略类别；不保证完全方法盲。用户上传中的模型名称、生成日期属于用户填写的元数据；本次检查无法独立证明八个隔离会话、实际服务模型版本、未重试或真实 token 消耗。ZIP、哈希、文件名也不构成可信时间戳或原始报告权利证明。

## 不得越过的实验边界

- 本次是授权的两案例探索性对比，不是完整预注册的确认性运行。原 `evaluation/refinement_20261120/factorial_preregistration.json` 不作任何改动，仍为 `PREREGISTERED_DESIGN_ONLY_NOT_RUN`，不得用本轮数据宣称统计显著、总体优越或训练增益。
- 本轮 **0 份参考答案已读取、0 次盲审、0 份评分、0 次重生成或结果修复**。结构 PASS 不是科学质量 PASS。
- 原始答案、协调员映射及含受控使用权益的生成材料留在私有交接包中，不上传公开 GitHub；独立评审者只接收匿名包和既有冻结评分规则。
- 待两位真正独立、方法盲态的评审者分别提交记录，且所有原始输出哈希已冻结后，再由保管人向评估方开放参考答案核对。保留分歧、失败、无效输出及负收益，不因结果变更阈值或案例。
- 因参考答案来自受控独立保管方，源身份、许可侧册与参考判断不得提前进入任何生成对话。
