from rest_framework import serializers
from app.scheduler.models import Scheduler

class SchedulerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheduler
        fields = [
            "id", "name", "owner", "mode",
            "schedule", "start_date", "timezone",
            "catchup", "max_active_runs", "enabled",
            "target_dag_id", "bash_command",
            "flowboard",
        ]
