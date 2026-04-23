# Deployment

[Home](../README.md) | [Quick Start](quick-start.md) | [FAQ](faq.md) | [Demo Script](demo-script.md) | [中文](deployment_zh-CN.md)

---

### Recommended v0.2 Architecture

DecisionAtlas v0.2 is designed as a single-machine demo deployment:

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

### Bring-up Order

```powershell
# 1. Start infrastructure
docker compose up -d postgres redis

# 2. Run migrations
cd services/engine
uv run alembic upgrade head
uv run python -m app.db.seed_demo
cd ..\..

# 3. Start all services
pnpm --filter @decisionatlas/api dev
pnpm --filter @decisionatlas/web dev
```

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
