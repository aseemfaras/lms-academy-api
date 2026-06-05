import os
import django
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def compare_tables():
    with connection.cursor() as cursor:
        for table in ['users', 'login_users']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"Table {table} has {count} rows")
            
            if count > 0:
                cursor.execute(f"SELECT email, full_name, role FROM {table} LIMIT 5")
                rows = cursor.fetchall()
                print(f"Sample data from {table}:")
                for row in rows:
                    print(f"  {row}")

if __name__ == "__main__":
    compare_tables()
