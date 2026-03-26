$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$statePath = Join-Path $repoRoot ".tmp\real-stack.json"
$targetPorts = @(3000, 3001, 8000)

function Stop-ManagedPid {
  param([int]$ProcessId)

  if (-not $ProcessId) {
    return
  }

  $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
  if ($process) {
    Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
  }
}

function Stop-PortListeners {
  param([int[]]$Ports)

  $listeners = Get-NetTCPConnection -LocalPort $Ports -State Listen -ErrorAction SilentlyContinue
  if (-not $listeners) {
    return
  }

  $processIds = $listeners | Select-Object -ExpandProperty OwningProcess -Unique
  foreach ($processId in $processIds) {
    Stop-ManagedPid -ProcessId $processId
  }
}

if (Test-Path $statePath) {
  $state = Get-Content $statePath | ConvertFrom-Json

  foreach ($service in $state.services) {
    Stop-ManagedPid -ProcessId $service.pid
  }

  Remove-Item $statePath -Force -ErrorAction SilentlyContinue
} else {
  Write-Host "No managed real stack state found. Falling back to port-based shutdown..." -ForegroundColor Yellow
}

Stop-PortListeners -Ports $targetPorts
Set-Location $repoRoot
docker compose stop postgres redis | Out-Null

Write-Host "DecisionAtlas real stack stopped." -ForegroundColor Green
