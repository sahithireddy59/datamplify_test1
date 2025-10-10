"""
File Path Resolver Utility
Resolves file paths using global parameters, similar to Diyotta's functionality
"""

import os
import re
from .models import GlobalParameters
from authentication.models import UserProfile


class FilePathResolver:
    """
    Resolves file paths with global parameter substitution
    Supports patterns like: ${PARAMETER_NAME} or $PARAMETER_NAME
    """
    def __init__(self, user):
        self.user = user
        self.parameters_cache = {}
        self._load_parameters()
    
    def get_all_parameters(self):
        """Get all available parameters (system + user + global)"""
        from .global_parameters_views import get_system_parameters
        
        params = {}
        
        # Get system parameters first
        system_params = get_system_parameters()
        for param in system_params:
            params[param['parameter_name']] = param['parameter_value']
        
        # Get user-defined global parameters (can override system if needed)
        global_params = GlobalParameters.objects.filter(
            user_id=self.user,
            is_active=True
        )
        
        for param in global_params:
            params[param.parameter_name] = param.parameter_value
        
        return params
    
    def resolve_path(self, path_template):
        """
        Resolve a path template with global parameters
        Examples:
            Input: "/data/${FILE_DATE}/customers.csv"
            Output: "/data/2024-01-15/customers.csv"
            
            Input: "$BASE_PATH/$FILE_NAME"
            Output: "/home/data/customers.csv"
        """
        if not path_template:
            return path_template
        
        resolved_path = path_template
        
        # Pattern 1: ${PARAMETER_NAME}
        pattern1 = r'\$\{([A-Za-z0-9_]+)\}'
        matches1 = re.finditer(pattern1, resolved_path)
        for match in matches1:
            param_name = match.group(1)
            param_value = self.parameters_cache.get(param_name, '')
            resolved_path = resolved_path.replace(match.group(0), param_value)
        
        # Pattern 2: $PARAMETER_NAME (word boundary)
        pattern2 = r'\$([A-Za-z0-9_]+)\b'
        matches2 = re.finditer(pattern2, resolved_path)
        for match in matches2:
            param_name = match.group(1)
            param_value = self.parameters_cache.get(param_name, '')
            resolved_path = resolved_path.replace(match.group(0), param_value)
        
        return resolved_path
    
    def validate_path(self, path_template):
        """
        Validate if all parameters in the path template exist
        Returns: (is_valid, missing_parameters)
        """
        missing_params = []
        
        # Find all parameter references
        pattern1 = r'\$\{([A-Za-z0-9_]+)\}'
        pattern2 = r'\$([A-Za-z0-9_]+)\b'
        
        params_found = set()
        params_found.update(re.findall(pattern1, path_template))
        params_found.update(re.findall(pattern2, path_template))
        
        for param_name in params_found:
            if param_name not in self.parameters_cache:
                missing_params.append(param_name)
        
        return len(missing_params) == 0, missing_params
    
    def get_available_parameters(self):
        """Get list of available parameters"""
        return list(self.parameters_cache.keys())
    
    def resolve_with_runtime_params(self, path_template, runtime_params=None):
        """
        Resolve path with both global and runtime parameters
        Runtime parameters take precedence over global parameters
        
        Args:
            path_template: Path template string
            runtime_params: Dict of runtime parameter overrides
        """
        if runtime_params is None:
            runtime_params = {}
        
        # Merge runtime params with global params (runtime takes precedence)
        merged_params = {**self.parameters_cache, **runtime_params}
        
        resolved_path = path_template
        
        # Pattern 1: ${PARAMETER_NAME}
        pattern1 = r'\$\{([A-Za-z0-9_]+)\}'
        matches1 = re.finditer(pattern1, resolved_path)
        for match in matches1:
            param_name = match.group(1)
            param_value = merged_params.get(param_name, '')
            resolved_path = resolved_path.replace(match.group(0), param_value)
        
        # Pattern 2: $PARAMETER_NAME
        pattern2 = r'\$([A-Za-z0-9_]+)\b'
        matches2 = re.finditer(pattern2, resolved_path)
        for match in matches2:
            param_name = match.group(1)
            param_value = merged_params.get(param_name, '')
            resolved_path = resolved_path.replace(match.group(0), param_value)
        
        return resolved_path
    
    @staticmethod
    def extract_parameters(path_template):
        """
        Extract all parameter names from a path template
        Returns: List of parameter names
        """
        pattern1 = r'\$\{([A-Za-z0-9_]+)\}'
        pattern2 = r'\$([A-Za-z0-9_]+)\b'
        
        params = set()
        params.update(re.findall(pattern1, path_template))
        params.update(re.findall(pattern2, path_template))
        
        return list(params)
    
    def resolve_file_list(self, directory_template, file_pattern=None):
        """
        Resolve directory path and optionally list files matching pattern
        
        Args:
            directory_template: Directory path with parameters
            file_pattern: Optional file pattern (e.g., "*.csv")
        
        Returns:
            List of resolved file paths
        """
        resolved_dir = self.resolve_path(directory_template)
        
        if not os.path.exists(resolved_dir):
            return []
        
        if not os.path.isdir(resolved_dir):
            return []
        
        if file_pattern:
            import glob
            pattern_path = os.path.join(resolved_dir, file_pattern)
            return glob.glob(pattern_path)
        else:
            return [os.path.join(resolved_dir, f) for f in os.listdir(resolved_dir)]


def resolve_file_path(user, path_template, runtime_params=None):
    """
    Convenience function to resolve a file path
    
    Args:
        user: Django user object
        path_template: Path template string
        runtime_params: Optional runtime parameter overrides
    
    Returns:
        Resolved file path string
    """
    resolver = FilePathResolver(user)
    if runtime_params:
        return resolver.resolve_with_runtime_params(path_template, runtime_params)
    return resolver.resolve_path(path_template)


def validate_file_path_template(user, path_template):
    """
    Validate if a file path template can be resolved
    
    Returns:
        Dict with 'valid' (bool) and 'missing_parameters' (list)
    """
    resolver = FilePathResolver(user)
    is_valid, missing_params = resolver.validate_path(path_template)
    
    return {
        'valid': is_valid,
        'missing_parameters': missing_params,
        'available_parameters': resolver.get_available_parameters()
    }
