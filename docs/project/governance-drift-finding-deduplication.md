# Governance Drift Finding Deduplication

## 目标

治理漂移报告应让管理员看到可执行问题，而不是大量标题相同但来源含义不清的卡片。本能力在 detector 边界先过滤误报，再对真正等价的信号做规范化合并，所有 API、guardrail、dashboard 和 evidence 消费同一结果。

## 工作方式

1. 历史问题候选必须是明确的问题标签或强失败词。
2. 否定句、普通策略说明和单词内部子串不进入 repeated issue 候选。
3. 历史问题与当前上下文至少有三个有效词重合，且覆盖率达到 60%。
4. repeated_postmortem_issue 按规范化问题词集合生成语义键。
5. 同组信号选择稳定代表，合并唯一 evidence，最多序列化 12 条。
6. occurrence_count 表示完整出现次数；source_count 表示完整唯一来源数。
7. 不同语义问题继续分开，不因标题相同而合并。

## 兼容性

- occurrence_count 和 source_count 是新增字段，默认值均为 1。
- 旧客户端可以忽略新增字段。
- 页面仅在 occurrence_count 大于 1 时显示 recurrence 标签。
- 去重不会修改治理文档、规则生命周期或人工 disposition。
- 整体治理策略继续保持 advisory。

## 真实结果

在当前 DecisionAtlas 工作树中，旧逻辑输出 28 条 repeated issue。修复候选识别后保留 3 条不同语义的问题，噪声下降 89.3%。

临时 recurrence rehearsal 使用两份表达相同问题但语序不同的历史日志，API 返回 1 条 canonical signal、2 次 occurrence、3 个来源。Chrome 页面显示“重复 2 次 · 3 个来源”，并可通过治理操作链接进入 Governance 页面。

临时日志已删除；正常仓库没有合成数据残留。

## 验证

- engine 完整测试：383 passed
- governance 聚焦测试：36 passed
- monorepo Vitest：2 packages passed；web 83 passed
- lint/typecheck：passed
- OpenSpec strict：86/86
- Chrome + DOM-CUA：passed，console error/warning 0
- evidence：docs/evidence/readiness/2026-07-13-governance-drift-finding-deduplication
