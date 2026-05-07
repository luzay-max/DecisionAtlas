# Quick Start

[Home](../README.md) | [Deployment](deployment.md) | [FAQ](faq.md) | [Demo Script](demo-script.md) | [Hosted Operator Guide](hosted-demo-operator-guide.md) | [Hosted Preview Readiness](hosted-preview-readiness.md) | [中文](quick-start_zh-CN.md)

---

This project is optimized for local development on a single machine.

### Prerequisites

- `pnpm`
- Python `3.11+`
- Docker Desktop
- `pandoc` (optional, for `.docx` import)

### Install

From the repository root:

```powershell
pnpm install
uv sync --project services/engine
Copy-Item .env.example .env
```

### Quick Demo (Fastest Path)

Start an isolated SQLite-backed demo in one command:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-demo-stack.ps1
```

This starts a curated demo workspace under `.tmp/` — isolated from your local PostgreSQL container state.

### Full Stack Setup

For a deployment-like environment with PostgreSQL and Redis:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-real-stack.ps1
```

This starts PostgreSQL and Redis, runs migrations, performs non-destructive demo workspace setup, checks seeded demo readiness, starts engine/API/web, and enables local bootstrap session recovery for the browser session. If an existing `demo-workspace` was consumed by a prior walkthrough, restore it explicitly before startup:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-real-stack.ps1 -ResetSeededDemo
```

Stop it with:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\stop-real-stack.ps1
```

`pnpm run dev:real` and `pnpm run dev:real:stop` call the same scripts and remain valid shortcuts.

Use the manual service commands only when debugging a specific layer.

### v0.3 Platform Flows

The v0.3 release-candidate baseline includes local/bootstrap login recovery, owner scope switching, admin/reviewer role gates, GitHub App installation binding, and token-backed private repository access binding.

These are operator/admin setup flows, not a full SaaS admin console. GitHub Marketplace/OAuth self-service installation, secret vault behavior, billing, and collaborative review workflows are still out of scope.

### Post Stage 7 Governance Flow

The current post-stage-7 baseline includes a local AI-agent governance guardrail. It aggregates the current diff checker and long-term drift detector into an advisory status:

- `continue`: no blocking governance concern detected.
- `caution`: review recommended actions before claiming completion.
- `pause`: stop and ask for human review; do not silently rewrite code, specs, or accepted rules.

Run it before committing or archiving an OpenSpec change:

```powershell
python scripts\governance\agent_guardrail.py --summary
```

Use `--pretty` when an AI agent or reviewer needs the full machine-readable JSON.

### Repeat Repository Analysis

When you enter a repository that already has an imported workspace in the current owner scope, the live-analysis form should show three explicit choices before starting new work:

- **Open existing workspace** when you want to review current results, inspect the latest import summary, or continue why/drift work.
- **Sync since last import** when the repository has changed and you want to fetch newer artifacts without treating the run as a fresh full re-analysis.
- **Run full analysis again** when you intentionally want to rebuild the imported workspace result from the repository baseline.

If a queued or running import already exists for that workspace, open the workspace/job progress instead of starting another repeat run.

### Live Provider Mode

Edit `.env` to connect to a real LLM provider:

```env
LLM_PROVIDER_MODE=openai_compatible
LLM_API_KEY=your_api_key
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
# Optional
EMBEDDING_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
```

### Verify

Check health endpoints:

```powershell
Invoke-WebRequest http://localhost:3001/health
Invoke-WebRequest http://localhost:8000/health
```

For an operator check against a running hosted or local demo environment:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\smoke-check.ps1
python scripts\demo\check_seeded_demo.py
```

Before an external hosted walkthrough, use [Hosted Preview Readiness](hosted-preview-readiness.md) to record health, smoke, reset/reseed recovery status, and any known limitations. These hosted checks are a post-RC confidence layer, not a replacement for the canonical release gate.

For release-style validation, run the canonical local gate from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1
```

For current governance-focused validation, also run:

```powershell
openspec validate --all --strict
python scripts\governance\agent_guardrail.py --summary
cd services/engine
.\.venv\Scripts\python.exe -m pytest tests/governance/test_diff_checker.py tests/governance/test_drift_detector.py tests/governance/test_agent_guardrail.py -q
.\.venv\Scripts\python.exe -m pytest tests/db/test_migrations.py tests/db/test_schema.py -q
```

Open the web app:

- Web UI: `http://localhost:3000`
- Demo Workspace: `http://localhost:3000/workspaces/demo-workspace`
- Review: `http://localhost:3000/review`
- Search: `http://localhost:3000/search`
- Drift: `http://localhost:3000/drift`

### Common Issues

| Issue | Solution |
|-------|----------|
| `uv` not on PATH | Use `python -m uv ...` instead. The pre-release script handles this automatically. |
| Import succeeds but no candidates | Verify `LLM_PROVIDER_MODE`, `LLM_API_KEY`, `LLM_MODEL`, and `EMBEDDING_MODEL` are set. |
| Live analysis fails | Public repository import remains the default path. Admin/operator setup flows can bind GitHub App installations or token-backed private repository access for owner-scoped workspaces. |
| Same repository already exists | Open the existing workspace for current results, use incremental sync for new repository changes, or choose full re-analysis only when you intentionally want a heavier rerun. |
| Import already running | Follow the existing workspace/job link and wait for the queued or running import to finish before starting another sync or rerun. |
| Docker services unavailable | Retry `docker compose up -d postgres redis` |
| Real stack migration fails with `value too long for type character varying(32)` | Ensure the code includes the shortened Alembic revision `0008_governance_ingest`; run `tests/db/test_migrations.py` to catch future revision IDs over 32 characters. |
| `.docx` import skipped | Confirm `pandoc` is installed and available in terminal. |
| Hosted demo state drifted | Run `python scripts\demo\check_seeded_demo.py`; then run `scripts\demo\reset-demo.ps1` for consumed review/demo state or `reseed-demo.ps1` when migrations or database drift need a deeper rebuild. |
