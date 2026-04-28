# 常见问题

[返回首页](../README_zh-CN.md) | [快速开始](quick-start_zh-CN.md) | [部署指南](deployment_zh-CN.md) | [演示脚本](demo-script_zh-CN.md) | [托管操作指南](hosted-demo-operator-guide_zh-CN.md) | [English](faq.md)

---

### DecisionAtlas 解决了什么问题？

工程决策通常分散在 issues、Pull Requests、ADR 和聊天记录中。DecisionAtlas 将这些分散的上下文转化为可搜索的决策记忆。

### 我需要训练模型吗？

不需要。MVP 版本使用提供商 API，专注于数据建模、检索、审核工作流和引用机制。

### 每个提取的决策都会自动被信任吗？

不会。提取的决策以 `candidate`（候选）状态进入系统，需要人工审核后才能成为可信决策。

### 系统可以在没有证据的情况下回答吗？

设计上是不可行的。Why 查询路径采用"引用优先"机制，在没有证据时会返回 `insufficient-evidence`（证据不足）作为备选，而不是盲目猜测。

### 漂移检测目前做什么？

当前 MVP 支持：

- **基于规则的告警**：高信号矛盾的检测，例如违反"仅用 Redis 作缓存"规则。
- **语义漂移丰富**：保守的标签，如 `possible_supersession`（可能取代）和 `needs_review`（需要审核）。

它目前还不是一个持续的 Git 监控工具。它是在运行漂移评估时，将已接受的决策与工作区中后来导入的工件进行对比。

导入漂移现在已经更加可用：

- 重复的弱后续告警被更紧凑地分组。
- 重新评估会取代之前过时的告警生成。
- 重实现维护工作不太可能被过度呈现为强决策替换。

> 设计上仍然保持保守，倾向于漏报而不是夸大仓库变更。

### v0.3 RC 还缺少什么？

| 功能 | 状态 |
|------|------|
| 本地/bootstrap session、owner scope 切换和角色门禁 | 已包含在 v0.3 RC |
| GitHub App 安装绑定 | 已作为 admin/operator 设置流程包含 |
| token-backed 私有仓库访问绑定 | 已作为 admin/operator 设置流程包含 |
| 完整 SaaS 组织管理台 | 不包含 |
| secret vault 和凭据轮换 UI | 不包含 |
| GitHub Marketplace/OAuth 自助安装 | 不包含 |
| 多人协作 review workflow | 不包含 |
| billing | 不包含 |
| GitHub 和本地文档以外的机构级连接器 | 计划中 |
| 成熟的异步任务编排 | 计划中 |
| hosted preview 上线打磨 | 计划中 |

### 支持 `.docx` 吗？

支持，但是可选的。`.docx` 导入依赖本地安装的 `pandoc`。

### 如何运行验证？

```powershell
# 标准本地发布基线
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1
```

只有在调试失败阶段时，才建议单独运行子命令：

```powershell
python scripts/ci/run_benchmark.py
pnpm --filter @decisionatlas/web exec playwright install chromium
pnpm --filter @decisionatlas/web exec playwright test
```

针对运行中的托管演示环境，使用操作员检查：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\smoke-check.ps1
```

这些是托管环境检查，不替代默认发布门禁。

### 实时分析支持所有仓库吗？

不是全部支持。公共 GitHub 仓库导入仍是默认 live-analysis 路径。

v0.3 RC 也包含 admin/operator 流程，可以在当前 owner scope 内将仓库绑定到 GitHub App 安装或 token-backed 私有访问源。这些流程尚不包含完整 Marketplace/OAuth 自助安装、secret vault 或持久化多仓库连接管理。

如果仓库缺乏 ADR、文档或理由，正确的结果可能是 `insufficient_evidence`（证据不足），而不是丰富的答案集。

导入的工作区也可能会明确停留在 `review_required`、`evidence_limited` 或 `conversion_limited`。这些都是预期的有界产品结果，不是运行时故障。

### 伪/实时提供商切换改变什么？

它会改变**下一次**真实分析或提取运行所使用的提供商。**不会**重写屏幕上已有的演示数据或导入结果。

### 什么让导入的 Why 搜索可信？

导入的 Why 答案只有在以下情况下才值得信任：

1. 工作区已有**已接受的决策**。
2. 答案**锚定在一个已接受的决策**上。
3. **引用支持**该已接受的决策。

工件块可以加强支持，但**不会**取代已接受决策作为信任锚的地位。
