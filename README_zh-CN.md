# DecisionAtlas

[English](README.md) | [中文](README_zh-CN.md)

**DecisionAtlas** 将工程仓库上下文转化为带有引用、漂移告警和 AI 可读取治理护栏的可搜索决策记忆。它会分析仓库工件，提取候选工程决策，让人类确认可沉淀的决策，并帮助 AI agent 检查新的代码变更是否仍符合项目方向。

## 🌟 核心特性

- **自动化知识提取**：导入 GitHub issues、PRs、commits、markdown、ADR 和纯文本笔记，从中提取候选决策。
- **引用优先搜索**：通过“引用优先”的回答机制、支持度评级以及基于代码块的证据支撑，精准回答“为什么”这类问题。
- **漂移检测**：通过保守的导入漂移语义，在人工评估后标记出基于规则和语义的漂移告警。
- **人工审核循环**：允许审核者接受、拒绝或取代提取出的决策。
- **实时仓库分析**：通过导入的工作区，支持对公共 GitHub 仓库进行一次性实时分析，并支持增量同步。
- **Owner Scope 产品流程**：支持本地/bootstrap 登录、owner scope 切换、基于角色的工作区操作、GitHub App 安装绑定和私有仓库访问绑定。
- **治理知识层**：导入 Markdown 形式的开发标准、路线图、复盘、检查清单和人工决策，并转化为可审核的治理规则草稿。
- **AI Agent 协议级 CLI 接口**：规范化 `scripts/governance/agent_guardrail.py` 命令行工具，支持 `--agent` 参数，返回结构化的 JSON 数据负载和精确的状态码（`0` 继续，`5` 警告，`10` 拦截暂停），以便外部 AI 编程助手（如 Cursor、Antigravity）完美集成。
- **极致视觉美学与双色主题切换**：支持炫酷的暗黑霓虹与 **"Crystal Aurora"（水晶极光）** 清透毛玻璃浅色模式。全面适配 SVG **决策网络拓扑图 (DecisionTopologyMap)** 与 **AI 治理看板 (GuardrailPauseBanner)** 等核心视觉元素，将主视界扩容至 **`1160px`** 宽屏布局，为大屏幕带来极佳的视觉呼吸感。
- **AI Agent 治理护栏**：聚合当前 diff 检查和长期治理漂移报告，输出面向 AI 开发流程的 advisory `continue`、`caution` 或 `pause` 结果。
- **灵活的模型提供商支持**：支持使用伪提供商（Fake Provider）的本地模式，或兼容 OpenAI 的实时 LLM 模式。

## 🏗 架构

平台主要由以下三个核心组件构成：

- `apps/web`: 基于 Next.js 的前端 UI，用于审核、搜索、时间线、仪表盘和漂移检测。
- `apps/api`: Fastify 边缘 API、session 恢复和 owner-scoped auth 边界。
- `services/engine`: FastAPI 引擎，负责数据摄取、提取、检索、漂移计算和治理检查。
- `scripts/governance`: 本地治理检查、漂移报告和 AI-agent guardrail 入口。
- **数据层**：`PostgreSQL + pgvector` 用于持久化存储和向量搜索，`Redis` 用于后台任务协调。

## 🚀 快速开始

### 前置条件
- Node.js (v18+) & pnpm
- Python (v3.10+) & uv
- Docker Desktop (用于 PostgreSQL & Redis)

### 单命令 Demo Stack

体验该产品最快的方式是在本地使用隔离的、基于 SQLite 的演示工作区：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-demo-stack.ps1
```

### 单命令 Real Stack

推荐的完整本地真实栈包含 Docker PostgreSQL、Redis、FastAPI Engine、Fastify API 和 Next.js Web：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-real-stack.ps1
```

停止真实栈：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\stop-real-stack.ps1
```

该脚本会先停止已有受管服务，再启动 PostgreSQL/Redis、执行 migrations、seed demo 数据，并启动三端服务。

### 手动全栈启动

只有在调试单个服务时才建议使用手动流程：

```powershell
pnpm install
uv sync --project services/engine
Copy-Item .env.example .env
docker compose up -d postgres redis

cd services/engine
$env:DATABASE_URL = "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/decisionatlas"
uv run alembic upgrade head
uv run python -m app.db.seed_demo
cd ..\..

pnpm run dev:real
```

然后在浏览器中打开：
- Web UI: `http://localhost:3000`
- API 运行状况: `http://localhost:3001/health`
- Engine 运行状况: `http://localhost:8000/health`

## ✅ 验证流程

在归档 OpenSpec change 或准备 release snapshot 前，建议运行：

```powershell
openspec validate --all --strict
python scripts\governance\agent_guardrail.py --summary
python scripts\governance\agent_guardrail.py --protocol-status --summary
pnpm --filter @decisionatlas/web exec playwright test
```

Engine 侧重点验证：

```powershell
cd services/engine
.\.venv\Scripts\python.exe -m pytest tests/governance/test_diff_checker.py tests/governance/test_drift_detector.py tests/governance/test_agent_guardrail.py -q
.\.venv\Scripts\python.exe -m pytest tests/db/test_migrations.py tests/db/test_schema.py -q
```

治理 guardrail 默认是 advisory：

- `continue`：未发现阻断级治理问题。
- `caution`：存在建议处理的风险，完成推荐动作后再声明完成。
- `pause`：必须暂停并请求人工审核，不应静默改代码、specs 或 accepted rules。

默认本地治理开发协议使用：

```powershell
python scripts\governance\agent_guardrail.py --protocol-status --summary
```

在非平凡实现前、targeted validation 后、归档 OpenSpec change 前以及提交完成工作前运行。它会报告 active OpenSpec context、guardrail status、required tests、recommended actions、human questions 和 handoff guidance。该协议仍是 advisory，独立于可选 enforcement preview 和 canonical release gate。

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

## 🧭 OpenSpec 开发流程

DecisionAtlas 使用 OpenSpec 管理有边界的变更。推荐流程：

1. 创建 change，包含 proposal、design、specs 和 tasks。
2. 运行 governance preflight：`python scripts\governance\agent_guardrail.py --protocol-status --summary`。
3. 按 tasks 增量实现。
4. 运行 targeted tests 和 `openspec validate --all --strict`。
5. 运行 governance postflight：`python scripts\governance\agent_guardrail.py --protocol-status --summary`。
6. 将 delta specs 同步到 main specs。
7. 将完成的 change 归档到 `openspec/changes/archive/`。
8. 将代码、specs、归档和文档一起提交，并在 handoff 中记录任何 `caution` 或 `pause` 证据。

当前阶段 7 后的规划记录在：

- [阶段 7 后总开发计划](./docs/plans/2026-05-06-decisionatlas-post-stage-7-master-plan.md)
- [2026-05-06 更新日志](./docs/project/2026-05-06-update-log.md)

## 📚 文档

- [快速开始](./docs/project/quick-start_zh-CN.md)
- [部署指南](./docs/project/deployment_zh-CN.md)
- [常见问题 (FAQ)](./docs/project/faq_zh-CN.md)
- [演示脚本](./docs/project/demo-script_zh-CN.md)
- [Hosted Preview Readiness](./docs/project/hosted-preview-readiness_zh-CN.md)
- [v0.3.0-rc.1 发布说明](./docs/project/release-notes-v0.3.0-rc.1_zh-CN.md)
- [Governance Markdown Ingest](./docs/project/governance-markdown-ingest-mvp.md)
- [Governance Diff Checker](./docs/project/governance-diff-checker.md)
- [Governance Drift Detection](./docs/project/governance-drift-detection.md)
- [AI Agent Governance Guardrail](./docs/project/governance-agent-guardrail.md)
- [架构与规划](./docs/plans/2026-03-18-decisionatlas-project-blueprint.md)
- [当前总计划](./docs/plans/2026-04-29-decisionatlas-next-master-plan.md)
- [真实仓库验证](./docs/project/real-repository-validation-baseline.md)

## ⚠️ 已知限制

- v0.3 RC 已包含本地/bootstrap session 恢复、owner scope 切换和基于角色的产品操作，但还不是完整 SaaS 组织管理台。
- GitHub App 安装绑定和 token-backed 私有仓库访问绑定是 admin/operator 流程；尚不包含完整 GitHub Marketplace/OAuth 自助安装和 secret vault。
- 暂不包含多人协作 review workflow 和 billing。
- 语义漂移标签较为保守，被刻意限制在较窄的范围内。
- 取决于仓库的信号质量，导入的工作区可能仍然会比较稀疏。
- 治理 guardrail 默认是 advisory，不会阻断 CI，除非未来有明确 change 启用该模式。
- Demo review queue 可能被之前的运行消费；下一阶段计划补稳定的 demo reset/reseed 流程。

---
*当前项目阶段：Post Stage 7 - AI-agent 治理护栏已实现；下一步聚焦治理流程硬化、demo reset 可靠性和真实仓库价值度量。*
