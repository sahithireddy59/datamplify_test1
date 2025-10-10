from django.db import models
from django.utils import timezone
from authentication.models import UserProfile
import uuid
# Create your models here.
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now) #, editable=False
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class DataSources(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField()
    type = models.CharField()
    class Meta:
        db_table="DataSources"




class Connections(models.Model):
    id = models.UUIDField(primary_key = True,default = uuid.uuid4,editable = False)
    table_id = models.UUIDField()
    type = models.ForeignKey(DataSources,on_delete=models.CASCADE,db_column='type') 
    user_id  = models.ForeignKey(UserProfile,on_delete=models.CASCADE,db_column='user_id')

    class  Meta:
        db_table = 'Connections'

class DatabaseConnections(TimeStampedModel):
    id  = models.UUIDField(primary_key = True,default = uuid.uuid4,editable = False)
    server_type = models.ForeignKey(DataSources, on_delete=models.CASCADE)
    hostname = models.CharField(max_length=500,null=True,db_column='hostname')
    username = models.CharField(max_length=500,null=True,db_column='username')
    password = models.CharField(max_length=500,null=True,db_column='password')
    database = models.CharField(max_length=500,null=True,db_column='database')
    database_path = models.CharField(max_length=1500,null=True,db_column='database_path')
    service_name = models.CharField(max_length=500,null=True,db_column='service_name')
    port = models.IntegerField(null=True,db_column='port')
    connection_name = models.CharField(max_length=500,null=True,db_column='connection_name')
    is_connected = models.BooleanField(default=True)
    user_id = models.ForeignKey(UserProfile,on_delete=models.CASCADE,db_column="user_id")
    schema = models.CharField(max_length=500,null=True)
    
    class Meta:
        db_table = 'Database_Connections'


class FileConnections(TimeStampedModel):
    id  = models.UUIDField(primary_key = True,default = uuid.uuid4,editable = False)
    file_type = models.ForeignKey(DataSources,on_delete=models.CASCADE)
    datapath = models.FileField(db_column='file_path', null=True, blank=True, upload_to='Datamplify/files/',max_length=1000)
    source = models.CharField(max_length=500,null=True,blank=True,db_column='source_path')
    connection_name = models.CharField(max_length=500,null=True,db_column='connection_name')
    uploaded_at = models.DateTimeField(default=timezone.now)
    user_id = models.ForeignKey(UserProfile,on_delete=models.CASCADE,db_column='user_id')
    
    # Dynamic file path support (for Looper component)
    use_dynamic_path = models.BooleanField(default=False, db_column='use_dynamic_path')
    dynamic_file_path = models.CharField(max_length=1000, null=True, blank=True, db_column='dynamic_file_path')
    file_name_parameter = models.CharField(max_length=200, null=True, blank=True, db_column='file_name_parameter')
    
    # File server details for dynamic path
    file_server_type = models.CharField(max_length=50, default='local', null=True, blank=True, db_column='file_server_type')
    file_server_host = models.CharField(max_length=500, null=True, blank=True, db_column='file_server_host')
    file_server_port = models.CharField(max_length=10, null=True, blank=True, db_column='file_server_port')
    file_server_protocol = models.CharField(max_length=20, null=True, blank=True, db_column='file_server_protocol')
    file_server_username = models.CharField(max_length=200, null=True, blank=True, db_column='file_server_username')
    file_server_password = models.CharField(max_length=500, null=True, blank=True, db_column='file_server_password')
    file_server_auth_type = models.CharField(max_length=20, default='password', null=True, blank=True, db_column='file_server_auth_type')
    file_server_auth_file = models.FileField(upload_to='Datamplify/auth_files/', null=True, blank=True, db_column='file_server_auth_file', max_length=1000)
    
    class Meta:
        db_table = 'File_connections'


class DataObjects(TimeStampedModel):
    id = models.UUIDField(primary_key = True,default = uuid.uuid4,editable = False)
    source_id = models.IntegerField()
    table_name = models.CharField(max_length=100)
    object_name = models.CharField()

    class Meta:
        db_table = 'DataObjects'


class GlobalParameters(TimeStampedModel):
    """
    Global parameters for CSV file loading configurations
    Similar to Diyotta's global parameter management
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parameter_name = models.CharField(max_length=200, unique=True, db_column='parameter_name')
    parameter_value = models.TextField(db_column='parameter_value')
    parameter_type = models.CharField(max_length=50, db_column='parameter_type', 
                                     choices=[
                                         ('STRING', 'String'),
                                         ('INTEGER', 'Integer'),
                                         ('BOOLEAN', 'Boolean'),
                                         ('PATH', 'File Path'),
                                         ('JSON', 'JSON Object')
                                     ])
    category = models.CharField(max_length=100, db_column='category',
                                choices=[
                                    ('DIRECT_LOAD', 'Direct Load'),
                                    ('INDIRECT_LOAD', 'Indirect Load'),
                                    ('GENERAL', 'General')
                                ])
    description = models.TextField(null=True, blank=True, db_column='description')
    is_active = models.BooleanField(default=True, db_column='is_active')
    user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column='user_id')
    
    class Meta:
        db_table = 'Global_Parameters'
        ordering = ['category', 'parameter_name']


class CSVLoadConfiguration(TimeStampedModel):
    """
    CSV Load Configuration for Direct and Indirect Load
    Stores configuration for how CSV files should be loaded
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    config_name = models.CharField(max_length=200, db_column='config_name')
    load_type = models.CharField(max_length=20, db_column='load_type',
                                 choices=[
                                     ('DIRECT', 'Direct Load'),
                                     ('INDIRECT', 'Indirect Load')
                                 ])
    
    # Direct Load Parameters
    batch_size = models.IntegerField(default=1000, null=True, db_column='batch_size')
    skip_rows = models.IntegerField(default=0, null=True, db_column='skip_rows')
    delimiter = models.CharField(max_length=10, default=',', null=True, db_column='delimiter')
    encoding = models.CharField(max_length=50, default='utf-8', null=True, db_column='encoding')
    quote_char = models.CharField(max_length=5, default='"', null=True, db_column='quote_char')
    escape_char = models.CharField(max_length=5, null=True, blank=True, db_column='escape_char')
    
    # Indirect Load Parameters
    staging_path = models.CharField(max_length=1000, null=True, blank=True, db_column='staging_path')
    staging_table = models.CharField(max_length=200, null=True, blank=True, db_column='staging_table')
    staging_schema = models.CharField(max_length=200, null=True, blank=True, db_column='staging_schema')
    use_bulk_insert = models.BooleanField(default=True, db_column='use_bulk_insert')
    truncate_before_load = models.BooleanField(default=False, db_column='truncate_before_load')
    
    # Common Parameters
    header_row = models.BooleanField(default=True, db_column='header_row')
    null_values = models.JSONField(default=list, null=True, blank=True, db_column='null_values')
    date_format = models.CharField(max_length=50, default='%Y-%m-%d', null=True, db_column='date_format')
    timestamp_format = models.CharField(max_length=50, default='%Y-%m-%d %H:%M:%S', null=True, db_column='timestamp_format')
    error_handling = models.CharField(max_length=20, default='SKIP', db_column='error_handling',
                                     choices=[
                                         ('SKIP', 'Skip Errors'),
                                         ('ABORT', 'Abort on Error'),
                                         ('LOG', 'Log and Continue')
                                     ])
    max_errors = models.IntegerField(default=100, null=True, db_column='max_errors')
    
    # Metadata
    is_default = models.BooleanField(default=False, db_column='is_default')
    user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column='user_id')
    
    class Meta:
        db_table = 'CSV_Load_Configuration'
        ordering = ['-is_default', 'config_name']