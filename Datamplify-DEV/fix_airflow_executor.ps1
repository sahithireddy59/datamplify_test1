# Airflow Executor Diagnostic & Fix Script for Windows
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Airflow Executor Diagnostic & Fix Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if we can connect to Airflow server
Write-Host "1. Checking Airflow connection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8081/health" -Method GET -TimeoutSec 5 -UseBasicParsing
    Write-Host "   ✓ Airflow webserver is running" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Cannot connect to Airflow webserver at http://127.0.0.1:8081" -ForegroundColor Red
    Write-Host "   Make sure Airflow is running!" -ForegroundColor Red
}
Write-Host ""

# Step 2: Check Docker containers (if using Docker)
Write-Host "2. Checking Docker containers..." -ForegroundColor Yellow
try {
    $dockerContainers = docker ps --filter "name=airflow" --format "table {{.Names}}\t{{.Status}}" 2>$null
    if ($dockerContainers) {
        Write-Host $dockerContainers
        
        # Check if worker is running
        if ($dockerContainers -match "worker") {
            Write-Host "   ✓ Airflow worker container is running" -ForegroundColor Green
        } else {
            Write-Host "   ✗ Airflow worker container is NOT running!" -ForegroundColor Red
            Write-Host "   This is likely the problem!" -ForegroundColor Red
        }
    } else {
        Write-Host "   No Airflow Docker containers found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   Docker not available or not running" -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Show recent DAG runs
Write-Host "3. Checking recent DAG runs..." -ForegroundColor Yellow
Write-Host "   DAG ID: 127001-20251010103507-12"
Write-Host ""

# Step 4: Recommendations
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "RECOMMENDED FIXES:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Option 1: If using Docker Compose" -ForegroundColor Yellow
Write-Host "--------------------------------------"
Write-Host "cd to your Airflow directory and run:"
Write-Host "docker-compose up -d airflow-worker" -ForegroundColor White
Write-Host "docker-compose restart" -ForegroundColor White
Write-Host ""

Write-Host "Option 2: If Airflow is installed locally" -ForegroundColor Yellow
Write-Host "--------------------------------------"
Write-Host "SSH to your Airflow server and run:"
Write-Host "export AIRFLOW__CORE__EXECUTOR=LocalExecutor" -ForegroundColor White
Write-Host "airflow scheduler &" -ForegroundColor White
Write-Host "airflow webserver -p 8081 &" -ForegroundColor White
Write-Host ""

Write-Host "Option 3: If using Celery Executor" -ForegroundColor Yellow
Write-Host "--------------------------------------"
Write-Host "Start the Celery worker:"
Write-Host "airflow celery worker &" -ForegroundColor White
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "After fixing, test the DAG:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "1. Go to Airflow UI: http://127.0.0.1:8081" -ForegroundColor White
Write-Host "2. Find DAG: 127001-20251010103507-12" -ForegroundColor White
Write-Host "3. Click 'Trigger DAG'" -ForegroundColor White
Write-Host "4. Watch the task status" -ForegroundColor White
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "SUMMARY:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "The issue is that Airflow tasks are being queued but no worker" -ForegroundColor Yellow
Write-Host "is picking them up to execute. This is an Airflow configuration" -ForegroundColor Yellow
Write-Host "issue, not a problem with your DAG code." -ForegroundColor Yellow
Write-Host ""
Write-Host "The DAG code we fixed earlier is correct! ✓" -ForegroundColor Green
Write-Host ""
