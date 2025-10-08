# Role-Based Access Control (RBAC) Design for Datamplify

## 🎯 Overview

This document defines the role-based permission system for Datamplify, including roles, permissions, and implementation strategy.

---

## 📋 Roles & Permissions Matrix

### Predefined Roles

| Role | Description | Level |
|------|-------------|-------|
| **Super Admin** | Full system access, can manage everything | 1 |
| **Admin** | Can manage users, roles, and system settings | 2 |
| **Data Engineer** | Can create and manage FlowBoards and connections | 3 |
| **Data Analyst** | Can view and execute FlowBoards, view data | 4 |
| **Viewer** | Read-only access to FlowBoards and data | 5 |

---

## 🔐 Permission Categories

### 1. User Management
- `user.view` - View user list
- `user.create` - Create new users
- `user.edit` - Edit user details
- `user.delete` - Delete users
- `user.manage_roles` - Assign/remove roles from users

### 2. Role Management
- `role.view` - View roles list
- `role.create` - Create new roles
- `role.edit` - Edit role details
- `role.delete` - Delete roles
- `role.assign_permissions` - Manage role permissions

### 3. FlowBoard Management
- `flowboard.view` - View FlowBoards
- `flowboard.create` - Create FlowBoards
- `flowboard.edit` - Edit FlowBoards
- `flowboard.delete` - Delete FlowBoards
- `flowboard.execute` - Run/execute FlowBoards
- `flowboard.schedule` - Schedule FlowBoard execution

### 4. Connection Management
- `connection.view` - View connections
- `connection.create` - Create connections
- `connection.edit` - Edit connections
- `connection.delete` - Delete connections
- `connection.test` - Test connections

### 5. Task Plan Management
- `taskplan.view` - View task plans
- `taskplan.create` - Create task plans
- `taskplan.edit` - Edit task plans
- `taskplan.delete` - Delete task plans
- `taskplan.execute` - Execute task plans

### 6. System Settings
- `system.view_settings` - View system settings
- `system.edit_settings` - Edit system settings
- `system.view_logs` - View activity logs
- `system.manage_api_keys` - Manage API keys
- `system.backup` - Perform system backup
- `system.maintenance` - Enable maintenance mode

### 7. Monitoring
- `monitor.view` - View monitoring dashboard
- `monitor.view_logs` - View execution logs
- `monitor.export` - Export monitoring data

---

## 📊 Role-Permission Mapping

### Super Admin
**All Permissions** ✅

### Admin
```python
ADMIN_PERMISSIONS = [
    # User Management
    'user.view', 'user.create', 'user.edit', 'user.delete', 'user.manage_roles',
    
    # Role Management
    'role.view', 'role.create', 'role.edit', 'role.delete', 'role.assign_permissions',
    
    # FlowBoard (View/Execute only)
    'flowboard.view', 'flowboard.execute',
    
    # System Settings
    'system.view_settings', 'system.edit_settings', 'system.view_logs', 
    'system.manage_api_keys',
    
    # Monitoring
    'monitor.view', 'monitor.view_logs', 'monitor.export',
]
```

### Data Engineer
```python
DATA_ENGINEER_PERMISSIONS = [
    # FlowBoard Management
    'flowboard.view', 'flowboard.create', 'flowboard.edit', 'flowboard.delete',
    'flowboard.execute', 'flowboard.schedule',
    
    # Connection Management
    'connection.view', 'connection.create', 'connection.edit', 'connection.delete',
    'connection.test',
    
    # Task Plan Management
    'taskplan.view', 'taskplan.create', 'taskplan.edit', 'taskplan.delete',
    'taskplan.execute',
    
    # Monitoring
    'monitor.view', 'monitor.view_logs', 'monitor.export',
]
```

### Data Analyst
```python
DATA_ANALYST_PERMISSIONS = [
    # FlowBoard (View/Execute only)
    'flowboard.view', 'flowboard.execute',
    
    # Connection (View only)
    'connection.view',
    
    # Task Plan (View/Execute only)
    'taskplan.view', 'taskplan.execute',
    
    # Monitoring
    'monitor.view', 'monitor.view_logs',
]
```

### Viewer
```python
VIEWER_PERMISSIONS = [
    # FlowBoard (View only)
    'flowboard.view',
    
    # Connection (View only)
    'connection.view',
    
    # Task Plan (View only)
    'taskplan.view',
    
    # Monitoring (View only)
    'monitor.view',
]
```

---

## 🗄️ Database Schema

### Permission Model
```python
class Permission(models.Model):
    code = models.CharField(max_length=100, unique=True)  # e.g., 'user.create'
    name = models.CharField(max_length=200)  # e.g., 'Create User'
    category = models.CharField(max_length=50)  # e.g., 'user', 'flowboard'
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Role Model
```python
class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, related_name='roles')
    is_system_role = models.BooleanField(default=False)  # Cannot be deleted
    level = models.IntegerField(default=5)  # Lower = more powerful
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### UserRole Model (Many-to-Many)
```python
class UserRole(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'role')
```

---

## 🔧 Implementation Components

### 1. Permission Decorator
```python
from functools import wraps
from django.http import JsonResponse

def require_permission(permission_code):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            if not user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            if has_permission(user, permission_code):
                return view_func(request, *args, **kwargs)
            else:
                return JsonResponse({'error': 'Permission denied'}, status=403)
        
        return wrapper
    return decorator
```

### 2. Permission Checker
```python
def has_permission(user, permission_code):
    """Check if user has specific permission"""
    # Super admin has all permissions
    if user.is_superuser:
        return True
    
    # Get all user's roles
    user_roles = UserRole.objects.filter(user=user).select_related('role')
    
    # Check if any role has the permission
    for user_role in user_roles:
        if user_role.role.permissions.filter(code=permission_code).exists():
            return True
    
    return False

def has_any_permission(user, permission_codes):
    """Check if user has any of the specified permissions"""
    return any(has_permission(user, code) for code in permission_codes)

def has_all_permissions(user, permission_codes):
    """Check if user has all of the specified permissions"""
    return all(has_permission(user, code) for code in permission_codes)
```

### 3. Middleware (Optional)
```python
class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add permission checker to request
        request.has_permission = lambda code: has_permission(request.user, code)
        
        response = self.get_response(request)
        return response
```

---

## 📡 API Endpoints

### Role Management
```
GET    /api/roles/                    # List all roles
POST   /api/roles/                    # Create role
GET    /api/roles/{id}/               # Get role details
PUT    /api/roles/{id}/               # Update role
DELETE /api/roles/{id}/               # Delete role
POST   /api/roles/{id}/permissions/  # Assign permissions to role
```

### Permission Management
```
GET    /api/permissions/              # List all permissions
GET    /api/permissions/categories/   # Get permission categories
```

### User Role Assignment
```
GET    /api/users/{id}/roles/         # Get user's roles
POST   /api/users/{id}/roles/         # Assign role to user
DELETE /api/users/{id}/roles/{role_id}/ # Remove role from user
```

### Permission Check
```
POST   /api/auth/check-permission/    # Check if user has permission
Body: { "permission": "flowboard.create" }
```

---

## 🚀 Usage Examples

### In Views
```python
from authentication.permissions import require_permission

@require_permission('flowboard.create')
def create_flowboard(request):
    # Only users with flowboard.create permission can access
    pass

@require_permission('user.delete')
def delete_user(request, user_id):
    # Only users with user.delete permission can access
    pass
```

### In Templates/Frontend
```python
# Check permission in view
def get_flowboard_list(request):
    flowboards = FlowBoard.objects.all()
    
    # Add permission flags
    context = {
        'flowboards': flowboards,
        'can_create': has_permission(request.user, 'flowboard.create'),
        'can_edit': has_permission(request.user, 'flowboard.edit'),
        'can_delete': has_permission(request.user, 'flowboard.delete'),
    }
    return JsonResponse(context)
```

### Programmatic Check
```python
if request.has_permission('flowboard.delete'):
    # Show delete button
    pass
```

---

## 🔄 Migration Strategy

### Step 1: Create Models
1. Create Permission, Role, UserRole models
2. Run migrations

### Step 2: Seed Initial Data
```python
# Create default permissions
permissions = [
    ('user.view', 'View Users', 'user'),
    ('user.create', 'Create User', 'user'),
    # ... all permissions
]

for code, name, category in permissions:
    Permission.objects.get_or_create(
        code=code,
        defaults={'name': name, 'category': category}
    )

# Create default roles
super_admin = Role.objects.create(
    name='Super Admin',
    is_system_role=True,
    level=1
)
super_admin.permissions.set(Permission.objects.all())
```

### Step 3: Migrate Existing Users
```python
# Assign default role to existing users
default_role = Role.objects.get(name='Data Analyst')
for user in UserProfile.objects.all():
    UserRole.objects.get_or_create(
        user=user,
        role=default_role
    )
```

### Step 4: Add Permission Checks
- Add decorators to existing views
- Update API responses with permission flags

---

## 🧪 Testing

### Test Permission Checks
```python
def test_user_has_permission():
    user = UserProfile.objects.create(username='test')
    role = Role.objects.create(name='Test Role')
    permission = Permission.objects.create(code='test.permission')
    role.permissions.add(permission)
    UserRole.objects.create(user=user, role=role)
    
    assert has_permission(user, 'test.permission') == True
    assert has_permission(user, 'other.permission') == False
```

---

## 📝 Best Practices

1. **Principle of Least Privilege**: Assign minimum required permissions
2. **Role Hierarchy**: Use role levels to prevent privilege escalation
3. **Audit Trail**: Log all permission changes
4. **Regular Review**: Periodically review and update permissions
5. **Custom Roles**: Allow creating custom roles for specific needs

---

**Version**: 1.0.0  
**Last Updated**: October 7, 2025
