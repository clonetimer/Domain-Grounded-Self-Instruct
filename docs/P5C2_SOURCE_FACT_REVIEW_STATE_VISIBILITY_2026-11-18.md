# P5-C2：专家审核附件增加 L0 来源确认状态（2026-11-18）

## 发现的科学审核风险

在 #139 的完整双专家审核包中，L0 事实卡附录公开了来源定位、事件、故障机理及处置事实，但没有显示 `domain_review_status`。这可能导致评审者误以为 AI 辅助整理的来源事实已经完成独立领域专家确认。独立审核必须能够同时看到内容**与其审核成熟度**。

## 实施

- 在审阅专用 JSON 的每条 `l0_public_source_context` 中增加来自实际 L0 卡的 `domain_review_status`、`domain_review_evidence_sha256` 和 `sft_eligible`，不推断审核结果，不包括 `internal_review` 或专家私有身份。
- 对**去重后的被引用 L0 卡**统计 `l0_bound_fact_card_count` 和 `l0_domain_review_status_counts`；多条 L1 任务共用同一来源不能重复算作多个专家确认事实。
- 审阅 HTML 首页明确显示来源审核状态及提醒。Word 双专家空白评分仍保留，两个独立压缩包均包含更新后的同版科学审阅正文。
- 保留原始 L0 与 L1、`collection_projection_sha256`、`packet_sha256`、来源指纹及旧任务准入状态；任何公开来源内容实际变更仍由现有指纹逻辑触发旧回执失效。

## 本批数据的准入边界

仓库当前 15 项 L1 SYNTHETIC 候选、9 个事件族仍然需要独立专家审核，绑定的 L0 事实卡处于 `AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION`。显示待审状态**不是**审核通过。使用权利尚未核实，Gold 与训练授权均为 false。

运行：
```bash
python -m unittest discover -s tests -p 'test_l1_c2_scientific_dossier.py' -v
python -m unittest discover -s tests -p 'test_l1_c2_complete_review_kit.py' -v
```

注意：用户获取旧版 ZIP 后不可视为自动拥有新版状态可见性；需从本 PR 最新 head 重新生成审核包，独立记录两名专家的审查结果。未经审核不得导出正式 SFT 数据、分配训练 split 或微调。
