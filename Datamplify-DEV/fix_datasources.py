"""
Script to fix DataSources table and add missing MySQL
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Datamplify.settings')
django.setup()

from Connections.models import DataSources

print("=" * 70)
print("Fixing DataSources Table")
print("=" * 70)

# 1. Fix CSV duplicate (ID 2 has wrong type "FILES" should be "FILE")
print("\n1. Fixing CSV duplicate...")
csv_old = DataSources.objects.filter(id=2, name='CSV', type='FILES').first()
if csv_old:
    print(f"   Found old CSV (ID: 2, Type: FILES)")
    csv_old.type = 'FILE'
    csv_old.save()
    print(f"   ✓ Updated CSV (ID: 2) type from 'FILES' to 'FILE'")
else:
    print(f"   ⊘ No fix needed for CSV")

# 2. Remove duplicate CSV if exists
print("\n2. Checking for duplicate CSV...")
csv_entries = DataSources.objects.filter(name='CSV', type='FILE')
if csv_entries.count() > 1:
    print(f"   Found {csv_entries.count()} CSV entries")
    # Keep the first one, delete others
    for csv in csv_entries[1:]:
        print(f"   ✗ Deleting duplicate CSV (ID: {csv.id})")
        csv.delete()
else:
    print(f"   ✓ No duplicates found")

# 3. Add MySQL if missing
print("\n3. Adding MySQL...")
mysql = DataSources.objects.filter(name='MYSQL', type='DATABASE').first()
if not mysql:
    # Find next available ID
    max_id = DataSources.objects.all().order_by('-id').first()
    next_id = (max_id.id + 1) if max_id else 1
    
    mysql = DataSources.objects.create(
        name='MYSQL',
        type='DATABASE'
    )
    print(f"   ✓ Added MYSQL (ID: {mysql.id})")
else:
    print(f"   ⊘ MYSQL already exists (ID: {mysql.id})")

print("\n" + "=" * 70)
print("Final DataSources List:")
print("=" * 70)

databases = DataSources.objects.filter(type='DATABASE').order_by('name')
files = DataSources.objects.filter(type='FILE').order_by('name')

print(f"\n📊 DATABASES ({databases.count()}):")
for ds in databases:
    print(f"  {ds.id:3d}. {ds.name}")

print(f"\n📁 FILES ({files.count()}):")
for ds in files:
    print(f"  {ds.id:3d}. {ds.name}")

print("\n" + "=" * 70)
print(f"✅ Total: {DataSources.objects.count()} datasources")
print("=" * 70)
