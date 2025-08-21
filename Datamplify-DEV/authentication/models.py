from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import uuid


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now) #, editable=False
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
class UserProfile(AbstractUser):
    id = models.UUIDField(primary_key = True,default = uuid.uuid4,editable = False,db_column='user_id')
    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField(db_column='email_id',unique=True)
    password = models.CharField(max_length=256)
    is_active = models.BooleanField(db_column='is_active',default=False)
    sub_identifier = models.CharField(max_length=100,null=True,unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    # role  = models.ForeignKey()
    class Meta:
        db_table="user_profile"


class Account_Activation(TimeStampedModel):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    email = models.CharField(max_length=50, null=True,blank=True,default='')
    key = models.CharField(max_length=100, blank=True, null=True)
    otp = models.PositiveIntegerField()
    expiry_date = models.DateTimeField(default=timezone.now() + timedelta(days=2)) #custom_expiry_date

    class Meta:
        db_table = 'account_activation'



class Reset_Password(models.Model):
    user = models.UUIDField(db_column='user_id', null=True)
    key = models.CharField(max_length=32, blank=True, null=False, db_column='key')
    created_at = models.DateTimeField(default=timezone.now)
    class Meta:
        db_table = 'reset_password'