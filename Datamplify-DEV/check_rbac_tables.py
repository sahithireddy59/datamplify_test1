import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Datamplify.settings')
django.setup()

from django.db import connection

# Check if RBAC tables exist
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('datamplify_permission', 'datamplify_role', 'datamplify_user_role')
    """)
    tables = cursor.fetchall()
    
    print("RBAC Tables in database:")
    if tables:
        for table in tables:
            print(f"  ✓ {table[0]}")
    else:
        print("  ✗ No RBAC tables found!")
        
    # List all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    all_tables = cursor.fetchall()
    print(f"\nAll tables in database ({len(all_tables)} total):")
    for table in all_tables:
        print(f"  - {table[0]}")
