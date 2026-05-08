$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $repoRoot

Write-Host "DecisionAtlas canonical release baseline validation" -ForegroundColor Cyan
Write-Host "Repository root: $repoRoot" -ForegroundColor DarkGray

function Invoke-Uv {
  param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
  )

  if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "Using uv CLI: uv $($Arguments -join ' ')" -ForegroundColor DarkGray
    & uv @Arguments
    if ($LASTEXITCODE -ne 0) {
      throw "uv $($Arguments -join ' ') failed with exit code $LASTEXITCODE."
    }
    return
  }

  Write-Host "Using python -m uv fallback: python -m uv $($Arguments -join ' ')" -ForegroundColor Yellow
  & python -m uv @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "python -m uv $($Arguments -join ' ') failed with exit code $LASTEXITCODE."
  }
}

function Invoke-Phase {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Title,
    [Parameter(Mandatory = $true)]
    [scriptblock]$Action
  )

  Write-Host ""
  Write-Host "==> $Title" -ForegroundColor Green
  $global:LASTEXITCODE = 0
  & $Action
  if ($LASTEXITCODE -ne 0) {
    throw "$Title failed with exit code $LASTEXITCODE."
  }
}

Invoke-Phase "Workspace tests and typechecks" {
  pnpm test
  pnpm typecheck
}

Invoke-Phase "Engine pytest suite" {
  Set-Location (Join-Path $repoRoot "services\engine")
  Invoke-Uv run pytest -q
  Set-Location $repoRoot
}

Invoke-Phase "Offline benchmark fixture validation" {
  python scripts\ci\run_benchmark.py
}

Invoke-Phase "Governance agent guardrail interface availability" {
  python scripts\governance\agent_guardrail.py --summary
  python scripts\governance\agent_guardrail.py --enforcement-preview release-checklist --summary
}

Invoke-Phase "Playwright smoke coverage" {
  pnpm --filter @decisionatlas/web exec playwright install chromium
  pnpm --filter @decisionatlas/web exec playwright test
}

Write-Host ""
Write-Host "Release baseline validation completed successfully." -ForegroundColor Cyan
