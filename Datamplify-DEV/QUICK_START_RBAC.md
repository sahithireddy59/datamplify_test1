# 🚀 RBAC Quick Start Guide

## ⚡ 5-Minute Setup

### **Step 1: Re-seed RBAC (30 seconds)**
```bash
cd c:\Users\vsahithi\Desktop\datamplify\Datamplify_backend\Datamplify-DEV
python manage.py seed_rbac
```

### **Step 2: Create SuperUser (1 minute)**
```bash
python manage.py createsuperuser
```
- Username: `superadmin`
- Email: `super@company.com`
- Password: `YourSecurePassword123!`

### **Step 3: Assign SuperUser Role (1 minute)**
```bash
python manage.py shell
```

```python
from authentication.models import UserProfile, Role, UserRole

superuser = UserProfile.objects.get(username='superadmin')
superuser.is_superuser = True
superuser.is_staff = True
superuser.save()

superuser_role = Role.objects.get(name='SuperUser')
UserRole.objects.create(user=superuser, role=superuser_role)

print("✓ SuperUser ready!")
exit()
```

### **Step 4: Assign Roles to Existing Users (2 minutes)**
```bash
python manage.py shell
```

```python
from authentication.models import UserProfile, Role, UserRole

# Get roles
admin_role = Role.objects.get(name='Admin')
employee_role = Role.objects.get(name='Employee')

# Assign Employee to all users (except superuser)
for user in UserProfile.objects.filter(is_superuser=False):
    UserRole.objects.get_or_create(user=user, role=employee_role)
    print(f"✓ {user.username} → Employee")

exit()
```

### **Step 5: Access Django Admin (30 seconds)**
```bash
python manage.py runserver
```

Open browser: `http://127.0.0.1:8000/admin/`
- Login: `superadmin` / `YourSecurePassword123!`

---

## ✅ Done!

Your RBAC system is now fully operational with:
- ✅ 4 Roles: SuperUser, Admin, Employee, Viewer
- ✅ 38 Permissions
- ✅ Django Admin Panel access
- ✅ All users assigned roles

---

## 📚 Full Documentation

- **Complete Guide**: `RBAC_4_ROLES_SUPERUSER_GUIDE.md`
- **Django Admin**: `DJANGO_ADMIN_LOGIN_GUIDE.md`
- **Assign Roles**: `HOW_TO_ASSIGN_ROLES.md`
- **Usage**: `HOW_TO_USE_RBAC.md`

---

## 🎯 The 4 Roles

| Role | Level | Permissions | Access |
|------|-------|-------------|--------|
| **SuperUser** | 1 | All 38 | Django Admin + Everything |
| **Admin** | 2 | 12 | Manage users, assign roles |
| **Employee** | 3 | 19 | Create FlowBoards, Connections |
| **Viewer** | 4 | 4 | Read-only access |

---

## 🔑 Quick Commands

**Create user with role:**
```python
from authentication.models import UserProfile, Role, UserRole

user = UserProfile.objects.create_user('username', 'email@company.com', 'password')
role = Role.objects.get(name='Employee')
UserRole.objects.create(user=user, role=role)
```

**Check user permissions:**
```python
from authentication.permissions import get_user_permissions
permissions = get_user_permissions(user)
print(f"Total: {len(permissions)} permissions")
```

**Protect a view:**
```python
from authentication.permissions import require_permission

@require_permission('flowboard.create')
def create_flowboard(request):
    # Only users with flowboard.create permission can access
    pass
```

---

**Your RBAC system is ready to use!** 🎉
