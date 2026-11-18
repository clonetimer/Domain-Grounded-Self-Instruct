# P5-C2：双专家完整科学审核包，一次生成、独立分发

## 目的

与 #137 的仅含元数据和十维评分表不同，#138 已提供完整的合成诊断输入与拟议结论。本阶段将两者组成**同一冻结 L1 集合**的离线审核包，避免专家拿到空白评分表但缺少科学证据正文，或不同版本的表与正文发生错配。

## 生成命令

```bash
python scripts/create_l1_c2_complete_review_kit.py \
  --collection examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json \
  --source-facts examples/l0_public_literature_fact_cards_2026-11-15.json \
  --output-file local_C2_15_tasks_unreviewed.zip
```

要求目标父目录已存在，目标 ZIP 文件不得存在。输出时先构建及验证全部条目，再在同目录写临时文件、通过 `os.link` 原子发布。既有文件、符号链接和同时运行的另一个写入者均不可覆盖。不支持硬链接的文件系统直接拒绝发布，不改用存在竞态的复制或重命名。

## 包结构与发送规则

```text
local_C2_15_tasks_unreviewed.zip
  README_REVIEW_ONLY.txt
  COORDINATOR_REVIEW_ONLY_MANIFEST.json
  SHA256SUMS.txt
  reviewer_A.zip
    C2_reviewer_A_BLANK.docx
    C2_reviewer_A_BLANK.json
    C2_SYNTHETIC_SCIENTIFIC_REVIEW_ONLY.json
    C2_SYNTHETIC_SCIENTIFIC_REVIEW_ONLY.html
    README_REVIEW_ONLY.txt
  reviewer_B.zip
    C2_reviewer_B_BLANK.docx
    C2_reviewer_B_BLANK.json
    C2_SYNTHETIC_SCIENTIFIC_REVIEW_ONLY.json
    C2_SYNTHETIC_SCIENTIFIC_REVIEW_ONLY.html
    README_REVIEW_ONLY.txt
```

只发送 `reviewer_A.zip` 给专家 A、`reviewer_B.zip` 给专家 B；协调员保留外层索引及 SHA-256。两位专家应**各自独立**阅读完整拟议诊断输入、正式 target、L0 文献事实与原始文献；独立填写十维评分、finding codes 和裁定。不得向专家提供其他人的已填结果。专家身份及私有评语仅在授权工作区保存，不提交公开仓库。

## 科学边界与门禁

- 当前 cohort 为 15 项待审的 `LITERATURE_DERIVED_SYNTHETIC` 任务、9 个来源事件族，来源文献的许可及再利用权利**未验证**。
- 合成上游 ML 结果、日志及任务设定绝不被称为真实运控记录或真实飞行诊断。
- L0 来源事件事实只是合成设定的约束，不是当前合成故障的确认证据。历史 Context 须核查 as-of、构型适用性、状态和迁移限制，不得投票确认当前根因。
- 正式 target 中故障源和受影响部件分开，区分处置已记录事实和 `follow_up_actions`；`disposal_status=NOT_RECORDED` 必须对应空处置措施。
- 每份 Word/JSON 空白表与正文使用相同 `collection_projection_sha256`；每条用 `packet_sha256`、`source_public_sha256`、`source_fact_bindings` 绑定。当任何 L0 或 L1 被修改，必须重新生成并重新独立审核。
- 输出严格为 **REVIEW ONLY**：`not_for_sft=true`、`gold_eligible=false`、`official_splits_assigned=false`、`training_authorized=false`、`sft_records_emitted=0`。真实 Gold、REAL 候选的证据补齐、独立身份核验与微调授权是分别存在的额外门禁。
- 不读取私有日志、不调用付费模型 API、不产生正式聊天训练数据、不触发微调、不合并主干。

## 本地测试

```bash
python -m unittest discover -s tests -p 'test_l1_c2_complete_review_kit.py' -v
```

测试使用仓库内 15 项 `SYNTHETIC_TEST_ONLY` 候选，检查全包内容、跨文档散列一致性、独立空白评分表、输出可复现、已存在目标拒绝、Windows/Ubuntu 悬空符号链接拒绝、并发写入单赢家及无效来源阻断。只有 PR 同一最新 head 的 Ubuntu 与 Windows 必需工作流全部通过，才可认定工程门禁通过。专家科学审核并不由 CI PASS 代替。
