# Multi-Tenant Airflow DAG Architecture

## Quick Start Guide

This implementation provides **user-wise DAG isolation** for multi-tenant ETL operations.

---

## 🎯 Key Features

✅ **Complete User Isolation** - Each user's data is fully isolated  
✅ **No Timeouts** - User-wise DAGs run without global timeout constraints  
✅ **Scalable** - Supports 10,000+ users efficiently  
✅ **Flexible Deployment** - Deploy all users or specific subsets  
✅ **Environment Filtering** - Filter DAGs by environment (production, staging, dev)  

---

## 📁 Directory Structure

```
/var/www/Configs/
├── FlowBoard/
│   ├── user-123/
│   │   ├── flow-1.json
│   │   └── flow-2.json
│   └── user-456/
│       └── flow-3.json
└── TaskPlan/
    ├── user-123/
    │   └── task-1.json
    └── user-456/
        └── task-2.json
```

---

## 🚀 Usage

### 1. Deploy All Users (Default)

```bash
# No filtering - all DAGs will be loaded
unset ONLY_CONFIGS
airflow scheduler
```

### 2. Filter by Specific Users

```bash
# Deploy only specific users' DAGs
export ONLY_CONFIGS="user:user-123,user-456"
airflow scheduler
```

### 3. Filter by Specific Flows

```bash
# Deploy only specific flow IDs
export ONLY_CONFIGS="flow-1,flow-2,flow-3"
airflow scheduler
```

### 4. Environment-Based Deployment

```bash
# Deploy production environment only
export AIRFLOW_ENV="production"
airflow scheduler
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ONLY_CONFIGS` | Filter DAGs by user or flow | `"user:user-123,user-456"` or `"flow-1,flow-2"` |
| `AIRFLOW_ENV` | Target environment | `"production"`, `"staging"`, `"development"` |

### Config File Format

Each user's config files should be placed in their respective folders:

```json
{
  "user_id": "user-123",
  "username": "alice",
  "flow_name": "ETL Pipeline",
  "environment": "production",
  "tasks": [
    {
      "id": "task1",
      "type": "source_data_object",
      "format": "csv",
      "path": "/data/input.csv"
    }
  ]
}
```

---

## 📊 Monitoring

### View Logs

```bash
# FlowBoard DAG logs
airflow dags list | grep FlowBoard

# TaskPlan DAG logs
airflow dags list | grep TaskPlan

# Check specific DAG
airflow dags show <dag_id>
```

### User Activity Logging

All user activities are logged with the format:
```
[USER:user-123] dag_registration | Details: {'dag_id': 'flow-1', 'flow_name': 'ETL Pipeline'}
```

---

## 🔍 Troubleshooting

### Issue: No DAGs Loading

**Check:**
1. Config directory exists: `/var/www/Configs/FlowBoard/` or `/opt/airflow/project/Configs/TaskPlan/`
2. User subdirectories exist
3. JSON files are valid
4. `ONLY_CONFIGS` syntax is correct

**Solution:**
```bash
# Verify directory structure
ls -R /var/www/Configs/FlowBoard/

# Check Airflow logs
airflow scheduler --log-file /tmp/scheduler.log
```

### Issue: ONLY_CONFIGS Not Working

**Correct Syntax:**
```bash
# Filter by users (note the "user:" prefix)
export ONLY_CONFIGS="user:user-123,user-456"

# Filter by flows (no prefix)
export ONLY_CONFIGS="flow-1,flow-2"
```

### Issue: DAG Parse Errors

**Check logs:**
```bash
# View scheduler logs
tail -f $AIRFLOW_HOME/logs/scheduler/latest/*.log

# Or check specific DAG
airflow dags test <dag_id> <execution_date>
```

---

## 🏗️ Architecture

### Multi-Tenant Flow

```
┌─────────────────────────────────────────┐
│   Airflow Scheduler                     │
│                                         │
│   ┌─────────────────────────────────┐  │
│   │  Config Loading                 │  │
│   │  • Check ONLY_CONFIGS           │  │
│   │  • Filter by user/flow          │  │
│   │  • Load JSON configs            │  │
│   └─────────────────────────────────┘  │
│                 │                       │
│                 ▼                       │
│   ┌─────────────────────────────────┐  │
│   │  DAG Registration               │  │
│   │  • User-123 DAGs                │  │
│   │  • User-456 DAGs                │  │
│   │  • User-789 DAGs                │  │
│   └─────────────────────────────────┘  │
└─────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│   User-Isolated Execution               │
│   • Separate data sources               │
│   • Separate schemas                    │
│   • Separate file paths                 │
└─────────────────────────────────────────┘
```

---

## 📝 Best Practices

### 1. Organize Configs by User

```
/var/www/Configs/FlowBoard/
  ├── user-123/          # Production user
  ├── user-456/          # Staging user
  └── user-789/          # Development user
```

### 2. Use Environment Tags

Add environment tags to your configs:
```json
{
  "environment": "production",
  "user_id": "user-123"
}
```

### 3. Monitor User Activity

Check logs regularly for user-specific activities:
```bash
grep "USER:user-123" $AIRFLOW_HOME/logs/scheduler/latest/*.log
```

### 4. Test Before Deployment

```bash
# Test with single user first
export ONLY_CONFIGS="user:test-user"
airflow dags list

# Then deploy to production
export ONLY_CONFIGS="user:prod-user-1,prod-user-2"
```

---

## 🔐 Security Considerations

1. **User Isolation**: Each user's data is completely isolated
2. **Access Control**: Validate user access before processing resources
3. **Audit Logging**: All user activities are logged
4. **Config Validation**: JSON configs are validated before loading

---

## 📚 Additional Resources

- **`multi_tenant_utils.py`** - Core utility functions
- **FlowBoard.py** - FlowBoard DAG implementation
- **TaskPlan.py** - TaskPlan DAG implementation

---

## 🆘 Support

For issues or questions:
1. Check Airflow scheduler logs
2. Verify config directory structure
3. Test with `ONLY_CONFIGS` filtering
4. Review `multi_tenant_utils.py` for available functions

---

## Summary

This multi-tenant architecture provides complete user isolation for Airflow DAGs with flexible deployment options:

- **Pattern 1**: Filter by user - `ONLY_CONFIGS="user:user-123"`
- **Pattern 2**: Filter by flow - `ONLY_CONFIGS="flow-1,flow-2"`
- **Pattern 3**: No filter - Load all DAGs

Choose the pattern that best fits your deployment needs!
