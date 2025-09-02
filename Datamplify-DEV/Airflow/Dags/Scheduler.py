from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
import os, json
import pendulum

def _start_dt(cfg):
    tz = pendulum.timezone(cfg.get('timezone', 'Asia/Kolkata'))
    raw = cfg.get('start_date', '2024-01-01T00:00:00')
    try:
        return pendulum.parse(raw).replace(tzinfo=tz)
    except Exception:
        return pendulum.datetime(2024, 1, 1, tz=tz)

def generate_scheduler_dag(cfg):
    dag_id   = cfg['dag_id']
    schedule = cfg.get('schedule')
    catchup  = bool(cfg.get('catchup', False))
    max_runs = int(cfg.get('max_active_runs', 1))
    start_dt = _start_dt(cfg)
    tags     = [cfg.get('owner', 'scheduler'), cfg.get('name', 'Scheduler')]

    dag = DAG(
        dag_id=dag_id,
        default_args={'owner': 'airflow', 'start_date': start_dt, 'retries': 0},
        schedule=schedule,
        catchup=catchup,
        max_active_runs=max_runs,
        is_paused_upon_creation=False,
        tags=tags,
    )

    with dag:
        mode = cfg.get('mode', 'trigger')

        if mode == 'trigger':
            # trigger another Airflow DAG by id
            TriggerDagRunOperator(
                task_id="trigger_target_dag",
                trigger_dag_id=cfg['target_dag_id'],
                conf=cfg.get('conf', {}),
                reset_dag_run=True,
                wait_for_completion=False,
            )
        elif mode == 'bash':
            # run shell / manage.py command
            BashOperator(
                task_id="run_scheduled_command",
                bash_command=cfg['bash_command'],
            )
        else:
            BashOperator(task_id="noop", bash_command="echo 'no-op'")
    return dag

def get_configs():
    CONFIG_DIR = '/opt/airflow/project/Configs/Scheduler'
    print(f"[INFO] Looking for Scheduler configs in: {CONFIG_DIR}")
    cfgs = []
    if not os.path.isdir(CONFIG_DIR):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            print(f"[INFO] Created {CONFIG_DIR} (no configs yet).")
        except Exception as e:
            print(f"[WARN] Could not create {CONFIG_DIR}: {e}")
        return cfgs

    for root, _, files in os.walk(CONFIG_DIR):
        for file in files:
            if not file.lower().endswith('.json'): continue
            path = os.path.join(root, file)
            try:
                with open(path) as f:
                    cfg = json.load(f)
                    if 'dag_id' not in cfg:
                        cfg['dag_id'] = os.path.splitext(os.path.basename(path))[0]
                    cfgs.append(cfg)
            except Exception as e:
                print(f"[ERROR] Failed to load {path}: {e}")
    return cfgs

for cfg in get_configs():
    try:
        globals()[cfg['dag_id']] = generate_scheduler_dag(cfg)
    except Exception as e:
        print(f"[ERROR] Failed to build scheduler DAG {cfg.get('dag_id')}: {e}")
        continue
