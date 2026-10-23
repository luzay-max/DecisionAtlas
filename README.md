# DecisionAtlas

**Engineering decision memory for humans and AI coding agents.**

Turn scattered GitHub issues, pull requests, commits, ADRs, and engineering notes into **searchable, evidence-backed architectural decisions**. DecisionAtlas helps teams understand *why* code looks the way it does, review which decisions become trusted, detect drift, and give AI coding agents project-specific governance guidance.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Self-hosted](https://img.shields.io/badge/Deployment-Self--hosted-2b6cb0)](docs/project/deployment.md)
[![AI Agent Guardrails](https://img.shields.io/badge/AI%20Agents-Governance%20Guardrails-6554c0)](docs/project/governance-agent-guardrail.md)

**English** · [简体中文](README_zh-CN.md) · [Quick start](docs/project/quick-start.md) · [Architecture](docs/plans/2026-03-18-decisionatlas-project-blueprint.md) · [Documentation](#-documentation)

> **Project status:** An actively developed, local-first/self-hosted platform with a v0.3 release-candidate baseline. Governance checks are **advisory by default**, and this is not yet a fully managed, multi-tenant SaaS product.
>
> **Current main:** [CI #227](https://github.com/luzay-max/DecisionAtlas/actions/runs/39913146099) passed after [PR #17 (read-only MCP)](https://github.com/luzay-max/DecisionAtlas/pull/17) and [PR #18 (historical plans)](https://github.com/luzay-max/DecisionAtlas/pull/18) merged. MCP remains an **optional experimental adapter**, not a production-ready Agent integration. See the [archive index](docs/plans/archive/2026-10-21-reviewed-plan-index.md).

## 📸 Real running UI

Captured by Playwright from the **actual Windows CI demo stack** at [main commit `93bbacd`](https://github.com/luzay-max/DecisionAtlas/commit/93bbacd378a8d24e1230d70d3cde3e3a7c719a06), not design mockups.

| Home · dark mode | Candidate decision review |
| --- | --- |
| ![DecisionAtlas home page, dark mode, actual browser screenshot](docs/assets/screenshots/01-home-desktop-dark-zh.png) | ![DecisionAtlas candidate review, actual browser screenshot](docs/assets/screenshots/03-review-desktop-dark-zh.png) |

**[See all 8 screenshots](docs/project/ui-screenshots.md)** (desktop light/dark, workspace, Why Search and mobile screens) · [Screenshot baseline CI](https://github.com/luzay-max/DecisionAtlas/actions/runs/39728035244) · [Latest verified main CI #227](https://github.com/luzay-max/DecisionAtlas/actions/runs/39913146099)

> Screenshots use **seeded demo data with Fake LLM providers**. They demonstrate real UI rendering, not the correctness of AI extraction from customer repositories or production deployment readiness.


## 🎯 Why DecisionAtlas?

Engineering teams often know **what** changed but lose track of **why**: the reasoning lives across PR conversations, issue discussions, ADRs, and internal notes. AI coding assistants face the same problem and can propose changes that unintentionally conflict with established decisions.

DecisionAtlas provides a reviewable decision layer between repository history and new work:

- **Remember the rationale** — preserve engineering decisions along with supporting source evidence.
- **Ask “why?”** — search decisions and retrieve citation-first, evidence-backed answers.
- **Detect drift** — flag potential mismatches between current changes and documented intent.
- **Guide AI coding agents** — give assistants structured `continue`, `caution`, or `pause` advice, while keeping human approval central.

## ✨ What you can do

| Capability | What it means |
| --- | --- |
| **Repository intelligence** | Import and incrementally sync GitHub issues, PRs, commits, Markdown, ADRs, and notes into a workspace. |
| **Decision extraction and review** | Generate candidate decisions and let reviewers accept, reject, or supersede them; candidates are not automatically trusted. |
| **Evidence-first search** | Ask architecture “why” questions with source citations and supporting context. |
| **Drift detection** | Evaluate rule-based and semantic drift signals, with conservative alert semantics. |
| **AI-agent guardrails** | Run governance checks against a change/diff and return structured JSON plus advisory status codes. |
| **Optional read-only MCP adapter (experimental)** | Expose human-accepted decisions and source evidence through four MCP tools scoped to one authorized workspace; not a general-purpose Agent or repository connector. |
| **Owner-scoped workflows** | Use local/bootstrap login, role-gated workspaces, and admin/operator GitHub App or private-repository bindings. |
| **Visual exploration** | Review decisions, timelines, search results, topology, and drift in a Next.js dashboard with dark/light themes. |
| **Flexible model setup** | Run an isolated demo with fake providers or configure an OpenAI-compatible LLM for live workflows. |

## 🔌 Optional read-only MCP (experimental)

[PR #17](https://github.com/luzay-max/DecisionAtlas/pull/17) has merged into `main`. The optional **MCP Python SDK v2 stdio adapter** reads decisions from the **existing authenticated Engine API**, without creating a second repository index. It exposes these **read-only** tools:

- `project_status` — report how many accepted decisions are available in the bound workspace.
- `list_project_decisions` — list reviewed, accepted decisions.
- `search_project_decisions` — search accepted decisions using **basic lexical matching** (not semantic search).
- `get_decision_evidence` — retrieve source references only for an accepted decision in that workspace.

The operator must supply a valid DecisionAtlas session and one explicitly authorized workspace. The adapter only connects to an Engine API on **loopback**; it cannot import repositories, approve candidates, write Git changes, or automatically detect the Agent's current repository. **SDK v2 in-process discovery and tool-call tests passed in CI; real stdio Agent-host integration, enterprise security sign-off, and decision-quality validation remain outstanding.** Human review is still required before candidate decisions can be treated as accepted.

For prerequisites and a local, optional launch example, see [MCP read-only adapter guide](docs/project/mcp-readonly-spike.md).

## 🔄 How it works

```mermaid
flowchart LR
    A["GitHub Issues / PRs / Commits<br/>ADRs / Markdown"] --> B["Ingest & extract evidence"]
    B --> C["Candidate decisions"]
    C --> D["Human review"]
    D --> E["Accepted decision memory"]
    E --> F["Citation-first search / why-queries"]
    E --> G["Drift checks & AI agent guardrails"]
    G --> H["continue / caution / pause"]
```

The key distinction: **extraction produces candidates, not policy by decree**. Humans review decisions, and agent-facing governance reports default to advice rather than silently rewriting code or blocking CI.

## 🏗 Architecture

```mermaid
flowchart TB
    UI["Next.js Web UI<br/>apps/web"] --> API["Fastify API<br/>apps/api"]
    API --> ENG["FastAPI Engine<br/>services/engine"]
    ENG --> DB[("PostgreSQL + pgvector<br/>or SQLite demo")]
    ENG --> REDIS["Redis<br/>background coordination"]
    GOV["Agent governance CLI<br/>scripts/governance"] --> ENG
```

| Layer | Technology | Responsibility |
| --- | --- | --- |
| Web | Next.js | Decision review, search, dashboards, timeline, drift, and topology |
| API | Fastify | Session/auth boundaries and owner-scoped actions |
| Engine | FastAPI / Python | Repository ingestion, extraction, retrieval, drift, and governance |
| Storage | PostgreSQL + pgvector / SQLite demo | Durable workspace data and vector retrieval |
| Background coordination | Redis | Full-stack background coordination |
| Agent integration | Python CLI | Machine-readable governance results and exit codes |

The repository also includes OpenSpec change management, automated tests, and a local setup workflow. See [deployment architecture](docs/project/deployment.md).

## 💬 Questions it helps answer

- *Why did we choose Redis as a cache rather than the primary database?*
- *Which PR or ADR explains our current authentication design?*
- *Does this new code change conflict with an accepted architecture decision?*
- *What should an AI coding agent review before making this change?*

## ⚡ Fastest way to try it

For a **Windows PowerShell local demo**, clone the repo, install the prerequisites below, and run:

```powershell
git clone https://github.com/luzay-max/DecisionAtlas.git
cd DecisionAtlas
pnpm install
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-demo-stack.ps1
```

The demo uses a **local SQLite workspace and fake LLM/embedding providers**; no real model API key is required for the fake-provider path. Once started, open [http://localhost:3000](http://localhost:3000).

For PostgreSQL/Redis and live-service development, use the [full-stack guide](docs/project/quick-start.md) and the commands below. Startup times and local prerequisites vary by machine.

## 🚀 Quick Start

### Prerequisites
- Node.js (v18+) & pnpm
- Python (3.11+) & uv
- Docker Desktop (for PostgreSQL & Redis)

### One-Command Demo Stack

The fastest way to experience the product locally using an isolated, SQLite-backed demo workspace:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-demo-stack.ps1
```

### One-Command Real Stack

The recommended full local stack uses Docker PostgreSQL, Redis, the FastAPI engine, the Fastify API, and the Next.js web app:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-real-stack.ps1
```

Stop it with:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\stop-real-stack.ps1
```

The script stops any existing managed stack, starts PostgreSQL/Redis, runs migrations, seeds demo data, and starts all three services.

### Manual Full Stack Setup

Use this only when debugging the individual services:

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

Then open your browser:
- Web UI: `http://localhost:3000`
- API Health: `http://localhost:3001/health`
- Engine Health: `http://localhost:8000/health`

## ✅ Validation Flow

Use these checks before archiving an OpenSpec change or preparing a release snapshot:

```powershell
openspec validate --all --strict
python scripts\governance\agent_guardrail.py --summary
python scripts\governance\agent_guardrail.py --protocol-status --summary
pnpm --filter @decisionatlas/web exec playwright test
```

Engine-focused checks:

```powershell
cd services/engine
.\.venv\Scripts\python.exe -m pytest tests/governance/test_diff_checker.py tests/governance/test_drift_detector.py tests/governance/test_agent_guardrail.py -q
.\.venv\Scripts\python.exe -m pytest tests/db/test_migrations.py tests/db/test_schema.py -q
```

The governance guardrail is advisory by default:

- `continue`: no blocking governance concern detected.
- `caution`: review recommended actions before claiming completion.
- `pause`: stop and ask for human review; do not silently rewrite code, specs, or accepted rules.

The default local governance development protocol uses:

```powershell
python scripts\governance\agent_guardrail.py --protocol-status --summary
```

Run it before non-trivial implementation, after targeted validation, before archiving an OpenSpec change, and before committing completed work. It reports active OpenSpec context, guardrail status, required tests, recommended actions, human questions, and handoff guidance. It remains advisory and is separate from optional enforcement preview or the canonical release gate.

## 💡 Example Queries

Once running, you can ask questions like:
- *Why did we choose Redis as cache only?*
- *Why is PostgreSQL still the primary database?*
- *Why did we move this workflow into a queue?*

## ⚙️ Configuration (Live Provider)

For a live provider-backed demo, configure these variables in your `.env`:

```env
LLM_PROVIDER_MODE=openai_compatible
LLM_API_KEY=your_api_key
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
# Optional
EMBEDDING_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
```

## 🧭 OpenSpec Development Flow

DecisionAtlas uses OpenSpec for scoped changes. The expected workflow is:

1. Propose a change with proposal, design, specs, and tasks.
2. Run governance preflight with `python scripts\governance\agent_guardrail.py --protocol-status --summary`.
3. Implement tasks incrementally.
4. Run targeted tests and `openspec validate --all --strict`.
5. Run governance postflight with `python scripts\governance\agent_guardrail.py --protocol-status --summary`.
6. Sync delta specs to main specs.
7. Archive the completed change under `openspec/changes/archive/`.
8. Commit the code, specs, archive, and documentation together, including any `caution` or `pause` evidence in the handoff.

Current post-stage-7 planning is captured in:

- [Post Stage 7 Master Plan](./docs/plans/2026-05-06-decisionatlas-post-stage-7-master-plan.md)
- [2026-05-06 Update Log](./docs/project/2026-05-06-update-log.md)

## 📚 Documentation

- [Usage Guide & Progress Update](./docs/project/usage-guide.md)
- [Quick Start](./docs/project/quick-start.md)
- [Deployment](./docs/project/deployment.md)
- [Self-Hosted Commercial Baseline](./docs/project/self-hosted-commercial-baseline.md)
- [Self-Hosted Readiness Checklist](./docs/project/self-hosted-readiness-checklist.md)
- [Code Decision Audit Template](./docs/project/code-decision-audit-template.md)
- [FAQ](./docs/project/faq.md)
- [Demo Script](./docs/project/demo-script.md)
- [Hosted Preview Readiness](./docs/project/hosted-preview-readiness.md)
- [Release Notes v0.3.0-rc.1](./docs/project/release-notes-v0.3.0-rc.1.md)
- [Governance Markdown Ingest](./docs/project/governance-markdown-ingest-mvp.md)
- [Governance Diff Checker](./docs/project/governance-diff-checker.md)
- [Governance Drift Detection](./docs/project/governance-drift-detection.md)
- [AI Agent Governance Guardrail](./docs/project/governance-agent-guardrail.md)
- [Optional read-only MCP adapter (experimental)](./docs/project/mcp-readonly-spike.md)
- [Architecture & Plans](./docs/plans/2026-03-18-decisionatlas-project-blueprint.md)
- [Current Execution Plan (2026-10-21): Security Hardening and Real-Repository Value Pilot](./docs/plans/2026-10-21-security-hardening-and-real-repo-validation-plan.md)
- [Historical Plans: Reviewed Archive Index](./docs/plans/archive/2026-10-21-reviewed-plan-index.md)
- [Real Repository Validation](./docs/project/real-repository-validation-baseline.md)

## ⚠️ Known Limitations

- v0.3 RC includes local/bootstrap session recovery, owner scope switching, and role-gated product actions, but not a full SaaS org-management console.
- GitHub App installation binding and token-backed private repository access binding are admin/operator flows; full GitHub Marketplace/OAuth self-service and secret vault behavior are not included.
- Multi-user collaborative review workflows and billing are not included.
- Near-term productization targets self-hosted Community / Team / Enterprise packaging; hosted managed service, billing, and Marketplace-style onboarding remain future optional work.
- Product/support tier boundaries are documented for self-hosted packaging, but runtime license enforcement is not part of the current baseline.
- Semantic drift labels are conservative and intentionally narrow.
- Imported workspaces can still be sparse depending on repository signal quality.
- **GitLab.com/Gitee.com public imports are not in the current `main` release**: [PR #15](https://github.com/luzay-max/DecisionAtlas/pull/15) and [PR #16](https://github.com/luzay-max/DecisionAtlas/pull/16) are still unmerged Draft PRs; private repos and GitLab self-managed access also remain unverified.
- MCP is currently a **read-only, single-workspace experiment**: real Agent-host integration, repository auto-binding and diff checking through MCP remain unverified.
- Governance guardrails are advisory by default and do not block CI unless a future explicit change enables that mode.
- Demo review queue state can be consumed by prior runs; the next planned hardening slice is a reliable demo reset/reseed workflow.

---
*Current project focus: evidence quality, Why Search validation, and reliable self-hosted workflows. The Stage-7 governance baseline and optional MCP adapter are present in main, but real Agent-host acceptance and GitLab/Gitee imports are not yet completed.*
