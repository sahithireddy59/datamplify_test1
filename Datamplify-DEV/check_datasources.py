import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Datamplify.settings')
django.setup()

from Connections.models import DataSources

print("Current DataSources in database:")
print("=" * 60)

datasources = DataSources.objects.all()
if datasources.exists():
    for ds in datasources:
        print(f"ID: {ds.id} | Name: {ds.name} | Type: {ds.type}")
else:
    print("No datasources found!")

print("\n" + "=" * 60)
print(f"Total: {datasources.count()} datasources")
