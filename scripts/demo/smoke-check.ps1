param(
  [string]$WebBaseUrl = "http://127.0.0.1:3000",
  [string]$ApiBaseUrl = "http://127.0.0.1:3001",
  [string]$EngineBaseUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

& (Join-Path $PSScriptRoot "health-check.ps1") `
  -WebBaseUrl $WebBaseUrl `
  -ApiBaseUrl $ApiBaseUrl `
  -EngineBaseUrl $EngineBaseUrl `
  -SkipDependencyChecks

Set-Location $repoRoot
$env:PLAYWRIGHT_BASE_URL = $WebBaseUrl.TrimEnd("/")
$env:PLAYWRIGHT_SKIP_WEBSERVER = "1"

Write-Host "Running hosted guided-demo smoke check against $env:PLAYWRIGHT_BASE_URL ..." -ForegroundColor Cyan
pnpm --filter @decisionatlas/web exec playwright test tests-e2e/demo-smoke.spec.ts
Write-Host "Hosted guided-demo smoke check passed." -ForegroundColor Green
