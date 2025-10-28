"""
Multi-Tenant DAG Utilities for User-Wise Isolation

This module provides utilities for implementing multi-tenant architecture in Airflow DAGs:
1. Pass user_id via dagrun.conf to parameterize tasks
2. Filter configs by user for environment-specific deployments
3. Shard configs into user-specific subfolders

Usage:
    # Option 1: Single DAG per process, parameterized by user_id
    from multi_tenant_utils import get_user_from_dagrun, filter_data_by_user
    
    # Option 2: Shard configs by user into separate subfolders
    from multi_tenant_utils import get_user_configs, filter_configs_by_env
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Generator
from pathlib import Path
from datetime import datetime

log = logging.getLogger(__name__)


# ============================================
# OPTION 1: User-ID Parameterization
# ============================================

def get_user_from_dagrun(context: Dict[str, Any]) -> Optional[str]:
    """
    Extract user_id from DAG run configuration.
    
    Args:
        context: Airflow task context containing dag_run
        
    Returns:
        user_id as string, or None if not found
        
    Example:
        def my_task(**context):
            user_id = get_user_from_dagrun(context)
            # Use user_id to filter data
    """
    dag_run = context.get('dag_run')
    if not dag_run:
        log.warning("No dag_run found in context")
        return None
    
    conf = dag_run.conf or {}
    user_id = conf.get('user_id')
    
    if not user_id:
        log.warning("No user_id found in dag_run.conf")
        return None
        
    log.info(f"Extracted user_id: {user_id}")
    return str(user_id)


def get_user_metadata_from_dagrun(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract all user-related metadata from DAG run configuration.
    
    Args:
        context: Airflow task context
        
    Returns:
        Dictionary containing user_id, username, tenant_id, etc.
    """
    dag_run = context.get('dag_run')
    if not dag_run:
        return {}
    
    conf = dag_run.conf or {}
    
    return {
        'user_id': conf.get('user_id'),
        'username': conf.get('username'),
        'tenant_id': conf.get('tenant_id'),
        'environment': conf.get('environment', 'production'),
        'user_role': conf.get('user_role', 'standard_user')
    }


def filter_data_by_user(data: Any, user_id: str, user_field: str = 'user_id') -> Any:
    """
    Filter data sources/sinks by user_id for multi-tenant isolation.
    
    Args:
        data: Data to filter (list, dict, or query result)
        user_id: User identifier
        user_field: Field name containing user_id
        
    Returns:
        Filtered data containing only user's records
    """
    if isinstance(data, list):
        return [item for item in data if item.get(user_field) == user_id]
    elif isinstance(data, dict):
        return data if data.get(user_field) == user_id else {}
    return data


def build_user_scoped_query(base_query: str, user_id: str, user_column: str = 'user_id') -> str:
    """
    Add user_id filter to SQL query for multi-tenant data isolation.
    
    Args:
        base_query: Original SQL query
        user_id: User identifier
        user_column: Column name for user filtering
        
    Returns:
        Modified query with user filter
        
    Example:
        query = "SELECT * FROM orders"
        scoped = build_user_scoped_query(query, "user-123")
        # Result: "SELECT * FROM orders WHERE user_id = 'user-123'"
    """
    query = base_query.strip().rstrip(';')
    
    # Check if WHERE clause exists
    if 'WHERE' in query.upper():
        return f"{query} AND {user_column} = '{user_id}'"
    else:
        return f"{query} WHERE {user_column} = '{user_id}'"


def get_user_specific_path(base_path: str, user_id: str) -> str:
    """
    Generate user-specific file path for data isolation.
    
    Args:
        base_path: Base directory or file path
        user_id: User identifier
        
    Returns:
        User-scoped path
        
    Example:
        path = get_user_specific_path("/data/output.csv", "user-123")
        # Result: "/data/user-123/output.csv"
    """
    base_dir = os.path.dirname(base_path)
    filename = os.path.basename(base_path)
    return os.path.join(base_dir, str(user_id), filename)


# ============================================
# OPTION 2: Config Sharding by User
# ============================================

def get_user_configs(config_dir: str, user_id: Optional[str] = None) -> Generator[tuple, None, None]:
    """
    Fetch configs from user-specific subfolders.
    
    Directory structure:
        /var/www/Configs/FlowBoard/
            user-123/
                flow-1.json
                flow-2.json
            user-456/
                flow-3.json
    
    Args:
        config_dir: Base configuration directory
        user_id: Optional user filter (if None, returns all users)
        
    Yields:
        Tuples of (flow_id, user_id, config_dict)
    """
    if not os.path.exists(config_dir):
        log.error(f"Config directory not found: {config_dir}")
        return
    
    # If user_id specified, only scan that user's folder
    if user_id:
        user_dirs = [os.path.join(config_dir, str(user_id))]
    else:
        user_dirs = [
            os.path.join(config_dir, d) 
            for d in os.listdir(config_dir) 
            if os.path.isdir(os.path.join(config_dir, d))
        ]
    
    for user_dir in user_dirs:
        if not os.path.isdir(user_dir):
            continue
            
        current_user_id = os.path.basename(user_dir)
        
        for filename in os.listdir(user_dir):
            if not filename.endswith('.json'):
                continue
                
            flow_id = filename[:-5]  # Remove .json extension
            filepath = os.path.join(user_dir, filename)
            
            try:
                with open(filepath, 'r') as f:
                    config = json.load(f)
                    yield flow_id, current_user_id, config
            except Exception as e:
                log.error(f"Failed to load config {filepath}: {e}")


def filter_configs_by_env(
    config_dir: str, 
    environment: str = 'production',
    user_filter: Optional[List[str]] = None
) -> Generator[tuple, None, None]:
    """
    Filter configs by environment and optionally by user list.
    
    Args:
        config_dir: Base configuration directory
        environment: Target environment (production, staging, dev)
        user_filter: Optional list of user_ids to include
        
    Yields:
        Tuples of (flow_id, user_id, config_dict) matching filters
        
    Example:
        # Deploy only specific users' DAGs
        for flow_id, user_id, config in filter_configs_by_env(
            '/var/www/Configs/FlowBoard',
            environment='production',
            user_filter=['user-123', 'user-456']
        ):
            generate_dag(flow_id, user_id, config)
    """
    for flow_id, user_id, config in get_user_configs(config_dir):
        # Filter by environment
        config_env = config.get('environment', 'production')
        if config_env != environment:
            continue
        
        # Filter by user list if provided
        if user_filter and user_id not in user_filter:
            continue
            
        yield flow_id, user_id, config


def get_only_configs_filter(
    config_dir: str,
    only_configs: Optional[str] = None
) -> Generator[tuple, None, None]:
    """
    Filter configs using ONLY_CONFIGS environment variable pattern.
    
    Args:
        config_dir: Base configuration directory
        only_configs: Comma-separated list of flow_ids or user_ids
                     Format: "flow-1,flow-2" or "user:user-123,user-456"
        
    Yields:
        Filtered configs matching the ONLY_CONFIGS pattern
        
    Example:
        # Set environment variable
        export ONLY_CONFIGS="user:user-123,user-456"
        
        # In DAG file
        only = os.getenv('ONLY_CONFIGS')
        for flow_id, user_id, config in get_only_configs_filter(CONFIG_DIR, only):
            generate_dag(flow_id, user_id, config)
    """
    if not only_configs:
        # No filter, return all
        yield from get_user_configs(config_dir)
        return
    
    filters = [f.strip() for f in only_configs.split(',')]
    
    # Check if filtering by user
    user_filter = None
    flow_filter = []
    
    for f in filters:
        if f.startswith('user:'):
            # Extract user IDs after "user:"
            user_ids = f[5:].split(',')
            user_filter = [u.strip() for u in user_ids]
        else:
            flow_filter.append(f)
    
    for flow_id, user_id, config in get_user_configs(config_dir):
        # Apply user filter
        if user_filter and user_id not in user_filter:
            continue
        
        # Apply flow filter
        if flow_filter and flow_id not in flow_filter:
            continue
            
        yield flow_id, user_id, config


# ============================================
# User-Scoped Connection Management
# ============================================

def get_user_connection_id(base_conn_id: str, user_id: str) -> str:
    """
    Generate user-specific connection ID for Airflow connections.
    
    Args:
        base_conn_id: Base connection identifier
        user_id: User identifier
        
    Returns:
        User-scoped connection ID
        
    Example:
        conn_id = get_user_connection_id("postgres_default", "user-123")
        # Result: "postgres_default_user_123"
    """
    safe_user_id = str(user_id).replace('-', '_')
    return f"{base_conn_id}_{safe_user_id}"


def get_user_schema(base_schema: str, user_id: str) -> str:
    """
    Generate user-specific database schema name.
    
    Args:
        base_schema: Base schema name
        user_id: User identifier
        
    Returns:
        User-scoped schema name
    """
    safe_user_id = str(user_id).replace('-', '_')
    return f"{base_schema}_{safe_user_id}"


# ============================================
# DAG Triggering with User Context
# ============================================

def trigger_dag_with_user_context(
    dag_id: str,
    user_id: str,
    additional_conf: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build configuration for triggering a DAG with user context.
    
    Args:
        dag_id: Target DAG ID
        user_id: User identifier
        additional_conf: Additional configuration parameters
        
    Returns:
        Configuration dict for TriggerDagRunOperator
        
    Example:
        from airflow.operators.trigger_dagrun import TriggerDagRunOperator
        
        trigger_task = TriggerDagRunOperator(
            task_id='trigger_user_dag',
            trigger_dag_id='process_user_data',
            conf=trigger_dag_with_user_context(
                'process_user_data',
                user_id='user-123',
                additional_conf={'batch_size': 1000}
            )
        )
    """
    conf = {
        'user_id': user_id,
        'triggered_at': str(datetime.now()),
        'parent_dag_id': dag_id
    }
    
    if additional_conf:
        conf.update(additional_conf)
    
    return conf


# ============================================
# User-Scoped XCom Management
# ============================================

def push_user_xcom(ti, key: str, value: Any, user_id: str):
    """
    Push XCom value with user-scoped key.
    
    Args:
        ti: Task instance
        key: XCom key
        value: Value to store
        user_id: User identifier
    """
    scoped_key = f"user_{user_id}_{key}"
    ti.xcom_push(key=scoped_key, value=value)
    log.info(f"Pushed XCom: {scoped_key}")


def pull_user_xcom(ti, key: str, user_id: str, task_ids=None) -> Any:
    """
    Pull XCom value with user-scoped key.
    
    Args:
        ti: Task instance
        key: XCom key
        user_id: User identifier
        task_ids: Optional task IDs to pull from
        
    Returns:
        XCom value
    """
    scoped_key = f"user_{user_id}_{key}"
    value = ti.xcom_pull(key=scoped_key, task_ids=task_ids)
    log.info(f"Pulled XCom: {scoped_key}")
    return value


# ============================================
# Monitoring & Logging
# ============================================

def log_user_activity(user_id: str, action: str, details: Dict[str, Any]):
    """
    Log user-specific activity for audit and monitoring.
    
    Args:
        user_id: User identifier
        action: Action performed
        details: Additional details
    """
    log.info(f"[USER:{user_id}] {action} | Details: {details}")


def create_user_run_history(
    run_id: str,
    user_id: str,
    source_type: str,
    source_id: str,
    name: str,
    status: str = 'running'
):
    """
    Create run history entry for user-specific DAG execution.
    
    Args:
        run_id: DAG run ID
        user_id: User identifier
        source_type: Type of source (flowboard, taskplan)
        source_id: Source identifier
        name: Run name
        status: Initial status
    """
    from Monitor.models import RunHistory
    
    RunHistory.objects.create(
        run_id=run_id,
        source_type=source_type,
        source_id=source_id,
        name=name,
        status=status,
        user_id=user_id
    )
    log.info(f"Created run history for user {user_id}: {run_id}")


# ============================================
# Utility Functions
# ============================================

def validate_user_access(user_id: str, resource_id: str, resource_type: str) -> bool:
    """
    Validate if user has access to a specific resource.
    
    Args:
        user_id: User identifier
        resource_id: Resource identifier
        resource_type: Type of resource (flowboard, taskplan, connection)
        
    Returns:
        True if user has access, False otherwise
    """
    try:
        if resource_type == 'flowboard':
            from FlowBoard.models import FlowBoard
            return FlowBoard.objects.filter(
                Flow_id=resource_id,
                user_id=user_id
            ).exists()
        elif resource_type == 'taskplan':
            from TaskPlan.models import TaskPlan
            return TaskPlan.objects.filter(
                id=resource_id,
                user_id=user_id
            ).exists()
        return False
    except Exception as e:
        log.error(f"Error validating user access: {e}")
        return False


def get_user_resource_quota(user_id: str) -> Dict[str, int]:
    """
    Get resource quotas for a specific user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Dictionary with quota limits
    """
    return {
        'max_concurrent_dags': 10,
        'max_task_instances': 100,
        'max_storage_mb': 10240,
        'max_execution_time_minutes': 60
    }
