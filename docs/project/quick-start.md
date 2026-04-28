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
pnpm run dev:real
```

This starts PostgreSQL and Redis, runs migrations, seeds demo data, starts engine/API/web, and enables local bootstrap session recovery for the browser session. Stop it with:

```powershell
pnpm run dev:real:stop
```

Use the manual service commands only when debugging a specific layer.

### v0.3 Platform Flows

The v0.3 release-candidate baseline includes local/bootstrap login recovery, owner scope switching, admin/reviewer role gates, GitHub App installation binding, and token-backed private repository access binding.

These are operator/admin setup flows, not a full SaaS admin console. GitHub Marketplace/OAuth self-service installation, secret vault behavior, billing, and collaborative review workflows are still out of scope.

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
```

Before an external hosted walkthrough, use [Hosted Preview Readiness](hosted-preview-readiness.md) to record health, smoke, reset/reseed recovery status, and any known limitations. These hosted checks are a post-RC confidence layer, not a replacement for the canonical release gate.

For release-style validation, run the canonical local gate from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ci\pre-release.ps1
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
| Docker services unavailable | Retry `docker compose up -d postgres redis` |
| `.docx` import skipped | Confirm `pandoc` is installed and available in terminal. |
| Hosted demo state drifted | Run `scripts\demo\reset-demo.ps1` for `demo-workspace`; use `reseed-demo.ps1` when migrations or database drift need a deeper rebuild. |
