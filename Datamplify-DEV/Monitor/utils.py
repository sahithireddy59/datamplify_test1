from Datamplify import settings
import requests
import logging

from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta



def airflow_token():
    login_url = settings.airflow_url
    payload = {"username": f"{settings.airflow_username}", "password": f"{settings.airflow_password}"}
    logging.getLogger(__name__).info(f"Getting Airflow token from {login_url}")
    response = requests.post(
            login_url,
            json=payload,  
            headers={"Content-Type": "application/json"}
        )
    if response.status_code in (200, 201):
        try:
            data = response.json()
            # token field name may vary depending on auth plugin
            return data.get('access_token') or data.get('token')
        except Exception:
            return None
    else:
        return None
    


def time_ago(timestamp_str):
    # Parse ISO timestamp
    if isinstance(timestamp_str, str):
        if timestamp_str.endswith("Z"):
            timestamp = timestamp_str[:-1] + "+00:00"
        timestamp = datetime.fromisoformat(timestamp)
    
    # If it's already datetime, use directly
    if isinstance(timestamp_str, datetime):
        timestamp = timestamp_str
        if timestamp.tzinfo is None:  # make it timezone-aware
            timestamp = timestamp.replace(tzinfo=timezone.utc)
    else:
        raise TypeError("time_ago() expects str or datetime, got %s" % type(timestamp))

    now = datetime.now(timezone.utc)
    delta = relativedelta(now, timestamp)
    
    if delta.years > 0:
        if delta.months > 0:
            return f"{delta.years} years {delta.months} months ago"
        return f"{delta.years} years ago"
    elif delta.months > 0:
        return f"{delta.months} months ago"
    elif delta.days > 0:
        return f"{delta.days} days ago"
    elif delta.hours > 0:
        return f"{delta.hours} hours ago"
    elif delta.minutes > 0:
        return f"{delta.minutes} mins ago"
    else:
        return "just now"

# Example usage

def list_airflow_dags():
    """List available DAGs in Airflow instance"""
    air_token = airflow_token()
    if not air_token:
        return {"error": "Failed to get Airflow token"}
    
    url = f"{settings.airflow_host}/api/v2/dags"
    headers = {
        "Authorization": f"Bearer {air_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Return list of DAG IDs
            return [dag["dag_id"] for dag in data.get("dags", [])]
        else:
            return {"error": f"Failed to list DAGs: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": str(e)}
