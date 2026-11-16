# 仿真运行证据入口：使用与移交

版本：receipt-v1 / engineering pilot。此模块是 DGSI Skill 的新增工程入口，不是完整工具包的替代品，也不是微调数据导出器。

## 本轮能够做什么

读取一个本地运行回执和它引用的 JSON/JSONL 文件，核对配置指纹、run ID、文件长度与 SHA-256、证据引用、模型可见与 QA 专用分区、声明的可用时间。分别保留六种状态，不把其中任何一项自动当作下一项成立的证明：

| 状态字段 | 含义 | 对应证据角色 |
|---|---|---|
| injection_configured | 已配置故障注入 | CONFIGURATION，QA_ONLY |
| injection_executed | 注入实际执行 | EXECUTION_RECORD，QA_ONLY |
| physical_effect_observed | 物理效应出现 | PHYSICS_QA，QA_ONLY |
| diagnostic_effect_observed | 诊断信号出现 | DIAGNOSTIC_LOG |
| upstream_ml_detected | 上游算法检测 | ML_RESULT |
| upstream_ml_localized | 上游定位经对照检查 | ML_EVALUATION，QA_ONLY |

每项使用 YES / NO / UNKNOWN。YES 和 NO 都必须引用相应角色的材料；UNKNOWN 可以没有材料。支持“有异常但算法漏检”“无对应物理效应但算法报警”等负面结果，不把它们修饰为成功。

运行引擎可标记 SIMULINK、BASILISK 或 OTHER；版本、模型修订、配置哈希必须明确。该字段仅记录来源声明，不独立证明原生模块调用链。已有 R84-R3A 的专用验收逻辑保持不变。

## Windows / Linux 使用

要求 Python 3.11+。在解压根目录运行：

```text
python -m pip install -r requirements-validation.txt
python scripts/create_simulation_receipt_fixture.py --output local_fixture --case unknown-physics
python scripts/audit_simulation_run_receipt.py --receipt local_fixture/receipt.json --artifact-root local_fixture
python -m unittest discover -s tests -p test_simulation_run_receipt.py -v
```

这是明确标注的 **SYNTHETIC_TEST_ONLY 测试夹具**，没有运行任何航天器仿真或 ML 模型。夹具生成器拒绝覆盖现有目录；切换场景时使用不同目录名。`complete` 也仅表示测试字段齐全，不表示真实试验成功。

接入实际材料时，在私有工作目录建立相同回执结构，使用真实文件的 SHA-256 和长度，保留缺失状态为 UNKNOWN。实际诊断日志、测试报告和上游结果不存在时，不得由其他 AI 编造以填满模板。

CLI 成功退出码为 0，校验失败为 2。输出只有计数、范围和固定错误代码，不输出文件路径、故障真值、诊断目标或原文。

## 接入边界

- `METADATA_ONLY`：Python API 未传 artifact_root，只核验声明关系，不代表文件存在或哈希已核对。CLI 必须提供本地材料根目录。
- `LOCAL_ARTIFACT_BYTES`：逐个检查文件字节；完整性不等于来源真实性、物理正确性或科学审核。
- `diagnostic_input_complete` 仅指声明的输入角色覆盖，**不保证日志内容充分**。
- `actual_simulation_run_count` 保持 0，表示没有独立认证的真实运行；`declared_actual_run_count` 单独统计来源声明。不可把两者相加。
- `model_visible_artifact_refs` 是待审核的可见文件清单。不会自动创建面向其他 AI 的提示词，也不会复制材料给外部服务。
- 回执整体包含 QA 引用，供摄取器/审核者使用，不应作为模型训练输入。故障注入参数和值只能留在 QA 文件中。
- 只支持 JSON/JSONL 规范化材料；PDF/DOCX、MAT、CSV 原始数据需另行适配，不能改后缀冒充 JSON。
- 文件上限 8 MiB，批次合计 64 MiB，回执上限 1 MiB，最多 128 个材料。读取只限指定根目录，拒绝路径穿越和符号链接。
- 已实现部分隐藏标签键名检查，但无法穷尽自然语言、编码内容或未知键名中的答案泄漏；仍需人工/独立语义审核。
- `available_at` 是提供者声明；只按此声明检查时序，不独立认证日志时间，也不解析任意引擎的全部日志语义。QA 的事后分析可以晚于截止时间，但不可进入可见清单。
- 回放字段只检查声明的场景/事件族一致，**不证明回放数值相等**。
- 本地文件应在静态快照中审核；此入口不是抵御恶意并发文件替换的隔离沙箱。
- 现有 L1 仿真任务轨道、正式 SFT 序列化和训练放行未在本模块开放。运行证据入口完成不等于完整仿真到微调链路完成。

## 交给其他 AI 的执行指令

```text
请先读取本模块说明和 simulation_run_receipt.schema.json。
当前只有设计报告，没有实际测试报告、运行日志或上游 ML 结果。
保留现有设计推演轨道，不把设计声明改成已观测事件。
可以用 create_simulation_receipt_fixture.py 验证工程接口，但所有夹具保持 SYNTHETIC_TEST_ONLY。
以后收到真实材料，再在私有目录建立回执；六项状态逐项引用对应文件，不得互相推断。
运行本地校验器并返回聚合报告；不要把 QA 文件、注入标签或回执整体放入 LLM 输入。
不得声称已完成跨 AI 盲测、物理验收、Gold 审核或 SFT 放行。
```

## 包与代码的关系

独立 ZIP 只含该模块、schema、命令行工具、夹具生成器、专项测试和说明。没有用户原文、提取事实、已有训练候选或真实日志。完整 DGSI 工具包由仓库的原打包器生成；新增入口与原 L0/L1 校验并存，不替代其逻辑。
