$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$stateDir = Join-Path $repoRoot ".tmp"
$logDir = Join-Path $stateDir "real-stack"
$statePath = Join-Path $stateDir "real-stack.json"
$powerShellPath = (Get-Process -Id $PID).Path

function Ensure-Directory {
  param([string]$Path)

  if (-not (Test-Path $Path)) {
    New-Item -ItemType Directory -Path $Path | Out-Null
  }
}

function Wait-HttpReady {
  param(
    [string]$Url,
    [int]$TimeoutSeconds = 120
  )

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    try {
      Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5 | Out-Null
      return
    } catch {
      Start-Sleep -Seconds 2
    }
  }

  throw "Timed out waiting for $Url"
}

function Get-PortOwnerDescription {
  param([int]$Port)

  $listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
  if (-not $listeners) {
    return $null
  }

  $processIds = $listeners | Select-Object -ExpandProperty OwningProcess -Unique
  $details = foreach ($processId in $processIds) {
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($process) {
      "{0} ({1})" -f $process.Id, $process.ProcessName
    } else {
      "$processId (unknown)"
    }
  }

  return ($details -join ", ")
}

function Assert-PortFree {
  param([int]$Port)

  $owner = Get-PortOwnerDescription -Port $Port
  if (-not $owner) {
    return
  }

  throw "Port $Port is already in use by: $owner"
}

function Assert-DockerPostgresProxy {
  $owner = Get-PortOwnerDescription -Port 5432
  if (-not $owner) {
    throw "Port 5432 is not listening. Start Docker Desktop and ensure the postgres container is published on 5432."
  }

  if ($owner -notmatch "com\.docker\.backend") {
    throw "Port 5432 is owned by $owner, not Docker. Stop the local Postgres service or change the project database port before starting the real stack."
  }
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

function Start-ManagedProcess {
  param(
    [string]$Name,
    [string]$Command,
    [string]$WorkingDirectory
  )

  $stdoutPath = Join-Path $logDir "$Name.stdout.log"
  $stderrPath = Join-Path $logDir "$Name.stderr.log"

  Remove-Item $stdoutPath, $stderrPath -Force -ErrorAction SilentlyContinue

  $process = Start-Process `
    -FilePath $powerShellPath `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $Command) `
    -WorkingDirectory $WorkingDirectory `
    -WindowStyle Hidden `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError $stderrPath `
    -PassThru

  return [pscustomobject]@{
    name = $Name
    pid = $process.Id
    stdout = $stdoutPath
    stderr = $stderrPath
  }
}

Ensure-Directory $stateDir
Ensure-Directory $logDir

Write-Host "Stopping any existing real stack processes first..." -ForegroundColor Yellow
& (Join-Path $PSScriptRoot "stop-real-stack.ps1") | Out-Null

Set-Location $repoRoot

Write-Host "Starting Docker postgres and redis..." -ForegroundColor Cyan
docker compose up -d postgres redis | Out-Null

Assert-DockerPostgresProxy

$databaseUrl = "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/decisionatlas"
$engineBaseUrl = "http://127.0.0.1:8000"
$apiBaseUrl = "http://127.0.0.1:3001"
$redisUrl = "redis://127.0.0.1:6379/0"

Write-Host "Running migrations..." -ForegroundColor Cyan
Set-Location (Join-Path $repoRoot "services\engine")
$env:DATABASE_URL = $databaseUrl
$env:REDIS_URL = $redisUrl
Invoke-Uv run alembic upgrade head

Write-Host "Seeding demo workspace into Postgres..." -ForegroundColor Cyan
Invoke-Uv run python -m app.db.seed_demo
Set-Location $repoRoot

foreach ($port in 8000, 3001, 3000) {
  Assert-PortFree -Port $port
}

$engineCommand = @"
`$env:DATABASE_URL = '$databaseUrl'
`$env:REDIS_URL = '$redisUrl'
Set-Location '$($repoRoot.Path)\services\engine'
if (Get-Command uv -ErrorAction SilentlyContinue) {
  uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
} else {
  python -m uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
}
"@

$apiCommand = @"
`$env:ENGINE_BASE_URL = '$engineBaseUrl'
`$env:PORT = '3001'
Set-Location '$($repoRoot.Path)'
pnpm --filter @decisionatlas/api dev
"@

$webCommand = @"
`$env:API_BASE_URL = '$apiBaseUrl'
Set-Location '$($repoRoot.Path)'
pnpm --filter @decisionatlas/web exec next dev --hostname 127.0.0.1 --port 3000
"@

Write-Host "Starting engine..." -ForegroundColor Cyan
$engineProcess = Start-ManagedProcess -Name "engine" -Command $engineCommand -WorkingDirectory (Join-Path $repoRoot "services\engine")
Wait-HttpReady -Url "$engineBaseUrl/health"

Write-Host "Starting API..." -ForegroundColor Cyan
$apiProcess = Start-ManagedProcess -Name "api" -Command $apiCommand -WorkingDirectory $repoRoot
Wait-HttpReady -Url "$apiBaseUrl/health"

Write-Host "Starting web..." -ForegroundColor Cyan
$webProcess = Start-ManagedProcess -Name "web" -Command $webCommand -WorkingDirectory $repoRoot
Wait-HttpReady -Url "http://127.0.0.1:3000"

@{
  started_at = (Get-Date).ToString("o")
  database_url = $databaseUrl
  redis_url = $redisUrl
  services = @($engineProcess, $apiProcess, $webProcess)
} | ConvertTo-Json -Depth 4 | Set-Content -Path $statePath

Write-Host ""
Write-Host "DecisionAtlas real stack is running." -ForegroundColor Green
Write-Host "Web:    http://127.0.0.1:3000" -ForegroundColor Green
Write-Host "API:    http://127.0.0.1:3001/health" -ForegroundColor Green
Write-Host "Engine: http://127.0.0.1:8000/health" -ForegroundColor Green
Write-Host ""
Write-Host "Stop the stack with:" -ForegroundColor DarkCyan
Write-Host "powershell -ExecutionPolicy Bypass -File .\scripts\dev\stop-real-stack.ps1"
