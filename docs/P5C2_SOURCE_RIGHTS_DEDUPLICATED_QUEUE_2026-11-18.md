# P5-C2 · 按来源文献去重的使用权利核查队列（2026-11-18）

## 风险与当前事实

C2 专家评分只覆盖科学内容；独立专家 ACCEPT 不等于论文可用于构造、发布或训练的许可。尤其是同一份报告可同时支撑多张 L0 卡、多个事件 episode 和多条 L1 合成任务；若按任务数统计使用许可，会虚增授权来源数。

当前候选集合含 **15 条 SYNTHETIC L1**，它们绑定 **12 张 L0 事实卡、7 份唯一来源文献**。仓库 L0 清单另外包含 1 张未绑定到本 C2 集合的 ISEE 专家系统事实卡，不能把它计入此次来源权利清单。以上是结构性覆盖数，不是许可通过数，也不是经审核 Gold 数。

## 实现

`build_c2_source_rights_queue` 使用已通过原有证据/任务指纹校验的只读科学审查 dossier，按 `source_reference.source_id` 合并相同文献，保留文献标题、URL、精确来源位置、每个 L0 的 public SHA-256、任务 ID、事件族及来源类型；同一 source ID 出现不同文献标题或 URL 时拒绝合并。

完整双专家审查包的协调员侧新增 `C2_SOURCE_RIGHTS_CLEARANCE_QUEUE_BLANK.json`。它绑定 `collection_projection_sha256`，每份文献的 `license_or_permission_evidence_ref`、`permitted_reuse_scope` 与 `rights_decision` 均为 null，明确 `rights_cleared=false`。这些占位符不是法律意见、使用许可或专家结论。

两位专家各自原有的 Word/JSON 评分表和科学审查 dossier 均保持独立，私人审核意见不进入 GitHub、正式提示或训练目标；不自动提升权限。

## 复查

```bash
python -m unittest discover -s tests -p 'test_l1_c2_source_rights_queue.py' -v
python -m unittest discover -s tests -p 'test_l1_c2_complete_review_kit.py' -v
```

真实权利核验须在受控渠道记录许可凭证、权利人、允许的用途、传播/训练边界，以及必要时取得进一步授权。**公开可访问不意味着商业再利用、重新发布或模型训练均获许可。** 本工具不判定不同权利制度下的法律结论，也不访问受限文献。

## 不变门禁

`REAL_GOLD_TRACK` 与 `LITERATURE_DERIVED_SYNTHETIC_TRACK` 不混用；本 PR 不改 L0 原始事实、L1 input/formal_target 或 split，不调用付费模型、不导出 SFT、不启动训练。领域科学审查、来源使用权利和用户授权仍为独立阻断门禁。
