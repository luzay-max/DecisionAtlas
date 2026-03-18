Write-Host "Starting DecisionAtlas infrastructure..." -ForegroundColor Cyan
docker compose up -d postgres redis
Write-Host ""
Write-Host "Service URLs" -ForegroundColor Green
Write-Host "Postgres: postgresql://postgres:postgres@localhost:5432/decisionatlas"
Write-Host "Redis: redis://localhost:6379/0"
Write-Host "Engine: http://localhost:8000/health"
Write-Host "API: http://localhost:3001/health"
