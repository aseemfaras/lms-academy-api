import os
import django
from django.db import connection

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

try:
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS login_users CASCADE;")
        print("Successfully dropped 'login_users' table.")
except Exception as e:
    print(f"Error dropping table: {e}")
