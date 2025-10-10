# 🎨 User Management UI - Complete Implementation Guide

## ✅ Backend Complete!

### **APIs Created:**

#### **User Management:**
- `GET /v1/authentication/users/` - List all users
- `GET /v1/authentication/users/{user_id}/` - Get user details
- `POST /v1/authentication/users/invite/` - Invite new user
- `PUT /v1/authentication/users/{user_id}/status/` - Update user status
- `DELETE /v1/authentication/users/{user_id}/delete/` - Delete user

#### **Role Management:**
- `GET /v1/authentication/roles/` - List all roles
- `GET /v1/authentication/roles/{role_id}/` - Get role details
- `POST /v1/authentication/users/{user_id}/roles/assign/` - Assign role to user
- `DELETE /v1/authentication/users/{user_id}/roles/{role_id}/remove/` - Remove role

#### **Permissions:**
- `GET /v1/authentication/permissions/` - List all permissions
- `GET /v1/authentication/permissions/my/` - Get my permissions

---

## 🎨 Frontend Implementation

### **Step 1: Create User Management Component**

```bash
cd c:\Users\vsahithi\Desktop\datamplify\Datamplify_backend\Datamplify-angular

ng generate component components/admin/user-management
ng generate component components/admin/permissions-management
ng generate component components/admin/invite-user-modal
```

### **Step 2: User Management Component (user-management.component.ts)**

```typescript
import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './user-management.component.html',
  styleUrls: ['./user-management.component.scss']
})
export class UserManagementComponent implements OnInit {
  users: any[] = [];
  roles: any[] = [];
  selectedRole: string = 'all';
  searchQuery: string = '';
  currentUser: any = null;
  showInviteModal: boolean = false;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadUsers();
    this.loadRoles();
    this.loadCurrentUser();
  }

  loadUsers() {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    });

    let url = '/v1/authentication/users/';
    if (this.searchQuery) {
      url += `?search=${this.searchQuery}`;
    }
    if (this.selectedRole && this.selectedRole !== 'all') {
      url += `${this.searchQuery ? '&' : '?'}role=${this.selectedRole}`;
    }

    this.http.get<any>(url, { headers }).subscribe({
      next: (response) => {
        this.users = response.users;
      },
      error: (error) => {
        console.error('Error loading users:', error);
      }
    });
  }

  loadRoles() {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    });

    this.http.get<any>('/v1/authentication/roles/', { headers }).subscribe({
      next: (response) => {
        this.roles = response.roles;
      },
      error: (error) => {
        console.error('Error loading roles:', error);
      }
    });
  }

  loadCurrentUser() {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    });

    this.http.get<any>('/v1/authentication/permissions/my/', { headers }).subscribe({
      next: (response) => {
        this.currentUser = response;
      }
    });
  }

  assignRole(userId: string, roleId: number) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json'
    });

    this.http.post<any>(
      `/v1/authentication/users/${userId}/roles/assign/`,
      { role_id: roleId },
      { headers }
    ).subscribe({
      next: (response) => {
        alert(response.message);
        this.loadUsers();
      },
      error: (error) => {
        alert(error.error.error || 'Error assigning role');
      }
    });
  }

  removeRole(userId: string, roleId: number) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    });

    this.http.delete<any>(
      `/v1/authentication/users/${userId}/roles/${roleId}/remove/`,
      { headers }
    ).subscribe({
      next: (response) => {
        alert(response.message);
        this.loadUsers();
      },
      error: (error) => {
        alert(error.error.error || 'Error removing role');
      }
    });
  }

  toggleUserStatus(userId: string, currentStatus: boolean) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json'
    });

    this.http.put<any>(
      `/v1/authentication/users/${userId}/status/`,
      { is_active: !currentStatus },
      { headers }
    ).subscribe({
      next: (response) => {
        this.loadUsers();
      },
      error: (error) => {
        alert(error.error.error || 'Error updating user status');
      }
    });
  }

  deleteUser(userId: string) {
    if (!confirm('Are you sure you want to delete this user?')) {
      return;
    }

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    });

    this.http.delete<any>(
      `/v1/authentication/users/${userId}/delete/`,
      { headers }
    ).subscribe({
      next: (response) => {
        alert(response.message);
        this.loadUsers();
      },
      error: (error) => {
        alert(error.error.error || 'Error deleting user');
      }
    });
  }

  inviteUser(userData: any) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json'
    });

    this.http.post<any>(
      '/v1/authentication/users/invite/',
      userData,
      { headers }
    ).subscribe({
      next: (response) => {
        alert(response.message);
        this.showInviteModal = false;
        this.loadUsers();
      },
      error: (error) => {
        alert(error.error.error || 'Error inviting user');
      }
    });
  }

  getUserInitials(user: any): string {
    if (user.first_name && user.last_name) {
      return (user.first_name[0] + user.last_name[0]).toUpperCase();
    }
    return user.username.substring(0, 2).toUpperCase();
  }

  getRoleBadgeClass(roleName: string): string {
    switch(roleName.toLowerCase()) {
      case 'superuser': return 'badge-superuser';
      case 'admin': return 'badge-admin';
      case 'employee': return 'badge-employee';
      case 'viewer': return 'badge-viewer';
      default: return 'badge-default';
    }
  }

  getLastActiveText(lastLogin: string): string {
    if (!lastLogin) return 'Never';
    
    const now = new Date();
    const login = new Date(lastLogin);
    const diff = now.getTime() - login.getTime();
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Now';
    if (minutes < 60) return `${minutes} minutes ago`;
    if (hours < 24) return `${hours} hours ago`;
    return `${days} days ago`;
  }
}
```

---

### **Step 3: User Management HTML Template**

Create file: `user-management.component.html`

```html
<div class="user-management-container">
  <!-- Header -->
  <div class="header">
    <div class="tabs">
      <button class="tab active">
        <i class="fas fa-users"></i> User Management
      </button>
      <button class="tab" routerLink="/admin/permissions">
        <i class="fas fa-shield-alt"></i> Permissions
      </button>
      <button class="tab">
        <i class="fas fa-lock"></i> Security
      </button>
      <button class="tab">
        <i class="fas fa-cog"></i> System
      </button>
    </div>
  </div>

  <!-- Filters and Actions -->
  <div class="filters-section">
    <div class="search-box">
      <i class="fas fa-search"></i>
      <input 
        type="text" 
        placeholder="Search users..." 
        [(ngModel)]="searchQuery"
        (input)="loadUsers()"
      />
    </div>

    <div class="role-filter">
      <select [(ngModel)]="selectedRole" (change)="loadUsers()">
        <option value="all">All Roles</option>
        <option *ngFor="let role of roles" [value]="role.name">
          {{ role.name }}
        </option>
      </select>
    </div>

    <button class="btn-invite" (click)="showInviteModal = true">
      <i class="fas fa-user-plus"></i> Invite User
    </button>
  </div>

  <!-- User List -->
  <div class="users-list">
    <div class="user-card" *ngFor="let user of users">
      <!-- User Header -->
      <div class="user-header">
        <div class="user-avatar">
          {{ getUserInitials(user) }}
        </div>
        <div class="user-info">
          <div class="user-name">
            {{ user.username }}
            <span class="you-badge" *ngIf="currentUser && user.id === currentUser.user">You</span>
          </div>
          <div class="user-email">{{ user.email }}</div>
          <div class="user-meta">
            <span class="last-active">Last active: {{ getLastActiveText(user.last_login) }}</span>
            <span 
              class="role-badge" 
              *ngFor="let role of user.roles"
              [ngClass]="getRoleBadgeClass(role.name)"
            >
              <i class="fas fa-crown" *ngIf="role.name === 'SuperUser'"></i>
              <i class="fas fa-user-shield" *ngIf="role.name === 'Admin'"></i>
              <i class="fas fa-users" *ngIf="role.name === 'Employee'"></i>
              {{ role.name }}
            </span>
            <span 
              class="status-badge" 
              [ngClass]="user.is_active ? 'status-active' : 'status-inactive'"
            >
              <i class="fas fa-circle"></i> {{ user.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
        </div>

        <!-- Role Selector -->
        <div class="role-selector" *ngIf="user.id !== currentUser?.user">
          <select 
            class="role-dropdown"
            (change)="assignRole(user.id, $any($event.target).value)"
          >
            <option value="">Change Role...</option>
            <option 
              *ngFor="let role of roles" 
              [value]="role.id"
              [disabled]="user.roles.some((r: any) => r.id === role.id)"
            >
              {{ role.name }}
            </option>
          </select>
        </div>

        <!-- Delete Button -->
        <button 
          class="btn-delete" 
          *ngIf="user.id !== currentUser?.user && !user.is_superuser"
          (click)="deleteUser(user.id)"
        >
          <i class="fas fa-trash"></i>
        </button>
      </div>

      <!-- Permissions -->
      <div class="user-permissions">
        <div class="permissions-label">
          <i class="fas fa-shield-alt"></i> Permissions:
        </div>
        <div class="permissions-badges">
          <span 
            class="permission-badge" 
            *ngFor="let perm of user.permissions.slice(0, 5)"
          >
            {{ perm }}
          </span>
          <span class="permission-count" *ngIf="user.permission_count > 5">
            +{{ user.permission_count - 5 }} more
          </span>
        </div>
      </div>
    </div>
  </div>

  <!-- Invite User Modal -->
  <div class="modal" *ngIf="showInviteModal">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Invite New User</h3>
        <button class="btn-close" (click)="showInviteModal = false">×</button>
      </div>
      <div class="modal-body">
        <form #inviteForm="ngForm" (ngSubmit)="inviteUser(inviteForm.value)">
          <div class="form-group">
            <label>Username</label>
            <input type="text" name="username" ngModel required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="email" name="email" ngModel required />
          </div>
          <div class="form-group">
            <label>Password</label>
            <input type="password" name="password" ngModel required />
          </div>
          <div class="form-group">
            <label>Role</label>
            <select name="role_id" ngModel>
              <option value="">Select Role...</option>
              <option *ngFor="let role of roles" [value]="role.id">
                {{ role.name }}
              </option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" (click)="showInviteModal = false">
              Cancel
            </button>
            <button type="submit" class="btn-submit">
              Invite User
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>
```

---

## 🎨 Styling (user-management.component.scss)

The styling matches your purple theme from the screenshots. Full CSS provided in implementation files.

---

## ✅ Summary

**Backend Complete:**
- ✅ User list API
- ✅ Role assignment API
- ✅ User invite API
- ✅ Permission management API
- ✅ All routes configured

**Frontend Ready:**
- ✅ User Management component code
- ✅ Permissions display
- ✅ Role assignment dropdown
- ✅ Invite user modal
- ✅ Search and filter
- ✅ Purple theme styling

**Next Steps:**
1. Create the Angular components
2. Copy the TypeScript code
3. Copy the HTML template
4. Add the SCSS styling
5. Add routes to app.routes.ts
6. Test the UI

**Your User Management UI is ready to implement!** 🎉
