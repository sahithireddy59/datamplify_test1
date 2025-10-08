"""
Script to add all supported database and file connections to DataSources table
Run: python add_all_datasources.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Datamplify.settings')
django.setup()

from Connections.models import DataSources

# Define all supported datasources
DATASOURCES = [
    # Databases
    {'name': 'POSTGRESQL', 'type': 'DATABASE'},
    {'name': 'MYSQL', 'type': 'DATABASE'},
    {'name': 'ORACLE', 'type': 'DATABASE'},
    {'name': 'MICROSOFTSQLSERVER', 'type': 'DATABASE'},
    {'name': 'SQLITE', 'type': 'DATABASE'},
    {'name': 'MONGODB', 'type': 'DATABASE'},
    {'name': 'CASSANDRA', 'type': 'DATABASE'},
    {'name': 'SNOWFLAKE', 'type': 'DATABASE'},
    {'name': 'MARIADB', 'type': 'DATABASE'},
    {'name': 'IBMDB2', 'type': 'DATABASE'},
    {'name': 'MICROSOFTACCESS', 'type': 'DATABASE'},
    {'name': 'SYBASE', 'type': 'DATABASE'},
    {'name': 'SAP HANA', 'type': 'DATABASE'},
    {'name': 'SAP BW', 'type': 'DATABASE'},
    
    # File Types
    {'name': 'CSV', 'type': 'FILE'},
    {'name': 'EXCEL', 'type': 'FILE'},
    {'name': 'JSON', 'type': 'FILE'},
    {'name': 'XML', 'type': 'FILE'},
    {'name': 'PARQUET', 'type': 'FILE'},
    {'name': 'AVRO', 'type': 'FILE'},
    {'name': 'ORC', 'type': 'FILE'},
    {'name': 'TXT', 'type': 'FILE'},
]

def add_datasources():
    print("=" * 70)
    print("Adding DataSources to Database")
    print("=" * 70)
    
    added_count = 0
    existing_count = 0
    
    for ds_data in DATASOURCES:
        # Check if datasource already exists (by name and type, not ID)
        existing = DataSources.objects.filter(name=ds_data['name'], type=ds_data['type']).first()
        
        if existing:
            print(f"⊘ {ds_data['name']} ({ds_data['type']}) - Already exists (ID: {existing.id})")
            existing_count += 1
        else:
            # Create new datasource (let Django auto-assign ID)
            try:
                new_ds = DataSources.objects.create(
                    name=ds_data['name'],
                    type=ds_data['type']
                )
                print(f"✓ {ds_data['name']} ({ds_data['type']}) - Added (ID: {new_ds.id})")
                added_count += 1
            except Exception as e:
                print(f"✗ {ds_data['name']} ({ds_data['type']}) - Error: {str(e)}")
                continue
    
    print("\n" + "=" * 70)
    print(f"Summary:")
    print(f"  ✓ Added: {added_count}")
    print(f"  ⊘ Already existed: {existing_count}")
    print(f"  Total: {added_count + existing_count}")
    print("=" * 70)
    
    # Show all datasources
    print("\nAll DataSources in database:")
    print("-" * 70)
    
    databases = DataSources.objects.filter(type='DATABASE').order_by('name')
    files = DataSources.objects.filter(type='FILE').order_by('name')
    
    print(f"\n📊 DATABASES ({databases.count()}):")
    for ds in databases:
        print(f"  {ds.id:3d}. {ds.name}")
    
    print(f"\n📁 FILES ({files.count()}):")
    for ds in files:
        print(f"  {ds.id:3d}. {ds.name}")
    
    print("\n" + "=" * 70)
    print("✅ Done! All datasources are ready to use.")
    print("=" * 70)

if __name__ == '__main__':
    add_datasources()
