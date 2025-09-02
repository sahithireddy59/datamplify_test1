import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Datamplify.settings')
django.setup()

# Test database connection
from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("Database connection successful!")
except Exception as e:
    print(f"Database connection failed: {e}")
