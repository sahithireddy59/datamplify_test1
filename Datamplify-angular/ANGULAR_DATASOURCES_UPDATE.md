# 🔌 Angular Frontend - Add All 22 Datasources

## 📋 Step-by-Step Update Guide

### **Step 1: Update TypeScript Component**

Add this to `easy-connection.component.ts`:

```typescript
// Add after existing properties (around line 27)
selectedDatabaseType: number = 1; // Default to PostgreSQL
selectedFileType: number = 15; // Default to CSV
serviceName: string = ''; // For Oracle
databasePath: string = ''; // For SQLite, Access

// Database and File type lists
databaseTypes = [
  { id: 1, name: 'PostgreSQL', icon: 'postgresql.png', port: 5432, requiresSchema: true },
  { id: 23, name: 'MySQL', icon: 'mysql.png', port: 3306, requiresSchema: false },
  { id: 3, name: 'Oracle', icon: 'oracle.png', port: 1521, requiresServiceName: true },
  { id: 4, name: 'Microsoft SQL Server', icon: 'sqlserver.png', port: 1433, requiresSchema: false },
  { id: 5, name: 'SQLite', icon: 'sqlite.png', requiresPath: true },
  { id: 6, name: 'MongoDB', icon: 'mongodb.png', port: 27017, requiresSchema: false },
  { id: 7, name: 'Cassandra', icon: 'cassandra.png', port: 9042, requiresSchema: false },
  { id: 8, name: 'Snowflake', icon: 'snowflake.png', port: 443, requiresSchema: false },
  { id: 9, name: 'MariaDB', icon: 'mariadb.png', port: 3306, requiresSchema: false },
  { id: 10, name: 'IBM DB2', icon: 'db2.png', port: 50000, requiresSchema: false },
  { id: 11, name: 'Microsoft Access', icon: 'access.png', requiresPath: true },
  { id: 12, name: 'Sybase', icon: 'sybase.png', port: 5000, requiresSchema: false },
  { id: 13, name: 'SAP HANA', icon: 'saphana.png', port: 30015, requiresSchema: false },
  { id: 14, name: 'SAP BW', icon: 'sapbw.png', port: 30015, requiresSchema: false }
];

fileTypes = [
  { id: 15, name: 'CSV', icon: 'csv.png', extensions: ['.csv'] },
  { id: 16, name: 'Excel', icon: 'excel.png', extensions: ['.xls', '.xlsx'] },
  { id: 17, name: 'JSON', icon: 'json.png', extensions: ['.json'] },
  { id: 18, name: 'XML', icon: 'xml.png', extensions: ['.xml'] },
  { id: 19, name: 'Parquet', icon: 'parquet.png', extensions: ['.parquet'] },
  { id: 20, name: 'Avro', icon: 'avro.png', extensions: ['.avro'] },
  { id: 21, name: 'ORC', icon: 'orc.png', extensions: ['.orc'] },
  { id: 22, name: 'TXT', icon: 'txt.png', extensions: ['.txt'] }
];

// Get selected database details
getSelectedDatabase() {
  return this.databaseTypes.find(db => db.id === this.selectedDatabaseType);
}

// Get selected file details
getSelectedFile() {
  return this.fileTypes.find(file => file.id === this.selectedFileType);
}

// Select database type
selectDatabaseType(dbType: any) {
  this.selectedDatabaseType = dbType.id;
  this.isFormEnabled = true;
  this.isEditPreview = false;
  
  // Set default port if available
  if (dbType.port) {
    this.portName = dbType.port.toString();
  }
  
  // Reset fields based on database type
  if (dbType.requiresPath) {
    this.serverName = '';
    this.portName = '';
    this.databaseName = '';
  }
}

// Select file type
selectFileType(fileType: any) {
  this.selectedFileType = fileType.id;
}

// Update getSchemaList method
getSchemaList() {
  let object = {
    database_type: this.selectedDatabaseType, // Changed from hardcoded 1
    hostname: this.serverName,
    port: this.portName,
    username: this.userName,
    password: this.password,
    database: this.databaseName,
    service_name: this.serviceName, // Add service name
    path: this.databasePath, // Add path
    schema: this.selectedSchema
  };
  
  this.workbenchService.getSchemaList(object).subscribe({
    next: (res: any) => {
      this.schemaList = res.data;
    },
    error: (err: any) => {
      console.log(err);
      this.toasterservice.error(err.error.message);
    }
  });
}

// Update DatabaseConnection method
DatabaseConnection() {
  let object = {
    database_type: this.selectedDatabaseType, // Changed from hardcoded 1
    hostname: this.serverName,
    port: this.portName,
    username: this.userName,
    password: this.password,
    database: this.databaseName,
    service_name: this.serviceName, // Add service name
    path: this.databasePath, // Add path
    schema: this.selectedSchema,
    connection_name: this.displayName
  };
  
  this.workbenchService.DatabaseConnection(object).subscribe({
    next: (res: any) => {
      this.toasterservice.success(res.message);
      this.resetForm();
      this.getConnectionList();
    },
    error: (err: any) => {
      this.toasterservice.error(err.error.message);
    }
  });
}

// Update updateDatabaseConnection method
updateDatabaseConnection(hierarchyId: any) {
  let object = {
    database_type: this.selectedDatabaseType, // Changed from hardcoded 1
    hostname: this.serverName,
    port: this.portName,
    username: this.userName,
    password: this.password,
    database: this.databaseName,
    service_name: this.serviceName, // Add service name
    path: this.databasePath, // Add path
    schema: this.selectedSchema,
    connection_name: this.displayName
  };
  
  this.workbenchService.updateDatabaseConnection(hierarchyId, object).subscribe({
    next: (res: any) => {
      this.toasterservice.success(res.message);
      this.resetForm();
      this.getConnectionList();
    },
    error: (err: any) => {
      this.toasterservice.error(err.error.message);
    }
  });
}

// Update FileUpload method
FileUpload() {
  if (this.selectedFile) {
    const formData = new FormData();
    formData.append('file', this.selectedFile);
    formData.append('file_type', this.selectedFileType.toString()); // Changed from hardcoded 2
    formData.append('connection_name', this.displayName);
    
    this.workbenchService.FileUpload(formData).subscribe({
      next: (res: any) => {
        this.toasterservice.success(res.message);
        this.modalService.dismissAll();
        this.resetForm();
        this.getConnectionList();
      },
      error: (err: any) => {
        this.toasterservice.error(err.error.message);
      }
    });
  }
}

// Reset form
resetForm() {
  this.serverName = '';
  this.portName = '';
  this.databaseName = '';
  this.userName = '';
  this.displayName = '';
  this.password = '';
  this.serviceName = '';
  this.databasePath = '';
  this.selectedSchema = 'public';
  this.selectedFile = null;
  this.isFormEnabled = false;
}
```

---

### **Step 2: Update HTML Template**

Replace the datasource selection section in `easy-connection.component.html`:

```html
<div *ngIf="!isFormEnabled && !showList" class="main-container container-fluid TopHeader">
  <div class="row p-4">
    <div class="col-sm-12 col-lg-12 col-xl-12 p-0">
      <div class="card-header mb-3 border-0 d-flex justify-content-between align-items-center">
        <h4 class="card-title mb-0">Connect to Datasource</h4>
        <button class="btn btn-primary rounded-2" type="button" (click)="viewConnections();">
          <i class="fa fa-eye me-2"></i> View Connections
        </button>
      </div>

      <!-- Relational Databases -->
      <div class="row">
        <div class="col-12">
          <div class="card card-body border Connect-Database-card">
            <h6 class="mb-3">Relational Databases</h6>
            <div class="image-card-container">
              <div class="database-logo" *ngFor="let db of databaseTypes">
                <div class="imgcard p-4" (click)="selectDatabaseType(db)">
                  <img [src]="'./assets/images/Db_server_images/Relational Database/' + db.icon" 
                       [alt]="db.name" class="card-img" />
                </div>
                <div class="logo-txt mt-2 text-center fw-600">
                  <span>{{ db.name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    
      <!-- File Sources -->
      <div class="row">
        <div class="col-12">
          <div class="card card-body border Connect-Database-card">
            <h6 class="mb-3">File Sources</h6>
            <div class="image-card-container">
              <div class="database-logo" *ngFor="let file of fileTypes">
                <div class="imgcard p-4" (click)="selectFileType(file); openUploadModal(uploadFileModal)">
                  <img [src]="'./assets/images/Db_server_images/File Source/' + file.icon" 
                       [alt]="file.name" class="card-img" />
                </div>
                <div class="logo-txt mt-2 text-center fw-600">
                  <span>{{ file.name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Database Connection Form -->
<div *ngIf="isFormEnabled" class="main-container container-fluid px-4 TopHeader">
  <div class="row">
    <div class="col-md-12 col-xl-6 p-1 mb-0">
      <div class="card Relational-database-height">
        <div class="card-header">
          <h4 class="card-title">Connect To {{ getSelectedDatabase()?.name }}</h4>
        </div>
        <div class="card-body">
          <form>
            <!-- Server (if not path-based) -->
            <div class="form-group" *ngIf="!getSelectedDatabase()?.requiresPath">
              <label [ngClass]="{'error-label': serverError}" class="col-form-label">
                Server<span class="text-danger ms-1">*</span>
              </label>
              <input [ngClass]="{'error-input': serverError}" type="text" class="form-control"
                [(ngModel)]="serverName" [ngModelOptions]="{standalone: true}" 
                placeholder="Host Name/Host Url" (input)="serverConditionError()">
            </div>

            <!-- Port (if not path-based) -->
            <div class="form-group" *ngIf="!getSelectedDatabase()?.requiresPath">
              <label [ngClass]="{'error-label': portError}" class="col-form-label">
                Port<span class="text-danger ms-1">*</span>
              </label>
              <input [ngClass]="{'error-input': portError}" type="text" class="form-control"
                [(ngModel)]="portName" [ngModelOptions]="{standalone: true}" 
                [placeholder]="'e.g. ' + (getSelectedDatabase()?.port || '5432')"
                (input)="portConditionError()">
            </div>

            <!-- Database Path (for SQLite, Access) -->
            <div class="form-group" *ngIf="getSelectedDatabase()?.requiresPath">
              <label class="col-form-label">
                Database Path<span class="text-danger ms-1">*</span>
              </label>
              <input type="text" class="form-control"
                [(ngModel)]="databasePath" [ngModelOptions]="{standalone: true}" 
                placeholder="e.g. C:\path\to\database.db">
            </div>

            <!-- Database Name (if not path-based) -->
            <div class="form-group" *ngIf="!getSelectedDatabase()?.requiresPath">
              <label [ngClass]="{'error-label': databaseError}" class="col-form-label">
                Database<span class="text-danger ms-1">*</span>
              </label>
              <input [ngClass]="{'error-input': databaseError}" type="text" class="form-control"
                [(ngModel)]="databaseName" [ngModelOptions]="{standalone: true}" 
                [placeholder]="'e.g. ' + getSelectedDatabase()?.name"
                (input)="databaseConditionError()">
            </div>

            <!-- Service Name (for Oracle) -->
            <div class="form-group" *ngIf="getSelectedDatabase()?.requiresServiceName">
              <label class="col-form-label">
                Service Name<span class="text-danger ms-1">*</span>
              </label>
              <input type="text" class="form-control"
                [(ngModel)]="serviceName" [ngModelOptions]="{standalone: true}" 
                placeholder="e.g. ORCL">
            </div>

            <!-- Username -->
            <div class="form-group" *ngIf="!getSelectedDatabase()?.requiresPath">
              <label [ngClass]="{'error-label': userNameError}" class="col-form-label">
                User Name<span class="text-danger ms-1">*</span>
              </label>
              <input [ngClass]="{'error-input': userNameError}" type="text" class="form-control"
                [(ngModel)]="userName" [ngModelOptions]="{standalone: true}" 
                autocomplete="new-myname" placeholder="Username" 
                (input)="userNameConditionError()">
            </div>

            <!-- Display Name -->
            <div class="mb-2">
              <label [ngClass]="{'error-label': displayNameError}" class="col-form-label">
                Display Name<span class="text-danger ms-1">*</span>
              </label>
              <input [ngClass]="{'error-input': displayNameError}" type="text" class="form-control"
                [(ngModel)]="displayName" [ngModelOptions]="{standalone: true}" 
                placeholder="Connection Name" (input)="displayNameConditionError()">
            </div>

            <!-- Password -->
            <div class="form-group" *ngIf="!getSelectedDatabase()?.requiresPath">
              <label [ngClass]="{'error-label': passwordError}" class="col-form-label">
                Password<span class="text-danger ms-1">*</span>
              </label>
              <div class="input-group">
                <input [ngClass]="{'error-input': passwordError}" 
                  [type]="showPassword ? 'text' : 'password'" 
                  class="form-control" [(ngModel)]="password" 
                  [ngModelOptions]="{standalone: true}" 
                  autocomplete="new-password" placeholder="Password" 
                  (input)="passwordConditionError()">
                <button class="btn btn-outline-secondary" type="button" 
                  (click)="showPassword = !showPassword">
                  <i [class]="showPassword ? 'fa fa-eye-slash' : 'fa fa-eye'"></i>
                </button>
              </div>
            </div>

            <!-- Schema (for PostgreSQL) -->
            <div class="form-group" *ngIf="getSelectedDatabase()?.requiresSchema">
              <label class="col-form-label">Schema</label>
              <select class="form-control" [(ngModel)]="selectedSchema" 
                [ngModelOptions]="{standalone: true}">
                <option value="public">public</option>
                <option *ngFor="let schema of schemaList" [value]="schema">
                  {{ schema }}
                </option>
              </select>
            </div>

            <!-- Buttons -->
            <div class="d-flex justify-content-end mt-3">
              <button type="button" class="btn btn-secondary me-2" 
                (click)="resetForm()">
                Cancel
              </button>
              <button type="button" class="btn btn-primary" 
                [disabled]="disableConnectBtn"
                (click)="isEditPreview ? updateDatabaseConnection(editPreviewData.id) : DatabaseConnection()">
                {{ isEditPreview ? 'Update' : 'Connect' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</div>
```

---

### **Step 3: Add Database Icons**

Place these icon files in: `src/assets/images/Db_server_images/Relational Database/`

**Required Icons:**
- postgresql.png ✓ (exists)
- mysql.png
- oracle.png
- sqlserver.png
- sqlite.png
- mongodb.png
- cassandra.png
- snowflake.png
- mariadb.png
- db2.png
- access.png
- sybase.png
- saphana.png
- sapbw.png

Place these icon files in: `src/assets/images/Db_server_images/File Source/`

**Required Icons:**
- csv.png ✓ (exists)
- excel.png
- json.png
- xml.png
- parquet.png
- avro.png
- orc.png
- txt.png

---

### **Step 4: Update CSS (Optional)**

Add to `easy-connection.component.scss`:

```scss
.image-card-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  
  .database-logo {
    flex: 0 0 calc(20% - 16px);
    min-width: 120px;
    
    .imgcard {
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s ease;
      background: white;
      
      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-color: #007bff;
      }
      
      img {
        width: 100%;
        height: 60px;
        object-fit: contain;
      }
    }
    
    .logo-txt {
      font-size: 14px;
      color: #333;
    }
  }
}
```

---

## ✅ Testing

### **Test Database Connection:**
1. Select PostgreSQL → Fill form → Click Connect
2. Select MySQL → Fill form → Click Connect
3. Select MongoDB → Fill form → Click Connect

### **Test File Upload:**
1. Select CSV → Upload file → Click Upload
2. Select Excel → Upload file → Click Upload
3. Select JSON → Upload file → Click Upload

---

## 🎉 Summary

After this update, your Angular frontend will support:
- ✅ 14 Database types
- ✅ 8 File types
- ✅ Dynamic form fields based on database type
- ✅ Proper validation
- ✅ Clean UI with icons

**Your Datamplify frontend is now ready for all 22 datasources!** 🚀
