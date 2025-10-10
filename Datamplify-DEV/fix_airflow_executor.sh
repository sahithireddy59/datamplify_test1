#!/bin/bash

echo "=========================================="
echo "Airflow Executor Diagnostic & Fix Script"
echo "=========================================="
echo ""

# Step 1: Check current executor
echo "1. Checking current executor configuration..."
EXECUTOR=$(python3 -c "from airflow.configuration import conf; print(conf.get('core', 'executor'))" 2>/dev/null)
echo "   Current Executor: $EXECUTOR"
echo ""

# Step 2: Check database
echo "2. Checking database configuration..."
DB_CONN=$(python3 -c "from airflow.configuration import conf; print(conf.get('database', 'sql_alchemy_conn'))" 2>/dev/null)
echo "   Database: $DB_CONN"
echo ""

# Step 3: Check running processes
echo "3. Checking Airflow processes..."
ps aux | grep -E "airflow (scheduler|webserver|worker)" | grep -v grep
echo ""

# Step 4: Check if using Docker
echo "4. Checking Docker containers..."
if command -v docker &> /dev/null; then
    docker ps | grep airflow
else
    echo "   Docker not found or not running"
fi
echo ""

# Step 5: Recommend fix
echo "=========================================="
echo "RECOMMENDED FIX:"
echo "=========================================="

if [[ "$EXECUTOR" == "SequentialExecutor" ]]; then
    echo "⚠️  You are using SequentialExecutor (very limited!)"
    echo ""
    echo "Run these commands to fix:"
    echo ""
    echo "# Stop Airflow"
    echo "pkill -f airflow"
    echo ""
    echo "# Set LocalExecutor"
    echo "export AIRFLOW__CORE__EXECUTOR=LocalExecutor"
    echo ""
    echo "# Restart Airflow"
    echo "airflow scheduler &"
    echo "airflow webserver -p 8081 &"
    echo ""
elif [[ "$EXECUTOR" == "CeleryExecutor" ]]; then
    echo "✓ You are using CeleryExecutor"
    echo ""
    echo "Make sure Celery worker is running:"
    echo "airflow celery worker &"
    echo ""
elif [[ "$EXECUTOR" == "LocalExecutor" ]]; then
    echo "✓ You are using LocalExecutor"
    echo ""
    echo "Check if scheduler is running. If not:"
    echo "airflow scheduler &"
    echo ""
fi

echo "=========================================="
echo "After fixing, clear and re-trigger DAG:"
echo "=========================================="
echo "airflow dags trigger 127001-20251010103507-12"
echo ""
