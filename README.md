# DecisionAtlas

[English](README.md) | [中文](README_zh-CN.md)

**DecisionAtlas** turns engineering repo context into a searchable decision memory with citations and drift alerts. It automatically analyzes GitHub issues, pull requests, and commits to extract key architectural and design decisions, making them searchable and verifiable.

## 🌟 Key Features

- **Automated Knowledge Extraction**: Imports GitHub issues, PRs, commits, markdown, ADRs, and text notes to extract candidate decisions.
- **Citation-First Search**: Answers "why" questions with citation-first responses, support grading, and chunk-backed supporting evidence.
- **Drift Detection**: Flags rule-first and semantic drift alerts after manual evaluation with conservative imported drift semantics.
- **Human-in-the-Loop Review**: Lets a reviewer accept, reject, or supersede extracted decisions.
- **Live Repository Analysis**: Supports one-off live analysis runs for public GitHub repositories through imported workspaces with incremental sync.
- **Flexible Provider Support**: Works in local mode with fake providers or live mode with OpenAI-compatible LLMs.

## 🏗 Architecture

The platform consists of three main components:

- `apps/web`: Next.js UI for review, search, timeline, dashboard, and drift.
- `apps/api`: Fastify edge API and future auth boundary.
- `services/engine`: FastAPI engine for ingest, extraction, retrieval, and drift.
- **Data Layer**: `PostgreSQL + pgvector` for durable storage and vector search, `Redis` for background coordination.

## 🚀 Quick Start

### Prerequisites
- Node.js (v18+) & pnpm
- Python (v3.10+) & uv
- Docker Desktop (for PostgreSQL & Redis)

### One-Command Local Bring-up

The fastest way to experience the product locally using an isolated, SQLite-backed demo workspace:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-demo-stack.ps1
```

### Full Stack Setup

To run the real stack with PostgreSQL and Redis:

```powershell
# Install dependencies
pnpm install
uv sync --project services/engine

# Setup environment variables
Copy-Item .env.example .env

# Start infrastructure
docker compose up -d postgres redis

# Run database migrations and seed demo data
cd services/engine
uv run alembic upgrade head
uv run python -m app.db.seed_demo
cd ..\..

# Start the application services
pnpm run dev:real
```

Then open your browser:
- Web UI: `http://localhost:3000`
- API Health: `http://localhost:3001/health`
- Engine Health: `http://localhost:8000/health`

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

## 📚 Documentation

- [Quick Start](./docs/project/quick-start.md)
- [Deployment](./docs/project/deployment.md)
- [FAQ](./docs/project/faq.md)
- [Architecture & Plans](./docs/plans/2026-03-18-decisionatlas-project-blueprint.md)
- [Real Repository Validation](./docs/project/real-repository-validation-baseline.md)

## ⚠️ Known Limitations

- MVP auth and multi-user permissions are not implemented yet.
- Semantic drift labels are conservative and intentionally narrow.
- Live analysis currently supports public GitHub repositories only (via token mode, not GitHub App auth).
- Imported workspaces can still be sparse depending on repository signal quality.

---
*Current Project Stage: Core MVP & `v0.2` Demo Hardening Complete.*
