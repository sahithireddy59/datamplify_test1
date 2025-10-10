# 🚀 Complete Guide: Adding New Connections to Datamplify

## 📋 Current Status

Your system already supports **22 datasources** (14 databases + 8 files) with a comprehensive connection management system.

---

## 🎯 Adding New Connection Types

### **Step 1: Backend - Add New Datasource Type**

Add to `Connections/models.py`:

```python
class DataSourceType(models.Model):
    # ... existing fields ...
    
    TYPES = [
        # ... existing types ...
        (25, 'Snowflake'),  # New example
        (26, 'MongoDB Atlas'),  # New example
    ]
```

### **Step 2: Backend - Update Connection Handler**

Add to `Connections/views.py`:

```python
# Add new connection types
NEW_CONNECTION_TYPES = {
    25: {  # Snowflake
        'name': 'Snowflake',
        'handler': 'handle_snowflake_connection',
        'fields': ['account', 'warehouse', 'database', 'schema', 'role']
    },
    26: {  # MongoDB Atlas
        'name': 'MongoDB Atlas',
        'handler': 'handle_mongodb_atlas_connection',
        'fields': ['connection_string', 'database']
    }
}
```

### **Step 3: Backend - Implement Connection Handler**

Add to `Connections/connection_handler.py`:

```python
def handle_snowflake_connection(connection_data):
    """Handle Snowflake connection"""
    try:
        import snowflake.connector
        
        conn = snowflake.connector.connect(
            user=connection_data['username'],
            password=connection_data['password'],
            account=connection_data['account'],
            warehouse=connection_data['warehouse'],
            database=connection_data['database'],
            schema=connection_data['schema'],
            role=connection_data['role']
        )
        
        # Test connection
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'message': f'Snowflake connection successful. Version: {version}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Snowflake connection failed: {str(e)}'
        }

def handle_mongodb_atlas_connection(connection_data):
    """Handle MongoDB Atlas connection"""
    try:
        from pymongo import MongoClient
        
        client = MongoClient(connection_data['connection_string'])
        
        # Test connection
        db = client[connection_data['database']]
        db.list_collection_names()
        client.close()
        
        return {
            'success': True,
            'message': 'MongoDB Atlas connection successful'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'MongoDB Atlas connection failed: {str(e)}'
        }
```

### **Step 4: Frontend - Add New Datasource Types**

Update `easy-connection.component.ts`:

```typescript
databaseTypes = [
  // ... existing types ...
  { id: 25, name: 'Snowflake', icon: 'snowflake.png', port: 443, requiresSchema: true },
  { id: 26, name: 'MongoDB Atlas', icon: 'mongodb-atlas.png', port: 27017 }
];

fileTypes = [
  // ... existing types ...
  { id: 25, name: 'Parquet', icon: 'parquet.png' },
  { id: 26, name: 'Avro', icon: 'avro.png' }
];
```

### **Step 5: Frontend - Add Connection Forms**

Update `easy-connection.component.html`:

```html
<!-- Snowflake Form Fields -->
<div *ngIf="selectedDatabaseType === 25" class="snowflake-fields">
  <div class="form-row">
    <div class="form-group">
      <label>Account *</label>
      <input type="text" [(ngModel)]="snowflakeAccount" placeholder="your-account.snowflakecomputing.com" required>
    </div>
    <div class="form-group">
      <label>Warehouse *</label>
      <input type="text" [(ngModel)]="snowflakeWarehouse" placeholder="COMPUTE_WH" required>
    </div>
  </div>
  <div class="form-row">
    <div class="form-group">
      <label>Database *</label>
      <input type="text" [(ngModel)]="snowflakeDatabase" placeholder="MY_DATABASE" required>
    </div>
    <div class="form-group">
      <label>Schema *</label>
      <input type="text" [(ngModel)]="snowflakeSchema" placeholder="PUBLIC" required>
    </div>
  </div>
  <div class="form-row">
    <div class="form-group">
      <label>Role *</label>
      <input type="text" [(ngModel)]="snowflakeRole" placeholder="PUBLIC" required>
    </div>
  </div>
</div>

<!-- MongoDB Atlas Form Fields -->
<div *ngIf="selectedDatabaseType === 26" class="mongodb-atlas-fields">
  <div class="form-group">
    <label>Connection String *</label>
    <input type="text" [(ngModel)]="mongodbConnectionString" 
           placeholder="mongodb+srv://username:password@cluster.mongodb.net/" required>
  </div>
  <div class="form-group">
    <label>Database *</label>
    <input type="text" [(ngModel)]="mongodbDatabase" placeholder="my-database" required>
  </div>
</div>
```

### **Step 6: Frontend - Add Form Validation**

Update `easy-connection.component.ts`:

```typescript
// Add new form fields
snowflakeAccount: string = '';
snowflakeWarehouse: string = '';
snowflakeDatabase: string = '';
snowflakeSchema: string = '';
snowflakeRole: string = '';

mongodbConnectionString: string = '';
mongodbDatabase: string = '';

// Add validation for new types
validateSnowflakeFields() {
  return this.snowflakeAccount && this.snowflakeWarehouse && 
         this.snowflakeDatabase && this.snowflakeSchema && this.snowflakeRole;
}

validateMongoDBAtlasFields() {
  return this.mongodbConnectionString && this.mongodbDatabase;
}
```

### **Step 7: Frontend - Update Connection Logic**

Update connection method:

```typescript
DatabaseConnection() {
  // ... existing validation ...
  
  // Add new connection types
  if (this.selectedDatabaseType === 25) { // Snowflake
    object = {
      ...object,
      account: this.snowflakeAccount,
      warehouse: this.snowflakeWarehouse,
      database: this.snowflakeDatabase,
      schema: this.snowflakeSchema,
      role: this.snowflakeRole
    };
  } else if (this.selectedDatabaseType === 26) { // MongoDB Atlas
    object = {
      ...object,
      connection_string: this.mongodbConnectionString,
      database: this.mongodbDatabase
    };
  }
  
  // ... rest of method ...
}
```

---

## 🎨 UI Updates for New Connections

### **Add Icons and Styling**

1. **Add new icons** to `assets/icons/`:
   - `snowflake.png`
   - `mongodb-atlas.png`

2. **Add CSS styles** for new connection forms:

```scss
.snowflake-fields {
  .form-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    
    .form-group {
      flex: 1;
    }
  }
}

.mongodb-atlas-fields {
  .form-group {
    margin-bottom: 1rem;
  }
}
```

---

## 📊 Complete Example: Adding Snowflake Connection

### **Backend Files to Update:**

1. **`Connections/models.py`** - Add datasource type
2. **`Connections/views.py`** - Add connection handler
3. **`Connections/connection_handler.py`** - Implement handler logic

### **Frontend Files to Update:**

1. **`easy-connection.component.ts`** - Add new types and validation
2. **`easy-connection.component.html`** - Add form fields
3. **`easy-connection.component.scss`** - Add styling

### **Testing:**

1. **Test Connection**: Try creating a Snowflake connection
2. **Test Data Preview**: Ensure data can be retrieved
3. **Test FlowBoard Integration**: Use in FlowBoards
4. **Test Transformations**: Apply transformations to Snowflake data

---

## 🚀 Benefits of This Approach

✅ **Extensible**: Easy to add any new datasource
✅ **Consistent**: Same pattern for all connection types  
✅ **User-Friendly**: Intuitive UI for all connection types
✅ **Robust**: Proper validation and error handling
✅ **Scalable**: Can support hundreds of datasources

---

## 📋 Summary

**Your system already has:**
- ✅ 22 datasource types
- ✅ Complete connection management
- ✅ UI for all connection types
- ✅ Backend handlers for all types

**To add new connections:**
1. Add datasource type to backend models
2. Implement connection handler
3. Add frontend form fields and validation
4. Update styling and icons

**You now have a complete, enterprise-ready connection management system!** 🎉

Would you like me to implement a specific new connection type as an example?
