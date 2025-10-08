# 👥 How to Add Roles to Users

## Method 1: Using Django Shell (Recommended for Initial Setup)

### Step 1: Open Django Shell
```bash
cd c:\Users\vsahithi\Desktop\datamplify\Datamplify_backend\Datamplify-DEV
python manage.py shell
```

### Step 2: Assign Role to Single User
```python
from authentication.models_rbac import Role, UserRole
from authentication.models import UserProfile

# Get the user
user = UserProfile.objects.get(username='john_doe')  # Replace with actual username
# OR get by email
# user = UserProfile.objects.get(email='john@example.com')

# Get the role
role = Role.objects.get(name='Data Engineer')  # Choose: Super Admin, Admin, Data Engineer, Data Analyst, Viewer

# Assign role to user
UserRole.objects.create(user=user, role=role)

print(f"✓ Assigned '{role.name}' to {user.username}")
```

### Step 3: Assign Role to Multiple Users
```python
from authentication.models_rbac import Role, UserRole
from authentication.models import UserProfile

# Get the role
analyst_role = Role.objects.get(name='Data Analyst')

# Get multiple users
users = UserProfile.objects.filter(username__in=['user1', 'user2', 'user3'])

# Assign role to all
for user in users:
    UserRole.objects.get_or_create(user=user, role=analyst_role)
    print(f"✓ {user.username} → {analyst_role.name}")
```

### Step 4: Assign Default Role to ALL Users
```python
from authentication.models_rbac import Role, UserRole
from authentication.models import UserProfile

# Get default role
default_role = Role.objects.get(name='Data Analyst')

# Assign to all users who don't have any role
for user in UserProfile.objects.all():
    if not UserRole.objects.filter(user=user).exists():
        UserRole.objects.create(user=user, role=default_role)
        print(f"✓ {user.username} → {default_role.name}")
    else:
        print(f"⊘ {user.username} already has roles")
```

---

## Method 2: Using API Endpoints

### Assign Role via API
```bash
# Replace:
# - YOUR_TOKEN with actual auth token
# - 1 with actual user_id
# - 3 with actual role_id (3 = Data Engineer)

curl -X POST http://localhost:8000/api/rbac/users/1/roles/assign/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"role_id": 3}'
```

### Get User's Current Roles
```bash
curl http://localhost:8000/api/rbac/users/1/roles/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Remove Role from User
```bash
curl -X DELETE http://localhost:8000/api/rbac/users/1/roles/3/remove/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Method 3: Programmatically in Views

### In Your View Code
```python
from authentication.models_rbac import Role, UserRole

def assign_role_on_user_creation(user):
    """Assign default role when user is created"""
    default_role = Role.objects.get(name='Data Analyst')
    UserRole.objects.create(user=user, role=default_role)
```

### In User Registration View
```python
from authentication.models_rbac import Role, UserRole

def register_user(request):
    # ... create user ...
    user = UserProfile.objects.create(username=username, email=email)
    
    # Assign default role
    default_role = Role.objects.get(name='Viewer')
    UserRole.objects.create(user=user, role=default_role)
    
    return JsonResponse({'message': 'User created with Viewer role'})
```

---

## 📋 Available Roles

| Role ID | Role Name | Level | Description |
|---------|-----------|-------|-------------|
| 1 | Super Admin | 1 | Full system access |
| 2 | Admin | 2 | User/Role management |
| 3 | Data Engineer | 3 | FlowBoard/Connection management |
| 4 | Data Analyst | 4 | View & execute FlowBoards |
| 5 | Viewer | 5 | Read-only access |

---

## 🔍 Check User's Roles and Permissions

### In Django Shell
```python
from authentication.models_rbac import UserRole
from authentication.permissions import get_user_permissions
from authentication.models import UserProfile

# Get user
user = UserProfile.objects.get(username='john_doe')

# Get all roles
user_roles = UserRole.objects.filter(user=user).select_related('role')
for ur in user_roles:
    print(f"Role: {ur.role.name} (Level {ur.role.level})")

# Get all permissions
permissions = get_user_permissions(user)
print(f"\nPermissions ({len(permissions)}):")
for perm in permissions:
    print(f"  - {perm}")
```

### Via API
```bash
# Get user's roles and permissions
curl http://localhost:8000/api/rbac/users/1/roles/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get current user's permissions
curl http://localhost:8000/api/rbac/my-permissions/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔄 Common Scenarios

### Scenario 1: New User Registration
```python
# When creating a new user, assign default role
from authentication.models_rbac import Role, UserRole

def create_user(username, email, password):
    user = UserProfile.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    # Assign default Viewer role
    viewer_role = Role.objects.get(name='Viewer')
    UserRole.objects.create(user=user, role=viewer_role)
    
    return user
```

### Scenario 2: Promote User
```python
# Remove old role and assign new role
from authentication.models_rbac import Role, UserRole

user = UserProfile.objects.get(username='john_doe')

# Remove current roles
UserRole.objects.filter(user=user).delete()

# Assign new role
new_role = Role.objects.get(name='Data Engineer')
UserRole.objects.create(user=user, role=new_role)

print(f"✓ Promoted {user.username} to {new_role.name}")
```

### Scenario 3: Assign Multiple Roles
```python
# User can have multiple roles
from authentication.models_rbac import Role, UserRole

user = UserProfile.objects.get(username='john_doe')

# Assign multiple roles
roles = ['Data Engineer', 'Data Analyst']
for role_name in roles:
    role = Role.objects.get(name=role_name)
    UserRole.objects.get_or_create(user=user, role=role)
    print(f"✓ Added {role_name}")
```

---

## 🛠️ Utility Functions

### Create Helper Function
```python
# Add to authentication/utils.py

from authentication.models_rbac import Role, UserRole
from authentication.permissions import clear_user_permission_cache

def assign_role(user, role_name):
    """Assign a role to a user"""
    role = Role.objects.get(name=role_name)
    user_role, created = UserRole.objects.get_or_create(user=user, role=role)
    clear_user_permission_cache(user)
    return created

def remove_role(user, role_name):
    """Remove a role from a user"""
    role = Role.objects.get(name=role_name)
    deleted = UserRole.objects.filter(user=user, role=role).delete()
    clear_user_permission_cache(user)
    return deleted[0] > 0

def get_user_role_names(user):
    """Get list of role names for a user"""
    return list(UserRole.objects.filter(user=user).values_list('role__name', flat=True))
```

### Usage
```python
from authentication.utils import assign_role, remove_role, get_user_role_names

user = UserProfile.objects.get(username='john_doe')

# Assign role
assign_role(user, 'Data Engineer')

# Remove role
remove_role(user, 'Viewer')

# Get roles
roles = get_user_role_names(user)
print(roles)  # ['Data Engineer']
```

---

## ⚠️ Important Notes

1. **Clear Cache**: When roles change, permission cache is automatically cleared
2. **Multiple Roles**: Users can have multiple roles (permissions are cumulative)
3. **System Roles**: Cannot delete Super Admin, Admin, Data Engineer, Data Analyst, Viewer
4. **Audit Trail**: UserRole tracks who assigned the role and when

---

## 🧪 Testing

### Test Role Assignment
```python
# In Django shell
from authentication.models_rbac import Role, UserRole
from authentication.permissions import has_permission
from authentication.models import UserProfile

# Create test user
user = UserProfile.objects.create(username='test_user')

# Assign Data Engineer role
role = Role.objects.get(name='Data Engineer')
UserRole.objects.create(user=user, role=role)

# Test permissions
assert has_permission(user, 'flowboard.create') == True
assert has_permission(user, 'user.delete') == False

print("✓ Tests passed!")
```

---

## 📞 Quick Commands Reference

```python
# Get user
user = UserProfile.objects.get(username='USERNAME')

# Get role
role = Role.objects.get(name='ROLE_NAME')

# Assign role
UserRole.objects.create(user=user, role=role)

# Remove role
UserRole.objects.filter(user=user, role=role).delete()

# Get user's roles
UserRole.objects.filter(user=user).values_list('role__name', flat=True)

# Get users with specific role
UserRole.objects.filter(role__name='Data Engineer').values_list('user__username', flat=True)
```

---

**Need more help?** Check `HOW_TO_USE_RBAC.md` for complete guide!
