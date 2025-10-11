# Celery Worker Startup Script
# This script starts the Celery worker with optimized logging configuration

Write-Host "Starting Celery Worker for Video Generation..." -ForegroundColor Cyan

# Change to project directory
Set-Location -Path "D:\dev\fastapi_web"

# Create logs directory if it doesn't exist
$logsDir = "logs\celery"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    Write-Host "Created logs directory: $logsDir" -ForegroundColor Green
}

# Get current date for log file name
$currentDate = Get-Date -Format "yyyy-MM-dd"
$logFile = "$logsDir\worker_$currentDate.log"

Write-Host "Logs will be saved to: $logFile" -ForegroundColor Green
Write-Host "Log Level: INFO" -ForegroundColor Green
Write-Host "Pool Type: solo (Windows compatible)" -ForegroundColor Green
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
Write-Host ""

# Start Celery worker
& ".\fastapp\Scripts\celery.exe" --app celery_app worker --loglevel=INFO --pool=solo --logfile="$logFile" --concurrency=1
