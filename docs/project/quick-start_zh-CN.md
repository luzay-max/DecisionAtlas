# 快速开始

[返回首页](../README_zh-CN.md) | [部署指南](deployment_zh-CN.md) | [常见问题](faq_zh-CN.md) | [演示脚本](demo-script_zh-CN.md) | [托管操作指南](hosted-demo-operator-guide_zh-CN.md) | [Hosted Preview Readiness](hosted-preview-readiness_zh-CN.md) | [English](quick-start.md)

---

本项目针对单台机器上的本地开发进行了优化。

### 前置条件

- `pnpm`
- Python `3.11+`
- Docker Desktop
- `pandoc`（可选，用于 `.docx` 导入）

### 安装

在仓库根目录执行：

```powershell
pnpm install
uv sync --project services/engine
Copy-Item .env.example .env
```

### 快速演示（最快路径）

一条命令启动基于 SQLite 的隔离演示：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-demo-stack.ps1
```

该脚本在 `.tmp/` 下启动一个精选的演示工作区，与本地 PostgreSQL 容器状态隔离。

### 全栈环境设置

需要与 PostgreSQL 和 Redis 一起运行的部署式环境：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-real-stack.ps1
```

该命令会启动 PostgreSQL 和 Redis、运行迁移、执行非破坏性 demo workspace setup、检查 seeded demo readiness、启动 engine/API/web，并为浏览器会话启用本地 bootstrap session 恢复。如果现有 `demo-workspace` 已被前一次 walkthrough 消耗，请在启动前显式恢复：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-real-stack.ps1 -ResetSeededDemo
```

停止命令：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\stop-real-stack.ps1
```

`pnpm run dev:real` 和 `pnpm run dev:real:stop` 会调用同一组脚本，仍然是有效快捷方式。

只有在调试某一层服务时，才建议手动拆开运行服务命令。

### v0.3 平台流程

v0.3 release-candidate 基线包含本地/bootstrap 登录恢复、owner scope 切换、admin/reviewer 角色门禁、GitHub App 安装绑定，以及 token-backed 私有仓库访问绑定。

这些是 operator/admin 设置流程，不是完整 SaaS 管理台。GitHub Marketplace/OAuth 自助安装、secret vault、billing 和多人协作 review workflow 仍不在范围内。

### 阶段 7 后治理流程

当前 post-stage-7 基线包含本地 AI-agent 治理护栏。它会聚合当前 diff checker 和长期 drift detector，输出 advisory 状态：

- `continue`：未发现阻断级治理问题。
- `caution`：声明完成前应先处理推荐动作。
- `pause`：停止并请求人工审核，不应静默改代码、specs 或 accepted rules。

提交或归档 OpenSpec change 前运行：

```powershell
python scripts\governance\agent_guardrail.py --summary
```

当 AI agent 或 reviewer 需要完整机器可读 JSON 时，使用 `--pretty`。

### 重复仓库分析

当你输入的仓库在当前 owner scope 中已经有 imported workspace 时，live-analysis 表单应先展示三个明确选择，而不是直接启动新任务：

- **打开已有工作区**：用于查看当前结果、检查最近导入摘要，或继续 review / why / drift。
- **自上次导入后同步**：用于仓库已有新变更，但不希望把这次运行当成完整重新分析。
- **重新完整分析**：用于你明确想从仓库基线重新构建导入结果。

如果该工作区已经有排队中或运行中的导入任务，请打开现有 workspace/job 进度，不要再启动重复运行。

### 实时大模型提供商模式

修改 `.env` 以连接真实的大模型提供商：

```env
LLM_PROVIDER_MODE=openai_compatible
LLM_API_KEY=your_api_key
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
# 可选配置
EMBEDDING_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
```

### 验证服务

检查健康端点：

```powershell
Invoke-WebRequest http://localhost:3001/health
Invoke-WebRequest http://localhost:8000/health
```

如需针对运行中的托管或本地演示环境做操作员检查：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\smoke-check.ps1
python scripts\demo\check_seeded_demo.py
```

外部 hosted walkthrough 前，请使用 [Hosted Preview Readiness](hosted-preview-readiness_zh-CN.md) 记录 health、smoke、reset/reseed recovery 状态和 known limitations。这些 hosted 检查是 post-RC confidence layer，不替代标准 release gate。

如需进行 release-style 验证，请在仓库根目录运行标准本地门禁：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1
```

当前治理相关验证还应运行：

```powershell
openspec validate --all --strict
python scripts\governance\agent_guardrail.py --summary
cd services/engine
.\.venv\Scripts\python.exe -m pytest tests/governance/test_diff_checker.py tests/governance/test_drift_detector.py tests/governance/test_agent_guardrail.py -q
.\.venv\Scripts\python.exe -m pytest tests/db/test_migrations.py tests/db/test_schema.py -q
```

打开 Web 应用：

- Web UI: `http://localhost:3000`
- 演示工作区: `http://localhost:3000/workspaces/demo-workspace`
- 审核: `http://localhost:3000/review`
- 搜索: `http://localhost:3000/search`
- 漂移检测: `http://localhost:3000/drift`

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| `uv` 不在 PATH 中 | 改用 `python -m uv ...`。预发布脚本会自动处理此问题。 |
| 导入成功但无候选项 | 确认 `LLM_PROVIDER_MODE`、`LLM_API_KEY`、`LLM_MODEL` 和 `EMBEDDING_MODEL` 已正确设置。 |
| 实时分析失败 | 公共仓库导入仍是默认路径。admin/operator 设置流程可以为 owner-scoped workspace 绑定 GitHub App 安装或 token-backed 私有仓库访问。 |
| 同一仓库已存在 | 打开已有工作区查看当前结果；仓库有新增变更时使用增量同步；只有明确需要重建时才选择完整重新分析。 |
| 导入任务已在运行 | 进入已有 workspace/job 进度，等待排队中或运行中的导入结束后，再启动新的同步或重跑。 |
| Docker 服务不可用 | 重试 `docker compose up -d postgres redis` |
| Real stack migration 报 `value too long for type character varying(32)` | 确认代码已包含缩短后的 Alembic revision `0008_governance_ingest`；运行 `tests/db/test_migrations.py` 防止未来 revision ID 超过 32 字符。 |
| `.docx` 导入被跳过 | 确认 `pandoc` 已安装并在终端中可用。 |
| 托管演示状态漂移 | 先运行 `python scripts\demo\check_seeded_demo.py`；review/demo 状态被消耗时运行 `scripts\demo\reset-demo.ps1`，迁移或数据库漂移需要更深重建时运行 `reseed-demo.ps1`。 |
