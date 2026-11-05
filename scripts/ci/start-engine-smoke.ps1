$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$engineDir = Join-Path $repoRoot "services\engine"
$dbPath = Join-Path $repoRoot ".tmp\smoke.db"
$dbDir = Split-Path $dbPath -Parent

if (-not (Test-Path $dbDir)) {
  New-Item -ItemType Directory -Path $dbDir | Out-Null
}

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

$env:DATABASE_URL = "sqlite:///$($dbPath -replace '\\','/')"
# Explicitly enable the local bootstrap only for the isolated Playwright smoke engine.
$env:APP_ENV = "test"
$env:AUTH_AUTO_BOOTSTRAP_LOCAL = "true"
Set-Location $engineDir
Invoke-Uv run alembic upgrade head
Invoke-Uv run python ..\..\scripts\ci\seed_smoke_demo.py
# Integration-only fixture is present exclusively on the non-merge B02+B03
# validation branch. It never imports real repositories or private data.
Invoke-Uv run python ..\..\scripts\ci\seed_b02_b03_composition.py
Invoke-Uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
