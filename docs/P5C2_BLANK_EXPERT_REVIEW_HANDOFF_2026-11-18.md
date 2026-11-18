# P5-C2：当前 15 项 L1 文献合成任务的双专家交接（空白、未准入）

## 适用范围与版本

基于 PR #136 的当前 C2 集成分支（15 项 L1、9 个事件族，全部 `LITERATURE_DERIVED_SYNTHETIC`）。提供给两位独立专家的**空白** Word/JSON 评分表；没有代填的专家分数、审核人身份或审批结论。L0 文献事实、L1 合成输入与正式 target 均不因此被改写。

## 生成（只读输入，创建全新输出目录）

```bash
python scripts/create_l1_c2_expert_review_handoff.py \
  --collection examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json \
  --source-facts examples/l0_public_literature_fact_cards_2026-11-15.json \
  --output-dir local_c2_expert_review_v1
```

工具会生成 `C2_reviewer_A_BLANK.json`、`C2_reviewer_A_BLANK.docx`、`C2_reviewer_B_BLANK.json`、`C2_reviewer_B_BLANK.docx`。必须在两位专家分别接收的受控路径中分发。已存在的输出目录（含符号链接）会被拒绝，不覆盖以前回执。

两份表包含准确的 collection projection SHA-256、packet SHA-256、当前和历史引用的 L0 公共事实卡指纹，以及 10 个独立评分维度。评分、finding codes、结论和 reviewer token 全部空白；模型输入、正式 target、curator review、私有专家身份/意见和 Gold/训练输出均不进入审核模板。专家需另行在授权的源文件和不可变 L1 候选上检查**完整诊断内容**，不可仅据元数据打分。

## 专家必须核查的科学项目

1. L0 来源具体定位、许可和事件类型（真实在轨、地面实验、工程仿真、文献综述）。
2. 合成的 ML 结果、诊断日志、任务构型是否全部明确注明 `SYNTHETIC` 与字段级生成谱系；严禁当作真实 run/log。
3. 现象、故障源、受影响部件、证据充分性及不确定性的边界；FUSE MOST_LIKELY 和 Lunar Orbiter 多候选不得改写成确定唯一根因。
4. 历史 Context 的 as-of 截止时间、同源事件族、状态和硬件适用范围；不得把 Cassini 未完全证实经验当作 FUSE 根因证据。
5. `disposal_status=NOT_RECORDED` 时 `disposal_measures=[]`；新检查建议只能写 `follow_up_actions`。
6. 两位专家分别独立填写十维 1–5 分、固定 finding codes、`ACCEPT_L1 / REVISE / REJECT`；分歧进入受控安全裁决，审核人 token 不允许公开提交。

## 门禁

**空白评分表绝不等于专家审核通过。** 当前状态为 15 项待审、REAL Gold 0、正式 split 0、`training_authorized=false`、SFT 记录 0。回执最终需要通过 `audit_c2_scored_review`、`audit_c2_scored_review_batch` 的 fingerprint+10 维规则，并在受控环境下验证真实专家身份、来源使用权利及裁决。若任一 L0 公共事实或 L1 task/cohort 变化，应重新生成并重审，禁止继承旧版本。

本工具不调用任何付费 API，不读取私有日志，不运行微调，不合并主干。文件生成的成功不是科学准入、Gold 或释放权利。

## 验证

```bash
python -m unittest discover -s tests -p 'test_l1_c2_expert_handoff.py' -v
```

生成材料只供专家在本地填写和回传，切勿将已填回执、审核人实名或受限材料推送到公开 GitHub。
