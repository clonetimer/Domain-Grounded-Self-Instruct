# DGSI 指令演化与选择

这是可选的候选构建策略。它借鉴 Evol-Instruct 的指令演化，以及
Auto-Instruct 的多指令生成与选择；不改变数据准入、来源权利或训练授权。
旧版 `baseline` 仍为默认值，旧对比数据保持原样。

## 使用

```bash
python scripts/run_dgsi_skill.py prepare --collection your_l1.json --source-facts your_l0.json --recipe select --output new_requests
```

`generation_requests.jsonl` 与 baseline 完全相同。新增
`authoring_recipe.json` 是给执行构建任务的 AI 的流程说明，`not_for_sft=true`。
把它和生成请求、正式 target schema 提供给构建 AI；不要把该文件拼入最终
SFT 的 user 消息或 assistant target。将构建记录附加到 L1 Case 时，只放
Case 根级 `internal_review` 并保留 `not_for_sft=true`。现有 schema 不接受新增
`internal_review.method_record` 字段；需要单文件携带记录时，将完整记录序列化
为 JSON 字符串，追加到已有的 `internal_review.curator_prompts` 数组：

```python
case["internal_review"]["curator_prompts"].append(
    "INSTRUCTION_DESIGN_RECORD_JSON:" + json.dumps(method_record, ensure_ascii=False)
)
```

这只是 curator 存储，不改变正式指令。比较实验保留的 `generations/*.json`
则是独立构建记录，回放时只投影正式指令和答案，不投影 `method_record`。

可选值：`evolve`（一条约束演化）、`select`（三个风格候选及一次选择）、
`evolve-select`（三个约束演化候选及一次选择）。

历史开发比较记录：`select` 四例均为 20/20、双审均接受；
`evolve-select` 为 19.625/20、两例双审接受。该四例仅为小样本、GPT
辅助评分的开发材料，且所有 M6/M7 选择均落在 I1，未观察到选中后续候选
带来的增益。这些结果不能证明 `select` 优于其他配方，也不能证明演化无效。
因此本 Skill 不指定任何新配方为推荐赢家：`baseline` 保持默认，
`evolve`、`select`、`evolve-select` 均为可选实验策略。方法取舍必须
依照预注册的独立留出实验结果，不从上述开发分数推导。

## 执行规则

1. 冻结输入哈希。只改变任务指令，不改变任务类型、ML 值、日志、设备、
   时间、历史条目、事实卡或合成标识。
2. 演化操作限定为可比性、证据角色、适用范围。输入没有证明同路径、同
   构型或时间对齐时，要求明确缺失，不能把检查条件写成已成立事实。
   对发射/注入路径，必须分别核验路径标识、观测窗口边界及窗口内切换事件；
   只有三者均有证据且确认未切换，才能表述为“同一发射路径、窗口内未切换”。
   路径标识或切换记录缺失时只能标为未知/未记录，不能将“没有看到切换记录”
   改写成“确认没有切换”。
3. ML 推断、独立观测、直接遥测/日志观测和未附原件的上游引用必须分成独立
   证据项。独立观测可单独支持或反驳 ML 推断，但不得并入同一条支持证据，
   也不得把 ML 推断重新标注成独立观测。
4. 先提出指令，按任务一致性、清晰度、输入可回答性、证据角色、范围保留
   五项分别评 0–2 分。这些是生成过程中的 GPT 自评，不是正式专家评分。
   明确表达不确定性或请求补证，也属于可回答任务。
5. 事实或范围自检不通过、任一项为 0 的候选不得入选。合格者按总分选择，
   平分取原序号最小者；全不合格则停止。所有候选、分数及选择都保留。
6. 选定后只生成一份正式答案。不得生成多份答案再用最终评审分数择优。
7. 用 `dgsi.instruction_design.resolve_instruction_design(user, method_record)`
   验证输入绑定、结构、候选数和确定性选择。该检查不证明语义或物理真实性。
8. 最终答案仍经独立审核；审核输入不显示方法、自评分或其他审核结果。

## 回放本轮前向比较

```bash
python scripts/run_dgsi_skill.py demo --bundle evaluation/refinement_20261119 --output refinement_demo
python evaluation/refinement_20261119/analyze.py --output refinement_analysis.json
```

该命令回放已保存生成和评审，不调用模型。`protocol.json` 固定了六个方法、
四个案例、两次 GPT 审核、排序规则和停止条件；原始生成在 `generations/`，
模型可见输入在 `shared_cases.json`，方法提示在 `prompts/`。重新生成时，每
个方法用新会话，只提供该方法提示、相同输入及 `target_schema.json`。
`coordinator/`、原有 target、其他方法输出和最终评分均不提供给生成会话。

第二条命令重新计算每方法、每案例和每来源连通组统计，保留全部并列。
三个 TROPICS 案例属于同一来源组，所以同时报告按案例平均和按两个来源组
等权平均；不能将其当作三个独立文献来源。两个命令都拒绝覆盖已有输出。

冻结协议事先将 `curated_arm` 定为 M7，所以本轮回放的
`dgsi_curated_preview_messages.jsonl` 保留 M7 的两条双审接受预览，不在看完
结果后偷偷换为 M6。M6 的四个原始候选和评审完整保存在 `generations/M6.json`
及 `gpt_reviews.json` 中；全部 24 条的 user/assistant 预览由回放命令输出。
推荐未来使用 M6 是单独记录的开发决策，不改变本轮协议或原始分数。

本轮四个案例覆盖三个任务类型、四个事件族，但只有两个来源文献连通组。
它们相对于旧四例比较做了来源隔离，并不是独立真实飞行 holdout，也不
代表模型预训练从未接触原文献。只有构建质量评估，没有下游微调实验。
评审模型与生成模型不同；两个评审会话仍可能产生相关错误。

六个方法为旧 Evol-style、旧 Auto-style、旧 DGSI、DGSI+evolve、DGSI+select、
DGSI+evolve-select。后三者共享改进的证据角色和适用范围约束，因此与旧
DGSI 的差异包含这些约束；后三者之间的比较才对应演化/选择组件差异。
各方法的候选指令数公开，实际 token/计算量不可观测，不宣称等算力。

只运行预先冻结的一轮，完整报告并列、失败和分歧。不以在同一测试集上
不断改提示直至第一名作为成功标准。评审只核验可见合成材料的支持性，
不把 GPT 分数当成物理真实性、真实 Gold 或微调增益。

本轮 M6、M7 的四例都按平分规则选了 I1，未展示“选中后续候选”带来的收益。
因此不能将 M6 的最高分单独归因于排序步骤；还可能与指令表述、共有的证据
约束、生成差异及评审差异有关。详见 `instruction_selection_audit.json`。

## 原方法来源

- Evol-Instruct / WizardLM: <https://arxiv.org/abs/2304.12244>
- Auto-Instruct: <https://aclanthology.org/2023.findings-emnlp.659/>

Auto-Instruct 原文使用训练后的排序模型，本工具使用 GPT 记录评分加确定性
选择，仍称 Auto-Instruct-style 适配，不宣称完整复现原算法。
