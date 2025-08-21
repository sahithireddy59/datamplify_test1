from django.db import models
from Connections.models import TimeStampedModel
from authentication.models import UserProfile
import uuid
# Create your models here.

class FlowBoard(TimeStampedModel):
    id = models.UUIDField(primary_key = True,default = uuid.uuid4,editable = False)
    Flow_id = models.CharField()
    Flow_name  = models.CharField()
    DrawFlow = models.CharField()
    user_id = models.ForeignKey(UserProfile,on_delete=models.CASCADE,db_column='user_id')
    parsed =  models.DateTimeField(blank=True,default=None,null=True)

    class Meta:
        db_table ='FlowBoard'

