# P5-C2：绑定当前 L0/L1 的双专家回填接收

## 已补齐的操作入口

`scripts/audit_l1_c2_current_expert_intake.py` 接收已交付 A/B JSON 表的副本，以及独立取得的当前 L1 collection、L0 source-facts JSON。它重新生成当前两份空白模板，检查回填表与当前材料的绑定，再将完整评分对适配到现有十维评分入口。该适配层不创建另一套评分规则。

模块 API：

```python
audit_c2_expert_intake_against_current_sources(
    reviewer_a, reviewer_b, current_l1_collection, current_l0_fact_cards
)
```

`current_l0_fact_cards` 是事实卡列表；CLI 从 L0 文件的 `cards` 字段取得该列表。当前材料必须来自协调人的独立、可信版本快照，不能从回填表复制摘要或指纹充当当前基准。

## 回填规则

只编辑 `tasks[].scorecard` 的 `reviewer_token`、`scores`、`finding_codes`、`decision`。原 schema、cohort/packet/source 指纹、任务与来源绑定、状态、计数和授权字段都保留原值。表中 `BLANK_EXTERNAL_EXPERT_REVIEW_REQUIRED` / `NOT_REVIEWED` 是不可变模板标签；接收结果另行报告完成状态，不要求专家手工提升这些字段。

每份表在整个 cohort 中使用同一个去首尾空白后的私有 reviewer token，两份表的 token 必须不同。token 只是本地声明的一致性约束，不能认证真实身份、专业能力或盲审独立性。所有任务必须各出现一次；允许对任务排序，不允许删掉未评的任务。

空白与部分填写均可接收：十维键必须完整；已填写分数必须为严格整数 1–5（布尔值、浮点数、字符串均不接受）；token、决定与 finding codes 必须符合既有字段域，未填值保留 `null` 或空 finding 列表。部分填写只通过形状与已填值域检查，不声明科学评分通过；例如尚未完成的 `NO_ISSUE` 与其他字段关系仍须在完整配对时经过原 rubric 的一致性检查。禁止复制另一位专家的评分、生成缺失评分或伪造第二个 reviewer 来补足调用条件。

只有两份完整 scorecard 同时存在时才调用 `validate_blind_l1_review` 及 `audit_c2_scored_review`。两分及以上维度差、不同决定、REVISE、REJECT 或实质 finding 依据原规则进入待裁决；一致 ACCEPT_L1 仍然只是待身份核验。原评分函数及阈值不变。

## 运行

```bash
python scripts/audit_l1_c2_current_expert_intake.py \
  --reviewer-a /authorized/review/reviewer-A-return.json \
  --reviewer-b /authorized/review/reviewer-B-return.json \
  --current-collection /authorized/input/l1-candidate-collection.json \
  --current-l0-facts /authorized/input/l0-source-facts.json \
  --output-file /authorized/review/current-expert-intake.json
```

运行前创建输出父目录，选择新的文件名。不带 `--output-file` 时只显示计数；带该参数时额外写入私有逐任务清单。CLI 不自动解析 Word，不自动转录专家意见。Word 回填应先转录到匹配的 JSON 副本，并由专家核对。

| 结果 | 含义 |
|---|---|
| `PENDING_REVIEW_COMPLETION` | 至少一份 scorecard 未填完；没有完整成对评分通过的声明。 |
| `PENDING_SECURE_ADJUDICATION` | 完整评分对要求受控裁决；身份与来源权利仍未核验。 |
| `PENDING_REVIEWER_AUTHENTICATION` | 完整评分对结构合格，仍需真实身份、独立性、权利及科学准入手续。 |
| CLI `REJECTED` / 退出码 2 | 当前材料、不可变字段、覆盖、字段类型、输入解析或输出发布不符合约束；没有生成可用结果文件。 |

成功接收（退出码 0）不意味着评分完成。当前原始空白表应得到 15 项待补全、30 份未完成 scorecard、0 个完整评分对。

## 输出与错误边界

默认 stdout 只有聚合计数、固定状态与授权标志。可选私有报告含当前可信任务 ID、材料指纹和固定待办信息，不含原始分数、reviewer token、原始 finding payload 或自由文本。输入重复 JSON key、额外字段、任务重复/缺失或固定字段篡改均拒绝；比较不可变 JSON 时保留类型差异，`false` 不等于 `0`。

输出使用同目录临时文件、flush/fsync 和原子 hard-link 发布，已有文件、符号链接及并发写入冲突均不覆盖。输入无效时不写结果。stdout 与异常不回显输入路径、任务内容或审核内容。

即使所有评分完整，输出仍是 `identity_authenticated=false`、`source_rights_verified=false`、专家裁决 0、权利清理 0、正式 split 未分配、Gold 未准入、SFT 行数 0、`training_authorized=false`。来源权利回填继续使用独立的 [current-source rights preflight](P5C2_CURRENT_SOURCE_RIGHTS_PREFLIGHT_20261118.md)。

## 兼容性与验证

原 RC2 审核表 schema 与 15 项候选没有改动，已交付空白表可以直接用于此入口。RC3 便携包增加新模块、CLI、测试和本说明；解压回归从工具包实际生成审核 ZIP，再将 A/B 原始空白 JSON 回送当前输入校验，仓库 `PYTHONPATH` 不参与运行。

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_l1_c2_expert_intake*.py' -v
PYTHONPATH=src python -m unittest discover -s tests -p 'test_portable_toolkit_package_build.py' -v
```

测试中的完整评分全部标记 `SYNTHETIC_TEST_ONLY`，不作为真实专家回执或准入证据交付。
