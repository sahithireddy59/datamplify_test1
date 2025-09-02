from pathlib import Path
from django.conf import settings
import json, pendulum

SCHED_ROOT = Path(getattr(settings, "AIRFLOW_SCHEDULER_CONFIG_ROOT", "/opt/airflow/project/Configs/Scheduler"))

def publish_scheduler(s):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Publishing scheduler {s.id} to {SCHED_ROOT}")
        SCHED_ROOT.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory created/exists: {SCHED_ROOT}")
        
        tz = s.timezone or "Asia/Kolkata"
        now = pendulum.now(tz)
        start = s.start_date or now.subtract(minutes=1)
        if pendulum.instance(start, tz=tz) > now:
            start = now.subtract(minutes=1)

        doc = {
            "dag_id": s.dag_id(),
            "name": s.name,
            "owner": s.owner,
            "mode": s.mode,
            "schedule": s.schedule if s.enabled else None,
            "start_date": pendulum.instance(start, tz=tz).to_iso8601_string(),
            "timezone": tz,
            "catchup": bool(s.catchup),
            "max_active_runs": int(s.max_active_runs),
        }
        if s.mode == "trigger":
            doc["target_dag_id"] = s.target_dag_id
        elif s.mode == "bash":
            doc["bash_command"] = s.bash_command

        out = SCHED_ROOT / f"{s.dag_id()}.json"
        logger.info(f"Writing scheduler JSON to: {out}")
        logger.info(f"JSON content: {json.dumps(doc, indent=2)}")
        
        out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"Successfully wrote scheduler JSON to: {out}")
        return str(out)
        
    except Exception as e:
        logger.error(f"Error publishing scheduler {s.id}: {str(e)}")
        logger.error(f"SCHED_ROOT: {SCHED_ROOT}")
        logger.error(f"Scheduler data: id={s.id}, name={s.name}, enabled={s.enabled}, schedule={s.schedule}")
        raise
