from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime
import os, json, sys, django, textwrap, uuid
from airflow.providers.smtp.operators.smtp import EmailOperator
from airflow.sensors.python import PythonSensor
from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.task_group import TaskGroup
from airflow.utils.state import State
import traceback
from airflow.utils import timezone
from datetime import timezone,datetime
from airflow.exceptions import AirflowFailException





# FlowBoard Functionalities:
# 1.Expression,
# 2.Joins
# 3.Remove duplicates
# 4.Filter
# 5.Extraction
import sys
sys.path.insert(0, "/var/www/Datamplify")

from django_setup import setup_django
setup_django()
  # 👈 Ensures Django is ready

from Datamplify import settings 
from TaskPlan.utils import run_sql_commands 
from FlowBoard.utils import (Extraction,Loading,ETL_Filter,Remove_duplicates,Expressions,Join,Rank,Union,Router,Normalizer)
from Connections.utils import generate_engine
from Monitor.models import RunHistory


GLOBAL_PARAM_HOLDER = '__global_param_store__'



# def check_dag_status(**context):
#     ti = context['ti']
#     dag_run = ti.get_dagrun()
#     failed_tasks = []

#     for task_instance in dag_run.get_task_instances():
#         if task_instance.task_id not in ['dag_success_marker', 'cleanup_temporary_tables'] \
#                 and task_instance.state != State.SUCCESS:
#             failed_tasks.append((task_instance.task_id, task_instance.state))


#     if failed_tasks:
#         raise Exception(f"DAG failed due to task(s): {failed_tasks}")

def cleanup_on_success(tasks_list,user_id,hierarchy_id,**kwargs):
    """
    Cleans Temporary Tables Created by Each Task Instances and it run End of The Pipeline
    """
    ti = kwargs['ti']
    if not user_id or not hierarchy_id:
        return

    engine_data = generate_engine(hierarchy_id, user_id)
    engine = engine_data['engine']
    schema = engine_data['schema']
    for task_id in tasks_list:
        table_name = ti.xcom_pull(task_ids=task_id, key=task_id)

        if table_name and table_name is not None:
            with engine.connect() as cursor:
                cursor.execute(f'DROP TABLE IF EXISTS "{schema}"."{table_name}"')
import re
now = datetime.now(timezone.utc)

def fail_task(**kwargs):
    raise AirflowFailException("Upstream task failed — DAG marked failed.")

# from airflow.operators.dummy import DummyOperator
def dag_success_callback(context):
    dag_run = context["dag_run"]
    run_id = dag_run.run_id
    dag_id = dag_run.dag_id

    RunHistory.objects.filter(
        run_id=run_id,
        source_id=dag_id
    ).update(
        status="success",
        finished_at=now
    )


def dag_failure_callback(context):
    dag_run = context["dag_run"]
    run_id = dag_run.run_id
    dag_id = dag_run.dag_id

    RunHistory.objects.filter(
        run_id=run_id,
        source_id=dag_id
    ).update(
        status="failed",
        finished_at=now
    )

def resolve_value(val, ti, xcom_cache, parent_task_name):
    """
    Check For parameter names and values in Task instance from 3 Levels:

    1.Parent Task
    2.__init_global_params Task (This Task is Initialised Starting of Pipeline)
    3.__sqlparam__{var_name} (This parameters used for SQL parameters )

    If None of the Xcom Keys Match it return None
    """

    if not isinstance(val, str):
        return val
    pattern = r'\$([a-zA-Z_]\w*)(?:\[(\d+)\])?'
    def replacer(match):
        var_name = match.group(1)
        index = match.group(2)
        value = None

        # Try parent task (like loop_start)
        if parent_task_name:
            value = ti.xcom_pull(task_ids=parent_task_name, key=var_name)

        # Then try __init_global_params
        if value is None:
            value = ti.xcom_pull(task_ids='__init_global_params', key=var_name)

        # Try fallback: SQL param tasks (task_ids start with '__sqlparam__')
        if value is None:
            try:
                sql_task_id = f'__sqlparam__{var_name}'
                value = ti.xcom_pull(task_ids=sql_task_id, key=var_name)
            except Exception:
                pass
        if value is None:
            loop_task_id = f'{var_name}'
            try:
                value = ti.xcom_pull(task_ids=loop_task_id, key=var_name)
            except Exception:
                pass

        if value is None:
            return "None"

        if index is not None:
            try:
                value = value[int(index)]
            except Exception:
                return  "None"

        return str(value)

    return re.sub(pattern, replacer, val)

def replace_params_in_json(data, xcom_cache=None, parent_task_name=None, **kwargs):
    """
    Here the config file Json Data convert into a proper key and pass to Resolve value functions

    json data encounters - list,dict,string
    """
    ti = kwargs.get('ti')
    if ti is None:
        return data
    if xcom_cache is None:
        xcom_cache = {}
    if isinstance(data, dict):
        return {
            replace_params_in_json(k, xcom_cache=xcom_cache, parent_task_name=parent_task_name, **kwargs):
            replace_params_in_json(v, xcom_cache=xcom_cache, parent_task_name=parent_task_name, **kwargs)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [replace_params_in_json(i, xcom_cache=xcom_cache, parent_task_name=parent_task_name, **kwargs) for i in data]
    elif isinstance(data, str) and '$' in data:
        return resolve_value(data, ti, xcom_cache, parent_task_name)
    return data



def init_global_params(param_list):
    """
    Create Global Parameter with default Value None and Push into Xcom Variables for __init_global_params Task
    """

    def _func(**context):
        ti = context['ti']
        conf = context.get('dag_run').conf or {}

        for param in param_list:
            name = param['param_name']
            default_val = param.get('value', 'None')
            if name in conf:
                print(f"Overriding param '{name}' from trigger input")
            else:
                print(f"Using default param '{name}' from config")

            raw_value = conf.get(name, default_val)
            resolved_value = resolve_value(raw_value, ti, {}, parent_task_name=None)
            ti.xcom_push(key=name, value=resolved_value)
    return _func


def create_sql_param_task(param, user_id):
    """
    It Create Sql Parameters and assign Value by Executing SQl Query 
    """
    def _sql_param_fn(**kwargs):
        ti = kwargs['ti']
        result = run_sql_commands(param['query'], param['database'], user_id)
        value = cast_output_by_type(result, param['data_type'])
        ti.xcom_push(key=param['param_name'], value=value)

    return _sql_param_fn

import subprocess
def run_external_command(user_command,return_type,fail=False):
    """
    command Line Execution
    """
    full_command = textwrap.dedent(f"""
        {user_command}
    """).strip()
    try:
        result = subprocess.run(
            full_command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            executable="/bin/bash"
        )

        output = result.stdout.strip()
        if fail and not output:
            raise ValueError("Command succeeded but returned no output")
        else:
            pass
        return cast_output_by_type(output,return_type)
    except subprocess.CalledProcessError as e:
        raise
        

def cast_output_by_type(raw_output, return_type: str, delimiter: str = ','):
    """
    Based on Data Type and Delimeter it Return the output from Raw output 
    """
    if isinstance(raw_output, str):
        raw_output = raw_output.strip().strip(delimiter)

    if return_type.lower() in ['array[string]', 'array<str>', 'array_str']:
        if isinstance(raw_output, list):
            return [str(item).strip() for item in raw_output]
        return [item.strip() for item in raw_output.split(delimiter) if item.strip()]

    elif return_type.lower() in ['array[int]', 'array[integer]', 'array<int>']:
        if isinstance(raw_output, list):
            return [int(item) for item in raw_output if str(item).strip().isdigit()]
        return [int(item.strip()) for item in raw_output.split(delimiter) if item.strip().isdigit()]

    elif return_type.lower() in ['array[float]', 'array<float>']:
        if isinstance(raw_output, list):
            return [float(item) for item in raw_output if str(item).strip()]
        return [float(item.strip()) for item in raw_output.split(delimiter) if item.strip()]

    elif return_type.lower() in ['string', 'str']:
        return str(raw_output)

    elif return_type.lower() in ['int', 'integer']:
        return int(raw_output)

    elif return_type.lower() in ['float', 'double']:
        return float(raw_output)

    elif return_type.lower() in ['boolean', 'bool']:
        if isinstance(raw_output, str):
            return raw_output.strip().lower() in ['true', '1', 'yes']
        return bool(raw_output)

    elif return_type.lower() in ['timestamp', 'date', 'time']:
        from dateutil import parser
        return parser.parse(str(raw_output))

    return raw_output


def Loop_parameters(task_details, user_id, **kwargs):
    """
    Creates Loop Parameters for command and sql and Push into Xcom Variables on Loop parameters Task Instance
    """
    ti = kwargs['ti']
    param_name = task_details['parameter_name']

    if task_details['loop_type'] == 'command':
        return_value = run_external_command(task_details['command'], task_details['return_type'], task_details['fail'])
    elif task_details['loop_type'] == 'sql':
        result = run_sql_commands(task_details['command'], task_details['hierarchy_id'], user_id)
        return_value = cast_output_by_type(result, task_details['return_type'])

    ti.xcom_push(key=param_name, value=return_value)




def task_creator(task_conf,dag_id,user_id,target_hierarchy_id,source_id,task_map,parent_task_id,**kwargs):
    """
    It Intializes The tasks Based on those Type for Execution of Pipelines
    """
    task_id = task_conf['id']
    task_type = task_conf['type']
    # overall_task_list.append(task_id)
    match task_type:
        case 'source_data_object':
            task = PythonOperator(
                task_id=task_id,
                python_callable=Extraction,
                op_kwargs={
                    'dag_id': dag_id,
                    'task_id': task_id,
                    'source_type': task_conf['format'],
                    'path': task_conf['path'],
                    'hierarchy_id': task_conf['hierarchy_id'],
                    'user_id': user_id,
                    'source_table_name': task_conf['source_table_name'],
                    'source_attributes': task_conf.get('source_attributes', ''),
                    "attributes": task_conf.get('attributes', ''),
                    "target_hierarchy_id": target_hierarchy_id
                }
            )
        case "target_data_object":
            task = PythonOperator(
                task_id=task_id,
                python_callable=Loading,
                op_kwargs={
                    'hierarchy_id': task_conf['hierarchy_id'],
                    'user_id': user_id,
                    'dag_id': dag_id,
                    'truncate': task_conf['truncate'],
                    'create': task_conf['create'],
                    'format': task_conf['format'],
                    'previous_id': task_conf['previous_task_id'],
                    'target_table_name': task_conf['target_table_name'],
                    'attribute_mapper': task_conf.get('attribute_mapper', ''),
                    'sources': source_id
                }
            )
        case "Filter":
            task = PythonOperator(
                task_id=task_id,
                python_callable=ETL_Filter,
                op_args=[task_conf['filter_conditions'], dag_id, task_id, task_conf['previous_task_id'], target_hierarchy_id, user_id, source_id]
            )
        case  "Expression":
            task = PythonOperator(
                task_id=task_id,
                python_callable=Expressions,
                op_args=[task_conf['expressions_list'], dag_id, task_id, task_conf['previous_task_id'], target_hierarchy_id, user_id, source_id]
            )
        case  "Rollup":
            task = PythonOperator(
                task_id=task_id,
                python_callable=Remove_duplicates,
                op_args=[task_conf['group_attributes'], task_conf['having_clause'], task_id, dag_id, task_conf['previous_task_id'], task_conf.get('attributes', ''), target_hierarchy_id, user_id, source_id]
            )
        case  "Joiner":
            task = PythonOperator(
                task_id=task_id,
                python_callable=Join,
                op_args=[task_conf['primary_table'], task_conf['joining_list'], task_conf['where_clause'], dag_id, task_id, task_conf['previous_task_id'], task_conf.get('attributes', ''), target_hierarchy_id, user_id, source_id]
            )
        case "Rank":
            task = PythonOperator(
                task_id=task_id,
                python_callable=Rank,
                op_args=[
                    task_conf['rank_by_cols'],['rank_type'],
                    task_conf.get('partition_by_cols', []),
                    task_conf['output_col'],
                    dag_id,
                    task_id,
                    task_conf['previous_task_id'],
                    target_hierarchy_id,
                    user_id,
                ],
                op_kwargs={
                    'ascending': task_conf.get('ascending', True),
                    'include_ties': task_conf.get('include_ties', True)
                }
            )

        case "Union":
            task = PythonOperator(
                task_id=task_id,
                python_callable=Union,
                op_args=[task_conf['previous_ids'], task_conf['column_mappings'], task_conf['remove_duplicates'], dag_id, task_id, target_hierarchy_id, user_id]
            )

        case "Router":
            task = PythonOperator(
                task_id=task_id,
                python_callable=Router,
                op_args=[task_conf['conditions'], dag_id, task_id, task_conf['previous_task_id'], target_hierarchy_id, user_id]
            )
        case "Normalizer":
            task = PythonOperator(
                task_id=task_id,
                python_callable=Normalizer,
                op_args=[
                    task_conf['group_by_cols'],
                    task_conf['pivot_col'],
                    task_conf['value_cols'],
                    task_conf['output_cols'],
                    dag_id,
                    task_id,
                    task_conf['previous_task_id'],
                    target_hierarchy_id,
                    user_id
                ],
                op_kwargs={}
            )

        case _:
            raise ValueError(f"Unsupported task type: '{task_type}' for task ID '{task_id}'")
        
    task_map[task_id] = task
    return task_map



def generate_dynamic_dag(dag_id, user_id, user_name, config, **kwargs):
    dag = DAG(
        dag_id,
        default_args={
            'owner': 'airflow',
            'start_date': timezone.datetime(2024, 1, 1),  # timezone-aware
            'retries': 0
        },
        schedule=None,  # ✅ correct param
        catchup=False,
        description=config.get('flow_name', 'No Description'),
        is_paused_upon_creation=False,
        tags=[str(user_name), str(config.get('flow_name', ''))],
        on_success_callback=dag_success_callback,
        on_failure_callback=dag_failure_callback,
    )
    task_map = {}
    with dag:
        target_hierarchy_id = next((task["hierarchy_id"] for task in config['tasks'] if task["type"] == "target_data_object"),
                                next((task["hierarchy_id"] for task in config['tasks'] if task["type"] == "source_data_object"), None))

        source_id = [(i['id'], i['source_table_name']) for i in config['tasks'] if i['type'] == 'source_data_object']

        param_list = config.get('parameters', [])
        sql_param_list = config.get('sql_parameters', [])
        
        init_param_task = PythonOperator(
            task_id='__init_global_params',
            python_callable=init_global_params(param_list),
        )
        global_store_task = PythonOperator(
            task_id=GLOBAL_PARAM_HOLDER,
            python_callable=lambda: print("Global param holder"),
            trigger_rule='all_done'
        )

        overall_task_list = []
        task_map = {}
        for task_conf in config['tasks']:
            task_conf = replace_params_in_json(task_conf,xcom_cache=None,parent_task_name = None,**kwargs)
            parameter_task= None
            task_map = task_creator(task_conf,dag_id,user_id,target_hierarchy_id,source_id,task_map,parameter_task)
            task_id = task_conf['id']
            if task_conf['type'] =='loop':
                for t in task_conf['loop_tasks']:
                    task_id = t['id']
                    overall_task_list.append(task_id)
            else:
                overall_task_list.append(task_id)
            

        cleanup_task = PythonOperator(
            task_id='cleanup_temporary_tables',
            python_callable=cleanup_on_success,
            op_kwargs={
                'tasks_list': overall_task_list,
                'user_id': user_id,
                'hierarchy_id': target_hierarchy_id
            },
            trigger_rule=TriggerRule.ALL_DONE,  # This ensures it runs no matter what
        )
        
# dag_success_marker = PythonOperator(
#             task_id='dag_success_marker',
#             python_callable=check_dag_status,
#             trigger_rule=TriggerRule.ALL_DONE  # Important: Run regardless of prior failures
#         )
        dag_success_marker = PythonOperator(
            task_id="propagate_failure",
            python_callable=fail_task,
            trigger_rule=TriggerRule.ONE_FAILED,
        )
        
        if config.get('flow',[]):
            for parent, child in config.get('flow', []):
                task_map[parent] >> task_map[child]
            last_task = config.get('flow')[-1][-1]
            task_map[last_task] >> cleanup_task >> dag_success_marker
        else:
            init_param_task >> cleanup_task >> dag_success_marker

        for param in sql_param_list:
            task_name = f"__sqlparam__{param['param_name']}"
            sql_task = PythonOperator(
                task_id=task_name,
                python_callable=create_sql_param_task(param, user_id),
            )
            task_map[task_name] = sql_task
            if param['order'] == 'before':
                sql_task >> task_map[param['dependent_task']]
            elif param['order'] =='after':
                task_map[param['dependent_task']] >> sql_task  
            else:
                sql_task  
    globals()[dag_id] = dag
    return dag

from django.db import connection

def fetch_and_lock_dag_configs(limit=100):
    CONFIG_DIR = '/var/www/Configs/FlowBoard'
    # try:
    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #             WITH to_parse AS (
    #                 SELECT "Flow_id", "user_id"
    #                 FROM "FlowBoard"
    #                 WHERE "parsed" IS NULL OR "updated_at" > "parsed"
    #                 ORDER BY "updated_at" ASC
    #                 LIMIT %s
    #                 FOR UPDATE SKIP LOCKED
    #             )
    #             UPDATE "FlowBoard"
    #             SET "parsed" = NOW()
    #             FROM to_parse
    #             WHERE "FlowBoard"."Flow_id" = to_parse."Flow_id"
    #             RETURNING "FlowBoard"."Flow_id" AS flow_id, "FlowBoard"."user_id" AS user_id;
    #         """, [limit])
            
    #         rows = cursor.fetchall()
    #         print('[DEBUG] Locked rows:', rows)

    #         if not rows:
    #             return

    #         for flow_id, user_id in rows:
    #             full_path = os.path.join(base_dir, f'{user_id}/{flow_id}.json')
    #             try:
    #                 with open(full_path) as f:
    #                     config_json = json.load(f)
    #                     yield flow_id, config_json
    #             except Exception as e:
    #                 print(f"[ERROR] Failed to parse {full_path}: {e}")

    # except Exception as e:
    #     print(f"[ERROR] Database error: {e}")
    for user_id in os.listdir(CONFIG_DIR):
        user_dir = os.path.join(CONFIG_DIR, user_id)
        if not os.path.isdir(user_dir):
            continue
        for filename in os.listdir(user_dir):
            if filename.endswith('.json'):
                flow_id = filename[:-5]
                filepath = os.path.join(user_dir, filename)
                try:
                    with open(filepath) as f:
                        config = json.load(f)
                        yield flow_id, config
                except Exception as e:
                    print(f"[ERROR] Failed to load {filepath}: {e}")



# def get_configs():
#     # CONFIG_DIR = '/var/www/configs' if settings.DATABASES['default']['NAME'] == 'analytify_qa' else 'configs'
#     configs = []

#     for file in os.listdir(CONFIG_DIR):
#         if file.endswith(".json"):
#             with open(os.path.join(CONFIG_DIR, file)) as f:
#                 configs.append(json.load(f))
#     return configs
dag_configs = list(fetch_and_lock_dag_configs() or [])

if not dag_configs:
    print("[INFO] No new DAG configs found to parse.")
else:
        
    for dag_id, config in dag_configs:
        try:
            print(f"[INFO] Attempting DAG generation for {dag_id}")
            dag = generate_dynamic_dag(
                dag_id=str(dag_id),
                user_id=uuid.UUID(config['user_id']),
                user_name=config['username'],
                config=config
            )

            if not isinstance(dag, DAG):
                print(f"[ERROR] {dag_id}: Not a DAG instance: {type(dag)}")
                continue
            if not dag.dag_id:
                print(f"[ERROR] {dag_id}: dag_id is None")
                continue

            # Optional debug dump

            globals()[dag.dag_id] = dag
        except Exception as e:
            print(f"[EXCEPTION] DAG creation failed for {dag_id}: {e}")
            traceback.print_exc()