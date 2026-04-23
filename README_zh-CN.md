# DecisionAtlas

[English](README.md) | [中文](README_zh-CN.md)

**DecisionAtlas** 将工程仓库上下文转化为带有引用和漂移告警的可搜索决策记忆。它能够自动分析 GitHub issues、Pull Requests 和提交记录，从中提取出关键的架构和设计决策，使其可搜索且可验证。

## 🌟 核心特性

- **自动化知识提取**：导入 GitHub issues、PRs、commits、markdown、ADR 和纯文本笔记，从中提取候选决策。
- **引用优先搜索**：通过“引用优先”的回答机制、支持度评级以及基于代码块的证据支撑，精准回答“为什么”这类问题。
- **漂移检测**：通过保守的导入漂移语义，在人工评估后标记出基于规则和语义的漂移告警。
- **人工审核循环**：允许审核者接受、拒绝或取代提取出的决策。
- **实时仓库分析**：通过导入的工作区，支持对公共 GitHub 仓库进行一次性实时分析，并支持增量同步。
- **灵活的模型提供商支持**：支持使用伪提供商（Fake Provider）的本地模式，或兼容 OpenAI 的实时 LLM 模式。

## 🏗 架构

平台主要由以下三个核心组件构成：

- `apps/web`: 基于 Next.js 的前端 UI，用于审核、搜索、时间线、仪表盘和漂移检测。
- `apps/api`: Fastify 边缘 API，以及未来的身份验证边界。
- `services/engine`: FastAPI 引擎，负责数据摄取、提取、检索和漂移计算。
- **数据层**：`PostgreSQL + pgvector` 用于持久化存储和向量搜索，`Redis` 用于后台任务协调。

## 🚀 快速开始

### 前置条件
- Node.js (v18+) & pnpm
- Python (v3.10+) & uv
- Docker Desktop (用于 PostgreSQL & Redis)

### 单命令本地启动

体验该产品最快的方式是在本地使用隔离的、基于 SQLite 的演示工作区：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-demo-stack.ps1
```

### 全栈环境设置

要运行包含 PostgreSQL 和 Redis 的真实技术栈：

```powershell
# 安装依赖
pnpm install
uv sync --project services/engine

# 设置环境变量
Copy-Item .env.example .env

# 启动基础设施
docker compose up -d postgres redis

# 运行数据库迁移并填充演示数据
cd services/engine
uv run alembic upgrade head
uv run python -m app.db.seed_demo
cd ..\..

# 启动应用服务
pnpm run dev:real
```

然后在浏览器中打开：
- Web UI: `http://localhost:3000`
- API 运行状况: `http://localhost:3001/health`
- Engine 运行状况: `http://localhost:8000/health`

## 💡 示例查询

项目运行后，您可以尝试询问以下问题：
- *为什么我们只将 Redis 用作缓存？ (Why did we choose Redis as cache only?)*
- *为什么 PostgreSQL 仍然是主要数据库？ (Why is PostgreSQL still the primary database?)*
- *为什么我们将这个工作流移到了队列中？ (Why did we move this workflow into a queue?)*

## ⚙️ 配置 (实时大模型提供商)

对于需要连接真实大模型提供商的演示，请在 `.env` 文件中配置以下变量：

```env
LLM_PROVIDER_MODE=openai_compatible
LLM_API_KEY=your_api_key
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
# 可选配置
EMBEDDING_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
```

## 📚 文档

- [快速开始](./docs/project/quick-start.md)
- [部署指南](./docs/project/deployment.md)
- [常见问题 (FAQ)](./docs/project/faq.md)
- [架构与规划](./docs/plans/2026-03-18-decisionatlas-project-blueprint.md)
- [真实仓库验证](./docs/project/real-repository-validation-baseline.md)

## ⚠️ 已知限制

- MVP 阶段尚未实现身份验证和多用户权限。
- 语义漂移标签较为保守，被刻意限制在较窄的范围内。
- 实时分析目前仅支持公共 GitHub 仓库（通过 Token 模式，暂不支持 GitHub App 认证）。
- 取决于仓库的信号质量，导入的工作区可能仍然会比较稀疏。

---
*当前项目阶段：核心 MVP & `v0.2` 演示版本强化已完成。*
