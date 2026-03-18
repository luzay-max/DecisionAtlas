$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $repoRoot

pnpm test
pnpm typecheck

Set-Location (Join-Path $repoRoot "services\engine")
python -m uv run pytest -q

Set-Location $repoRoot
python scripts\ci\run_benchmark.py
pnpm --filter @decisionatlas/web exec playwright install chromium
pnpm --filter @decisionatlas/web exec playwright test
