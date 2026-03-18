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
Set-Location $engineDir
Invoke-Uv run alembic upgrade head
Invoke-Uv run python ..\..\scripts\ci\seed_smoke_demo.py
Invoke-Uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
