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


# ==================== RBAC Models ====================

class Permission(models.Model):
    """
    Represents a single permission in the system
    """
    code = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, db_index=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'datamplify_permission'
        ordering = ['category', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Role(models.Model):
    """
    Represents a role that can be assigned to users
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, related_name='roles', blank=True)
    is_system_role = models.BooleanField(default=False)
    level = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'datamplify_role'
        ordering = ['level', 'name']
    
    def __str__(self):
        return self.name
    
    def get_permission_codes(self):
        """Get list of permission codes for this role"""
        return list(self.permissions.values_list('code', flat=True))


class UserRole(models.Model):
    """
    Many-to-Many relationship between Users and Roles with metadata
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_assignments')
    assigned_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'datamplify_user_role'
        unique_together = ('user', 'role')
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"