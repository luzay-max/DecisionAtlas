param(
  [string]$WebBaseUrl = "http://127.0.0.1:3000",
  [string]$ApiBaseUrl = "http://127.0.0.1:3001",
  [string]$EngineBaseUrl = "http://127.0.0.1:8000",
  [switch]$SkipDependencyChecks
)

$ErrorActionPreference = "Stop"

function Test-HttpEndpoint {
  param(
    [string]$Name,
    [string]$Url
  )

  try {
    $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -lt 200 -or $response.StatusCode -ge 400) {
      throw "Unexpected HTTP status $($response.StatusCode)"
    }
    Write-Host "[ok] $Name $Url" -ForegroundColor Green
  } catch {
    throw "[fail] $Name $Url - $($_.Exception.Message)"
  }
}

function Test-TcpEndpoint {
  param(
    [string]$Name,
    [string]$HostName,
    [int]$Port
  )

  $result = Test-NetConnection -ComputerName $HostName -Port $Port -WarningAction SilentlyContinue
  if (-not $result.TcpTestSucceeded) {
    throw "[fail] $Name ${HostName}:${Port} is not reachable"
  }

  Write-Host "[ok] $Name ${HostName}:${Port}" -ForegroundColor Green
}

function Get-DatabaseEndpoint {
  param([string]$DatabaseUrl)

  if (-not $DatabaseUrl -or $DatabaseUrl.StartsWith("sqlite")) {
    return $null
  }

  if ($DatabaseUrl -match "@(?<host>[^:/?#]+)(:(?<port>\d+))?") {
    $port = if ($Matches.port) { [int]$Matches.port } else { 5432 }
    return [pscustomobject]@{ host = $Matches.host; port = $port }
  }

  return $null
}

function Get-RedisEndpoint {
  param([string]$RedisUrl)

  if (-not $RedisUrl) {
    return $null
  }

  $uri = [Uri]$RedisUrl
  $port = if ($uri.Port -gt 0) { $uri.Port } else { 6379 }
  return [pscustomobject]@{ host = $uri.Host; port = $port }
}

Write-Host "Checking hosted demo services..." -ForegroundColor Cyan
Test-HttpEndpoint -Name "web" -Url $WebBaseUrl
Test-HttpEndpoint -Name "api" -Url "$($ApiBaseUrl.TrimEnd('/'))/health"
Test-HttpEndpoint -Name "engine" -Url "$($EngineBaseUrl.TrimEnd('/'))/health"

if (-not $SkipDependencyChecks) {
  $databaseEndpoint = Get-DatabaseEndpoint -DatabaseUrl $env:DATABASE_URL
  if ($databaseEndpoint) {
    Test-TcpEndpoint -Name "postgres" -HostName $databaseEndpoint.host -Port $databaseEndpoint.port
  } else {
    Write-Host "[skip] postgres DATABASE_URL not set or uses sqlite" -ForegroundColor Yellow
  }

  $redisEndpoint = Get-RedisEndpoint -RedisUrl $env:REDIS_URL
  if ($redisEndpoint) {
    Test-TcpEndpoint -Name "redis" -HostName $redisEndpoint.host -Port $redisEndpoint.port
  } else {
    Write-Host "[skip] redis REDIS_URL not set" -ForegroundColor Yellow
  }
}

Write-Host "Hosted demo health check passed." -ForegroundColor Green
