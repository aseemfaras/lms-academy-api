
from django.db import connection
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def check_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Tables in public schema: {tables}")
        
        if 'courses' in tables:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='courses'")
            columns = [c[0] for c in cursor.fetchall()]
            print(f"Columns in 'courses': {columns}")
            
        if 'modules' in tables:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='modules'")
            columns = [c[0] for c in cursor.fetchall()]
            print(f"Columns in 'modules': {columns}")

if __name__ == "__main__":
    check_db()
