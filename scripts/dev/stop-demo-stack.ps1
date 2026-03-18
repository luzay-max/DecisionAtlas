$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$statePath = Join-Path $repoRoot ".tmp\demo-stack.json"

if (-not (Test-Path $statePath)) {
  Write-Host "No recorded demo stack is running." -ForegroundColor Yellow
  return
}

$state = Get-Content -Raw $statePath | ConvertFrom-Json

foreach ($service in $state.services) {
  $processId = [int]$service.pid
  $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
  if (-not $process) {
    continue
  }

  Write-Host "Stopping $($service.name) (PID $processId)..." -ForegroundColor Cyan
  & taskkill /PID $processId /T /F | Out-Null
}

Remove-Item $statePath -Force -ErrorAction SilentlyContinue
Write-Host "DecisionAtlas demo stack stopped." -ForegroundColor Green
