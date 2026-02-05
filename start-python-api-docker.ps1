# Start Python API i Docker (för lokal utveckling och moln)
# Detta är det rekommenderade sättet att köra Python API

Write-Host "=== STARTAR PYTHON API I DOCKER ===" -ForegroundColor Green
Write-Host ""

# Kontrollera att Docker körs
$dockerRunning = docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host " Docker körs inte! Starta Docker Desktop först." -ForegroundColor Red
    exit 1
}

# Stoppa eventuella gamla containrar
Write-Host "Stoppar gamla containrar..." -ForegroundColor Yellow
docker compose -f docker-compose.yml -f docker-compose.dev.yml down python-service 2>&1 | Out-Null

# Starta Python API
Write-Host "Startar Python API..." -ForegroundColor Yellow
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d python-service

# Vänta på att containern startar
Write-Host ""
Write-Host "Väntar på att Python API ska starta..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Kontrollera status
$containerStatus = docker ps --filter "name=python-service" --format "{{.Status}}"
if ($containerStatus) {
    Write-Host " Python API körs!" -ForegroundColor Green
    Write-Host "Status: $containerStatus" -ForegroundColor White
    Write-Host ""
    Write-Host "Kontrollerar hälsa..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/api/version1/health" -TimeoutSec 5
        Write-Host " Python API är redo!" -ForegroundColor Green
    } catch {
        Write-Host " Python API startar fortfarande, vänta lite till..." -ForegroundColor Yellow
    }
} else {
    Write-Host " Python API startade inte korrekt" -ForegroundColor Red
    Write-Host "Kolla loggarna med: docker logs genassista-python-python-service-1" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "För att se loggar:" -ForegroundColor Cyan
Write-Host "  docker logs -f genassista-python-python-service-1" -ForegroundColor White
Write-Host ""
Write-Host "För att stoppa:" -ForegroundColor Cyan
Write-Host "  docker compose -f docker-compose.yml -f docker-compose.dev.yml down python-service" -ForegroundColor White
