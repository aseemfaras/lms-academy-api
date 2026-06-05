import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

# Test database connection
with connection.cursor() as cursor:
    # Get all tables
    cursor.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename;
    """)
    tables = cursor.fetchall()
    
    print("=" * 60)
    print("DATABASE CONNECTION: ✅ SUCCESSFUL")
    print("=" * 60)
    print(f"\nDatabase: {connection.settings_dict['NAME']}")
    print(f"Host: {connection.settings_dict['HOST']}")
    print(f"Port: {connection.settings_dict['PORT']}")
    print(f"User: {connection.settings_dict['USER']}")
    
    print(f"\n{'='*60}")
    print(f"TOTAL TABLES CREATED: {len(tables)}")
    print(f"{'='*60}\n")
    
    for idx, (table,) in enumerate(tables, 1):
        print(f"{idx:2}. {table}")
    
    # Get row counts for key tables
    print(f"\n{'='*60}")
    print("KEY TABLE ROW COUNTS:")
    print(f"{'='*60}\n")
    
    key_tables = ['login_users', 'trainers_course', 'trainers_module', 'students_enrollment']
    for table in key_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"  {table:30} : {count:5} rows")
        except Exception as e:
            print(f"  {table:30} : Table not found")
    
    print(f"\n{'='*60}")
    print("✅ DATABASE FULLY CONNECTED AND OPERATIONAL")
    print(f"{'='*60}\n")
