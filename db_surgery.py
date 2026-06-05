
from django.db import connection
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def perform_surgery():
    with connection.cursor() as cursor:
        # Check if image column exists
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='courses' AND column_name='image'")
        if not cursor.fetchone():
            print("Adding 'image' column to 'courses' table...")
            cursor.execute("ALTER TABLE courses ADD COLUMN image varchar(500)")
        else:
            print("'image' column already exists.")

        # Cleanup redundant tables
        tables_to_drop = ['trainers_course', 'trainers_module']
        for table in tables_to_drop:
            cursor.execute(f"SELECT 1 FROM information_schema.tables WHERE table_name='{table}'")
            if cursor.fetchone():
                print(f"Dropping redundant table '{table}'...")
                cursor.execute(f"DROP TABLE {table} CASCADE")

if __name__ == "__main__":
    try:
        perform_surgery()
        print("Surgery completed successfully.")
    except Exception as e:
        print(f"Surgery failed: {e}")
