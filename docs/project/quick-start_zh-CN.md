# 快速开始

[返回首页](../README_zh-CN.md) | [部署指南](deployment_zh-CN.md) | [常见问题](faq_zh-CN.md) | [演示脚本](demo-script_zh-CN.md) | [English](quick-start.md)

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
# 1. 启动基础设施
docker compose up -d postgres redis

# 2. 初始化数据库
cd services/engine
uv run alembic upgrade head
uv run python -m app.db.seed_demo
cd ..\..

# 3. 启动服务
# 终端 1: Engine
cd services/engine
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# 终端 2: API
pnpm --filter @decisionatlas/api dev

# 终端 3: Web
pnpm --filter @decisionatlas/web dev
```

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
| 实时分析失败 | 目前仅支持**公共 GitHub 仓库**。私有仓库和 GitHub App 流程不在范围内。 |
| Docker 服务不可用 | 重试 `docker compose up -d postgres redis` |
| `.docx` 导入被跳过 | 确认 `pandoc` 已安装并在终端中可用。 |
