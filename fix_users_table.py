import os
import django
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def fix_schema():
    with connection.cursor() as cursor:
        print("Adding portal_link to users table...")
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN portal_link VARCHAR(500);")
            print("Successfully added portal_link.")
        except Exception as e:
            print(f"Error adding portal_link: {e}")

if __name__ == "__main__":
    fix_schema()
