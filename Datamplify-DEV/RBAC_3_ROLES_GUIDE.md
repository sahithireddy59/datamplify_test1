# 🔐 Datamplify RBAC - 3 Roles System

## 📋 Overview

Your Datamplify system now has **3 simple roles**:
1. **Admin** - Full access to everything
2. **Employee** - Can work with FlowBoards, Connections, and Task Plans
3. **Viewer** - Read-only access

---

## 🎯 The 3 Roles Explained

### 1. **Admin** (Level 1)
**Description**: Full system access - can manage users, roles, and all system features

**Total Permissions**: ALL 38 permissions

**What they can do**:
- ✅ **Everything** - Full control of the system
- ✅ Manage users (create, edit, delete)
- ✅ Manage roles and permissions
- ✅ Create, edit, delete FlowBoards
- ✅ Manage connections
- ✅ Configure system settings
- ✅ View activity logs
- ✅ Manage API keys
- ✅ Everything else

**Use Case**: System administrators, IT managers, Super users

---

### 2. **Employee** (Level 2)
**Description**: Can create and manage FlowBoards, connections, and task plans

**Total Permissions**: 15 permissions

**What they can do**:
- ✅ **FlowBoards**: View, Create, Edit, Delete, Execute, Schedule
- ✅ **Connections**: View, Create, Edit, Delete, Test
- ✅ **Task Plans**: View, Create, Edit, Delete, Execute
- ✅ **Monitoring**: View dashboard, View logs, Export data
- ❌ **Cannot**: Manage users, Manage roles, Change system settings

**Use Case**: Data engineers, ETL developers, Regular employees who build data pipelines

---

### 3. **Viewer** (Level 3)
**Description**: Read-only access - can view but not modify anything

**Total Permissions**: 4 permissions

**What they can do**:
- ✅ **FlowBoards**: View only
- ✅ **Connections**: View only
- ✅ **Task Plans**: View only
- ✅ **Monitoring**: View dashboard only
- ❌ **Cannot**: Create, Edit, Delete, Execute anything

**Use Case**: Stakeholders, Managers, Auditors, Guests

---

## 📊 Permission Comparison Table

| Feature | Admin | Employee | Viewer |
|---------|-------|----------|--------|
| **User Management** | ✅ All | ❌ None | ❌ None |
| **Role Management** | ✅ All | ❌ None | ❌ None |
| **FlowBoard - View** | ✅ | ✅ | ✅ |
| **FlowBoard - Create** | ✅ | ✅ | ❌ |
| **FlowBoard - Edit** | ✅ | ✅ | ❌ |
| **FlowBoard - Delete** | ✅ | ✅ | ❌ |
| **FlowBoard - Execute** | ✅ | ✅ | ❌ |
| **FlowBoard - Schedule** | ✅ | ✅ | ❌ |
| **Connection - View** | ✅ | ✅ | ✅ |
| **Connection - Create** | ✅ | ✅ | ❌ |
| **Connection - Edit** | ✅ | ✅ | ❌ |
| **Connection - Delete** | ✅ | ✅ | ❌ |
| **Connection - Test** | ✅ | ✅ | ❌ |
| **Task Plan - View** | ✅ | ✅ | ✅ |
| **Task Plan - Create** | ✅ | ✅ | ❌ |
| **Task Plan - Edit** | ✅ | ✅ | ❌ |
| **Task Plan - Delete** | ✅ | ✅ | ❌ |
| **Task Plan - Execute** | ✅ | ✅ | ❌ |
| **System Settings** | ✅ All | ❌ None | ❌ None |
| **Activity Logs** | ✅ View | ❌ None | ❌ None |
| **API Keys** | ✅ Manage | ❌ None | ❌ None |
| **Monitoring** | ✅ All | ✅ View/Export | ✅ View only |

---

## 🚀 Setup Instructions

### Step 1: Run Migrations
```bash
cd c:\Users\vsahithi\Desktop\datamplify\Datamplify_backend\Datamplify-DEV

# Create migration files
python manage.py makemigrations authentication

# Apply migrations
python manage.py migrate authentication
```

### Step 2: Seed RBAC Data
```bash
# This creates 38 permissions and 3 roles
python manage.py seed_rbac
```

**Output:**
```
✓ Created 38 permissions
✓ Created 3 roles
  • Admin (Level 1): 38 permissions
  • Employee (Level 2): 15 permissions
  • Viewer (Level 3): 4 permissions
```

### Step 3: Assign Roles to Users

#### **Option A: Django Shell**
```bash
python manage.py shell
```

```python
from authentication.models import UserProfile
from authentication.models_rbac import Role, UserRole

# Example 1: Make someone an Admin
admin_user = UserProfile.objects.get(username='admin')
admin_role = Role.objects.get(name='Admin')
UserRole.objects.create(user=admin_user, role=admin_role)

# Example 2: Make someone an Employee
employee_user = UserProfile.objects.get(username='john_doe')
employee_role = Role.objects.get(name='Employee')
UserRole.objects.create(user=employee_user, role=employee_role)

# Example 3: Make someone a Viewer
viewer_user = UserProfile.objects.get(username='jane_smith')
viewer_role = Role.objects.get(name='Viewer')
UserRole.objects.create(user=viewer_user, role=viewer_role)
```

#### **Option B: Assign Default Role to All Users**
```python
from authentication.models import UserProfile
from authentication.models_rbac import Role, UserRole

# Assign Employee role to all existing users
employee_role = Role.objects.get(name='Employee')

for user in UserProfile.objects.all():
    if not UserRole.objects.filter(user=user).exists():
        UserRole.objects.create(user=user, role=employee_role)
        print(f"✓ {user.username} → Employee")
```

---

## 💡 Common Use Cases

### Use Case 1: New Employee Joins
```python
# Create user with Employee role
user = UserProfile.objects.create_user(
    username='new_employee',
    email='new@company.com',
    password='temp_password'
)

employee_role = Role.objects.get(name='Employee')
UserRole.objects.create(user=user, role=employee_role)
```

### Use Case 2: Promote Employee to Admin
```python
user = UserProfile.objects.get(username='john_doe')

# Remove Employee role
UserRole.objects.filter(user=user, role__name='Employee').delete()

# Assign Admin role
admin_role = Role.objects.get(name='Admin')
UserRole.objects.create(user=user, role=admin_role)
```

### Use Case 3: Give Guest Viewer Access
```python
guest = UserProfile.objects.create_user(
    username='guest_user',
    email='guest@company.com',
    password='guest_password'
)

viewer_role = Role.objects.get(name='Viewer')
UserRole.objects.create(user=guest, role=viewer_role)
```

---

## 🔍 Check User Permissions

### Check User's Role
```python
from authentication.models_rbac import UserRole

user = UserProfile.objects.get(username='john_doe')
user_roles = UserRole.objects.filter(user=user).values_list('role__name', flat=True)
print(list(user_roles))  # ['Employee']
```

### Check User's Permissions
```python
from authentication.permissions import get_user_permissions

user = UserProfile.objects.get(username='john_doe')
permissions = get_user_permissions(user)
print(f"Total permissions: {len(permissions)}")
for perm in permissions:
    print(f"  - {perm}")
```

### Check Specific Permission
```python
from authentication.permissions import has_permission

user = UserProfile.objects.get(username='john_doe')

print(f"Can create FlowBoards: {has_permission(user, 'flowboard.create')}")
print(f"Can delete users: {has_permission(user, 'user.delete')}")
```

---

## 🛡️ Protecting Your Views

### Example 1: Protect FlowBoard Creation
```python
# FlowBoard/views.py
from authentication.permissions import require_permission

@require_permission('flowboard.create')
def create_flowboard(request):
    # Only Admin and Employee can access
    # Viewer gets 403 Forbidden
    pass
```

### Example 2: Protect User Management
```python
# authentication/views.py
from authentication.permissions import require_permission

@require_permission('user.create')
def create_user(request):
    # Only Admin can access
    # Employee and Viewer get 403 Forbidden
    pass
```

### Example 3: Check Permission in Logic
```python
def list_flowboards(request):
    flowboards = FlowBoard.objects.all()
    
    return JsonResponse({
        'flowboards': list(flowboards.values()),
        'can_create': has_permission(request.user, 'flowboard.create'),
        'can_edit': has_permission(request.user, 'flowboard.edit'),
        'can_delete': has_permission(request.user, 'flowboard.delete'),
    })
```

---

## 🎨 Frontend Integration

### Angular Example
```typescript
// Load user permissions
ngOnInit() {
  this.workbenchService.getMyPermissions().subscribe(data => {
    this.userRole = data.roles[0].name;  // 'Admin', 'Employee', or 'Viewer'
    this.permissions = data.permissions;
    
    this.canCreate = this.permissions.includes('flowboard.create');
    this.canEdit = this.permissions.includes('flowboard.edit');
    this.canDelete = this.permissions.includes('flowboard.delete');
  });
}
```

### Template Example
```html
<!-- Show for Admin and Employee only -->
<button *ngIf="canCreate" (click)="createFlowboard()">
  Create FlowBoard
</button>

<!-- Show for Admin only -->
<button *ngIf="permissions.includes('user.create')" (click)="createUser()">
  Add User
</button>

<!-- Show for everyone -->
<button (click)="viewFlowboard()">
  View FlowBoard
</button>
```

---

## 📝 Quick Reference

### Get Role
```python
admin_role = Role.objects.get(name='Admin')
employee_role = Role.objects.get(name='Employee')
viewer_role = Role.objects.get(name='Viewer')
```

### Assign Role
```python
UserRole.objects.create(user=user, role=role)
```

### Remove Role
```python
UserRole.objects.filter(user=user, role=role).delete()
```

### Check Permission
```python
has_permission(user, 'flowboard.create')  # True/False
```

---

## ✅ Summary

**3 Simple Roles:**
1. **Admin** → Everything (38 permissions)
2. **Employee** → Work with data (15 permissions)
3. **Viewer** → Read-only (4 permissions)

**Setup:**
1. Run migrations
2. Run `seed_rbac`
3. Assign roles to users

**Usage:**
- Use `@require_permission()` decorator to protect views
- Use `has_permission()` to check permissions
- Frontend shows/hides UI based on permissions

**Your RBAC system is now ready!** 🎉
