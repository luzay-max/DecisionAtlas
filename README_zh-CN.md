# DecisionAtlas · 工程决策记忆与 AI 治理平台

**让工程决策可追溯，让 AI 编程更了解项目的技术方向。**

DecisionAtlas 可以将分散在 **GitHub Issues、Pull Requests、Commits、ADR 和工程文档**中的信息，整理成**可搜索、可追溯且经过人工审核的工程决策记忆**。团队可以查询“当初为什么这样设计”，检查代码是否偏离既有架构决策，并为 AI 编程助手提供有依据的治理建议。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Self-hosted](https://img.shields.io/badge/Deployment-Self--hosted-2b6cb0)](docs/project/deployment_zh-CN.md)
[![AI Agent Guardrails](https://img.shields.io/badge/AI%20Agents-Governance%20Guardrails-6554c0)](docs/project/governance-agent-guardrail.md)

[English](README.md) · **简体中文** · [快速开始](docs/project/quick-start_zh-CN.md) · [项目架构](docs/plans/2026-03-18-decisionatlas-project-blueprint.md) · [完整文档](#-文档)

> **项目现状：** 持续开发中的本地优先 / 可自托管平台，目前具有 v0.3 RC 阶段的能力基础。AI 治理检查默认是**建议性（advisory）**的；项目目前还不是完整的多租户 SaaS 服务。
>
> **当前主分支：** [CI #227](https://github.com/luzay-max/DecisionAtlas/actions/runs/39913146099) 已通过，[PR #17（只读 MCP）](https://github.com/luzay-max/DecisionAtlas/pull/17)和 [PR #18（历史计划归档）](https://github.com/luzay-max/DecisionAtlas/pull/18)均已合并。MCP 目前是**可选的实验性适配器**，还不是经过真实 Agent 验收的生产集成。详见[归档索引](docs/plans/archive/2026-10-21-reviewed-plan-index.md)。

## 📸 真实运行截图

以下截图由 [主分支 `93bbacd` 的 GitHub Actions](https://github.com/luzay-max/DecisionAtlas/actions/runs/39728035244) 使用 Playwright 启动真实演示栈自动生成，**不是 AI 设计效果图**。

| 首页 · 深色模式 | 候选决策审核 |
| --- | --- |
| ![DecisionAtlas 中文首页真实浏览器截图](docs/assets/screenshots/01-home-desktop-dark-zh.png) | ![DecisionAtlas 候选决策审核真实浏览器截图](docs/assets/screenshots/03-review-desktop-dark-zh.png) |

**[查看全部 8 张真实截图](docs/project/ui-screenshots.md)**：桌面深浅色、工作区、原因检索、手机首页 / 工作区 / 审核。图片保存在 GitHub 仓库内，可长期查看。截图基线与最新主分支测试分开记录：[截图基线 CI](https://github.com/luzay-max/DecisionAtlas/actions/runs/39728035244) · [主分支最新已验证 CI #227](https://github.com/luzay-max/DecisionAtlas/actions/runs/39913146099)。

> 截图使用**预置演示数据与 Fake Provider**，证明真实浏览器的界面与交互可运行，不代表真实仓库 AI 提取质量或生产环境已经完成验收。


## 🎯 为什么需要 DecisionAtlas？

开发者通常可以在 Git 中找到“改了什么”，却难以快速知道“**为什么这么改**”。理由可能散落在 PR 讨论、Issue、ADR 或 Markdown 规范里。AI 编程助手也面临相同的问题，容易在不了解历史决策的情况下提出与原定架构相冲突的修改。

DecisionAtlas 希望在历史代码和新变更之间，建立一层**可审核的工程决策知识层**：

- **记住决策依据**：记录工程决策，并保留对应的原始证据。
- **解释设计原因**：通过引用优先的搜索回答“为什么这样设计”。
- **发现技术漂移**：识别代码或方案与既定决策之间的潜在偏差。
- **辅助 AI 编程**：输出 `continue`、`caution`、`pause` 等结构化建议，保留人工审核环节。

## ✨ 核心能力

| 能力 | 作用 |
| --- | --- |
| **仓库知识摄取** | 导入 GitHub Issues、PR、Commit、Markdown、ADR 和工程笔记，支持增量同步。 |
| **决策提取和审核** | 提取候选决策，并由人工接受、拒绝或替代；候选决策不会自动变成可信规则。 |
| **有引用的智能搜索** | 查询项目的技术决策背景，并查看支撑结论的来源。 |
| **架构 / 治理漂移检测** | 通过规则和语义信号提示潜在偏差，采用保守的告警策略。 |
| **AI Agent 治理护栏** | 对代码变更执行治理检查，输出机器可读取的 JSON、状态和退出码。 |
| **可选只读 MCP 适配器（实验性）** | 通过 4 个 MCP 工具读取单个授权工作区的已人工接受决策及引用证据；不承担自动编码或仓库导入。 |
| **多工作区与权限边界** | 支持本地登录、Owner Scope、角色操作，以及管理员操作的 GitHub App / 私有仓库绑定。 |
| **可视化工作台** | 提供决策审核、搜索、时间线、仪表盘、拓扑图和漂移视图，支持深浅色主题。 |
| **灵活模型接入** | 可用 Fake Provider 进行本地演示，也可配置兼容 OpenAI 的模型提供商。 |

## 🔌 可选只读 MCP（实验性）

[PR #17](https://github.com/luzay-max/DecisionAtlas/pull/17) 已合并进 `main`。这个基于 **MCP Python SDK v2 stdio** 的可选适配器复用 DecisionAtlas **现有的已认证 Engine API**，不另建一套仓库索引。它提供 4 个**只读**工具：

- `project_status`：查看指定工作区中已接受决策的数量与状态。
- `list_project_decisions`：列出经人工审核并接受的决策。
- `search_project_decisions`：对已接受决策做**基础关键词检索**（不是语义搜索）。
- `get_decision_evidence`：查询当前授权工作区内已接受决策的引用证据。

操作人员必须提供有效的 DecisionAtlas 会话及**一个已授权 Workspace**，适配器仅能访问本机环回地址上的 Engine API。它**不能**自动识别 Agent 当前 Git 仓库、导入仓库、通过候选审核或修改代码。**官方 SDK v2 的进程内工具发现和调用测试已在 CI 通过，但真实 stdio Agent 宿主联调、企业安全放行和决策质量验证仍未完成。** 候选决策仍须由人工审核，才能作为已接受决策使用。

启动前提和可选本地运行示例参见：[MCP 只读适配器说明](docs/project/mcp-readonly-spike.md)。

## 🔄 工作原理

```mermaid
flowchart LR
    A["GitHub Issues / PR / Commit<br/>ADR / Markdown"] --> B["证据导入与决策提取"]
    B --> C["候选工程决策"]
    C --> D["人工审核"]
    D --> E["已接受的决策记忆"]
    E --> F["带来源引用的搜索 / 为什么查询"]
    E --> G["漂移检测与 Agent 治理"]
    G --> H["continue / caution / pause"]
```

**项目不会把自动提取的结果直接当成权威规则。** 候选决策仍需人工审核；AI Agent 治理默认提供建议，不会自行改写项目代码或强制阻断 CI。

## 🏗 技术架构

```mermaid
flowchart TB
    UI["Next.js 前端<br/>apps/web"] --> API["Fastify API<br/>apps/api"]
    API --> ENG["FastAPI 引擎<br/>services/engine"]
    ENG --> DB[("PostgreSQL + pgvector<br/>或 SQLite Demo")]
    ENG --> REDIS["Redis<br/>后台任务协调"]
    GOV["AI 治理 CLI<br/>scripts/governance"] --> ENG
```

| 模块 | 技术 | 职责 |
| --- | --- | --- |
| Web | Next.js | 决策审核、搜索、仪表盘、时间线、漂移和拓扑 |
| API | Fastify | Session、鉴权边界、Owner Scope |
| Engine | Python / FastAPI | 数据摄取、提取、检索、漂移检测、治理 |
| 数据层 | PostgreSQL + pgvector / SQLite Demo | 持久化数据和向量检索 |
| 后台协调 | Redis | 完整本地栈中的任务协调 |
| AI Agent 接口 | Python CLI | 机器可读的治理结果、状态码 |

仓库还包含 OpenSpec 变更管理、测试与部署脚本。详见[部署说明](docs/project/deployment_zh-CN.md)。

## 💬 可以解决哪些实际问题？

- *当初为什么选择 PostgreSQL 作为主数据库？*
- *哪一次 PR 或 ADR 记录了当前鉴权架构的设计理由？*
- *最近的代码修改是否与已接受的架构决策冲突？*
- *AI 编程助手在实施本次变更前，应该复查哪些约束？*

## ⚡ 最快体验方式

以下为 **Windows PowerShell 本地 Demo**。安装所需工具后，在终端执行：

```powershell
git clone https://github.com/luzay-max/DecisionAtlas.git
cd DecisionAtlas
pnpm install
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-demo-stack.ps1
```

Demo 使用**隔离的 SQLite 工作区和 Fake LLM / Embedding Provider**；在 Fake Provider 路径下不需要真实模型 API Key。启动后访问 [http://localhost:3000](http://localhost:3000)。

如需 PostgreSQL、Redis 和完整服务，请参考[快速开始文档](docs/project/quick-start_zh-CN.md)及后续启动说明。

## 🚀 快速开始

### 前置条件
- Node.js (v18+) & pnpm
- Python (3.11+) & uv
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

- [使用流程与优化建议 (Usage Guide)](./docs/project/usage-guide.md)
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
- [可选只读 MCP 适配器（实验性）](./docs/project/mcp-readonly-spike.md)
- [架构与规划](./docs/plans/2026-03-18-decisionatlas-project-blueprint.md)
- [当前执行计划（2026-10-21）：安全整改与真实仓库价值验证](./docs/plans/2026-10-21-security-hardening-and-real-repo-validation-plan.md)
- [历史计划审查与归档索引](./docs/plans/archive/2026-10-21-reviewed-plan-index.md)
- [真实仓库验证](./docs/project/real-repository-validation-baseline.md)

## ⚠️ 已知限制

- v0.3 RC 已包含本地/bootstrap session 恢复、owner scope 切换和基于角色的产品操作，但还不是完整 SaaS 组织管理台。
- GitHub App 安装绑定和 token-backed 私有仓库访问绑定是 admin/operator 流程；尚不包含完整 GitHub Marketplace/OAuth 自助安装和 secret vault。
- 暂不包含多人协作 review workflow 和 billing。
- 语义漂移标签较为保守，被刻意限制在较窄的范围内。
- 取决于仓库的信号质量，导入的工作区可能仍然会比较稀疏。
- **当前 `main` 尚未正式提供 GitLab/Gitee 公共仓库导入**：[PR #15](https://github.com/luzay-max/DecisionAtlas/pull/15)、[PR #16](https://github.com/luzay-max/DecisionAtlas/pull/16) 仍是未合并的 Draft，私有仓库与 GitLab 自建实例仍待安全和真实仓库验收。
- MCP 目前仅为**单工作区、只读实验能力**：真实 Agent Host 联调、自动绑定仓库及经 MCP 的 diff 检查尚未验收。
- 治理 guardrail 默认是 advisory，不会阻断 CI，除非未来有明确 change 启用该模式。
- Demo review queue 可能被之前的运行消费；下一阶段计划补稳定的 demo reset/reseed 流程。

---
*当前优化重点：决策证据质量、Why Search 验证和自托管可靠性。Stage-7 治理能力及可选 MCP 基础代码已进入 main，但真实 Agent 宿主验收和 GitLab/Gitee 完整导入尚未完成。*
