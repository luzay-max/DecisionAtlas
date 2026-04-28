# 快速开始

[返回首页](../README_zh-CN.md) | [部署指南](deployment_zh-CN.md) | [常见问题](faq_zh-CN.md) | [演示脚本](demo-script_zh-CN.md) | [托管操作指南](hosted-demo-operator-guide_zh-CN.md) | [English](quick-start.md)

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
pnpm run dev:real
```

该命令会启动 PostgreSQL 和 Redis、运行迁移、seed 演示数据、启动 engine/API/web，并为浏览器会话启用本地 bootstrap session 恢复。停止命令：

```powershell
pnpm run dev:real:stop
```

只有在调试某一层服务时，才建议手动拆开运行服务命令。

### v0.3 平台流程

v0.3 release-candidate 基线包含本地/bootstrap 登录恢复、owner scope 切换、admin/reviewer 角色门禁、GitHub App 安装绑定，以及 token-backed 私有仓库访问绑定。

这些是 operator/admin 设置流程，不是完整 SaaS 管理台。GitHub Marketplace/OAuth 自助安装、secret vault、billing 和多人协作 review workflow 仍不在范围内。

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
```

如需进行 release-style 验证，请在仓库根目录运行标准本地门禁：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1
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
| Docker 服务不可用 | 重试 `docker compose up -d postgres redis` |
| `.docx` 导入被跳过 | 确认 `pandoc` 已安装并在终端中可用。 |
| 托管演示状态漂移 | 对 `demo-workspace` 运行 `scripts\demo\reset-demo.ps1`；当迁移或数据库漂移需要更深重建时使用 `reseed-demo.ps1`。 |
