# P5-C2：15 项 SYNTHETIC L1 科学审核正文附件（review only）

## 解决的实质问题

PR #137 的两份专家 Word/JSON 空白评分表已经绑定了每个 task/collection/L0 公共事实指纹，但评分表**只有任务标识和评分维度，不展示真实待审内容**。仅凭元数据无法判断现象分析、ML 候选解释、证据忠实度或处置方案是否符合科研要求。

本 PR 新增与 A/B 评分表配套的**同一集合指纹**的只读审阅附件：完整合成上游 ML 输入、合成诊断日志、航天器及任务上下文、拟议正式 target、历史 Context、字段级 synthetic provenance，以及 L0 来源事实卡的公开字段与原文定位。L0 `internal_review`、L1 Case `internal_review`、curator prompts、匿名 reviewer token、评语、真实身份均不导出。

## 本地生成（受控工作区）

```bash
python scripts/create_l1_c2_scientific_dossier.py \
  --collection examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json \
  --source-facts examples/l0_public_literature_fact_cards_2026-11-15.json \
  --output-dir local_c2_scientific_dossier_new
```

仅在不存在的目录中生成 `C2_SYNTHETIC_SCIENTIFIC_REVIEW_ONLY.json` 与离线静态 `C2_SYNTHETIC_SCIENTIFIC_REVIEW_ONLY.html`；不得覆盖已填写材料。分别将**同一版本**附件交给两个独立审核者，与 PR #137 的专家 A/B 空白评分表配套。审核意见和身份仅在授权工作区保存，不提交公开 GitHub。

## 审核门禁

1. 对照 `collection_projection_sha256`、`packet_sha256`、`source_public_sha256` 与两份空白表，避免旧审核回执跨任务版本复用。
2. 所有 ML 结果、分数、日志和时间戳均带有 `SYNTHETIC` 场景声明。它们不是实际 ML run、运控日志或飞行记录。原始遥测不进入 LLM 默认输入。
3. L0 文献只支持历史事件事实及其不确定性，不是当前合成故障的直接物理证据。原始文献使用/IP 权利仍需单独审查。
4. 审核故障源与受影响部件、候选概率语义、证据 ID、处置是否来源支持、follow-up 与历史检索 as-of/硬件迁移限制。
5. `NOT_RECORDED` 处置不得写出已执行措施；未确认历史根因不得升级为当前确诊。
6. 任一公开 L0 事实或 L1 任务发生变化，须重生成资料并重新审核，不继承旧表。
7. 附件 **not_for_sft=true, gold_eligible=false, training_authorized=false, sft_records_emitted=0**，不产生 chat messages 训练格式，不分配正式 split。

运行 `python -m unittest discover -s tests -p 'test_l1_c2_scientific_dossier.py' -v`。工程 CI 必须在当前最新 head Ubuntu、Windows 两平台全部 PASS。专家科学审核与来源许可另外独立完成。PR 保持 Draft，不合并主干、不运行付费模型或微调。
