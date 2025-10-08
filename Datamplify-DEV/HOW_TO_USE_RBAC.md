# 🚀 How to Use RBAC - Quick Guide

## Step 1: Setup (One-Time)

### 1.1 Run Migrations
```bash
cd c:\Users\vsahithi\Desktop\datamplify\Datamplify_backend\Datamplify-DEV

python manage.py makemigrations authentication
python manage.py migrate
```

### 1.2 Seed Permissions and Roles
```bash
python manage.py seed_rbac
```

You should see:
```
✓ Created 38 permissions
✓ Created 5 roles
  • Super Admin (Level 1): 38 permissions
  • Admin (Level 2): 20 permissions
  • Data Engineer (Level 3): 15 permissions
  • Data Analyst (Level 4): 7 permissions
  • Viewer (Level 5): 4 permissions
```

### 1.3 Update Settings
Open `Datamplify/settings.py` and add to MIDDLEWARE:

```python
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
    'authentication.middleware.PermissionMiddleware',  # ← Add this line
]
```

### 1.4 Add RBAC URLs
Open `Datamplify/urls.py` and add:

```python
from django.urls import path, include

urlpatterns = [
    # ... existing patterns ...
    path('api/rbac/', include('authentication.urls_rbac')),  # ← Add this line
]
```

---

## Step 2: Assign Roles to Users

### Option A: Via Django Shell
```bash
python manage.py shell
```

```python
from authentication.models_rbac import Role, UserRole
from authentication.models import UserProfile

# Get user
user = UserProfile.objects.get(username='john_doe')

# Get role
role = Role.objects.get(name='Data Engineer')

# Assign role
UserRole.objects.create(user=user, role=role)

print(f"✓ Assigned {role.name} to {user.username}")
```

### Option B: Via API
```bash
# Assign role to user (user_id=1, role_id=3)
curl -X POST http://localhost:8000/api/rbac/users/1/roles/assign/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"role_id": 3}'
```

### Option C: Assign Default Role to All Users
```python
# In Django shell
from authentication.models_rbac import Role, UserRole
from authentication.models import UserProfile

default_role = Role.objects.get(name='Data Analyst')

for user in UserProfile.objects.all():
    if not UserRole.objects.filter(user=user).exists():
        UserRole.objects.create(user=user, role=default_role)
        print(f"✓ {user.username} → {default_role.name}")
```

---

## Step 3: Protect Your Views

### Example 1: Protect FlowBoard Views

Open `FlowBoard/views.py` and add:

```python
from authentication.permissions import require_permission

# Protect create endpoint
@require_permission('flowboard.create')
def create_flowboard(request):
    # Your existing code
    pass

# Protect delete endpoint
@require_permission('flowboard.delete')
def delete_flowboard(request, flowboard_id):
    # Your existing code
    pass

# Protect execute endpoint
@require_permission('flowboard.execute')
def execute_flowboard(request, flowboard_id):
    # Your existing code
    pass
```

### Example 2: Check Permission in View Logic

```python
from authentication.permissions import has_permission

def list_flowboards(request):
    flowboards = FlowBoard.objects.all()
    
    # Add permission flags to response
    return JsonResponse({
        'flowboards': list(flowboards.values()),
        'permissions': {
            'can_create': has_permission(request.user, 'flowboard.create'),
            'can_edit': has_permission(request.user, 'flowboard.edit'),
            'can_delete': has_permission(request.user, 'flowboard.delete'),
            'can_execute': has_permission(request.user, 'flowboard.execute'),
        }
    })
```

### Example 3: Use Middleware (After Step 1.3)

```python
def some_view(request):
    # Check single permission
    if request.has_permission('flowboard.create'):
        # User can create
        pass
    
    # Check any permission
    if request.has_any_permission('flowboard.edit', 'flowboard.delete'):
        # User can edit OR delete
        pass
    
    # Get all user permissions
    user_permissions = request.get_permissions()
    # Returns: ['flowboard.view', 'flowboard.create', ...]
```

---

## Step 4: Test It

### 4.1 Check User Permissions
```bash
# Get current user's permissions
curl http://localhost:8000/api/rbac/my-permissions/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "user": "john_doe",
  "roles": [
    {"id": 3, "name": "Data Engineer", "level": 3}
  ],
  "permissions": [
    "flowboard.view",
    "flowboard.create",
    "flowboard.edit",
    "flowboard.delete",
    "flowboard.execute",
    "connection.view",
    "connection.create"
  ],
  "is_superuser": false
}
```

### 4.2 Check Specific Permission
```bash
curl -X POST http://localhost:8000/api/rbac/check-permission/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"permission": "flowboard.create"}'
```

Response:
```json
{
  "has_permission": true,
  "permission": "flowboard.create",
  "user": "john_doe"
}
```

### 4.3 List All Roles
```bash
curl http://localhost:8000/api/rbac/roles/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Step 5: Frontend Integration

### 5.1 Update Angular Service

Add to `workbench.service.ts`:

```typescript
// Get user permissions
getMyPermissions() {
  const currentUser = localStorage.getItem('currentUser');
  const token = JSON.parse(currentUser!)['Token'];
  return this.http.get(`${environment.apiUrl}/rbac/my-permissions/${token}`);
}

// Check specific permission
checkPermission(permission: string) {
  const currentUser = localStorage.getItem('currentUser');
  const token = JSON.parse(currentUser!)['Token'];
  return this.http.post(`${environment.apiUrl}/rbac/check-permission/${token}`, 
    { permission }
  );
}
```

### 5.2 Use in Component

```typescript
// flowboard-list.component.ts
export class FlowboardListComponent implements OnInit {
  permissions: string[] = [];
  canCreate = false;
  canDelete = false;

  ngOnInit() {
    // Load user permissions
    this.workbenchService.getMyPermissions().subscribe({
      next: (data: any) => {
        this.permissions = data.permissions;
        this.canCreate = this.permissions.includes('flowboard.create');
        this.canDelete = this.permissions.includes('flowboard.delete');
      }
    });
  }
}
```

### 5.3 Use in Template

```html
<!-- flowboard-list.component.html -->
<button *ngIf="canCreate" (click)="createFlowboard()">
  Create FlowBoard
</button>

<button *ngIf="canDelete" (click)="deleteFlowboard(flow.id)">
  Delete
</button>
```

---

## 📋 Quick Reference

### Available Permissions

**FlowBoard:**
- `flowboard.view` - View FlowBoards
- `flowboard.create` - Create FlowBoards
- `flowboard.edit` - Edit FlowBoards
- `flowboard.delete` - Delete FlowBoards
- `flowboard.execute` - Execute FlowBoards
- `flowboard.schedule` - Schedule FlowBoards

**User Management:**
- `user.view` - View users
- `user.create` - Create users
- `user.edit` - Edit users
- `user.delete` - Delete users
- `user.manage_roles` - Assign roles

**System:**
- `system.view_settings` - View settings
- `system.edit_settings` - Edit settings
- `system.view_logs` - View logs
- `system.manage_api_keys` - Manage API keys

[See RBAC_DESIGN.md for full list]

### Default Roles

| Role | Level | Permissions |
|------|-------|-------------|
| Super Admin | 1 | All (38) |
| Admin | 2 | User/Role mgmt, System settings (20) |
| Data Engineer | 3 | FlowBoard, Connection, TaskPlan (15) |
| Data Analyst | 4 | View & Execute (7) |
| Viewer | 5 | Read-only (4) |

---

## 🔧 Common Tasks

### Create Custom Role
```bash
curl -X POST http://localhost:8000/api/rbac/roles/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Custom Role",
    "description": "My custom role",
    "level": 4,
    "permissions": [1, 2, 3, 5, 8]
  }'
```

### Remove Role from User
```bash
curl -X DELETE http://localhost:8000/api/rbac/users/1/roles/3/remove/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get User's Roles
```bash
curl http://localhost:8000/api/rbac/users/1/roles/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ Checklist

- [ ] Run migrations
- [ ] Run seed_rbac command
- [ ] Add middleware to settings.py
- [ ] Add RBAC URLs to urls.py
- [ ] Assign roles to users
- [ ] Add @require_permission to views
- [ ] Update frontend to check permissions
- [ ] Test with different user roles

---

## 🆘 Troubleshooting

**Issue: Permission denied even with correct role**
- Clear cache: Restart Django server
- Check role assignment: `UserRole.objects.filter(user=user)`

**Issue: Middleware not working**
- Verify middleware is added to settings.py
- Ensure it's after AuthenticationMiddleware

**Issue: API endpoints not found**
- Check urls.py includes RBAC URLs
- Restart Django server

---

**Need Help?** Check `RBAC_DESIGN.md` and `RBAC_IMPLEMENTATION_GUIDE.md`
