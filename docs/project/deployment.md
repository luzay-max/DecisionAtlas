# Deployment

[Home](../README.md) | [Quick Start](quick-start.md) | [FAQ](faq.md) | [Demo Script](demo-script.md) | [Hosted Operator Guide](hosted-demo-operator-guide.md) | [Hosted Preview Readiness](hosted-preview-readiness.md) | [中文](deployment_zh-CN.md)

---

### Recommended Post-Stage-7 Architecture

DecisionAtlas remains designed around a single-machine demo or preview deployment, with explicit owner-scoped product flows and local governance guardrails layered on the existing web/API/engine topology:

```
┌─────────────────────────────────────────────────────┐
│                    Public Traffic                    │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                      Web (Next.js)                   │
│                  Port: 3000                          │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│              API (Fastify)                           │
│              Port: 3001                             │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│              Engine (FastAPI)                        │
│              Port: 8000                              │
└──────────┬───────────────────────┬───────────────────┘
           │                       │
┌──────────▼──────────┐  ┌─────────▼────────┐
│    PostgreSQL        │  │      Redis       │
│    Port: 5432        │  │    Port: 6379   │
└─────────────────────┘  └──────────────────┘
```

### Environment Variables

**Required:**

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `ENGINE_BASE_URL` | Engine service URL |
| `API_BASE_URL` | API service URL |
| `AUTO_BOOTSTRAP_AUTH` | Enables local/bootstrap session recovery for local demo and real-stack operation |

For hosted operation, `DATABASE_URL`, `REDIS_URL`, and provider credentials belong on host-managed or backend service surfaces. Browser-facing config should only receive the web/API URLs it needs to call the API.

**For Live Provider Mode:**

| Variable | Description |
|----------|-------------|
| `LLM_PROVIDER_MODE` | Set to `openai_compatible` |
| `LLM_API_KEY` | Your API key |
| `LLM_MODEL` | Model name (e.g., `gpt-4o`) |
| `EMBEDDING_MODEL` | Embedding model name |

**Optional:**

| Variable | Description |
|----------|-------------|
| `EMBEDDING_API_KEY` | Embedding API key |
| `LLM_BASE_URL` | Custom LLM endpoint |
| `LLM_TIMEOUT_SECONDS` | Request timeout |
| `GITHUB_TOKEN` | GitHub access token |
| `DEMO_REPO` | Demo repository identifier |

### Platform Access Boundary

The v0.3 RC includes productized operator/admin flows for:

- local/bootstrap session recovery and login
- owner scope switching
- role-gated workspace actions
- GitHub App installation binding
- token-backed private repository access binding

The RC does not include a full SaaS org-management console, secret vault, billing, GitHub Marketplace/OAuth self-service installation, or multi-user collaborative review workflow.

### Governance Guardrail Boundary

The post-stage-7 baseline includes local advisory governance tools:

```powershell
python scripts\governance\check.py --pretty
python scripts\governance\drift_report.py --pretty
python scripts\governance\agent_guardrail.py --summary
```

These tools are intended for developers, operators, and AI agents before commit/archive/release review. They do not modify project files or block CI by default.

### Hosted Operator Flow

Use the hosted operator guide when running a persistent demo environment:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\health-check.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\smoke-check.ps1
```

For recovery, start with the seeded demo reset:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo\reset-demo.ps1
```

Use `reseed-demo.ps1` when migrations or database drift require a deeper rebuild of `demo-workspace`. The default recovery scripts do not delete imported workspaces.

Before showing the environment externally, run the [Hosted Preview Readiness](hosted-preview-readiness.md) checklist. Hosted preview readiness is a post-RC confidence layer for a running environment; it does not replace the canonical release gate.

### Bring-up Order

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\start-real-stack.ps1
```

For local real-stack shutdown:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\stop-real-stack.ps1
```

`pnpm run dev:real` and `pnpm run dev:real:stop` are shortcuts for the same scripts.

Use manual service startup only when debugging a specific layer.

### Network Security

- **Public traffic** → `web` (Port 3000)
- `web` → `api` → `engine`
- `engine` → `postgres` + `redis`

> ⚠️ **Important**: Never expose provider API keys to the browser. Keep them only on the host or inject into backend containers.

### Verification

After startup, verify:

1. Open `/workspaces/demo-workspace`
2. Run the demo import
3. Check `/review`
4. Ask a why-question on `/search`
5. Verify `/drift`

For a hosted environment, run [Hosted Demo Operator Guide](hosted-demo-operator-guide.md) checks before a public walkthrough.

Also run the advisory governance guardrail before archiving or publishing a milestone:

```powershell
openspec validate --all --strict
python scripts\governance\agent_guardrail.py --summary
```
