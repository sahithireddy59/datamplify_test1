# Datamplify Admin Portal - User Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [Accessing the Admin Portal](#accessing-the-admin-portal)
3. [Admin Dashboard](#admin-dashboard)
4. [User Management](#user-management)
5. [Role Management](#role-management)
6. [System Settings](#system-settings)
7. [Activity Logs](#activity-logs)
8. [API Keys Management](#api-keys-management)

---

## Overview

The **Datamplify Admin Portal** is a unified administrative interface that brings together all system management features in one centralized location. It provides administrators with comprehensive tools to manage users, roles, system settings, and monitor application activity.

### Key Features:
- ✅ **Centralized Dashboard** - Overview of system statistics and health
- ✅ **User Management** - Create, edit, and manage user accounts
- ✅ **Role & Permissions** - Define roles and assign permissions
- ✅ **System Settings** - Configure application settings
- ✅ **Activity Logs** - Monitor user and system activity
- ✅ **API Keys** - Manage external service API keys

---

## Accessing the Admin Portal

### URL Access
Navigate to: `http://your-domain/admin`

### Navigation from Workbench
1. From the main Datamplify workbench
2. Look for the "Admin" link in the navigation menu
3. Click to access the Admin Portal

### Required Permissions
- Only users with **Administrator** role can access the Admin Portal
- Standard users will be redirected to the login page

---

## Admin Dashboard

The **Admin Dashboard** is the central hub of the Admin Portal, providing:

### Statistics Cards
- **Total Users** - Number of registered users and active users
- **Roles** - Total roles with permissions configured
- **FlowBoards** - Total FlowBoards and currently running flows
- **Connections** - Database connections configured

### Quick Actions
Four quick action buttons for common tasks:
- **Add New User** - Quickly create a new user account
- **Create Role** - Define a new role with permissions
- **System Settings** - Access configuration settings
- **View Logs** - Check recent activity logs

### System Health
Real-time system status including:
- System status (Healthy/Warning/Critical)
- Uptime percentage
- Disk usage
- Last backup timestamp

### Recent Activity
Timeline of recent system and user activities:
- User logins and logouts
- FlowBoard creation/updates
- Role permission changes
- System events and errors

---

## User Management

Access: **Admin Portal → User Management**

### Features:
1. **View All Users**
   - List of all registered users
   - Filter by status (Active/Inactive)
   - Search by name or email

2. **Add New User**
   - Username (required)
   - First Name & Last Name
   - Email address
   - Password (with strength validation)
   - Assign roles
   - Set active/inactive status

3. **Edit User**
   - Update user information
   - Change assigned roles
   - Reset password
   - Enable/disable account

4. **Delete User**
   - Remove user from system
   - Confirmation required
   - Audit trail maintained

### User Roles Assignment
- Users can have multiple roles
- Permissions are cumulative from all assigned roles
- Changes take effect immediately

---

## Role Management

Access: **Admin Portal → Role Management**

### Features:
1. **View All Roles**
   - List of all defined roles
   - Number of users per role
   - Permissions summary

2. **Create New Role**
   - Role name and description
   - Select privileges/permissions
   - Assign to users

3. **Edit Role**
   - Modify role name and description
   - Add/remove permissions
   - View assigned users

4. **Delete Role**
   - Remove role from system
   - Reassign users to other roles
   - Cannot delete if users are assigned

### Available Permissions
- **FlowBoard Management** - Create, edit, delete FlowBoards
- **Connection Management** - Manage database connections
- **User Management** - Manage user accounts
- **Role Management** - Manage roles and permissions
- **System Settings** - Access system configuration
- **View Logs** - Access activity logs
- **Execute Flows** - Run FlowBoards
- **Monitor Flows** - View execution status

---

## System Settings

Access: **Admin Portal → System Settings**

### General Settings
- **Application Name** - Display name for the application
- **Version** - Current application version (read-only)
- **Max Upload Size** - Maximum file upload size in MB
- **Session Timeout** - User session timeout in minutes

### Feature Toggles
- **Enable Audit Logging** - Track all user and system activities
- **Enable Email Notifications** - Send email alerts for events
- **Maintenance Mode** - Put system in maintenance mode

### How to Update Settings
1. Navigate to System Settings
2. Modify the desired settings
3. Click "Save Settings" button
4. Settings are applied immediately

---

## Activity Logs

Access: **Admin Portal → Activity Logs**

### Features:
1. **View All Logs**
   - Chronological list of all activities
   - Pagination for large datasets

2. **Filter Logs**
   - **By Type**: User Activity, System Events, Errors, Security
   - **By Search**: Search in action, details, or user fields
   - **By Date**: Filter by date range (coming soon)

3. **Log Details**
   - **Type** - Category of log entry
   - **User** - Who performed the action
   - **Action** - What action was performed
   - **Details** - Additional information
   - **Timestamp** - When it occurred
   - **Severity** - Info, Success, Warning, Error

### Log Types:
- **User Activity** - Logins, logouts, user actions
- **System Events** - Backups, scheduled tasks, system operations
- **Errors** - Application errors and exceptions
- **Security** - Permission changes, failed login attempts

---

## API Keys Management

Access: **Admin Portal → API Keys**

### Features:
1. **View All API Keys**
   - List of configured API keys
   - Provider information
   - Last used timestamp
   - Status (Active/Inactive)

2. **Add New API Key**
   - Key name (descriptive)
   - Provider selection (Google AI, Perplexity, OpenAI, AWS, Azure)
   - API key value (encrypted storage)
   - Automatic masking for security

3. **Manage API Keys**
   - **Copy to Clipboard** - Quickly copy key value
   - **Delete Key** - Remove API key
   - **View Usage** - See when key was last used

### Supported Providers:
- **Google AI** - For Gemini AI integration
- **Perplexity AI** - For Perplexity AI integration
- **OpenAI** - For GPT models
- **AWS** - Amazon Web Services
- **Azure** - Microsoft Azure services

### Security:
- API keys are encrypted in the database
- Keys are masked in the UI (only first/last 4 characters shown)
- Copy to clipboard for secure usage
- Audit trail for all key operations

---

## Navigation & Layout

### Sidebar Navigation
The Admin Portal features a collapsible sidebar with:
- **Dashboard** - Main overview page
- **User Management** - User administration
- **Role Management** - Role and permissions
- **System Settings** - Configuration
- **Activity Logs** - Audit trail
- **API Keys** - External service keys

### Top Navigation Bar
- **Admin Portal** title with icon
- **Back to Workbench** button - Return to main application
- **User Profile** dropdown - Profile, settings, logout

### Responsive Design
- Desktop: Full sidebar with descriptions
- Tablet: Collapsible sidebar
- Mobile: Hidden sidebar with toggle button

---

## Best Practices

### User Management
1. Always assign appropriate roles to users
2. Use strong password requirements
3. Regularly review inactive users
4. Enable audit logging for compliance

### Role Management
1. Follow principle of least privilege
2. Create specific roles for different user types
3. Regularly audit role permissions
4. Document role purposes

### System Settings
1. Test settings in development before production
2. Keep session timeout reasonable (15-30 minutes)
3. Enable audit logging for security
4. Schedule regular backups

### API Keys
1. Rotate API keys regularly
2. Use different keys for dev/staging/production
3. Monitor key usage for anomalies
4. Delete unused keys immediately

---

## Troubleshooting

### Cannot Access Admin Portal
- **Issue**: Redirected to login page
- **Solution**: Ensure your user has Administrator role

### Changes Not Saving
- **Issue**: Settings not persisting
- **Solution**: Check browser console for errors, verify permissions

### API Keys Not Working
- **Issue**: AI features not functioning
- **Solution**: Verify API key is correct, check provider status

### Logs Not Showing
- **Issue**: Activity logs are empty
- **Solution**: Ensure audit logging is enabled in System Settings

---

## Support & Contact

For additional help or to report issues:
- **Documentation**: Check the main Datamplify documentation
- **Support Email**: support@datamplify.com
- **Issue Tracker**: GitHub repository issues section

---

## Version History

### Version 1.0.0 (Current)
- Initial release of unified Admin Portal
- Dashboard with statistics and quick actions
- User and Role management integration
- System Settings configuration
- Activity Logs monitoring
- API Keys management

---

*Last Updated: October 7, 2025*
