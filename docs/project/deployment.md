# Deployment

## Recommended v0.2 shape

DecisionAtlas v0.2 is intended to run as a single-machine demo deployment:

- `web`: public HTTP entrypoint
- `api`: internal proxy and future auth boundary
- `engine`: internal FastAPI service for import, extraction, retrieval, drift
- `postgres`: persistent storage
- `redis`: queue/cache support

## Environment requirements

Required:

- `DATABASE_URL`
- `REDIS_URL`
- `ENGINE_BASE_URL`
- `API_BASE_URL`

For live-provider demo mode:

- `LLM_PROVIDER_MODE=openai_compatible`
- `LLM_API_KEY`
- `LLM_MODEL`
- `EMBEDDING_MODEL`

Optional:

- `EMBEDDING_API_KEY`
- `LLM_BASE_URL`
- `LLM_TIMEOUT_SECONDS`
- `GITHUB_TOKEN`
- `DEMO_REPO`

## Network layout

- Public traffic should hit `web`
- `web` talks to `api`
- `api` talks to `engine`
- `engine` talks to `postgres` and `redis`

Do not expose provider keys to the browser. Keep them on the host or injected into the backend containers only.

## Recommended bring-up order

```powershell
docker compose up -d postgres redis
cd services/engine
uv run alembic upgrade head
uv run python app/db/seed_demo.py
cd ..\..
pnpm --filter @decisionatlas/api dev
pnpm --filter @decisionatlas/web dev
```

## Demo verification

After startup:

1. Open `/workspaces/demo-workspace`
2. Run the demo import
3. Check `/review`
4. Ask a why-question on `/search`
5. Verify `/drift`

If the import succeeds but candidate decisions remain sparse, verify the live provider variables are set and the demo repo is reachable.
