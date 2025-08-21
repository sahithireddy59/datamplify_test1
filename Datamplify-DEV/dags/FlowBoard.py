from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.bash import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime
import os, json, sys, django, textwrap, glob
from airflow.providers.smtp.operators.smtp import EmailOperator
from airflow.sensors.python import PythonSensor
from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.task_group import TaskGroup


# FlowBoard Functionalities:
# 1.Expression,
# 2.Joins
# 3.Remove duplicates
# 4.Filter
# 5.Extraction


if __name__ != "__main__":
    sys.path.append("Datamplify")
    # sys.path.append("Analytify/")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
    django.setup()
    from ..Service.utils import run_sql_commands 
    from ..FlowBoard.utils import Extraction,Loading,ETL_Filter,Remove_duplicates,Expressions,Join
    # from dashboard.ETL import generate_engine

from Datamplify import settings



GLOBAL_PARAM_HOLDER = '__global_param_store__'

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
                cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
import re

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

    if task_type == 'source_data_object':
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
    elif task_type == "target_data_object":
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
    elif task_type == "Filter":
        task = PythonOperator(
            task_id=task_id,
            python_callable=ETL_Filter,
            op_args=[task_conf['filter_conditions'], dag_id, task_id, task_conf['previous_task_id'], target_hierarchy_id, user_id, source_id]
        )
    elif task_type == "Expression":
        task = PythonOperator(
            task_id=task_id,
            python_callable=Expressions,
            op_args=[task_conf['expressions_list'], dag_id, task_id, task_conf['previous_task_id'], target_hierarchy_id, user_id, source_id]
        )
    elif task_type == "Rollup":
        task = PythonOperator(
            task_id=task_id,
            python_callable=Remove_duplicates,
            op_args=[task_conf['group_attributes'], task_conf['having_clause'], task_id, dag_id, task_conf['previous_task_id'], task_conf.get('attributes', ''), target_hierarchy_id, user_id, source_id]
        )
    elif task_type == "Joiner":
        task = PythonOperator(
            task_id=task_id,
            python_callable=Join,
            op_args=[task_conf['primary_table'], task_conf['joining_list'], task_conf['where_clause'], dag_id, task_id, task_conf['previous_task_id'], task_conf.get('attributes', ''), target_hierarchy_id, user_id, source_id]
        )
    return task_map



def generate_dynamic_dag(dag_id, user_id, user_name, config, **kwargs):
    dag = DAG(dag_id, default_args={
        'owner': 'airflow',
        'start_date': datetime(2024, 1, 1),
        'retries': 0
    }, schedule=None, catchup=False, is_paused_upon_creation=False, tags=[f"{user_name}",f"{config['dag_name']}"])

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

        if config.get('flow',[]):
            for parent, child in config.get('flow', []):
                task_map[parent] >> task_map[child]
            last_task = config.get('flow')[-1][-1]
            task_map[last_task] >> cleanup_task
        else:
            init_param_task >> cleanup_task

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

def get_configs():
    CONFIG_DIR = '/var/www/configs' if settings.DATABASES['default']['NAME'] == 'analytify_qa' else 'configs'
    configs = []
    for file in os.listdir(CONFIG_DIR):
        if file.endswith(".json"):
            with open(os.path.join(CONFIG_DIR, file)) as f:
                configs.append(json.load(f))
    return configs

for config in get_configs():
    try:
        globals()[config['dag_id']] = generate_dynamic_dag(config['dag_id'], config['user_id'], config['username'], config)
    except Exception as e:
        pass
