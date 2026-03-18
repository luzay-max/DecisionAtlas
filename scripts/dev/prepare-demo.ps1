$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $repoRoot

$env:DATABASE_URL = "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/decisionatlas"
$env:REDIS_URL = "redis://127.0.0.1:6379/0"
$env:ENGINE_BASE_URL = "http://127.0.0.1:8000"
$env:API_BASE_URL = "http://127.0.0.1:3001"

function Invoke-Uv {
  param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
  )

  if (Get-Command uv -ErrorAction SilentlyContinue) {
    & uv @Arguments
    return
  }

  & python -m uv @Arguments
}

if (-not (Test-Path ".env")) {
  Copy-Item .env.example .env
  Write-Host "Created .env from .env.example" -ForegroundColor Yellow
}

Write-Host "Starting demo infrastructure..." -ForegroundColor Cyan
docker compose up -d postgres redis

Write-Host "Aligning local PostgreSQL credentials for the demo stack..." -ForegroundColor Cyan
docker exec decisionatlas-postgres psql -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';" | Out-Null

Write-Host "Syncing engine environment..." -ForegroundColor Cyan
Invoke-Uv sync --project services/engine

Write-Host "Running migrations and seeding the workspace..." -ForegroundColor Cyan
Set-Location (Join-Path $repoRoot "services\engine")
Invoke-Uv run alembic upgrade head
Invoke-Uv run python ..\..\scripts\ci\seed_smoke_demo.py

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
