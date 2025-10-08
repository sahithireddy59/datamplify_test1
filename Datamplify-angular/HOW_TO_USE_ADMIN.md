# 📖 How to Use the Admin Portal - Visual Guide

## 🎯 Quick Access

### Step 1: Open Your Browser
Navigate to:
```
http://localhost:4200/admin
```

---

## 🖥️ Admin Portal Interface

```
┌─────────────────────────────────────────────────────────────────┐
│  ☰  Admin Portal              [Back to Workbench]  [👤 Admin ▼] │
├──────────┬──────────────────────────────────────────────────────┤
│          │                                                       │
│  SIDEBAR │              MAIN CONTENT AREA                       │
│          │                                                       │
│  📊 Dashboard                                                    │
│  👥 User Mgmt     ┌─────────────────────────────────────┐       │
│  🛡️ Role Mgmt     │  📊 Statistics Cards                │       │
│  ⚙️ Settings      │  [Users] [Roles] [Flows] [Conns]   │       │
│  📝 Logs          └─────────────────────────────────────┘       │
│  🔑 API Keys                                                     │
│                   ┌─────────────────────────────────────┐       │
│                   │  ⚡ Quick Actions                    │       │
│                   │  [Add User] [Create Role]           │       │
│                   │  [Settings] [View Logs]             │       │
│                   └─────────────────────────────────────┘       │
│                                                                  │
│                   ┌─────────────────────────────────────┐       │
│                   │  📝 Recent Activity                 │       │
│                   │  • User logged in                   │       │
│                   │  • FlowBoard created                │       │
│                   └─────────────────────────────────────┘       │
└──────────┴──────────────────────────────────────────────────────┘
```

---

## 📋 Step-by-Step Usage

### 1️⃣ DASHBOARD (Home Page)

**What you see:**
- 📊 **4 Statistics Cards** showing counts
- ⚡ **4 Quick Action Buttons** for common tasks
- ❤️ **System Health** panel
- 📝 **Recent Activity** timeline

**What you can do:**
- View system overview at a glance
- Click quick action buttons to jump to specific pages
- Monitor recent user and system activities

---

### 2️⃣ USER MANAGEMENT

**How to access:**
```
Click "User Management" in sidebar
OR
Click "Add New User" quick action button
```

**What you can do:**

#### Add a New User:
1. Click **"Add User"** button (top right)
2. Fill in the form:
   ```
   Username:    john_doe
   First Name:  John
   Last Name:   Doe
   Email:       john.doe@company.com
   Password:    ********
   Roles:       [✓] Data Analyst
   Status:      [✓] Active
   ```
3. Click **"Save"**

#### Edit Existing User:
1. Find user in the list
2. Click **"Edit"** icon
3. Modify details
4. Click **"Update"**

#### Delete User:
1. Find user in the list
2. Click **"Delete"** icon
3. Confirm deletion

---

### 3️⃣ ROLE MANAGEMENT

**How to access:**
```
Click "Role Management" in sidebar
OR
Click "Create Role" quick action button
```

**What you can do:**

#### Create a New Role:
1. Click **"Add Role"** button
2. Enter role details:
   ```
   Role Name:        Data Analyst
   Description:      Can view and analyze data
   
   Permissions:
   [✓] View FlowBoards
   [✓] Execute Flows
   [✓] View Connections
   [ ] Manage Users
   [ ] Manage Roles
   ```
3. Click **"Save"**

#### Assign Role to Users:
1. Edit the role
2. Select users from the list
3. Click **"Assign"**

---

### 4️⃣ SYSTEM SETTINGS

**How to access:**
```
Click "System Settings" in sidebar
OR
Click "System Settings" quick action button
```

**What you can do:**

#### Configure Application:
```
┌─────────────────────────────────────┐
│  General Settings                   │
├─────────────────────────────────────┤
│  Application Name:  Datamplify      │
│  Version:          1.0.0 (readonly) │
│  Max Upload Size:  100 MB           │
│  Session Timeout:  30 minutes       │
│                                     │
│  Feature Toggles:                   │
│  [✓] Enable Audit Logging           │
│  [✓] Enable Email Notifications     │
│  [ ] Maintenance Mode               │
│                                     │
│  [Save Settings]                    │
└─────────────────────────────────────┘
```

---

### 5️⃣ ACTIVITY LOGS

**How to access:**
```
Click "Activity Logs" in sidebar
OR
Click "View Logs" quick action button
```

**What you can do:**

#### View and Filter Logs:
```
┌─────────────────────────────────────────────────────┐
│  Filter: [All Logs ▼]  Search: [____________] 🔍   │
├─────────────────────────────────────────────────────┤
│  Type    User              Action         Time      │
├─────────────────────────────────────────────────────┤
│  👤 user  admin@email.com  User Login     5m ago    │
│  📊 user  john.doe         FlowBoard      15m ago   │
│  ⚠️ error system           DB Failed      30m ago   │
│  🛡️ sec   admin            Role Changed   1h ago    │
└─────────────────────────────────────────────────────┘
```

**Filter Options:**
- All Logs
- User Activity
- System Events
- Errors
- Security

---

### 6️⃣ API KEYS MANAGEMENT

**How to access:**
```
Click "API Keys" in sidebar
```

**What you can do:**

#### Add New API Key:
1. Click **"Add API Key"** button
2. Fill in the form:
   ```
   ┌─────────────────────────────────────┐
   │  Add New API Key                    │
   ├─────────────────────────────────────┤
   │  Key Name:  Production Google AI    │
   │  Provider:  [Google AI ▼]           │
   │  API Key:   ************************│
   │                                     │
   │  [Cancel]  [Add Key]                │
   └─────────────────────────────────────┘
   ```
3. Click **"Add Key"**

#### Manage Existing Keys:
```
┌─────────────────────────────────────────┐
│  🤖 Google AI          [Active]         │
│  Production Google AI                   │
│  AIza...tz4c           [📋 Copy]        │
│  Created: Oct 1, 2025                   │
│  Last used: 30 min ago                  │
│  [🗑️ Delete]                            │
└─────────────────────────────────────────┘
```

---

## 🎨 UI Elements Guide

### Buttons
- **Primary (Purple)** → Main actions (Save, Add, Create)
- **Secondary (Gray)** → Cancel, Back
- **Success (Green)** → Confirm, Approve
- **Danger (Red)** → Delete, Remove
- **Info (Blue)** → View, Details

### Status Badges
- 🟢 **Active** → Item is active/enabled
- ⚪ **Inactive** → Item is disabled
- 🔵 **Info** → Informational status
- 🟡 **Warning** → Warning state
- 🔴 **Error** → Error state

### Icons
- ☰ → Toggle sidebar
- 📊 → Dashboard/Statistics
- 👥 → Users
- 🛡️ → Roles/Security
- ⚙️ → Settings
- 📝 → Logs/History
- 🔑 → API Keys
- ➕ → Add/Create
- ✏️ → Edit
- 🗑️ → Delete
- 📋 → Copy

---

## 💡 Pro Tips

### Tip 1: Use Quick Actions
Instead of navigating through sidebar, use quick action buttons on dashboard for faster access.

### Tip 2: Collapse Sidebar
Click the hamburger icon (☰) to collapse sidebar and get more screen space.

### Tip 3: Search Logs
Use the search box in Activity Logs to quickly find specific events or users.

### Tip 4: Copy API Keys
Use the copy button (📋) to safely copy API keys to clipboard without exposing them.

### Tip 5: Filter by Type
In Activity Logs, filter by type (User/System/Error/Security) to focus on specific events.

---

## 🔄 Common Workflows

### Workflow 1: Onboard New User
```
1. Dashboard → Click "Add New User"
2. Fill user details
3. Assign role (e.g., "Data Analyst")
4. Save
5. User can now login
```

### Workflow 2: Setup AI Integration
```
1. Dashboard → Click "API Keys" (sidebar)
2. Click "Add API Key"
3. Enter Google AI key
4. Save
5. AI features now available in FlowBoards
```

### Workflow 3: Audit User Activity
```
1. Dashboard → Click "View Logs"
2. Filter by "User Activity"
3. Search for specific user
4. Review their actions
5. Check for any issues
```

### Workflow 4: Create Custom Role
```
1. Dashboard → Click "Create Role"
2. Enter role name and description
3. Select permissions
4. Save
5. Assign to users
```

---

## 📱 Mobile Usage

### On Phone/Tablet:
1. **Sidebar is hidden** by default
2. **Tap hamburger icon** (☰) to show menu
3. **Tap menu item** to navigate
4. **Tap outside** sidebar to hide it
5. **All features work** the same

---

## ❓ FAQ

**Q: How do I access the admin portal?**  
A: Navigate to `http://localhost:4200/admin`

**Q: Who can access the admin portal?**  
A: Only users with Administrator role

**Q: Can I customize the dashboard?**  
A: Currently shows default statistics. Customization coming soon.

**Q: How do I add Google AI for FlowBoards?**  
A: Go to API Keys → Add API Key → Select Google AI → Enter key

**Q: Where can I see user login history?**  
A: Activity Logs → Filter by "User Activity" → Search for user

**Q: How do I enable maintenance mode?**  
A: System Settings → Check "Maintenance Mode" → Save

---

## 🚀 Next Steps

1. ✅ Access admin portal at `/admin`
2. ✅ Explore the dashboard
3. ✅ Add your first user
4. ✅ Create a custom role
5. ✅ Configure API keys for AI
6. ✅ Monitor activity logs

---

**Need More Help?**
- 📖 Detailed Guide: `ADMIN_PORTAL_GUIDE.md`
- 🔧 Technical Docs: `ADMIN_PORTAL_README.md`
- 🚀 Quick Start: `ADMIN_QUICK_START.md`

---

*You're all set to manage Datamplify like a pro! 🎉*
