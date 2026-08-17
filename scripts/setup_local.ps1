# Local development setup (Windows PowerShell)
# Run from project root:  .\scripts\setup_local.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "=== Car App Reports - Local Setup ===" -ForegroundColor Cyan

# 1. .env file
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example"
} else {
    Write-Host ".env already exists"
}

# 2. Virtual environment
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

Write-Host "Installing Python dependencies..."
.\.venv\Scripts\pip install -r requirements.txt -q

# 3. Docker services
Write-Host "Starting PostgreSQL, Redis, Neo4j via Docker..."
docker compose up db redis neo4j -d

Write-Host "Waiting for PostgreSQL to be ready..."
Start-Sleep -Seconds 8

# 4. Database migrations
Write-Host "Running Alembic migrations..."
.\.venv\Scripts\alembic upgrade head

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Start the API (terminal 1):" -ForegroundColor Yellow
Write-Host "  .\.venv\Scripts\uvicorn app.main:app --reload"
Write-Host ""
Write-Host "Start Celery worker (terminal 2):" -ForegroundColor Yellow
Write-Host "  .\scripts\celery_worker.ps1"
Write-Host ""
Write-Host "Start Celery beat (terminal 3, optional):" -ForegroundColor Yellow
Write-Host "  .\.venv\Scripts\celery -A car_tasks.celery_app beat --loglevel=info"
Write-Host ""
Write-Host "Manual sync for test data:" -ForegroundColor Yellow
Write-Host "  .\.venv\Scripts\celery -A car_tasks.celery_app call car_tasks.sync_cars.sync_car_data"
Write-Host ""
Write-Host "API docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Start frontend UI (terminal 4):" -ForegroundColor Yellow
Write-Host "  .\scripts\start_frontend.ps1"
Write-Host "  (requires Node.js — OR run: docker compose up frontend -d)"
Write-Host ""
Write-Host "Frontend UI: http://localhost:5173" -ForegroundColor Cyan
