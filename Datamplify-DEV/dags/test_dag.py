from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator

# Simple test DAG to verify Airflow is working
default_args = {
    'owner': 'test',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 0,
}

# Create a simple test DAG
test_dag = DAG(
    'test_simple_dag',
    default_args=default_args,
    description='Simple test DAG',
    schedule_interval=None,
    catchup=False,
)

start_task = DummyOperator(
    task_id='start',
    dag=test_dag,
)

# Also create the specific DAG that should be triggered
flowboard_dag = DAG(
    '127001-20250821105336-1',
    default_args=default_args,
    description='FlowBoard DAG for testing',
    schedule_interval=None,
    catchup=False,
)

flowboard_start = DummyOperator(
    task_id='flowboard_start',
    dag=flowboard_dag,
)
