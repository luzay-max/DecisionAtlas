# DecisionAtlas · pallets/click 8 条候选的独立证据核查报告

> 日期：2026-10-21 · [PR #7](https://github.com/luzay-max/DecisionAtlas/pull/7) · **仅做免费公开 GitHub 证据核查；没有调用付费 AI，也没有合并 PR**。
> 评审属性：**AI 助手逐条独立核查（不是独立人类签名评审）**。人类审核门禁仍为 `not_run`；本报告可供维护者或非作者人工复核。

## 1. 数据来源与结论

- 原始样本：[GitHub Actions #39565932265](https://github.com/luzay-max/DecisionAtlas/actions/runs/39565932265) 的 `pilot-pallets-click-review-packet.json`；8 条候选全部来自 **FakeProvider**，真实 GitHub import 与假模型生成应分开理解。
- 文档重新核查使用公开仓库固定 commit [`2247b35ea1c47c727d7a06e51fa280e12a863ff6`](https://github.com/pallets/click/commit/2247b35ea1c47c727d7a06e51fa280e12a863ff6)（7 个 docs 文件在该 SHA 均可打开）；PR #2559/#2562 的合并状态通过 GitHub API 核查。
- **接受：0；拒绝：7；不确定：1。** 无可直接作为“已采纳且证据充分的工程决策”接受的候选。
- **来源 URL 可打开：8/8**，不等于引用支撑结构化结论。原审核包未导出完整 `SourceRef.quote` 和精确跨度，所以没有臆测“原文引用匹配率”。
- **0/8 达到完整的决策结构标准**（明确问题、被选择的选项、准确引用与采纳状态）。这并非真实 DeepSeek 模型的准确率，不能写成“AI 模型通过率 0%”。

## 2. 判断口径

- **接受**：候选的问题与被选择方案均具体且正确；链接证据足以核对已采纳的工程决策。即便链接可打开，没有明确决策字段也不接受。
- **拒绝**：候选只有文档主题或模板占位词，无法辨认做了何种取舍/决定。
- **不确定**：找到相符的真实决策线索，但样本字段或源 PR 采纳状态不足以直接接受；需要重建决策与证据。

## 3. 八条逐项结果

| ID | 原始候选标题 | 判定 | 原始来源 | 核查原因 |
| --- | --- | --- | --- | --- |
| 1 | `advanced` | **拒绝** | [固定版本文档](https://github.com/pallets/click/blob/2247b35ea1c47c727d7a06e51fa280e12a863ff6/docs/advanced.md) | 仅是 Advanced Patterns 使用说明；含 eager callback、validation 等范例，但候选没有具体问题或选项。 |
| 2 | `commands-and-groups` | **拒绝** | [固定版本文档](https://github.com/pallets/click/blob/2247b35ea1c47c727d7a06e51fa280e12a863ff6/docs/commands-and-groups.md) | 页面介绍 Command/Group/Context 的概念和示例；没有从源材料提取明确的采纳决定。 |
| 3 | `complex` | **拒绝** | [固定版本文档](https://github.com/pallets/click/blob/2247b35ea1c47c727d7a06e51fa280e12a863ff6/docs/complex.md) | 页面讲组合 CLI、上下文和调用约定；有设计背景但候选没有写出选定方案。 |
| 4 | `options` | **拒绝** | [固定版本文档](https://github.com/pallets/click/blob/2247b35ea1c47c727d7a06e51fa280e12a863ff6/docs/options.md) | 选项装饰器的 API 教程，包含参数名推断等规则；候选仅套用模糊占位句。 |
| 5 | `upgrade-guides` | **拒绝** | [固定版本文档](https://github.com/pallets/click/blob/2247b35ea1c47c727d7a06e51fa280e12a863ff6/docs/upgrade-guides.md) | 文档确有 9.0 迁移与弃用决策、PR #3827/#3866 等线索，但候选未指出具体弃用对象、变更原因或替代方案。 |
| 6 | `Fix decorator typing with _Decorator type alias` | **不确定** | [PR #2559](https://github.com/pallets/click/pull/2559) | 标题指向真实的类型兼容问题。PR #2559 建议将 _Decorator[FC] 替换为 Callable[[FC], FC]，但原 PR 关闭未合并；维护者说明替代 PR #2562 更全面，#2562 已合并。候选仍没有实际问题/选项，且引用到未合并 PR，须重建证据链后重审。 |
| 7 | `commands` | **拒绝** | [固定版本文档](https://github.com/pallets/click/blob/2247b35ea1c47c727d7a06e51fa280e12a863ff6/docs/commands.md) | Advanced Groups and Context 文档主要说明 group callbacks 和 context 等用法；并非已经提取的具体工程决策。 |
| 8 | `parameter-types` | **拒绝** | [固定版本文档](https://github.com/pallets/click/blob/2247b35ea1c47c727d7a06e51fa280e12a863ff6/docs/parameter-types.md) | 页面介绍 Choice、数字范围等内置参数类型，候选没有选择、否决选项或决策理由。 |

## 4. 必须重视的第 6 条

- [PR #2559](https://github.com/pallets/click/pull/2559) 提出的技术问题确实具体：`mypy` 对 `_Decorator[FC]` 的推断有问题，而 `Callable[[FC], FC]` 可避免这一问题。
- **PR #2559 已关闭但未合并**。维护者和作者在 [该 PR 的讨论](https://github.com/pallets/click/pull/2559) 中指出 [PR #2562](https://github.com/pallets/click/pull/2562) 提供了更全面的相同修复。
- **PR #2562 已合并（2023-07-13）**，代码修改包含将 `_Decorator[FC]` 改为 `Callable[[FC], FC]` 并新增类型测试。
- 所以可以**重建一条真实工程决策**，但不能把 #2559 当作已合并证据，也不能接受原始占位的 `problem/chosen_option` 字段。本条标记“不确定，待重提取”。

## 5. 数据质量根因

- [FakeProvider 实现](https://github.com/luzay-max/DecisionAtlas/blob/fix/security-bootstrap-webhook-import-20261021/services/engine/app/llm/fake_provider.py) 直接赋值：`problem = "Recovered from artifact content"`、`chosen_option = "Use the option described in the artifact"`；另外 `tradeoffs` 也是固定的占位模板。
- 这说明本次“真实仓库 + FakeProvider”的链路测试能证明数据采集、任务运行、候选写入和引用连通，但**不能证明模型成功理解源文档**。
- 候选标题多为文档文件名，且没有从明确的 PR/ADR 里抽取真实选择。因此不应把导出的 8 条算作 8 条工程知识资产。

## 6. 结论与下一步

1. 本轮 AI 辅助独立核查：**0 接受 / 7 拒绝 / 1 不确定**；需由真正的非作者人类复核后，才能进入执行计划中的人类评分门禁。
2. 保留 #2559 → #2562 为后续真实模型试验的**正样本与反例**：必须正确区分未合并提案和已采纳实现。
3. 继续使用预注册的 `pallets/click` PR #3877、#3884 验证真实提取；尚**没有付费 DeepSeek 调用**，也没有 Why Search/Drift 的人工成绩。
4. 先改进审核的观测口径：把是否有链接、链接是否证明“方案被采纳”、提取内容是否是占位词分别计数。不要因此扩展新产品功能。

---

证据快照：`pallets/click@2247b35ea1c47c727d7a06e51fa280e12a863ff6` · DecisionAtlas GitHub Actions Artifact `decisionatlas-pallets-click-public-import-20`。
