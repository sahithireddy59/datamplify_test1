# 🔐 Django Admin Panel - Complete Setup Guide

## 📋 Overview

The Django Admin panel is a powerful interface for managing your Datamplify system. **Only SuperUsers** can access it.

---

## 🚀 Step-by-Step Setup

### **Step 1: Re-seed RBAC with 4 Roles**

```bash
cd c:\Users\vsahithi\Desktop\datamplify\Datamplify_backend\Datamplify-DEV

python manage.py seed_rbac
```

**Expected Output:**
```
Starting RBAC seeding...
Creating permissions...
✓ Created 38 permissions
Creating roles...
✓ Created 4 roles

=== RBAC Seeding Complete ===
Total Permissions: 38
Total Roles: 4

Roles created:
  • SuperUser (Level 1): 38 permissions
  • Admin (Level 2): 12 permissions
  • Employee (Level 3): 19 permissions
  • Viewer (Level 4): 4 permissions
```

---

### **Step 2: Create SuperUser Account**

```bash
python manage.py createsuperuser
```

**You'll be prompted:**
```
Username (leave blank to use 'vsahithi'): superadmin
Email address: super@company.com
Password: ********
Password (again): ********
Superuser created successfully.
```

**Password Requirements:**
- At least 8 characters
- Not too similar to username/email
- Mix of letters, numbers, and symbols

---

### **Step 3: Assign SuperUser Role**

```bash
python manage.py shell
```

**Run this code:**
```python
from authentication.models import UserProfile, Role, UserRole

# Get the superuser you just created
superuser = UserProfile.objects.get(username='superadmin')

# Ensure admin flags are set
superuser.is_superuser = True
superuser.is_staff = True
superuser.save()

# Assign SuperUser role
superuser_role = Role.objects.get(name='SuperUser')
UserRole.objects.create(user=superuser, role=superuser_role)

print(f"✓ {superuser.username} can now access Django Admin")
print(f"✓ is_superuser: {superuser.is_superuser}")
print(f"✓ is_staff: {superuser.is_staff}")
print(f"✓ Role: {superuser_role.name}")
```

**Exit shell:**
```python
exit()
```

---

### **Step 4: Start Django Server**

```bash
python manage.py runserver
```

**Output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

### **Step 5: Access Django Admin Panel**

1. **Open your browser**
2. **Go to:** `http://127.0.0.1:8000/admin/`
3. **Login with:**
   - Username: `superadmin`
   - Password: (the password you set in Step 2)

4. **Click "Log in"**

---

## 🎯 What You Can Manage in Django Admin

### **1. User Profiles**
- View all users
- Create new users
- Edit user details
- Set user permissions (is_staff, is_superuser)
- Activate/deactivate users

### **2. Permissions**
- View all 38 permissions
- See permission categories
- Search permissions by code or name

### **3. Roles**
- View all 4 roles (SuperUser, Admin, Employee, Viewer)
- See which permissions each role has
- Edit role permissions (be careful with system roles!)

### **4. User Roles**
- See which users have which roles
- Assign roles to users
- View assignment history (who assigned, when)

### **5. Account Activations**
- View pending account activations
- See OTPs and expiry dates
- Manually activate accounts if needed

### **6. Password Resets**
- View password reset requests
- See reset tokens
- Manage reset requests

---

## 📸 Django Admin Interface

### **Main Dashboard:**
```
┌─────────────────────────────────────────────────────────┐
│  Django administration                                  │
├─────────────────────────────────────────────────────────┤
│  AUTHENTICATION                                         │
│    • User profiles          [+ Add] [Change]            │
│    • Permissions            [+ Add] [Change]            │
│    • Roles                  [+ Add] [Change]            │
│    • User roles             [+ Add] [Change]            │
│    • Account activations    [+ Add] [Change]            │
│    • Reset passwords        [+ Add] [Change]            │
│                                                         │
│  OAUTH2 PROVIDER                                        │
│    • Applications           [+ Add] [Change]            │
│    • Access tokens          [+ Add] [Change]            │
│    • ...                                                │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Common Admin Tasks

### **Task 1: Create New User from Admin Panel**

1. Click **"User profiles"** → **"+ Add user profile"**
2. Fill in:
   - Username: `new_employee`
   - Password: (set password)
   - Email: `employee@company.com`
3. Check **"Active"** checkbox
4. Click **"Save"**
5. Go to **"User roles"** → **"+ Add user role"**
6. Select:
   - User: `new_employee`
   - Role: `Employee`
7. Click **"Save"**

### **Task 2: Make User an Admin**

1. Go to **"User roles"**
2. Find the user's current role
3. Click to edit
4. Change Role to: `Admin`
5. Click **"Save"**

### **Task 3: View User's Permissions**

1. Go to **"User profiles"**
2. Click on username
3. Scroll to **"Permissions"** section
4. See:
   - Active status
   - Staff status
   - Superuser status
   - Groups
   - User permissions

### **Task 4: View Role Permissions**

1. Go to **"Roles"**
2. Click on role name (e.g., "Employee")
3. See:
   - Description
   - Level
   - System role status
   - All assigned permissions (with filter)

---

## 🛡️ Security Best Practices

### **1. Protect SuperUser Credentials**
```
✓ Use strong, unique password
✓ Don't share credentials
✓ Change password regularly
✓ Only create 1-2 SuperUsers maximum
```

### **2. Regular Audits**
```python
# Check who has SuperUser access
from authentication.models import UserProfile

superusers = UserProfile.objects.filter(is_superuser=True)
for user in superusers:
    print(f"SuperUser: {user.username} - {user.email}")
```

### **3. Monitor Admin Actions**
Django automatically logs all admin actions in `django_admin_log` table.

---

## 🔍 Troubleshooting

### **Problem 1: Can't Login to Admin**

**Check 1: Is user a superuser?**
```python
from authentication.models import UserProfile

user = UserProfile.objects.get(username='superadmin')
print(f"is_superuser: {user.is_superuser}")  # Must be True
print(f"is_staff: {user.is_staff}")          # Must be True
print(f"is_active: {user.is_active}")        # Must be True
```

**Fix:**
```python
user.is_superuser = True
user.is_staff = True
user.is_active = True
user.save()
```

### **Problem 2: Forgot SuperUser Password**

**Reset password:**
```bash
python manage.py changepassword superadmin
```

### **Problem 3: Admin Page Not Found**

**Check URL configuration:**
```python
# In Datamplify/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),  # Must be present
    # ...
]
```

### **Problem 4: Models Not Showing in Admin**

**Check admin.py:**
```python
# authentication/admin.py must have:
from django.contrib import admin
from .models import UserProfile, Permission, Role, UserRole

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass
```

---

## 📊 Admin vs Regular User Interface

| Feature | Django Admin | Regular App |
|---------|-------------|-------------|
| **Access** | SuperUser only | All users |
| **URL** | `/admin/` | `/` |
| **Purpose** | System management | Daily operations |
| **Interface** | Django default | Angular UI |
| **Users** | 1-2 SuperUsers | All employees |

---

## 🎯 Quick Reference

### **Access Admin:**
```
URL: http://127.0.0.1:8000/admin/
Username: superadmin
Password: (your password)
```

### **Create SuperUser:**
```bash
python manage.py createsuperuser
```

### **Check SuperUser Status:**
```python
from authentication.models import UserProfile
user = UserProfile.objects.get(username='USERNAME')
print(f"SuperUser: {user.is_superuser}")
print(f"Staff: {user.is_staff}")
```

### **Make User SuperUser:**
```python
user.is_superuser = True
user.is_staff = True
user.save()
```

---

## ✅ Checklist

- [ ] Run `python manage.py seed_rbac`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Assign SuperUser role via shell
- [ ] Start server: `python manage.py runserver`
- [ ] Access admin: `http://127.0.0.1:8000/admin/`
- [ ] Login with superuser credentials
- [ ] Verify all models are visible
- [ ] Create test user from admin panel

---

## 🎉 You're All Set!

Your Django Admin panel is now fully configured with:
- ✅ SuperUser account created
- ✅ RBAC models registered
- ✅ User management interface
- ✅ Role and permission management
- ✅ Secure access control

**Access it at: http://127.0.0.1:8000/admin/** 🚀
