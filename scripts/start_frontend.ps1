# Start frontend dev server (requires Node.js 18+)
# Run from project root: .\scripts\start_frontend.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js/npm not found. Install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

Set-Location frontend

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created frontend/.env"
}

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm packages..."
    npm install
}

Write-Host "Starting frontend at http://localhost:5173" -ForegroundColor Cyan
Write-Host "Ensure backend is running at http://localhost:8000" -ForegroundColor Yellow
npm run dev
