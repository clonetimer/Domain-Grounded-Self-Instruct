# DGSI v0.2.0：复现与复用说明

本版交付可重复使用的数据构建 Skill、离线工具，以及一组已经实际生成并经过两次独立会话 GPT 评分的文献衍生合成候选。人工专家缺席时，按用户授权采用 **GPT 辅助审核**；这足以运行开发示例和检查候选质量。GPT 的身份、评分和分歧均保留，不填写人类专家签名。

当前范围冻结为：输入材料整理 → L0/L1 来源绑定 → 模型可见输入 → AI 生成正式候选 → 独立 AI 复核 → 可查看的三消息 JSONL。正式 Gold、真实案例准入和实际微调另行决定。工具已经可用；不要因这些外部事项尚未发生而重复扩展工具流程。

## 1. 最快运行：重放本次完整结果

解压完整 toolkit，在解压后的根目录运行。Python 3.11；Ubuntu、Windows 使用同样命令：

```text
python -m pip install -r requirements-validation.txt
python scripts/run_dgsi_skill.py demo --output local_demo
```

依赖安装完成后，`demo` 本身不联网、不调用模型。它验证冻结材料的哈希、4 案例 × 5 方法完整性、候选指令与回答绑定、每条两份不同 token 的 GPT 评分，再生成：

| 输出 | 用途 |
|---|---|
| `local_demo/preview_messages.jsonl` | 20 条可直接查看的 system/user/assistant 开发候选，含方法比较的全部结果 |
| `local_demo/dgsi_preview_messages.jsonl` | 其中 4 条 DGSI 方法原始候选，保留原始评分和待修订项 |
| `local_demo/dgsi_curated_preview_messages.jsonl` | 经过 GPT 双评接受的交付候选；采用单独复审的修订版替换需要修订的原版 |
| `local_demo/gpt_review_report.json` | 逐条十维评分、方法均值、重大错误、分歧及修订状态 |
| `local_demo/source_and_generation_manifest.json` | 本次输入、生成结果、评分、来源绑定和版本的文件哈希清单 |

这些文件不是空白表。`demo` 是对已保存的实际生成及审核结果的重放，**不会新生成答案**。候选是否需要修改，以每条评分状态为准；所有行保留 `preview_only=true`、`split=null`，没有自动训练授权。已有输出目录会被拒绝，第二次请使用新的目录名。

完整实验材料在 `evaluation/closeout_20261119/`：

- `shared_cases.json`：四个模型可见输入；不含参考答案、内部审稿提醒或当前事件文献答案。
- `prompts/M0.json` 至 `M4.json`：五种方法的实际生成要求。
- `generations/`：五个独立生成会话的原始候选，未按评审结果回填修改。
- `review_inputs.json`、`review_prompt.json`：隐藏方法标签的完整评审输入与统一评分规则。
- `reviews/`、`gpt_reviews.json`：两次独立会话 GPT 评分；身份明确为 GPT。
- `trials.json`：解盲后的方法映射、有效指令、答案及哈希。
- `delivery_revisions.json`：针对实际发现的单项交付修订、原版绑定及两份新 GPT 评分；不回填原始比较分数。
- `coordinator/`、`fixtures/`：来源、原候选和生成字段的追溯材料；含参考结论，只给协调者查看，**不要上传给生成会话**。

## 2. 在自己的 GPT 会话中重新生成

可用当前聊天模型，也可用用户自行选择的其他模型；本工具不会启动或支付外部 API。模型输出有随机性，因此可以复现流程和检查，不能保证重新生成的文字逐字相同。

1. 每种方法开一个全新会话，固定同一种生成模型。只提供 `shared_cases.json`、`target_schema.json` 和该方法的 `prompts/Mx.json`。不要提供原始 `generations/`、`trials.json`、评分、`fixtures/` 或 `coordinator/`。
2. 对模型说：“按 prompt 文件生成四条中文 SYNTHETIC/DEV_ONLY 候选，按指定顺序输出约定 JSON。只使用输入可见证据；未知字段保持未知；不要假装做过真实 ML/仿真/专家审核。复制输入哈希。不要输出推理草稿。”
3. 保存五个原始 JSON。先做 JSON Schema 校验；若只修 JSON 语法或缺失字段，记录修订次数。不要只优化 DGSI 的答案再与未经修订的其他方法比较。
4. 给每个候选分配随机不含方法名的 `trial_id`。用下述 Python API 生成绑定哈希。两名评审各开新会话，只看对应可见输入、候选指令/答案、哈希及 `review_prompt.json`；不看方法映射、原始参考目标或对方评分。可使用同一评审模型的两个独立会话，但应报告同模型误差相关性。
5. 每个评审使用不同 `reviewer_token` 并标注 `reviewer_kind=GPT`。保留全部逐项评分和具体证据位置。调用 `summarize_ai_reviews` 汇总；有分歧就保留分歧，不把均分当作物理确诊或人类认可。重新生成须使用新哈希和新审核，不能沿用本包的旧评分。

在项目根目录或解压根目录，Python API 的最小用法：

```python
import sys
sys.path.insert(0, "src")
from dgsi.skill_delivery import digest, candidate_digest, summarize_ai_reviews

# trial 字段与本包 trials.json 一致：trial_id、arm、comparison_unit_id、
# shared_input_sha256、instruction、formal_target。
trial["shared_input_sha256"] = digest(model_visible_user)
trial["target_sha256"] = digest(trial["formal_target"])
trial["candidate_sha256"] = candidate_digest(trial)
# 将三个哈希和 trial_id 交给各评审原样复制，不交出 arm 的名称。
report = summarize_ai_reviews(trials, reviewer_a_rows + reviewer_b_rows)
```

该 API 只汇总并验证所提供的审核记录；不会生成缺失评分，也不验证 GPT 或人类身份。完整文件级重放可复制本包目录结构，更新所有内容对应的 `replay_manifest.json` 后，用 `demo --bundle <自己的冻结目录> --output <新目录>`；变更的文件必须重新审核，不能只改哈希来复用旧结论。

## 3. 换成自己的授权材料

先用 Skill 的 `INGEST` 流程整理上游 ML 结果、诊断日志、任务构型和历史案例。若原材料是 DOCX/PDF，可先运行本地提取：

```text
python scripts/ingest_dgsi_document.py --source input/report.docx --source-id LOCAL-SOURCE-001 --output local_ingest.json
```

普通文本提取不是自动科学解释。模型可根据来源定位生成 L0 事实卡、L1 候选，但必须保留原始事实、合成设定、缺失材料和结论确定性；真实来源缺上游 ML/日志时，不能补成真实运行记录。真实候选与文献合成候选分别建集合。

先用包内四个公开合成任务验证输入准备步骤：

```text
python scripts/run_dgsi_skill.py prepare --collection evaluation/closeout_20261119/fixtures/l1_collection.json --source-facts evaluation/closeout_20261119/fixtures/l0_source_facts.json --output local_prepare
```

实际结果是 4 条生成请求，其中 1 条历史命中因缺可信时间元数据而阻断。换材料时替换 `--collection` 与 `--source-facts` 即可。输出：

- `generation_requests.jsonl`：只有 system/user，供生成模型逐条处理；没有预填 assistant、参考 target 或 internal_review。
- `coordinator/bindings.json`：请求与原 packet、source hash 的对应关系，`not_for_sft=true`。
- `coordinator/human_review_manifest.json`：保留日后真人审核的原始绑定；GPT 评分不要填入其中冒充真人。
- `status.json`：准备数量、阻断历史数量及授权状态。

生成模型只接收 `generation_requests.jsonl`，以及 Skill 中正式输出格式和合成来源规则。准备程序会隔离当前事件文献答案；历史资料必须有带来源的 `available_at`、`verified_at` 且不晚于 cutoff。缺失时只告知阻断，不给历史摘要、不猜时间。可用历史的状态和硬件迁移限制仍由既有 validator 检查。

若需要新合成情景，GPT 应在 L1 中记录 `synthetic_provenance` 的 recipe/version、生成字段、假设、未模拟内容，再重复上述准备、生成及 GPT 复核。GPT 可以做预审和提出修订；真实飞行数据、许可和工程真实性仍需要真实材料来证明。

## 4. 本次比较能说明什么

四类任务为二次诊断综合、历史经验拒绝迁移、冲突协调和证据充分性。五组共 20 个答案来自同一生成模型类型，两个评审会话使用不同于生成器的 GPT 模型；双方都没有看到方法名称。所有方法使用同一四个可见输入和共同输出格式。

Self-Instruct、Evol-Instruct、Magpie、Auto-Instruct 在本包中均是明确记录的聊天工作流适配：一次生成、一次复杂化、用户查询仿写、候选指令自评排序。没有运行原论文全部生成规模、训练排序器或原生 Magpie pre-query 推理。总 token 和实际算力未由会话工具暴露，因此不声称严格等算力。

评分仅衡量这四种情景下的候选构建质量。未开展下游微调；未测独立真实 holdout；历史案例因可信时间缺失被阻断，因此没有测到“有效历史检索带来诊断提升”。同模型两次 GPT 评审也可能共享偏差。用本包可以复查这些边界、定位需修订的候选，而不能推出广泛 SOTA 排名。

## 5. 常见问题

| 情况 | 处理 |
|---|---|
| `OUTPUT_ALREADY_EXISTS` | 换一个输出目录，原结果保留 |
| `REPLAY_HASH_MISMATCH` | 输入或原始输出已变化；检查版本，重建绑定并重新审核 |
| `STALE_GPT_REVIEW` | 指令、答案、输入或方法归属与评分不一致，必须重新评分 |
| `REPLAY_MATRIX_INCOMPLETE` | 缺方法/案例、重复候选或实验计数不一致，补齐实际运行结果 |
| 缺少可信历史时间 | 保持阻断；先补真实时间来源，不能手填猜测时间 |
| 没有人类专家 | 按本版 GPT 辅助路径运行开发候选和复现；不要生成假人类身份 |
| 需要实际训练 | 另行决定适用数据、许可、分组 holdout 和训练授权；本命令不启动训练 |

本轮收尾以能解压运行、能看到实质候选、能复查生成与 GPT 评分、能按同一说明换材料为验收标准。后续只修复复用中出现的具体问题，不因待办外部材料而继续自动增加新流程。
