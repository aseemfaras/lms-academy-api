import os
import django
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def cleanup_database():
    with connection.cursor() as cursor:
        print("Dropping redundant login_users tables...")
        try:
            # Order matters for foreign keys if any
            cursor.execute("DROP TABLE IF EXISTS login_users_groups CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS login_users_user_permissions CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS login_users CASCADE;")
            print("Successfully cleaned up login_users tables.")
        except Exception as e:
            print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    cleanup_database()
