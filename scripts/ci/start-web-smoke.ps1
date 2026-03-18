$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

$env:API_BASE_URL = "http://127.0.0.1:3001"
Set-Location $repoRoot
pnpm --filter @decisionatlas/web exec next dev --hostname 127.0.0.1 --port 3000
