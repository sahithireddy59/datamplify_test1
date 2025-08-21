from Datamplify import settings
import requests

from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta



def airflow_token():
    login_url = settings.airflow_url
    payload = {"username": f"{settings.airflow_username}", "password": f"{settings.airflow_password}"}
    response = requests.post(
            login_url,
            json=payload,  
            headers={"Content-Type": "application/json"}
        )
    if response.status_code ==201:
        data = response.json()
        return data.get('access_token')
    else:
        return 'unauthorised'
    


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
