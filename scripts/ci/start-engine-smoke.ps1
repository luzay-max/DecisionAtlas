$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$engineDir = Join-Path $repoRoot "services\engine"
$dbPath = Join-Path $repoRoot ".tmp\smoke.db"
$dbDir = Split-Path $dbPath -Parent

if (-not (Test-Path $dbDir)) {
  New-Item -ItemType Directory -Path $dbDir | Out-Null
}

$env:DATABASE_URL = "sqlite:///$($dbPath -replace '\\','/')"
Set-Location $engineDir
python -m uv run alembic upgrade head
python -m uv run python ..\..\scripts\ci\seed_smoke_demo.py
python -m uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
