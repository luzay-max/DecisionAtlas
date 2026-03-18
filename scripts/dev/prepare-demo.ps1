$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $repoRoot

if (-not (Test-Path ".env")) {
  Copy-Item .env.example .env
  Write-Host "Created .env from .env.example" -ForegroundColor Yellow
}

Write-Host "Starting demo infrastructure..." -ForegroundColor Cyan
docker compose up -d postgres redis

Write-Host "Syncing engine environment..." -ForegroundColor Cyan
python -m uv sync --project services/engine

Write-Host "Running migrations and seeding the workspace..." -ForegroundColor Cyan
Set-Location (Join-Path $repoRoot "services\engine")
python -m uv run alembic upgrade head
python -m uv run python -m app.db.seed_demo

Set-Location $repoRoot
Write-Host ""
Write-Host "DecisionAtlas demo is prepared." -ForegroundColor Green
Write-Host "Next commands:" -ForegroundColor Green
Write-Host "1. pnpm --filter @decisionatlas/api dev"
Write-Host "2. pnpm --filter @decisionatlas/web dev"
Write-Host "3. Open http://localhost:3000/workspaces/demo-workspace"
Write-Host ""
Write-Host "Optional live-provider demo vars in .env:" -ForegroundColor DarkCyan
Write-Host "LLM_PROVIDER_MODE=openai_compatible"
Write-Host "LLM_API_KEY=..."
Write-Host "LLM_MODEL=..."
Write-Host "EMBEDDING_MODEL=..."
