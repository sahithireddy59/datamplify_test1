# ✅ Optional File Path Template - COMPLETE!

## 🎉 **Flexible Path Configuration!**

The File Path Template is now **OPTIONAL** - users have 3 flexible options for specifying file paths!

---

## 📋 **Three Options for File Paths:**

### **Option 1: Specify Base Path in Connection**
- Enter a main/base directory in the connection
- Provide specific file paths in the Looper component
- **Use Case:** When you have a base directory and files in subdirectories

**Example:**
```
Connection Configuration:
  File Path Template: /data/files/

Looper Configuration:
  File Path: customers/2024-01-15/sales.csv
  
Final Path: /data/files/customers/2024-01-15/sales.csv
```

### **Option 2: Leave Empty, Specify Full Path in Looper**
- Leave File Path Template empty in connection
- Provide the complete file path in Looper component
- **Use Case:** When file paths vary significantly or are determined at runtime

**Example:**
```
Connection Configuration:
  File Path Template: (empty)

Looper Configuration:
  File Path: /var/data/2024/january/customers.csv
  
Final Path: /var/data/2024/january/customers.csv
```

### **Option 3: Dynamic Path with Global Parameters**
- Use global parameters in the connection
- Parameters resolved at runtime
- **Use Case:** When file paths follow a pattern with dynamic values

**Example:**
```
Connection Configuration:
  File Path Template: /data/${FILE_DATE}/${FILE_NAME}.csv

Global Parameters:
  FILE_DATE = 2024-01-15
  FILE_NAME = customers

Looper Configuration:
  (uses connection template)
  
Final Path: /data/2024-01-15/customers.csv
```

---

## 🎯 **Detailed Usage Scenarios:**

### **Scenario 1: Base Directory Approach**

**Setup:**
```
Connection Name: FTP Customer Files
Server Type: FTP Server
Server Host: ftp.company.com
File Path Template: /uploads/customers/
```

**Looper Usage:**
```
Iteration 1: 2024-01-15/morning_batch.csv
Iteration 2: 2024-01-15/evening_batch.csv
Iteration 3: 2024-01-16/morning_batch.csv
```

**Results:**
- `/uploads/customers/2024-01-15/morning_batch.csv`
- `/uploads/customers/2024-01-15/evening_batch.csv`
- `/uploads/customers/2024-01-16/morning_batch.csv`

**Benefits:**
- Base path defined once
- Easy to change base directory
- Looper focuses on relative paths

---

### **Scenario 2: Full Path in Looper**

**Setup:**
```
Connection Name: SFTP Data Files
Server Type: SFTP Server
Server Host: sftp.company.com
File Path Template: (empty)
```

**Looper Usage:**
```
Iteration 1: /home/data/sales/2024/Q1/january.csv
Iteration 2: /home/data/sales/2024/Q1/february.csv
Iteration 3: /home/reports/summary/2024/Q1.csv
```

**Results:**
- `/home/data/sales/2024/Q1/january.csv`
- `/home/data/sales/2024/Q1/february.csv`
- `/home/reports/summary/2024/Q1.csv`

**Benefits:**
- Maximum flexibility
- Different paths per iteration
- No path restrictions

---

### **Scenario 3: Dynamic Parameters**

**Setup:**
```
Connection Name: S3 Daily Files
Server Type: AWS S3
File Path Template: my-bucket/${ENVIRONMENT}/${YEAR}/${MONTH}/${FILE_NAME}.csv

Global Parameters:
  ENVIRONMENT = production
  YEAR = 2024
  MONTH = 01
  FILE_NAME = sales
```

**Looper Usage:**
```
Iteration 1: (FILE_NAME = sales)
Iteration 2: (FILE_NAME = customers)
Iteration 3: (FILE_NAME = products)
```

**Results:**
- `my-bucket/production/2024/01/sales.csv`
- `my-bucket/production/2024/01/customers.csv`
- `my-bucket/production/2024/01/products.csv`

**Benefits:**
- Pattern-based paths
- Parameter reusability
- Easy date/environment changes

---

## 🔄 **How Looper Handles Each Option:**

### **Looper Logic:**

```python
def resolve_file_path(connection, looper_path=None):
    """
    Resolve final file path based on connection and looper configuration
    """
    base_path = connection.dynamic_file_path or ''
    
    if not base_path:
        # Option 2: No base path, use full path from looper
        if looper_path:
            return looper_path
        else:
            raise ValueError("File path must be provided in Looper")
    
    # Check if base path has parameters
    if has_parameters(base_path):
        # Option 3: Resolve parameters
        resolved_base = resolve_parameters(base_path, global_params)
    else:
        # Option 1: Use base path as-is
        resolved_base = base_path
    
    # Combine base path with looper path if provided
    if looper_path:
        return os.path.join(resolved_base, looper_path)
    else:
        return resolved_base
```

---

## 🎨 **UI Updates:**

### **File Path Template Field:**

**Label:**
```
File Path Template (Optional)
```

**Hint:**
```
Use global parameters like ${FILE_NAME} or $BASE_PATH, 
or leave empty to specify in Looper
```

**Placeholder:**
```
e.g., /data/${FILE_DATE}/${FILE_NAME}.csv or leave empty
```

**Info Box:**
```
How to use:
- Option 1: Specify base path here (e.g., /data/files/)
- Option 2: Leave empty and provide full path in Looper
- Option 3: Use global parameters for dynamic paths
```

### **Validation:**

**Before (Required):**
```typescript
[disabled]="!displayName || (csvSourceType === 'dynamic' && !dynamicFilePath)"
```

**After (Optional):**
```typescript
[disabled]="!displayName || (csvSourceType === 'upload' && !selectedFile)"
```

**Result:** File path template is no longer required for dynamic connections!

---

## 📊 **Comparison Table:**

| Aspect | Option 1: Base Path | Option 2: Full in Looper | Option 3: Parameters |
|--------|---------------------|-------------------------|---------------------|
| **Connection Path** | `/data/files/` | (empty) | `/data/${DATE}/${FILE}.csv` |
| **Looper Path** | `subfolder/file.csv` | `/full/path/file.csv` | (uses connection) |
| **Final Path** | `/data/files/subfolder/file.csv` | `/full/path/file.csv` | `/data/2024-01-15/sales.csv` |
| **Flexibility** | Medium | High | Medium |
| **Reusability** | High | Low | High |
| **Complexity** | Low | Low | Medium |
| **Best For** | Consistent base dir | Varied paths | Pattern-based paths |

---

## 💡 **Best Practices:**

### **When to Use Option 1 (Base Path):**
- ✅ All files in same base directory
- ✅ Subdirectories follow a pattern
- ✅ Base path rarely changes
- ✅ Multiple files in similar structure

**Example:** `/data/customers/` with files in `2024/01/`, `2024/02/`, etc.

### **When to Use Option 2 (Full Path in Looper):**
- ✅ Files scattered across different directories
- ✅ Paths determined at runtime
- ✅ No common base directory
- ✅ Maximum flexibility needed

**Example:** Files in `/sales/`, `/reports/`, `/archives/` with no pattern

### **When to Use Option 3 (Parameters):**
- ✅ Paths follow a predictable pattern
- ✅ Date-based or environment-based paths
- ✅ Need to change parameters frequently
- ✅ Multiple connections with similar patterns

**Example:** `/data/${ENV}/${YEAR}/${MONTH}/${FILE}.csv`

---

## 🔧 **Looper Component Configuration:**

### **Looper UI Fields:**

**Connection Selection:**
```html
<select [(ngModel)]="selectedConnection">
  <option *ngFor="let conn of csvConnections" [value]="conn.id">
    {{ conn.connection_name }}
  </option>
</select>
```

**File Path Input (Conditional):**
```html
<!-- Show if connection has no base path or needs relative path -->
<div *ngIf="!connectionHasCompletePath">
  <label>File Path</label>
  <input [(ngModel)]="looperFilePath" 
         placeholder="Enter file path or pattern" />
  <small>
    <span *ngIf="connectionBasePath">
      Will be combined with base: {{ connectionBasePath }}
    </span>
    <span *ngIf="!connectionBasePath">
      Provide full file path
    </span>
  </small>
</div>
```

**Path Preview:**
```html
<div class="alert alert-info">
  <strong>Final Path:</strong> {{ getFinalPath() }}
</div>
```

---

## ✨ **Example Configurations:**

### **Example 1: Daily Sales Files**

**Connection:**
```
Name: Daily Sales FTP
Server: ftp.sales.com
Path Template: /sales/${YEAR}/${MONTH}/
```

**Looper:**
```
File Path: day_${DAY}.csv
Iterations: 01, 02, 03, ..., 31
```

**Results:**
- `/sales/2024/01/day_01.csv`
- `/sales/2024/01/day_02.csv`
- `/sales/2024/01/day_03.csv`

### **Example 2: Multi-Region Processing**

**Connection:**
```
Name: Regional Data SFTP
Server: sftp.company.com
Path Template: (empty)
```

**Looper:**
```
Iterations:
  - /data/us/customers.csv
  - /data/eu/customers.csv
  - /data/apac/customers.csv
```

**Results:**
- `/data/us/customers.csv`
- `/data/eu/customers.csv`
- `/data/apac/customers.csv`

### **Example 3: Cloud Storage with Base Path**

**Connection:**
```
Name: S3 Data Lake
Server: AWS S3
Path Template: my-bucket/raw-data/
```

**Looper:**
```
File Path: ${SOURCE_SYSTEM}/${FILE_DATE}/${FILE_TYPE}.csv
Iterations: Various source systems
```

**Results:**
- `my-bucket/raw-data/crm/2024-01-15/customers.csv`
- `my-bucket/raw-data/erp/2024-01-15/orders.csv`
- `my-bucket/raw-data/web/2024-01-15/events.csv`

---

## ✅ **Summary:**

**File Path Template is now OPTIONAL with 3 flexible options!**

✅ **Option 1**: Base path in connection + relative path in Looper
✅ **Option 2**: Empty in connection + full path in Looper
✅ **Option 3**: Dynamic parameters in connection

**Benefits:**
- ✅ Maximum flexibility
- ✅ Supports all use cases
- ✅ Easy to understand
- ✅ No forced patterns
- ✅ Looper-friendly

**Validation:**
- ✅ Connection name always required
- ✅ File path template optional
- ✅ Path can be provided in Looper
- ✅ No breaking changes

**UI Updates:**
- ✅ "(Optional)" label added
- ✅ Helpful hints and examples
- ✅ Three options explained
- ✅ Validation updated

**Status:** ✅ PRODUCTION READY!

---

**Your users now have complete flexibility in how they specify file paths!** 🎉🚀
