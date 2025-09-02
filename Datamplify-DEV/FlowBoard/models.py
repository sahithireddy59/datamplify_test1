from django.db import models
from Connections.models import TimeStampedModel
from authentication.models import UserProfile
import uuid

class FlowBoard(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Flow_id = models.CharField(max_length=255)
    Flow_name = models.CharField(max_length=255)
    DrawFlow = models.JSONField(default=dict)
    user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column='user_id')
    parsed = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'FlowBoard'
        ordering = ['-created_at']
