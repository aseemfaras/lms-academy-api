import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

tables = connection.introspection.table_names()
print("Available tables:")
for table in sorted(tables):
    print(f" - {table}")
