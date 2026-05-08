# DecisionAtlas

[English](README.md) | [中文](README_zh-CN.md)

**DecisionAtlas** turns engineering repo context into searchable decision memory with citations, drift alerts, and AI-readable governance guardrails. It analyzes repository artifacts to extract candidate engineering decisions, lets humans accept the durable decisions, and helps AI agents check whether new changes still follow project direction.

## 🌟 Key Features

- **Automated Knowledge Extraction**: Imports GitHub issues, PRs, commits, markdown, ADRs, and text notes to extract candidate decisions.
- **Citation-First Search**: Answers "why" questions with citation-first responses, support grading, and chunk-backed supporting evidence.
- **Drift Detection**: Flags rule-first and semantic drift alerts after manual evaluation with conservative imported drift semantics.
- **Human-in-the-Loop Review**: Lets a reviewer accept, reject, or supersede extracted decisions.
- **Live Repository Analysis**: Supports one-off live analysis runs for public GitHub repositories through imported workspaces with incremental sync.
- **Owner-Scoped Product Flows**: Provides local/bootstrap login, owner scope switching, role-gated workspace actions, GitHub App installation binding, and private repository access binding.
- **Governance Knowledge Layer**: Imports Markdown standards, roadmap notes, postmortems, checklists, and human decisions into reviewable governance rule drafts.
- **AI Agent Governance Guardrails**: Aggregates current diff checks and long-term governance drift reports into advisory `continue`, `caution`, or `pause` results for AI development workflows.
- **Flexible Provider Support**: Works in local mode with fake providers or live mode with OpenAI-compatible LLMs.

## 🏗 Architecture

The platform consists of three main components:

- `apps/web`: Next.js UI for review, search, timeline, dashboard, and drift.
- `apps/api`: Fastify edge API, session recovery, and owner-scoped auth boundary.
- `services/engine`: FastAPI engine for ingest, extraction, retrieval, drift, and governance checks.
- `scripts/governance`: Local governance checker, drift report, and AI-agent guardrail entrypoints.
- **Data Layer**: `PostgreSQL + pgvector` for durable storage and vector search, `Redis` for background coordination.

## 🚀 Quick Start

### Prerequisites
- Node.js (v18+) & pnpm
- Python (v3.10+) & uv
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

- [Quick Start](./docs/project/quick-start.md)
- [Deployment](./docs/project/deployment.md)
- [FAQ](./docs/project/faq.md)
- [Demo Script](./docs/project/demo-script.md)
- [Hosted Preview Readiness](./docs/project/hosted-preview-readiness.md)
- [Release Notes v0.3.0-rc.1](./docs/project/release-notes-v0.3.0-rc.1.md)
- [Governance Markdown Ingest](./docs/project/governance-markdown-ingest-mvp.md)
- [Governance Diff Checker](./docs/project/governance-diff-checker.md)
- [Governance Drift Detection](./docs/project/governance-drift-detection.md)
- [AI Agent Governance Guardrail](./docs/project/governance-agent-guardrail.md)
- [Architecture & Plans](./docs/plans/2026-03-18-decisionatlas-project-blueprint.md)
- [Current Master Plan](./docs/plans/2026-04-29-decisionatlas-next-master-plan.md)
- [Real Repository Validation](./docs/project/real-repository-validation-baseline.md)

## ⚠️ Known Limitations

- v0.3 RC includes local/bootstrap session recovery, owner scope switching, and role-gated product actions, but not a full SaaS org-management console.
- GitHub App installation binding and token-backed private repository access binding are admin/operator flows; full GitHub Marketplace/OAuth self-service and secret vault behavior are not included.
- Multi-user collaborative review workflows and billing are not included.
- Semantic drift labels are conservative and intentionally narrow.
- Imported workspaces can still be sparse depending on repository signal quality.
- Governance guardrails are advisory by default and do not block CI unless a future explicit change enables that mode.
- Demo review queue state can be consumed by prior runs; the next planned hardening slice is a reliable demo reset/reseed workflow.

---
*Current Project Stage: Post Stage 7 - AI-agent governance guardrails are implemented; the next focus is governance workflow hardening, demo reset reliability, and real-repository value measurement.*
