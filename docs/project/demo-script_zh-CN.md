# 演示脚本

[返回首页](../README_zh-CN.md) | [快速开始](quick-start_zh-CN.md) | [部署指南](deployment_zh-CN.md) | [常见问题](faq_zh-CN.md) | [English](demo-script.md)

---

本演示脚本设计用于 **60-90 秒的产品演示**。主要故事线是稳定的引导式演示车道，最后有一个可选的真实仓库可信度检查。

### 开场白

**访问路径**: `http://localhost:3000/`

**话术**:
> "今晚的主要路径是引导式演示。它使用预设的演练数据，使产品故事保持稳定。"
> "实时分析和提供商控制仍然存在，但被有意移到了高级部分。"

### 步骤 1：打开引导式演示工作区

**访问路径**: `http://localhost:3000/workspaces/demo-workspace`

**话术**:
> "仪表盘现在是演练控制面板。它告诉我们当前处于哪个步骤以及下一步该做什么。"
> "来源横幅明确表示这是预设的演示数据，而非导入的仓库输出。"

### 步骤 2：运行或确认演示导入

**访问路径**: `http://localhost:3000/workspaces/demo-workspace`

**话术**:
> "如果需要重置演示，导入操作现在会显示阶段感知的进度。"
> "一旦工作区准备就绪，UI 会直接指向审核步骤。"

### 步骤 3：展示审核队列

**访问路径**: `http://localhost:3000/review?workspace=demo-workspace`

**话术**:
> "候选决策不会被自动提升。审核步骤使人工检查点变得明确。"
> "页面解释了这一步的目标，完成后直接进入 why-search。"

### 步骤 4：展示 Why-Search

**访问路径**: `http://localhost:3000/search?workspace=demo-workspace`

**建议问题**: `why use redis cache`（为什么使用 Redis 缓存）

**话术**:
> "Why-search 从推荐的演示问题开始，因此我们不需要在演示过程中临时构思。"
> "当证据存在时，答案包含引用。当不存在时，系统会保守地返回失败，而不是猜测。"

### 步骤 5：展示时间线

**访问路径**: `http://localhost:3000/timeline?workspace=demo-workspace`

**话术**:
> "已接受的决策成为时间有序的记忆，而不是消失在 issues 和 Pull Requests 中。"
> "引导式演示框架保持故事推进，并明确指向漂移步骤。"

### 步骤 6：展示漂移告警并结束

**访问路径**: `http://localhost:3000/drift?workspace=demo-workspace`

**话术**:
> "漂移通过将较新的工件与已接受的决策进行对比，使记忆变得可操作。"
> "最后一步闭合循环，使我们明显完成了演示车道，而非实验性分析流程。"

### 结束语

> "DecisionAtlas 没有在训练新模型。它正在将工程决策转化为持久的、可审核的、可搜索的操作记忆。"

### 可选：30 秒真实仓库证明

这是**操作员引导的可信度检查**，不属于核心引导式演练。

**访问路径**: `http://localhost:3000/`

**话术**:
> "预设车道是我们的稳定演练路径，但相同的产品也可以将真实的公共 GitHub 仓库分析到单独导入的工作区中。"
> "该导入工作区现在会显示审核、why-search 和漂移是否已就绪，而不是让操作员猜测下一步。"
> "导入的 why 答案锚定在已接受的决策上，工件块作为支持证据而非取代信任锚。"
> "我们将其作为真实能力的有界证明，而非主要演示故事。"

---

### 快速参考

| 步骤 | 路径 | 关键点 |
|------|------|--------|
| 1 | `/workspaces/demo-workspace` | 演练控制面板 |
| 2 | `/workspaces/demo-workspace` | 阶段感知导入进度 |
| 3 | `/review?workspace=demo-workspace` | 人工检查点 |
| 4 | `/search?workspace=demo-workspace` | 引用优先的回答 |
| 5 | `/timeline?workspace=demo-workspace` | 时间有序的决策记忆 |
| 6 | `/drift?workspace=demo-workspace` | 可操作的漂移检测 |
