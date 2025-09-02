from django.db import models
from django.utils import timezone

class Scheduler(models.Model):
    name = models.CharField(max_length=128, default="Scheduler")
    owner = models.CharField(max_length=64, default="scheduler")

    MODE_CHOICES = (("trigger", "Trigger DAG"), ("bash", "Bash/Command"))
    mode = models.CharField(max_length=16, choices=MODE_CHOICES, default="trigger")

    # schedule fields
    schedule = models.CharField(max_length=64, null=True, blank=True)  # cron or @daily/@hourly/@weekly/@monthly/@once
    start_date = models.DateTimeField(default=timezone.now)
    timezone = models.CharField(max_length=64, default="Asia/Kolkata")
    catchup = models.BooleanField(default=False)
    max_active_runs = models.PositiveIntegerField(default=1)
    # link to FlowBoard (avoid circular import with app_label.model_name string)
    flowboard = models.ForeignKey(
        'FlowBoard.FlowBoard',
        on_delete=models.CASCADE,
        related_name='schedules',
        null=True,
        blank=True,
        db_column='flowboard_id'
    )
    enabled = models.BooleanField(default=True)

    # mode-specific
    target_dag_id = models.CharField(max_length=128, null=True, blank=True)  # for mode=trigger
    bash_command = models.TextField(null=True, blank=True)                    # for mode=bash

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def dag_id(self) -> str:
        return f"scheduler_{self.pk}"

    def __str__(self):
        return f"{self.name} ({self.dag_id()})"
