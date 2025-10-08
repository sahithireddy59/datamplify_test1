# 🔌 Datamplify Database Connections - Complete Guide

## 📋 Overview

Your Datamplify system currently supports **PostgreSQL and CSV**. This guide will help you add support for **all remaining databases and file types**.

---

## 🎯 Currently Implemented in Backend

Your `Connections/utils.py` already has connection logic for:

### **✅ Databases (14 types):**
1. **PostgreSQL** ✓ (Already in use)
2. **MySQL**
3. **Oracle**
4. **Microsoft SQL Server**
5. **SQLite**
6. **MongoDB**
7. **Cassandra**
8. **Snowflake**
9. **MariaDB**
10. **IBM DB2**
11. **Microsoft Access**
12. **Sybase**
13. **SAP HANA**
14. **SAP BW**

### **✅ File Types (8 types):**
1. **CSV** ✓ (Already in use)
2. **Excel** (XLS, XLSX)
3. **JSON**
4. **XML**
5. **Parquet**
6. **Avro**
7. **ORC**
8. **TXT**

---

## 🚀 Quick Setup - Add All Datasources

### **Step 1: Run the Script**

```bash
cd c:\Users\vsahithi\Desktop\datamplify\Datamplify_backend\Datamplify-DEV

python add_all_datasources.py
```

**Expected Output:**
```
======================================================================
Adding DataSources to Database
======================================================================
⊘ POSTGRESQL (DATABASE) - Already exists
✓ MYSQL (DATABASE) - Added
✓ ORACLE (DATABASE) - Added
✓ MICROSOFTSQLSERVER (DATABASE) - Added
✓ SQLITE (DATABASE) - Added
✓ MONGODB (DATABASE) - Added
✓ CASSANDRA (DATABASE) - Added
✓ SNOWFLAKE (DATABASE) - Added
✓ MARIADB (DATABASE) - Added
✓ IBMDB2 (DATABASE) - Added
✓ MICROSOFTACCESS (DATABASE) - Added
✓ SYBASE (DATABASE) - Added
✓ SAP HANA (DATABASE) - Added
✓ SAP BW (DATABASE) - Added
⊘ CSV (FILE) - Already exists
✓ EXCEL (FILE) - Added
✓ JSON (FILE) - Added
✓ XML (FILE) - Added
✓ PARQUET (FILE) - Added
✓ AVRO (FILE) - Added
✓ ORC (FILE) - Added
✓ TXT (FILE) - Added

======================================================================
Summary:
  ✓ Added: 20
  ⊘ Already existed: 2
  Total: 22
======================================================================

All DataSources in database:
----------------------------------------------------------------------

📊 DATABASES (14):
    1. CASSANDRA
    2. IBMDB2
    3. MARIADB
    4. MICROSOFTACCESS
    5. MICROSOFTSQLSERVER
    6. MONGODB
    7. MYSQL
    8. ORACLE
    9. POSTGRESQL
   10. SAP BW
   11. SAP HANA
   12. SNOWFLAKE
   13. SQLITE
   14. SYBASE

📁 FILES (8):
   15. AVRO
   16. CSV
   17. EXCEL
   18. JSON
   19. ORC
   20. PARQUET
   21. TXT
   22. XML

======================================================================
✅ Done! All datasources are ready to use.
======================================================================
```

---

## 📊 Database Connection Details

### **1. PostgreSQL** ✓ (Already Working)
```json
{
  "database_type": 1,
  "hostname": "localhost",
  "port": 5432,
  "username": "postgres",
  "password": "password",
  "database": "mydb",
  "schema": "public",
  "connection_name": "My PostgreSQL"
}
```

### **2. MySQL**
```json
{
  "database_type": 7,
  "hostname": "localhost",
  "port": 3306,
  "username": "root",
  "password": "password",
  "database": "mydb",
  "connection_name": "My MySQL"
}
```

### **3. Oracle**
```json
{
  "database_type": 8,
  "hostname": "localhost",
  "port": 1521,
  "username": "system",
  "password": "password",
  "service_name": "ORCL",
  "connection_name": "My Oracle"
}
```

### **4. Microsoft SQL Server**
```json
{
  "database_type": 5,
  "hostname": "localhost",
  "port": 1433,
  "username": "sa",
  "password": "password",
  "database": "mydb",
  "connection_name": "My SQL Server"
}
```

### **5. SQLite**
```json
{
  "database_type": 4,
  "path": "path/to/database.db",
  "connection_name": "My SQLite"
}
```

### **6. MongoDB**
```json
{
  "database_type": 6,
  "hostname": "localhost",
  "port": 27017,
  "username": "admin",
  "password": "password",
  "database": "mydb",
  "connection_name": "My MongoDB"
}
```

### **7. Snowflake**
```json
{
  "database_type": 12,
  "hostname": "account.snowflakecomputing.com",
  "port": 443,
  "username": "user",
  "password": "password",
  "database": "mydb",
  "connection_name": "My Snowflake"
}
```

### **8. MariaDB**
```json
{
  "database_type": 9,
  "hostname": "localhost",
  "port": 3306,
  "username": "root",
  "password": "password",
  "database": "mydb",
  "connection_name": "My MariaDB"
}
```

### **9. IBM DB2**
```json
{
  "database_type": 10,
  "hostname": "localhost",
  "port": 50000,
  "username": "db2admin",
  "password": "password",
  "database": "mydb",
  "connection_name": "My DB2"
}
```

### **10. Cassandra**
```json
{
  "database_type": 2,
  "hostname": "localhost",
  "port": 9042,
  "username": "cassandra",
  "password": "cassandra",
  "connection_name": "My Cassandra"
}
```

### **11. Microsoft Access**
```json
{
  "database_type": 11,
  "path": "C:\\path\\to\\database.accdb",
  "connection_name": "My Access DB"
}
```

### **12. Sybase**
```json
{
  "database_type": 13,
  "hostname": "localhost",
  "port": 5000,
  "username": "sa",
  "password": "password",
  "database": "mydb",
  "connection_name": "My Sybase"
}
```

### **13. SAP HANA**
```json
{
  "database_type": 14,
  "hostname": "localhost",
  "port": 30015,
  "username": "SYSTEM",
  "password": "password",
  "database": "mydb",
  "connection_name": "My SAP HANA"
}
```

---

## 📁 File Connection Details

### **1. CSV** ✓ (Already Working)
```json
{
  "file_type": 16,
  "file": "<uploaded file>",
  "connection_name": "My CSV File"
}
```

### **2. Excel (XLS, XLSX)**
```json
{
  "file_type": 17,
  "file": "<uploaded file>",
  "connection_name": "My Excel File"
}
```

### **3. JSON**
```json
{
  "file_type": 18,
  "file": "<uploaded file>",
  "connection_name": "My JSON File"
}
```

### **4. Parquet**
```json
{
  "file_type": 20,
  "file": "<uploaded file>",
  "connection_name": "My Parquet File"
}
```

---

## 🔧 Required Python Packages

Make sure these packages are installed:

```bash
# Core
pip install sqlalchemy psycopg2-binary

# MySQL/MariaDB
pip install mysql-connector-python

# Oracle
pip install cx_Oracle

# SQL Server
pip install pyodbc

# MongoDB
pip install pymongo

# Cassandra
pip install cassandra-driver

# Snowflake
pip install snowflake-sqlalchemy

# IBM DB2
pip install ibm_db_sa

# SAP HANA
pip install hdbcli

# File formats
pip install pandas openpyxl xlrd pyarrow fastavro
```

---

## 🎨 Frontend Integration

### **Update Angular Connection Component**

Add all database types to your dropdown:

```typescript
// In your connection component
databaseTypes = [
  { id: 1, name: 'PostgreSQL', icon: 'postgresql-icon' },
  { id: 7, name: 'MySQL', icon: 'mysql-icon' },
  { id: 8, name: 'Oracle', icon: 'oracle-icon' },
  { id: 5, name: 'Microsoft SQL Server', icon: 'sqlserver-icon' },
  { id: 4, name: 'SQLite', icon: 'sqlite-icon' },
  { id: 6, name: 'MongoDB', icon: 'mongodb-icon' },
  { id: 2, name: 'Cassandra', icon: 'cassandra-icon' },
  { id: 12, name: 'Snowflake', icon: 'snowflake-icon' },
  { id: 9, name: 'MariaDB', icon: 'mariadb-icon' },
  { id: 10, name: 'IBM DB2', icon: 'db2-icon' },
  { id: 11, name: 'Microsoft Access', icon: 'access-icon' },
  { id: 13, name: 'Sybase', icon: 'sybase-icon' },
  { id: 14, name: 'SAP HANA', icon: 'sap-icon' },
];

fileTypes = [
  { id: 16, name: 'CSV', icon: 'csv-icon' },
  { id: 17, name: 'Excel', icon: 'excel-icon' },
  { id: 18, name: 'JSON', icon: 'json-icon' },
  { id: 19, name: 'XML', icon: 'xml-icon' },
  { id: 20, name: 'Parquet', icon: 'parquet-icon' },
  { id: 21, name: 'Avro', icon: 'avro-icon' },
  { id: 22, name: 'ORC', icon: 'orc-icon' },
  { id: 23, name: 'TXT', icon: 'txt-icon' },
];
```

---

## ✅ Testing Connections

### **Test Database Connection:**

```bash
curl -X POST http://localhost:8000/v1/connections/server/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "database_type": 7,
    "hostname": "localhost",
    "port": 3306,
    "username": "root",
    "password": "password",
    "database": "testdb",
    "connection_name": "Test MySQL"
  }'
```

### **Test File Upload:**

```bash
curl -X POST http://localhost:8000/v1/connections/file/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.xlsx" \
  -F "file_type=17" \
  -F "connection_name=Test Excel"
```

---

## 📝 Summary

**After running the script, you'll have:**
- ✅ 14 Database types available
- ✅ 8 File types available
- ✅ All backend connection logic ready
- ✅ Ready for frontend integration

**Next Steps:**
1. Run `python add_all_datasources.py`
2. Update Angular frontend with all database/file types
3. Test connections
4. Deploy!

🎉 **Your Datamplify system will support 22 different data sources!**
