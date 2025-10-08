# 🚀 Admin Portal - Quick Start Guide

## Step 1: Access the Admin Portal

### Option A: Direct URL
Open your browser and navigate to:
```
http://localhost:4200/admin
```

### Option B: From Workbench (if integrated)
1. Login to Datamplify
2. Look for "Admin" link in the navigation menu
3. Click to access the Admin Portal

---

## Step 2: Explore the Dashboard

When you first access `/admin`, you'll see the **Admin Dashboard**:

### What You'll See:
1. **Top Navigation Bar**
   - Admin Portal title
   - "Back to Workbench" button (to return to main app)
   - User profile dropdown (logout option)

2. **Sidebar Menu** (left side)
   - 📊 Dashboard
   - 👥 User Management
   - 🛡️ Role Management
   - ⚙️ System Settings
   - 📝 Activity Logs
   - 🔑 API Keys

3. **Dashboard Content**
   - Statistics cards (Users, Roles, FlowBoards, Connections)
   - Quick action buttons
   - System health status
   - Recent activity timeline

---

## Step 3: Common Tasks

### Task 1: Add a New User
1. Click **"User Management"** in sidebar
2. Click **"Add User"** button
3. Fill in user details:
   - Username
   - First Name, Last Name
   - Email
   - Password
   - Assign roles
4. Click **"Save"**

### Task 2: Create a New Role
1. Click **"Role Management"** in sidebar
2. Click **"Add Role"** button
3. Enter role details:
   - Role name
   - Description
   - Select permissions/privileges
4. Click **"Save"**

### Task 3: Configure System Settings
1. Click **"System Settings"** in sidebar
2. Modify settings:
   - Application name
   - Max upload size
   - Session timeout
   - Enable/disable features
3. Click **"Save Settings"**

### Task 4: View Activity Logs
1. Click **"Activity Logs"** in sidebar
2. Use filters:
   - Select log type (All, User, System, Error, Security)
   - Search by keyword
3. View log details in the table

### Task 5: Manage API Keys
1. Click **"API Keys"** in sidebar
2. Click **"Add API Key"** button
3. Enter details:
   - Key name (e.g., "Production Google AI")
   - Provider (Google AI, Perplexity, etc.)
   - API key value
4. Click **"Add Key"**
5. Use **Copy** button to copy key to clipboard

---

## Step 4: Navigation Tips

### Sidebar Navigation
- Click any menu item to navigate
- Active page is highlighted in purple
- Hover over items to see descriptions

### Collapse Sidebar
- Click the **hamburger icon** (☰) in top left
- Sidebar collapses to icons only
- Click again to expand

### Quick Actions (from Dashboard)
- **Add New User** → Goes to User Management
- **Create Role** → Goes to Role Management
- **System Settings** → Goes to Settings
- **View Logs** → Goes to Activity Logs

---

## Step 5: Understanding the Interface

### Color Coding
- **Purple/Blue gradient** → Primary actions and active items
- **Green** → Success states and healthy status
- **Yellow/Orange** → Warnings
- **Red** → Errors or delete actions

### Icons Guide
- 📊 `fa-tachometer-alt` → Dashboard
- 👥 `fa-users` → Users
- 🛡️ `fa-user-shield` → Roles
- ⚙️ `fa-cog` → Settings
- 📝 `fa-history` → Logs
- 🔑 `fa-key` → API Keys

### Status Badges
- **Active** (Green) → Item is active
- **Inactive** (Gray) → Item is disabled
- **Info** (Blue) → Informational
- **Success** (Green) → Successful operation
- **Warning** (Yellow) → Warning state
- **Error** (Red) → Error state

---

## Step 6: Mobile/Tablet Usage

### On Mobile Devices:
1. Sidebar is hidden by default
2. Click hamburger icon (☰) to show sidebar
3. Click outside sidebar to hide it
4. All features work the same

### On Tablets:
1. Sidebar can be toggled
2. Cards stack vertically
3. Tables scroll horizontally if needed

---

## Common Scenarios

### Scenario 1: Onboard a New Team Member
1. Go to **User Management**
2. Click **"Add User"**
3. Enter their details
4. Assign appropriate role (e.g., "Data Analyst")
5. User receives credentials and can login

### Scenario 2: Setup Google AI Integration
1. Go to **API Keys**
2. Click **"Add API Key"**
3. Name: "Google AI Production"
4. Provider: "Google AI"
5. Paste your Google AI API key
6. Click **"Add Key"**
7. Key is now available for FlowBoard AI features

### Scenario 3: Monitor System Activity
1. Go to **Activity Logs**
2. Filter by type: "User Activity"
3. Search for specific user or action
4. Review timeline of events
5. Check for any errors or security issues

### Scenario 4: Configure Application Settings
1. Go to **System Settings**
2. Update session timeout (e.g., 30 minutes)
3. Enable audit logging
4. Enable email notifications
5. Click **"Save Settings"**
6. Settings apply immediately

---

## Troubleshooting

### Issue: Can't Access Admin Portal
**Problem**: Redirected to login page  
**Solution**: Ensure your user account has Administrator role

### Issue: Sidebar Not Showing
**Problem**: Sidebar is hidden  
**Solution**: Click hamburger icon (☰) in top left corner

### Issue: Changes Not Saving
**Problem**: Settings or data not persisting  
**Solution**: 
- Check browser console for errors (F12)
- Verify you have proper permissions
- Ensure backend API is running

### Issue: API Keys Not Working
**Problem**: AI features not functioning  
**Solution**:
- Verify API key is correct
- Check provider status
- Ensure key has proper permissions

---

## Keyboard Shortcuts (Future Enhancement)

Coming soon:
- `Ctrl + /` → Toggle sidebar
- `Ctrl + D` → Go to Dashboard
- `Ctrl + U` → Go to Users
- `Ctrl + R` → Go to Roles

---

## Security Best Practices

1. **User Management**
   - Use strong passwords
   - Assign minimum required permissions
   - Regularly review user access
   - Disable inactive accounts

2. **Role Management**
   - Follow principle of least privilege
   - Create specific roles for job functions
   - Audit role permissions regularly

3. **API Keys**
   - Rotate keys regularly
   - Use different keys for dev/prod
   - Delete unused keys immediately
   - Monitor key usage

4. **Activity Logs**
   - Review logs regularly
   - Look for suspicious activity
   - Set up alerts for critical events

---

## Getting Help

### Documentation
- **User Guide**: See `ADMIN_PORTAL_GUIDE.md` for detailed documentation
- **Technical Docs**: See `ADMIN_PORTAL_README.md` for developer info

### Support
- Check browser console (F12) for error messages
- Review activity logs for system issues
- Contact your system administrator

---

## What's Next?

After getting familiar with the Admin Portal:

1. **Customize** system settings for your organization
2. **Setup** user accounts and roles
3. **Configure** API keys for AI features
4. **Monitor** activity logs regularly
5. **Maintain** user permissions and access

---

**Quick Reference Card**

| Task | Location | Action |
|------|----------|--------|
| Add User | User Management | Click "Add User" |
| Create Role | Role Management | Click "Add Role" |
| View Stats | Dashboard | See statistics cards |
| Check Logs | Activity Logs | Filter and search |
| Add API Key | API Keys | Click "Add API Key" |
| Configure App | System Settings | Modify and save |

---

*Happy Administrating! 🎉*

**Version**: 1.0.0  
**Last Updated**: October 7, 2025
