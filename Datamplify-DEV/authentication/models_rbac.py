"""
Role-Based Access Control (RBAC) Data Configuration for Datamplify

NOTE: The actual models (Permission, Role, UserRole) are defined in models.py
This file only contains the default permissions and roles data.
"""


# Default Permissions Data
DEFAULT_PERMISSIONS = [
    # User Management
    ('user.view', 'View Users', 'user', 'Can view user list and details'),
    ('user.create', 'Create User', 'user', 'Can create new users'),
    ('user.edit', 'Edit User', 'user', 'Can edit user details'),
    ('user.delete', 'Delete User', 'user', 'Can delete users'),
    ('user.manage_roles', 'Manage User Roles', 'user', 'Can assign/remove roles from users'),
    
    # Role Management
    ('role.view', 'View Roles', 'role', 'Can view roles list'),
    ('role.create', 'Create Role', 'role', 'Can create new roles'),
    ('role.edit', 'Edit Role', 'role', 'Can edit role details'),
    ('role.delete', 'Delete Role', 'role', 'Can delete roles'),
    ('role.assign_permissions', 'Assign Permissions', 'role', 'Can manage role permissions'),
    
    # FlowBoard Management
    ('flowboard.view', 'View FlowBoards', 'flowboard', 'Can view FlowBoards'),
    ('flowboard.create', 'Create FlowBoard', 'flowboard', 'Can create FlowBoards'),
    ('flowboard.edit', 'Edit FlowBoard', 'flowboard', 'Can edit FlowBoards'),
    ('flowboard.delete', 'Delete FlowBoard', 'flowboard', 'Can delete FlowBoards'),
    ('flowboard.execute', 'Execute FlowBoard', 'flowboard', 'Can run/execute FlowBoards'),
    ('flowboard.schedule', 'Schedule FlowBoard', 'flowboard', 'Can schedule FlowBoard execution'),
    
    # Connection Management
    ('connection.view', 'View Connections', 'connection', 'Can view connections'),
    ('connection.create', 'Create Connection', 'connection', 'Can create connections'),
    ('connection.edit', 'Edit Connection', 'connection', 'Can edit connections'),
    ('connection.delete', 'Delete Connection', 'connection', 'Can delete connections'),
    ('connection.test', 'Test Connection', 'connection', 'Can test connections'),
    
    # Task Plan Management
    ('taskplan.view', 'View Task Plans', 'taskplan', 'Can view task plans'),
    ('taskplan.create', 'Create Task Plan', 'taskplan', 'Can create task plans'),
    ('taskplan.edit', 'Edit Task Plan', 'taskplan', 'Can edit task plans'),
    ('taskplan.delete', 'Delete Task Plan', 'taskplan', 'Can delete task plans'),
    ('taskplan.execute', 'Execute Task Plan', 'taskplan', 'Can execute task plans'),
    
    # System Settings
    ('system.view_settings', 'View Settings', 'system', 'Can view system settings'),
    ('system.edit_settings', 'Edit Settings', 'system', 'Can edit system settings'),
    ('system.view_logs', 'View Logs', 'system', 'Can view activity logs'),
    ('system.manage_api_keys', 'Manage API Keys', 'system', 'Can manage API keys'),
    ('system.backup', 'System Backup', 'system', 'Can perform system backup'),
    ('system.maintenance', 'Maintenance Mode', 'system', 'Can enable maintenance mode'),
    
    # Monitoring
    ('monitor.view', 'View Monitoring', 'monitor', 'Can view monitoring dashboard'),
    ('monitor.view_logs', 'View Execution Logs', 'monitor', 'Can view execution logs'),
    ('monitor.export', 'Export Data', 'monitor', 'Can export monitoring data'),
]

# Default Roles Configuration
DEFAULT_ROLES = {
    'SuperUser': {
        'description': 'System owner - full access including Django admin panel and all system features',
        'level': 1,
        'is_system_role': True,
        'permissions': 'ALL'  # Gets all 38 permissions
    },
    'Admin': {
        'description': 'Can manage users (add Employee/Viewer) and assign permissions',
        'level': 2,
        'is_system_role': True,
        'permissions': [
            # User Management
            'user.view', 'user.create', 'user.edit', 'user.delete', 'user.manage_roles',
            
            # Role Management (view only, can assign roles)
            'role.view',
            
            # FlowBoard (view and execute only)
            'flowboard.view', 'flowboard.execute',
            
            # Connection (view only)
            'connection.view',
            
            # System Settings (view only)
            'system.view_settings', 'system.view_logs',
            
            # Monitoring
            'monitor.view', 'monitor.view_logs',
        ]
    },
    'Employee': {
        'description': 'Can create and manage FlowBoards, connections, and task plans',
        'level': 3,
        'is_system_role': True,
        'permissions': [
            # FlowBoard Management
            'flowboard.view', 'flowboard.create', 'flowboard.edit', 'flowboard.delete',
            'flowboard.execute', 'flowboard.schedule',
            
            # Connection Management
            'connection.view', 'connection.create', 'connection.edit', 'connection.delete', 'connection.test',
            
            # Task Plan Management
            'taskplan.view', 'taskplan.create', 'taskplan.edit', 'taskplan.delete', 'taskplan.execute',
            
            # Monitoring
            'monitor.view', 'monitor.view_logs', 'monitor.export',
        ]
    },
    'Viewer': {
        'description': 'Read-only access - can view but not modify anything',
        'level': 4,
        'is_system_role': True,
        'permissions': [
            'flowboard.view',
            'connection.view',
            'taskplan.view',
            'monitor.view',
        ]
    },
}
