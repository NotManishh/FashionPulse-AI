# PowerShell script to run FashionPulse AI locally
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Starting FashionPulse AI Platform (Local Dev Server)    " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$projectRoot = Split-Path -Parent $PSScriptRoot

# 1. Seed demo data if database does not exist
$dbPath = Join-Path $projectRoot "fashionpulse.db"
if (-Not (Test-Path $dbPath)) {
    Write-Host "[1/3] Initializing database and generating seed observations..." -ForegroundColor Yellow
    python "$projectRoot\scripts\seed_demo_data.py"
}

# 2. Start Backend FastAPI
Write-Host "[2/3] Starting FastAPI backend on http://127.0.0.1:8000..." -ForegroundColor Green
$backendJob = Start-Process python -ArgumentList "-m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload" -PassThru

# 3. Start Frontend Vite
Write-Host "[3/3] Starting Vite frontend on http://localhost:5173..." -ForegroundColor Green
Set-Location "$projectRoot\frontend"
npm run dev

# Cleanup when frontend exits
Stop-Process -Id $backendJob.Id -Force -ErrorAction SilentlyContinue
