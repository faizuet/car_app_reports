# Start Celery worker (Windows - use solo pool)
# Run from project root: .\scripts\celery_worker.ps1

Set-Location $PSScriptRoot\..

Write-Host "Starting Celery worker (solo pool for Windows)..." -ForegroundColor Cyan
.\.venv\Scripts\celery -A car_tasks.celery_app worker --loglevel=info --pool=solo
