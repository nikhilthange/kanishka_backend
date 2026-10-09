<#
.SYNOPSIS
    Convenience CLI script for evaluation & development.
.DESCRIPTION
    Usage:
        .\run.ps1 test     - Run all 33 automated tests
        .\run.ps1 seed     - Seed the database with sample users and tasks
        .\run.ps1 migrate  - Run Alembic database migrations
        .\run.ps1 start    - Start development server with hot-reload
#>
param(
    [Parameter(Position=0)]
    [ValidateSet("test", "seed", "migrate", "start")]
    [string]$Command = "start"
)

$ErrorActionPreference = "Stop"

switch ($Command) {
    "test" {
        Write-Host "Running pytest test suite..." -ForegroundColor Cyan
        & ".\venv\Scripts\pytest.exe" -v
    }
    "seed" {
        Write-Host "Running database seeder..." -ForegroundColor Cyan
        & ".\venv\Scripts\python.exe" seed.py
    }
    "migrate" {
        Write-Host "Running Alembic migrations..." -ForegroundColor Cyan
        & ".\venv\Scripts\alembic.exe" upgrade head
    }
    "start" {
        Write-Host "Starting FastAPI server at http://127.0.0.1:8000 (Docs at /docs)..." -ForegroundColor Green
        & ".\venv\Scripts\uvicorn.exe" app.main:app --host 0.0.0.0 --port 8000 --reload
    }
}
