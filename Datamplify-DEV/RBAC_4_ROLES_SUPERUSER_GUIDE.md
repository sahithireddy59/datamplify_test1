# 🔐 Datamplify RBAC - 4 Roles with SuperUser

## 📋 Role Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│  1. SuperUser (Level 1)                                     │
│     ↓ can manage                                            │
│  2. Admin (Level 2)                                         │
│     ↓ can create/manage                                     │
│  3. Employee (Level 3)                                      │
│  4. Viewer (Level 4)                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 The 4 Roles Explained

### 1. **SuperUser** (Level 1) 👑
**Description**: System owner - full access including Django admin panel

**Total Permissions**: ALL 38 permissions

**What they can do**:
- ✅ **Everything** - Complete system control
- ✅ Access Django Admin Panel (`/admin`)
- ✅ Manage all users including Admins
- ✅ Manage all roles and permissions
- ✅ Configure system settings
- ✅ Manage API keys
- ✅ Full FlowBoard, Connection, TaskPlan access
- ✅ View all logs and monitoring

**Use Case**: System owner, CTO, IT Director

**How to create**: 
```python
user.is_superuser = True
user.is_staff = True
user.save()
```

---

### 2. **Admin** (Level 2) 👨‍💼
**Description**: Can manage users (add Employee/Viewer) and assign permissions

**Total Permissions**: 12 permissions

**What they can do**:
- ✅ **User Management**: Create, Edit, Delete users
- ✅ **Assign Roles**: Can assign Employee or Viewer roles to users
- ✅ **View Roles**: Can see available roles
- ✅ **FlowBoard**: View and Execute (cannot create/edit/delete)
- ✅ **Connections**: View only
- ✅ **System**: View settings and logs
- ✅ **Monitoring**: View dashboard and logs
- ❌ **Cannot**: Access Django admin, Create FlowBoards, Manage system settings

**Use Case**: HR managers, Team leads, Department heads

---

### 3. **Employee** (Level 3) 👨‍💻
**Description**: Can create and manage FlowBoards, connections, and task plans

**Total Permissions**: 19 permissions

**What they can do**:
- ✅ **FlowBoard**: Full CRUD + Execute + Schedule
- ✅ **Connections**: Full CRUD + Test
- ✅ **Task Plans**: Full CRUD + Execute
- ✅ **Monitoring**: View, Logs, Export
- ❌ **Cannot**: Manage users, Access admin panel, Change system settings

**Use Case**: Data engineers, ETL developers, Regular employees

---

### 4. **Viewer** (Level 4) 👁️
**Description**: Read-only access - can view but not modify anything

**Total Permissions**: 4 permissions

**What they can do**:
- ✅ **FlowBoard**: View only
- ✅ **Connections**: View only
- ✅ **Task Plans**: View only
- ✅ **Monitoring**: View only
- ❌ **Cannot**: Create, Edit, Delete, Execute anything

**Use Case**: Stakeholders, Managers, Auditors, Guests

---

## 📊 Permission Comparison Table

| Feature | SuperUser | Admin | Employee | Viewer |
|---------|-----------|-------|----------|--------|
| **Django Admin Panel** | ✅ | ❌ | ❌ | ❌ |
| **Manage All Users** | ✅ | ✅ | ❌ | ❌ |
| **Assign Roles** | ✅ | ✅ | ❌ | ❌ |
| **Manage Roles** | ✅ | ❌ | ❌ | ❌ |
| **System Settings** | ✅ Edit | ✅ View | ❌ | ❌ |
| **API Keys** | ✅ | ❌ | ❌ | ❌ |
| **FlowBoard - View** | ✅ | ✅ | ✅ | ✅ |
| **FlowBoard - Create** | ✅ | ❌ | ✅ | ❌ |
| **FlowBoard - Edit** | ✅ | ❌ | ✅ | ❌ |
| **FlowBoard - Delete** | ✅ | ❌ | ✅ | ❌ |
| **FlowBoard - Execute** | ✅ | ✅ | ✅ | ❌ |
| **Connection - View** | ✅ | ✅ | ✅ | ✅ |
| **Connection - Create** | ✅ | ❌ | ✅ | ❌ |
| **Connection - Edit** | ✅ | ❌ | ✅ | ❌ |
| **Task Plan - Create** | ✅ | ❌ | ✅ | ❌ |
| **Monitoring** | ✅ All | ✅ View | ✅ Export | ✅ View |

---

## 🚀 Setup Instructions

### Step 1: Update RBAC Data
```bash
cd c:\Users\vsahithi\Desktop\datamplify\Datamplify_backend\Datamplify-DEV

# Re-seed with 4 roles
python manage.py seed_rbac
```

**Output:**
```
✓ Created 38 permissions
✓ Created 4 roles
  • SuperUser (Level 1): 38 permissions
  • Admin (Level 2): 12 permissions
  • Employee (Level 3): 19 permissions
  • Viewer (Level 4): 4 permissions
```

### Step 2: Create SuperUser

#### **Option A: Using Django Command**
```bash
python manage.py createsuperuser
```
Follow prompts to create username, email, password.

#### **Option B: Using Django Shell**
```bash
python manage.py shell
```

```python
from authentication.models import UserProfile, Role, UserRole

# Create superuser
superuser = UserProfile.objects.create_superuser(
    username='superadmin',
    email='super@company.com',
    password='SuperSecurePassword123!'
)

# Assign SuperUser role
superuser_role = Role.objects.get(name='SuperUser')
UserRole.objects.create(user=superuser, role=superuser_role)

print(f"✓ Created SuperUser: {superuser.username}")
```

### Step 3: Assign Roles to Existing Users

```python
from authentication.models import UserProfile, Role, UserRole

# Get roles
admin_role = Role.objects.get(name='Admin')
employee_role = Role.objects.get(name='Employee')
viewer_role = Role.objects.get(name='Viewer')

# Assign Admin to specific users
admin_users = ['hr_manager', 'team_lead']
for username in admin_users:
    user = UserProfile.objects.get(username=username)
    UserRole.objects.get_or_create(user=user, role=admin_role)
    print(f"✓ {username} → Admin")

# Assign Employee to regular users
for user in UserProfile.objects.filter(is_superuser=False):
    if not UserRole.objects.filter(user=user).exists():
        UserRole.objects.get_or_create(user=user, role=employee_role)
        print(f"✓ {user.username} → Employee")
```

---

## 🔐 Django Admin Panel Access

### **Only SuperUser Can Access:**
```
URL: http://localhost:8000/admin/
```

**Requirements:**
```python
user.is_superuser = True  # Must be True
user.is_staff = True      # Must be True
```

**To make existing user a SuperUser:**
```python
from authentication.models import UserProfile

user = UserProfile.objects.get(username='admin')
user.is_superuser = True
user.is_staff = True
user.save()

print(f"✓ {user.username} can now access Django Admin")
```

---

## 👨‍💼 Admin Role: Managing Users

### **What Admin Can Do:**

#### **1. Create New Employee:**
```python
from authentication.models import UserProfile, Role, UserRole

# Admin creates new employee
new_user = UserProfile.objects.create_user(
    username='new_employee',
    email='employee@company.com',
    password='TempPassword123!'
)

# Assign Employee role
employee_role = Role.objects.get(name='Employee')
UserRole.objects.create(user=new_user, role=employee_role)

print(f"✓ Created Employee: {new_user.username}")
```

#### **2. Create New Viewer:**
```python
new_viewer = UserProfile.objects.create_user(
    username='guest_user',
    email='guest@company.com',
    password='GuestPass123!'
)

viewer_role = Role.objects.get(name='Viewer')
UserRole.objects.create(user=new_viewer, role=viewer_role)

print(f"✓ Created Viewer: {new_viewer.username}")
```

#### **3. Change User's Role:**
```python
from authentication.permissions import clear_user_permission_cache

user = UserProfile.objects.get(username='john_doe')

# Remove current role
UserRole.objects.filter(user=user).delete()

# Assign new role
viewer_role = Role.objects.get(name='Viewer')
UserRole.objects.create(user=user, role=viewer_role)

# Clear cache
clear_user_permission_cache(user)

print(f"✓ Changed {user.username} to Viewer")
```

---

## 🔄 Typical Workflow

### **Scenario 1: Company Setup**

```python
# 1. SuperUser creates the system (done once)
superuser = UserProfile.objects.create_superuser(
    username='cto',
    email='cto@company.com',
    password='SecurePass123!'
)

# 2. SuperUser creates Admins (HR managers)
admin_role = Role.objects.get(name='Admin')
for email in ['hr1@company.com', 'hr2@company.com']:
    admin = UserProfile.objects.create_user(
        username=email.split('@')[0],
        email=email,
        password='TempPass123!'
    )
    UserRole.objects.create(user=admin, role=admin_role)

# 3. Admins create Employees and Viewers
# (Admins do this through the UI or API)
```

### **Scenario 2: New Employee Joins**

```
1. Admin logs into system
2. Admin goes to "User Management"
3. Admin clicks "Add User"
4. Admin fills: username, email, password
5. Admin selects role: "Employee"
6. Admin clicks "Create"
7. ✓ New employee can now login and work
```

### **Scenario 3: Employee Promoted to Admin**

```python
from authentication.models import UserProfile, Role, UserRole
from authentication.permissions import clear_user_permission_cache

# SuperUser promotes employee
user = UserProfile.objects.get(username='john_doe')

# Remove Employee role
UserRole.objects.filter(user=user).delete()

# Assign Admin role
admin_role = Role.objects.get(name='Admin')
UserRole.objects.create(user=user, role=admin_role)

clear_user_permission_cache(user)

print(f"✓ {user.username} promoted to Admin")
```

---

## 🛡️ Security Best Practices

### **1. Protect SuperUser Account**
```python
# Only 1-2 SuperUsers maximum
# Use strong passwords
# Enable 2FA (if available)
# Regularly audit SuperUser actions
```

### **2. Admin Limitations**
```python
# Admins CANNOT:
# - Access Django admin panel
# - Create other Admins (only SuperUser can)
# - Change system settings
# - Manage API keys
```

### **3. Audit Trail**
```python
# Track who assigned roles
UserRole.objects.filter(user=user).values('assigned_by', 'assigned_at')
```

---

## 📝 Quick Reference Commands

### **Create SuperUser:**
```bash
python manage.py createsuperuser
```

### **Assign Roles:**
```python
from authentication.models import UserProfile, Role, UserRole

user = UserProfile.objects.get(username='USERNAME')
role = Role.objects.get(name='ROLE_NAME')  # SuperUser, Admin, Employee, Viewer
UserRole.objects.create(user=user, role=role)
```

### **Check User's Role:**
```python
user_roles = UserRole.objects.filter(user=user).values_list('role__name', flat=True)
print(list(user_roles))
```

### **Check Permissions:**
```python
from authentication.permissions import get_user_permissions
permissions = get_user_permissions(user)
print(f"Total: {len(permissions)} permissions")
```

---

## ✅ Summary

**4-Role Hierarchy:**
1. **SuperUser** (Level 1) - System owner, Django admin access, ALL permissions
2. **Admin** (Level 2) - Manages users, assigns Employee/Viewer roles
3. **Employee** (Level 3) - Works with FlowBoards, Connections, TaskPlans
4. **Viewer** (Level 4) - Read-only access

**Key Points:**
- ✅ Only SuperUser can access Django admin panel
- ✅ Admin can create/manage Employee and Viewer users
- ✅ Admin can assign roles but cannot create other Admins
- ✅ SuperUser manages Admins
- ✅ Clear separation of responsibilities

**Your 4-role RBAC system is ready!** 🎉
