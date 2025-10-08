# RBAC Implementation Guide

## 📋 Step-by-Step Implementation

### Step 1: Update Django Models

Add RBAC models to your authentication app's `models.py`:

```python
# In authentication/models.py
from .models_rbac import Permission, Role, UserRole

# Or import them directly in your models.py file
```

### Step 2: Create Migrations

```bash
# Create migration files
python manage.py makemigrations authentication

# Apply migrations
python manage.py migrate
```

### Step 3: Seed Initial Data

```bash
# Run the seed command to create permissions and roles
python manage.py seed_rbac
```

This will create:
- **38 Permissions** across 7 categories
- **5 Default Roles**: Super Admin, Admin, Data Engineer, Data Analyst, Viewer

### Step 4: Update Settings

Add the permission middleware to `settings.py`:

```python
# In Datamplify/settings.py

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'authentication.middleware.PermissionMiddleware',  # Add this line
]
```

### Step 5: Update URL Configuration

Add RBAC URLs to your main `urls.py`:

```python
# In Datamplify/urls.py

from django.urls import path, include

urlpatterns = [
    # ... existing patterns ...
    path('api/rbac/', include('authentication.urls_rbac')),
]
```

### Step 6: Apply Permissions to Views

#### Example 1: Protect FlowBoard Views

```python
# In FlowBoard/views.py
from authentication.permissions import require_permission

@require_permission('flowboard.create')
def create_flowboard(request):
    # Only users with flowboard.create permission can access
    pass

@require_permission('flowboard.delete')
def delete_flowboard(request, flowboard_id):
    # Only users with flowboard.delete permission can access
    pass
```

#### Example 2: Check Permissions in View Logic

```python
# In FlowBoard/views.py
from authentication.permissions import has_permission

def list_flowboards(request):
    flowboards = FlowBoard.objects.all()
    
    # Add permission flags to response
    return JsonResponse({
        'flowboards': list(flowboards.values()),
        'can_create': has_permission(request.user, 'flowboard.create'),
        'can_edit': has_permission(request.user, 'flowboard.edit'),
        'can_delete': has_permission(request.user, 'flowboard.delete'),
    })
```

#### Example 3: Use Middleware Methods

```python
# After adding PermissionMiddleware, you can use:
def some_view(request):
    if request.has_permission('flowboard.create'):
        # User has permission
        pass
    
    if request.has_any_permission('flowboard.edit', 'flowboard.delete'):
        # User has at least one permission
        pass
```

### Step 7: Assign Roles to Users

#### Via API:

```bash
# Assign role to user
curl -X POST http://localhost:8000/api/rbac/users/1/roles/assign/ \
  -H "Content-Type: application/json" \
  -d '{"role_id": 3}'

# Get user's roles and permissions
curl http://localhost:8000/api/rbac/users/1/roles/
```

#### Via Django Admin or Shell:

```python
from authentication.models_rbac import Role, UserRole
from authentication.models import UserProfile

user = UserProfile.objects.get(username='john_doe')
role = Role.objects.get(name='Data Engineer')

UserRole.objects.create(user=user, role=role)
```

---

## 🔌 API Endpoints Reference

### Permissions
- `GET /api/rbac/permissions/` - List all permissions
- `GET /api/rbac/permissions/categories/` - List permission categories

### Roles
- `GET /api/rbac/roles/` - List all roles
- `GET /api/rbac/roles/{id}/` - Get role details
- `POST /api/rbac/roles/create/` - Create new role
- `PUT /api/rbac/roles/{id}/update/` - Update role
- `DELETE /api/rbac/roles/{id}/delete/` - Delete role

### User Roles
- `GET /api/rbac/users/{id}/roles/` - Get user's roles
- `POST /api/rbac/users/{id}/roles/assign/` - Assign role to user
- `DELETE /api/rbac/users/{id}/roles/{role_id}/remove/` - Remove role from user

### Permission Checks
- `POST /api/rbac/check-permission/` - Check if user has permission
- `GET /api/rbac/my-permissions/` - Get current user's permissions

---

## 🎯 Usage Examples

### 1. Protect FlowBoard Endpoints

```python
# FlowBoard/views.py
from authentication.permissions import require_permission

@require_permission('flowboard.view')
def list_flowboards(request):
    # Implementation
    pass

@require_permission('flowboard.create')
def create_flowboard(request):
    # Implementation
    pass

@require_permission('flowboard.edit')
def update_flowboard(request, flowboard_id):
    # Implementation
    pass

@require_permission('flowboard.delete')
def delete_flowboard(request, flowboard_id):
    # Implementation
    pass
```

### 2. Protect Connection Endpoints

```python
# Connections/views.py
from authentication.permissions import require_permission

@require_permission('connection.view')
def list_connections(request):
    pass

@require_permission('connection.create')
def create_connection(request):
    pass

@require_permission('connection.test')
def test_connection(request):
    pass
```

### 3. Protect User Management

```python
# authentication/views.py
from authentication.permissions import require_permission

@require_permission('user.view')
def list_users(request):
    pass

@require_permission('user.create')
def create_user(request):
    pass

@require_permission('user.manage_roles')
def assign_role(request):
    pass
```

### 4. Frontend Permission Checks

Update your Angular services to check permissions:

```typescript
// workbench.service.ts
getMyPermissions() {
  return this.http.get(`${environment.apiUrl}/rbac/my-permissions/`);
}

checkPermission(permission: string) {
  return this.http.post(`${environment.apiUrl}/rbac/check-permission/`, 
    { permission }
  );
}
```

Use in components:

```typescript
// flowboard-list.component.ts
ngOnInit() {
  this.workbenchService.getMyPermissions().subscribe(data => {
    this.permissions = data.permissions;
    this.canCreate = this.permissions.includes('flowboard.create');
    this.canDelete = this.permissions.includes('flowboard.delete');
  });
}
```

---

## 🔄 Migration for Existing Users

If you have existing users, assign them default roles:

```python
# Create a migration or run in Django shell
from authentication.models_rbac import Role, UserRole
from authentication.models import UserProfile

# Get default role (e.g., Data Analyst)
default_role = Role.objects.get(name='Data Analyst')

# Assign to all existing users without roles
for user in UserProfile.objects.all():
    if not UserRole.objects.filter(user=user).exists():
        UserRole.objects.create(user=user, role=default_role)
        print(f"Assigned {default_role.name} to {user.username}")
```

---

## 🧪 Testing

### Test Permission Checks

```python
# In Django shell or tests
from authentication.models_rbac import Role, UserRole, Permission
from authentication.permissions import has_permission
from authentication.models import UserProfile

# Create test user
user = UserProfile.objects.create(username='test_user')

# Assign role
role = Role.objects.get(name='Data Engineer')
UserRole.objects.create(user=user, role=role)

# Test permissions
assert has_permission(user, 'flowboard.create') == True
assert has_permission(user, 'user.delete') == False
```

### Test API Endpoints

```bash
# Get my permissions
curl http://localhost:8000/api/rbac/my-permissions/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check specific permission
curl -X POST http://localhost:8000/api/rbac/check-permission/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"permission": "flowboard.create"}'
```

---

## 📊 Default Roles & Permissions

### Super Admin (Level 1)
- **All permissions** ✅

### Admin (Level 2)
- User management (all)
- Role management (all)
- FlowBoard (view, execute)
- System settings (all)
- Monitoring (all)

### Data Engineer (Level 3)
- FlowBoard (all)
- Connection (all)
- Task Plan (all)
- Monitoring (all)

### Data Analyst (Level 4)
- FlowBoard (view, execute)
- Connection (view)
- Task Plan (view, execute)
- Monitoring (view, logs)

### Viewer (Level 5)
- FlowBoard (view)
- Connection (view)
- Task Plan (view)
- Monitoring (view)

---

## 🔒 Security Best Practices

1. **Principle of Least Privilege**: Assign minimum required permissions
2. **Regular Audits**: Review user permissions periodically
3. **Cache Clearing**: Permission cache is cleared when roles change
4. **System Roles**: Cannot delete or modify system roles
5. **Audit Trail**: All role assignments are logged with timestamp and assigner

---

## 🚀 Quick Start Checklist

- [ ] Run migrations: `python manage.py migrate`
- [ ] Seed RBAC data: `python manage.py seed_rbac`
- [ ] Add middleware to settings.py
- [ ] Add RBAC URLs to main urls.py
- [ ] Assign roles to existing users
- [ ] Add permission decorators to views
- [ ] Update frontend to check permissions
- [ ] Test permission checks

---

**Version**: 1.0.0  
**Last Updated**: October 7, 2025
