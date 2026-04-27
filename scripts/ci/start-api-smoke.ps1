$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$dbPath = Join-Path $repoRoot ".tmp\smoke.db"

$env:DATABASE_URL = "sqlite:///$($dbPath -replace '\\','/')"
$env:ENGINE_BASE_URL = "http://127.0.0.1:8000"
$env:AUTO_BOOTSTRAP_AUTH = "true"
$env:PORT = "3001"
Set-Location $repoRoot
pnpm --filter @decisionatlas/api dev
