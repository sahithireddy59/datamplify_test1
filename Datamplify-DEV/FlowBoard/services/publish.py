import json
import pendulum
from pathlib import Path
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def ensure_directory_exists(path):
    """Ensure the directory exists, create if it doesn't"""
    path.mkdir(parents=True, exist_ok=True)
    return path

def publish_flowboard(flowboard, user_slug: str):
    """
    Publish FlowBoard configuration to a JSON file for Airflow to pick up.
    
    Args:
        flowboard: FlowBoard instance
        user_slug: Slug/username of the FlowBoard owner
    """
    try:
        # Ensure the output directory exists
        base_dir = Path(getattr(settings, 'AIRFLOW_CONFIG_ROOT', '/opt/airflow/project/Configs/FlowBoard'))
        out_dir = base_dir / user_slug / str(flowboard.id)
        ensure_directory_exists(out_dir)
        
        # Build the configuration document
        doc = {
            "dag_id": str(flowboard.id),
            "dag_name": flowboard.Flow_name,
            "username": flowboard.user_id.username,
            "user_id": str(flowboard.user_id.id),
            "parameters": {},
            "tasks": {},
            "flow": {}
        }
        
        # Add DrawFlow data if available
        if hasattr(flowboard, 'DrawFlow') and flowboard.DrawFlow:
            doc.update({
                "parameters": flowboard.DrawFlow.get('data', {}).get('parameters', {}),
                "tasks": flowboard.DrawFlow.get('nodes', {}),
                "flow": flowboard.DrawFlow.get('edges', {})
            })
        
        # Write to JSON file
        output_file = out_dir / f"{flowboard.id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Published FlowBoard {flowboard.id} to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error publishing FlowBoard {flowboard.id}: {str(e)}", exc_info=True)
        return False
