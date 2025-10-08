# 🛡️ Datamplify Admin Portal

A unified administrative interface for managing the Datamplify ETL platform.

## 🎯 Overview

The Admin Portal consolidates all administrative functions into a single, intuitive interface with a modern design and comprehensive features.

## 📁 Project Structure

```
src/app/components/admin/
├── admin-layout/              # Main layout with sidebar navigation
│   ├── admin-layout.component.ts
│   ├── admin-layout.component.html
│   └── admin-layout.component.scss
├── admin-dashboard/           # Dashboard with statistics
│   ├── admin-dashboard.component.ts
│   ├── admin-dashboard.component.html
│   └── admin-dashboard.component.scss
├── admin-settings/            # System settings management
│   ├── admin-settings.component.ts
│   ├── admin-settings.component.html
│   └── admin-settings.component.scss
├── admin-logs/                # Activity logs viewer
│   ├── admin-logs.component.ts
│   ├── admin-logs.component.html
│   └── admin-logs.component.scss
├── admin-api-keys/            # API keys management
│   ├── admin-api-keys.component.ts
│   ├── admin-api-keys.component.html
│   └── admin-api-keys.component.scss
└── admin.routes.ts            # Admin routing configuration
```

## 🚀 Quick Start

### 1. Access the Admin Portal

Navigate to: `http://localhost:4200/admin`

### 2. Admin Routes

The following routes are available:

- `/admin` - Redirects to dashboard
- `/admin/dashboard` - Main dashboard
- `/admin/users` - User management (existing component)
- `/admin/roles` - Role management (existing component)
- `/admin/settings` - System settings
- `/admin/logs` - Activity logs
- `/admin/api-keys` - API keys management

### 3. Features

#### 📊 Admin Dashboard
- **Statistics Cards**: Users, Roles, FlowBoards, Connections
- **Quick Actions**: Add User, Create Role, Settings, View Logs
- **System Health**: Status, uptime, disk usage, last backup
- **Recent Activity**: Timeline of user and system events

#### 👥 User Management
- Integrated existing `users-dashboard` component
- Create, edit, delete users
- Assign roles and permissions
- Manage user status (active/inactive)

#### 🛡️ Role Management
- Integrated existing `roles-dashboard` component
- Create and manage roles
- Assign privileges/permissions
- View users per role

#### ⚙️ System Settings
- Application configuration
- Feature toggles (audit logging, email notifications)
- Session timeout settings
- Maintenance mode

#### 📝 Activity Logs
- View all system and user activities
- Filter by type (User, System, Error, Security)
- Search functionality
- Severity indicators (Info, Success, Warning, Error)

#### 🔑 API Keys Management
- Add/manage API keys for external services
- Support for: Google AI, Perplexity, OpenAI, AWS, Azure
- Secure key storage (encrypted)
- Copy to clipboard functionality
- Usage tracking (last used timestamp)

## 🎨 Design Features

### Modern UI/UX
- **Gradient theme**: Purple/blue gradient for primary elements
- **Card-based layout**: Clean, organized information display
- **Responsive design**: Works on desktop, tablet, and mobile
- **Collapsible sidebar**: Maximize content area when needed
- **Smooth animations**: Hover effects and transitions

### Color Scheme
- Primary: `#667eea` to `#764ba2` (gradient)
- Success: `#38ef7d` to `#11998e`
- Info: `#6dd5ed` to `#2193b0`
- Warning: `#f5576c` to `#f093fb`

### Icons
Uses Font Awesome icons throughout:
- Dashboard: `fa-tachometer-alt`
- Users: `fa-users`
- Roles: `fa-user-shield`
- Settings: `fa-cog`
- Logs: `fa-history`
- API Keys: `fa-key`

## 🔧 Technical Implementation

### Components

All components are **standalone** with the following imports:
- `CommonModule` - Angular common directives
- `RouterModule` - Navigation
- `FormsModule` - Form handling
- `NgbModule` - Bootstrap components
- `NgxPaginationModule` - Pagination (where needed)

### Routing

Admin routes are lazy-loaded for performance:

```typescript
{
  path: 'admin',
  children: [
    {
      path: '',
      component: AdminLayoutComponent,
      children: [
        { path: 'dashboard', component: AdminDashboardComponent },
        { path: 'users', loadComponent: ... },
        { path: 'roles', loadComponent: ... },
        // ... more routes
      ]
    }
  ]
}
```

### Data Flow

1. **Dashboard Statistics**: Fetches data from `WorkbenchService`
2. **User/Role Management**: Uses existing services
3. **Settings**: Local state (TODO: API integration)
4. **Logs**: Mock data (TODO: API integration)
5. **API Keys**: Local state (TODO: API integration)

## 📋 TODO: Backend Integration

The following components need backend API integration:

### 1. System Settings API
```typescript
// POST /api/admin/settings
{
  appName: string,
  maxUploadSize: number,
  sessionTimeout: number,
  enableAuditLog: boolean,
  enableEmailNotifications: boolean,
  maintenanceMode: boolean
}
```

### 2. Activity Logs API
```typescript
// GET /api/admin/logs?type=all&search=&page=1&pageSize=10
{
  logs: [{
    id: number,
    type: string,
    user: string,
    action: string,
    details: string,
    timestamp: Date,
    severity: string
  }],
  total: number
}
```

### 3. API Keys API
```typescript
// POST /api/admin/api-keys
{
  name: string,
  provider: string,
  key: string (encrypted)
}

// GET /api/admin/api-keys
// DELETE /api/admin/api-keys/:id
```

## 🔒 Security Considerations

### Authentication & Authorization
- Add route guards to protect admin routes
- Verify user has admin role before access
- Implement token-based authentication

### API Key Security
- Encrypt API keys before storing in database
- Never expose full keys in responses
- Use environment variables for sensitive keys
- Implement key rotation policies

### Audit Logging
- Log all admin actions
- Track who, what, when, where
- Maintain immutable audit trail
- Regular log reviews

## 🧪 Testing

### Manual Testing Checklist
- [ ] Access admin portal from `/admin`
- [ ] Navigate through all menu items
- [ ] Test sidebar collapse/expand
- [ ] Verify statistics display correctly
- [ ] Test quick actions navigation
- [ ] Add/edit/delete users (if permissions allow)
- [ ] Create/modify roles
- [ ] Update system settings
- [ ] Filter and search logs
- [ ] Add/delete API keys
- [ ] Test responsive design on mobile

### Unit Tests (TODO)
- Component rendering tests
- Service integration tests
- Route guard tests
- Form validation tests

## 📱 Responsive Breakpoints

- **Desktop**: > 1024px - Full sidebar with descriptions
- **Tablet**: 768px - 1024px - Collapsible sidebar
- **Mobile**: < 768px - Hidden sidebar with toggle

## 🎯 Future Enhancements

1. **Advanced Analytics**
   - Charts and graphs for statistics
   - Trend analysis
   - Predictive insights

2. **Email Notifications**
   - Alert configuration
   - Email templates
   - Notification preferences

3. **Backup Management**
   - Schedule backups
   - Restore functionality
   - Backup history

4. **System Monitoring**
   - Real-time metrics
   - Performance monitoring
   - Resource usage graphs

5. **Multi-tenancy Support**
   - Organization management
   - Tenant isolation
   - Cross-tenant reporting

## 📚 Related Documentation

- [Admin Portal User Guide](./ADMIN_PORTAL_GUIDE.md) - Detailed user documentation
- [API Documentation](./API_DOCS.md) - Backend API reference
- [Security Guide](./SECURITY.md) - Security best practices

## 🤝 Contributing

When adding new admin features:

1. Create component in `components/admin/`
2. Add route to `admin.routes.ts`
3. Update sidebar menu in `admin-layout.component.ts`
4. Follow existing design patterns
5. Update documentation

## 📄 License

Copyright © 2025 Datamplify. All rights reserved.

---

**Version**: 1.0.0  
**Last Updated**: October 7, 2025  
**Maintainer**: Datamplify Development Team
