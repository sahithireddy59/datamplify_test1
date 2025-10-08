# 🎨 Database Icons - Download Guide

## 📁 Icon Locations

### **Relational Database Icons**
Path: `src/assets/images/Db_server_images/Relational Database/`

### **File Source Icons**
Path: `src/assets/images/Db_server_images/File Source/`

---

## 🔽 Where to Get Icons

### **Option 1: Free Icon Sources**

1. **Icons8** - https://icons8.com/
   - Search for database names
   - Download PNG format (64x64 or 128x128)
   - Free with attribution

2. **Flaticon** - https://www.flaticon.com/
   - Search for database logos
   - Download PNG format
   - Free with attribution

3. **Official Logos** - Company websites
   - PostgreSQL: https://www.postgresql.org/media/img/about/press/elephant.png
   - MySQL: https://www.mysql.com/common/logos/
   - Oracle: https://www.oracle.com/
   - MongoDB: https://www.mongodb.com/brand-resources
   - Snowflake: https://www.snowflake.com/
   - Microsoft: https://www.microsoft.com/

### **Option 2: Create Simple Icons**

Use a simple colored square with database name:

```html
<!-- Temporary placeholder until you get real icons -->
<div class="icon-placeholder" style="background: #336791;">
  <span>PG</span>
</div>
```

---

## 📋 Required Icons List

### **Databases (14 icons):**
- [ ] postgresql.png ✓ (Already have)
- [ ] mysql.png
- [ ] oracle.png
- [ ] sqlserver.png
- [ ] sqlite.png
- [ ] mongodb.png
- [ ] cassandra.png
- [ ] snowflake.png
- [ ] mariadb.png
- [ ] db2.png
- [ ] access.png
- [ ] sybase.png
- [ ] saphana.png
- [ ] sapbw.png

### **Files (8 icons):**
- [ ] csv.png ✓ (Already have)
- [ ] excel.png
- [ ] json.png
- [ ] xml.png
- [ ] parquet.png
- [ ] avro.png
- [ ] orc.png
- [ ] txt.png

---

## 🎨 Icon Specifications

**Recommended Size:** 128x128 pixels or 256x256 pixels
**Format:** PNG with transparent background
**Style:** Flat, modern, consistent across all icons

---

## 🚀 Quick Setup (Temporary)

If you want to test without icons first, you can use text placeholders:

```typescript
// In your component
getDatabaseIcon(dbName: string): string {
  // Return first 2-3 letters as placeholder
  return dbName.substring(0, 3).toUpperCase();
}
```

```html
<!-- In your template -->
<div class="icon-text-placeholder">
  {{ getDatabaseIcon(db.name) }}
</div>
```

```scss
// In your styles
.icon-text-placeholder {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: bold;
  font-size: 18px;
  border-radius: 8px;
}
```

This will display "POS" for PostgreSQL, "MYS" for MySQL, etc. until you get proper icons.

---

## ✅ Once You Have Icons

1. Place all icons in the correct folders
2. Ensure filenames match exactly (case-sensitive)
3. Test each database type selection
4. Icons should load and display properly

**Your UI will look professional with proper database icons!** 🎨
