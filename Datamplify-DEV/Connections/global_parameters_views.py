"""
Global Parameters and CSV Load Configuration Views
Handles CRUD operations for global parameters and CSV load configurations
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import GlobalParameters, CSVLoadConfiguration
from authentication.models import UserProfile
import json
from datetime import datetime
import os


def get_system_parameters():
    """
    Get built-in system parameters that are always available
    These are read-only and automatically populated
    """
    now = datetime.now()
    
    return [
        {
            'parameter_name': 'CURRENT_DATE',
            'parameter_value': now.strftime('%Y-%m-%d'),
            'parameter_type': 'DATE',
            'category': 'SYSTEM',
            'description': 'Current system date (YYYY-MM-DD)',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'CURRENT_DATETIME',
            'parameter_value': now.strftime('%Y-%m-%d %H:%M:%S'),
            'parameter_type': 'DATETIME',
            'category': 'SYSTEM',
            'description': 'Current system date and time',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'CURRENT_YEAR',
            'parameter_value': now.strftime('%Y'),
            'parameter_type': 'STRING',
            'category': 'SYSTEM',
            'description': 'Current year (YYYY)',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'CURRENT_MONTH',
            'parameter_value': now.strftime('%m'),
            'parameter_type': 'STRING',
            'category': 'SYSTEM',
            'description': 'Current month (MM)',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'CURRENT_DAY',
            'parameter_value': now.strftime('%d'),
            'parameter_type': 'STRING',
            'category': 'SYSTEM',
            'description': 'Current day (DD)',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'CURRENT_TIMESTAMP',
            'parameter_value': str(int(now.timestamp())),
            'parameter_type': 'NUMBER',
            'category': 'SYSTEM',
            'description': 'Current Unix timestamp',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'YESTERDAY_DATE',
            'parameter_value': (now - datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
            'parameter_type': 'DATE',
            'category': 'SYSTEM',
            'description': 'Yesterday\'s date (YYYY-MM-DD)',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'TOMORROW_DATE',
            'parameter_value': (now + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
            'parameter_type': 'DATE',
            'category': 'SYSTEM',
            'description': 'Tomorrow\'s date (YYYY-MM-DD)',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'WEEK_START_DATE',
            'parameter_value': (now - datetime.timedelta(days=now.weekday())).strftime('%Y-%m-%d'),
            'parameter_type': 'DATE',
            'category': 'SYSTEM',
            'description': 'Start of current week (Monday)',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'MONTH_START_DATE',
            'parameter_value': now.replace(day=1).strftime('%Y-%m-%d'),
            'parameter_type': 'DATE',
            'category': 'SYSTEM',
            'description': 'First day of current month',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'YEAR_START_DATE',
            'parameter_value': now.replace(month=1, day=1).strftime('%Y-%m-%d'),
            'parameter_type': 'DATE',
            'category': 'SYSTEM',
            'description': 'First day of current year',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'USER_HOME',
            'parameter_value': os.path.expanduser('~'),
            'parameter_type': 'PATH',
            'category': 'SYSTEM',
            'description': 'User home directory',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'TEMP_DIR',
            'parameter_value': os.environ.get('TEMP', '/tmp'),
            'parameter_type': 'PATH',
            'category': 'SYSTEM',
            'description': 'System temporary directory',
            'is_system': True,
            'is_active': True
        },
        # Diyotta-style system parameters
        {
            'parameter_name': 'mpfilepath',
            'parameter_value': os.path.join(os.getcwd(), 'media', 'Datamplify'),
            'parameter_type': 'PATH',
            'category': 'SYSTEM',
            'description': 'Datamplify base file path for uploaded files',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'mpprojectpath',
            'parameter_value': os.getcwd(),
            'parameter_type': 'PATH',
            'category': 'SYSTEM',
            'description': 'Datamplify project root directory',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'mptemppath',
            'parameter_value': os.path.join(os.getcwd(), 'media', 'Datamplify', 'temp'),
            'parameter_type': 'PATH',
            'category': 'SYSTEM',
            'description': 'Datamplify temporary processing directory',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'mplogpath',
            'parameter_value': os.path.join(os.getcwd(), 'logs'),
            'parameter_type': 'PATH',
            'category': 'SYSTEM',
            'description': 'Datamplify logs directory',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'mparchivepath',
            'parameter_value': os.path.join(os.getcwd(), 'media', 'Datamplify', 'archive'),
            'parameter_type': 'PATH',
            'category': 'SYSTEM',
            'description': 'Datamplify archive directory for processed files',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'mpbackuppath',
            'parameter_value': os.path.join(os.getcwd(), 'media', 'Datamplify', 'backup'),
            'parameter_type': 'PATH',
            'category': 'SYSTEM',
            'description': 'Datamplify backup directory',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'mpusername',
            'parameter_value': os.environ.get('USERNAME', os.environ.get('USER', 'datamplify')),
            'parameter_type': 'STRING',
            'category': 'SYSTEM',
            'description': 'Current system username',
            'is_system': True,
            'is_active': True
        },
        {
            'parameter_name': 'mphostname',
            'parameter_value': os.environ.get('COMPUTERNAME', os.environ.get('HOSTNAME', 'localhost')),
            'parameter_type': 'STRING',
            'category': 'SYSTEM',
            'description': 'Current system hostname',
            'is_system': True,
            'is_active': True
        },
    ]


class GlobalParametersView(APIView):
    """
    API View for managing Global Parameters
    GET: List all parameters or filter by category
    POST: Create new parameter
    PUT: Update existing parameter
    DELETE: Delete parameter
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all global parameters including system parameters"""
        try:
            user = UserProfile.objects.get(user=request.user)
            category = request.query_params.get('category', None)
            include_system = request.query_params.get('include_system', 'true').lower() == 'true'
            
            # Get user-defined parameters
            if category and category != 'SYSTEM':
                parameters = GlobalParameters.objects.filter(user_id=user, category=category, is_active=True)
            elif category == 'SYSTEM':
                parameters = []
            else:
                parameters = GlobalParameters.objects.filter(user_id=user, is_active=True)
            
            # Build user parameters list
            data = []
            for param in parameters:
                data.append({
                    'id': str(param.id),
                    'parameter_name': param.parameter_name,
                    'parameter_value': param.parameter_value,
                    'parameter_type': param.parameter_type,
                    'category': param.category,
                    'description': param.description,
                    'is_active': param.is_active,
                    'is_system': False,
                    'created_at': param.created_at,
                    'updated_at': param.updated_at
                })
            
            # Add system parameters if requested
            if include_system:
                system_params = get_system_parameters()
                if category == 'SYSTEM':
                    # Only system parameters
                    data = system_params
                else:
                    # Prepend system parameters to user parameters
                    data = system_params + data
            
            return Response({
                'status': 'success',
                'data': data,
                'count': len(data),
                'system_count': len(get_system_parameters()),
                'user_count': len(data) - len(get_system_parameters()) if include_system else len(data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Create new global parameter"""
        try:
            user = UserProfile.objects.get(user=request.user)
            data = request.data
            
            # Check if parameter already exists
            if GlobalParameters.objects.filter(
                parameter_name=data.get('parameter_name'),
                user_id=user
            ).exists():
                return Response({
                    'status': 'error',
                    'message': 'Parameter with this name already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            parameter = GlobalParameters.objects.create(
                parameter_name=data.get('parameter_name'),
                parameter_value=data.get('parameter_value'),
                parameter_type=data.get('parameter_type', 'STRING'),
                category=data.get('category', 'GENERAL'),
                description=data.get('description', ''),
                is_active=data.get('is_active', True),
                user_id=user
            )
            
            return Response({
                'status': 'success',
                'message': 'Parameter created successfully',
                'data': {
                    'id': str(parameter.id),
                    'parameter_name': parameter.parameter_name
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """Update existing global parameter"""
        try:
            user = UserProfile.objects.get(user=request.user)
            param_id = request.data.get('id')
            
            parameter = GlobalParameters.objects.get(id=param_id, user_id=user)
            
            # Update fields
            if 'parameter_value' in request.data:
                parameter.parameter_value = request.data['parameter_value']
            if 'parameter_type' in request.data:
                parameter.parameter_type = request.data['parameter_type']
            if 'category' in request.data:
                parameter.category = request.data['category']
            if 'description' in request.data:
                parameter.description = request.data['description']
            if 'is_active' in request.data:
                parameter.is_active = request.data['is_active']
            
            parameter.save()
            
            return Response({
                'status': 'success',
                'message': 'Parameter updated successfully'
            }, status=status.HTTP_200_OK)
            
        except GlobalParameters.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Parameter not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request):
        """Delete global parameter (soft delete)"""
        try:
            user = UserProfile.objects.get(user=request.user)
            param_id = request.query_params.get('id')
            
            parameter = GlobalParameters.objects.get(id=param_id, user_id=user)
            parameter.is_active = False
            parameter.save()
            
            return Response({
                'status': 'success',
                'message': 'Parameter deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except GlobalParameters.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Parameter not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CSVLoadConfigurationView(APIView):
    """
    API View for managing CSV Load Configurations
    GET: List all configurations or get specific config
    POST: Create new configuration
    PUT: Update existing configuration
    DELETE: Delete configuration
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all CSV load configurations or specific one"""
        try:
            user = UserProfile.objects.get(user=request.user)
            config_id = request.query_params.get('id', None)
            load_type = request.query_params.get('load_type', None)
            
            if config_id:
                config = CSVLoadConfiguration.objects.get(id=config_id, user_id=user)
                data = self._serialize_config(config)
                return Response({
                    'status': 'success',
                    'data': data
                }, status=status.HTTP_200_OK)
            
            # Get all configurations
            if load_type:
                configs = CSVLoadConfiguration.objects.filter(user_id=user, load_type=load_type)
            else:
                configs = CSVLoadConfiguration.objects.filter(user_id=user)
            
            data = [self._serialize_config(config) for config in configs]
            
            return Response({
                'status': 'success',
                'data': data,
                'count': len(data)
            }, status=status.HTTP_200_OK)
            
        except CSVLoadConfiguration.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Configuration not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Create new CSV load configuration"""
        try:
            user = UserProfile.objects.get(user=request.user)
            data = request.data
            
            # If this is set as default, unset other defaults
            if data.get('is_default', False):
                CSVLoadConfiguration.objects.filter(
                    user_id=user,
                    load_type=data.get('load_type')
                ).update(is_default=False)
            
            config = CSVLoadConfiguration.objects.create(
                config_name=data.get('config_name'),
                load_type=data.get('load_type', 'DIRECT'),
                batch_size=data.get('batch_size', 1000),
                skip_rows=data.get('skip_rows', 0),
                delimiter=data.get('delimiter', ','),
                encoding=data.get('encoding', 'utf-8'),
                quote_char=data.get('quote_char', '"'),
                escape_char=data.get('escape_char', ''),
                staging_path=data.get('staging_path', ''),
                staging_table=data.get('staging_table', ''),
                staging_schema=data.get('staging_schema', ''),
                use_bulk_insert=data.get('use_bulk_insert', True),
                truncate_before_load=data.get('truncate_before_load', False),
                header_row=data.get('header_row', True),
                null_values=data.get('null_values', []),
                date_format=data.get('date_format', '%Y-%m-%d'),
                timestamp_format=data.get('timestamp_format', '%Y-%m-%d %H:%M:%S'),
                error_handling=data.get('error_handling', 'SKIP'),
                max_errors=data.get('max_errors', 100),
                is_default=data.get('is_default', False),
                user_id=user
            )
            
            return Response({
                'status': 'success',
                'message': 'Configuration created successfully',
                'data': {
                    'id': str(config.id),
                    'config_name': config.config_name
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """Update existing CSV load configuration"""
        try:
            user = UserProfile.objects.get(user=request.user)
            config_id = request.data.get('id')
            
            config = CSVLoadConfiguration.objects.get(id=config_id, user_id=user)
            
            # If setting as default, unset other defaults
            if request.data.get('is_default', False):
                CSVLoadConfiguration.objects.filter(
                    user_id=user,
                    load_type=config.load_type
                ).exclude(id=config_id).update(is_default=False)
            
            # Update all fields
            update_fields = [
                'config_name', 'load_type', 'batch_size', 'skip_rows', 'delimiter',
                'encoding', 'quote_char', 'escape_char', 'staging_path', 'staging_table',
                'staging_schema', 'use_bulk_insert', 'truncate_before_load', 'header_row',
                'null_values', 'date_format', 'timestamp_format', 'error_handling',
                'max_errors', 'is_default'
            ]
            
            for field in update_fields:
                if field in request.data:
                    setattr(config, field, request.data[field])
            
            config.save()
            
            return Response({
                'status': 'success',
                'message': 'Configuration updated successfully'
            }, status=status.HTTP_200_OK)
            
        except CSVLoadConfiguration.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Configuration not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request):
        """Delete CSV load configuration"""
        try:
            user = UserProfile.objects.get(user=request.user)
            config_id = request.query_params.get('id')
            
            config = CSVLoadConfiguration.objects.get(id=config_id, user_id=user)
            config.delete()
            
            return Response({
                'status': 'success',
                'message': 'Configuration deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except CSVLoadConfiguration.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Configuration not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _serialize_config(self, config):
        """Helper method to serialize configuration object"""
        return {
            'id': str(config.id),
            'config_name': config.config_name,
            'load_type': config.load_type,
            'batch_size': config.batch_size,
            'skip_rows': config.skip_rows,
            'delimiter': config.delimiter,
            'encoding': config.encoding,
            'quote_char': config.quote_char,
            'escape_char': config.escape_char,
            'staging_path': config.staging_path,
            'staging_table': config.staging_table,
            'staging_schema': config.staging_schema,
            'use_bulk_insert': config.use_bulk_insert,
            'truncate_before_load': config.truncate_before_load,
            'header_row': config.header_row,
            'null_values': config.null_values,
            'date_format': config.date_format,
            'timestamp_format': config.timestamp_format,
            'error_handling': config.error_handling,
            'max_errors': config.max_errors,
            'is_default': config.is_default,
            'created_at': config.created_at,
            'updated_at': config.updated_at
        }


class DefaultConfigurationView(APIView):
    """
    API View to get default configuration for a load type
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get default configuration for specified load type"""
        try:
            user = UserProfile.objects.get(user=request.user)
            load_type = request.query_params.get('load_type', 'DIRECT')
            
            config = CSVLoadConfiguration.objects.filter(
                user_id=user,
                load_type=load_type,
                is_default=True
            ).first()
            
            if not config:
                # Return default values if no configuration exists
                return Response({
                    'status': 'success',
                    'data': self._get_default_values(load_type)
                }, status=status.HTTP_200_OK)
            
            view = CSVLoadConfigurationView()
            data = view._serialize_config(config)
            
            return Response({
                'status': 'success',
                'data': data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_default_values(self, load_type):
        """Return default configuration values"""
        return {
            'load_type': load_type,
            'batch_size': 1000,
            'skip_rows': 0,
            'delimiter': ',',
            'encoding': 'utf-8',
            'quote_char': '"',
            'escape_char': '',
            'staging_path': '',
            'staging_table': '',
            'staging_schema': '',
            'use_bulk_insert': True,
            'truncate_before_load': False,
            'header_row': True,
            'null_values': ['', 'NULL', 'null', 'None'],
            'date_format': '%Y-%m-%d',
            'timestamp_format': '%Y-%m-%d %H:%M:%S',
            'error_handling': 'SKIP',
            'max_errors': 100,
            'is_default': False
        }


class FilePathResolverView(APIView):
    """
    API View for resolving file paths with global parameters
    Similar to Diyotta's file path resolution
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Resolve file path template with global parameters
        
        Request body:
        {
            "path_template": "/data/${FILE_DATE}/${FILE_NAME}",
            "runtime_params": {"FILE_DATE": "2024-01-15"}  // Optional
        }
        """
        try:
            from .file_path_resolver import FilePathResolver
            
            path_template = request.data.get('path_template')
            runtime_params = request.data.get('runtime_params', {})
            
            if not path_template:
                return Response({
                    'status': 'error',
                    'message': 'path_template is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            resolver = FilePathResolver(request.user)
            
            # Validate path template
            is_valid, missing_params = resolver.validate_path(path_template)
            
            # Check if runtime params cover missing params
            if missing_params:
                uncovered_params = [p for p in missing_params if p not in runtime_params]
                if uncovered_params:
                    return Response({
                        'status': 'error',
                        'message': 'Missing parameters',
                        'missing_parameters': uncovered_params,
                        'available_parameters': resolver.get_available_parameters()
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Resolve the path
            resolved_path = resolver.resolve_with_runtime_params(path_template, runtime_params)
            
            return Response({
                'status': 'success',
                'data': {
                    'original_template': path_template,
                    'resolved_path': resolved_path,
                    'parameters_used': FilePathResolver.extract_parameters(path_template)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """
        Get available global parameters for file path resolution
        """
        try:
            from .file_path_resolver import FilePathResolver
            
            resolver = FilePathResolver(request.user)
            available_params = resolver.get_available_parameters()
            
            # Get parameter details
            user = UserProfile.objects.get(user=request.user)
            parameters = GlobalParameters.objects.filter(
                user_id=user,
                is_active=True
            )
            
            param_details = []
            for param in parameters:
                param_details.append({
                    'name': param.parameter_name,
                    'value': param.parameter_value,
                    'type': param.parameter_type,
                    'category': param.category,
                    'description': param.description
                })
            
            return Response({
                'status': 'success',
                'data': {
                    'available_parameters': available_params,
                    'parameter_details': param_details,
                    'usage_examples': [
                        '/data/${FILE_DATE}/customers.csv',
                        '$BASE_PATH/$FILE_NAME',
                        '/home/data/${YEAR}/${MONTH}/${FILE_NAME}.csv'
                    ]
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
