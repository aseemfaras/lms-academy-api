import os
import django
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def check_table_schema(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        print(f"Schema for {table_name}:")
        for col in columns:
            print(f"  {col[0]}: {col[1]}")

def check_migrations():
    with connection.cursor() as cursor:
        cursor.execute("SELECT app, name, applied FROM django_migrations WHERE app = 'users' ORDER BY applied DESC;")
        migrations = cursor.fetchall()
        print("\nMigrations for 'users':")
        for m in migrations:
            print(f"  {m[0]}: {m[1]} (Applied at: {m[2]})")

if __name__ == "__main__":
    check_table_schema('users')
    check_migrations()
