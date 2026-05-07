param(
  [switch]$UseLocalDemoDatabase
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$engineDir = Join-Path $repoRoot "services\engine"

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

if ($UseLocalDemoDatabase) {
  $dbPath = Join-Path $repoRoot ".tmp\demo-stack.db"
  $env:DATABASE_URL = "sqlite:///$($dbPath -replace '\\','/')"
}

if (-not $env:DATABASE_URL) {
  throw "DATABASE_URL is required. Set it for the hosted environment, or pass -UseLocalDemoDatabase for the local isolated demo stack."
}

Write-Host "Running migrations before reseeding the hosted demo lane..." -ForegroundColor Cyan
Set-Location $engineDir
Invoke-Uv run alembic upgrade head
Invoke-Uv run python ..\..\scripts\demo\reset_seeded_demo.py
Invoke-Uv run python ..\..\scripts\demo\check_seeded_demo.py

Write-Host "Seeded demo lane reseed complete." -ForegroundColor Green
