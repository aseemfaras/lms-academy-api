import os
import django
import sys
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "apps"))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

print("--- Listing all users ---")
for user in User.objects.all():
    print(f"Email: {user.email}, Role: {user.role}, IsActive: {user.is_active}, Username: {user.username}")

print("\n--- Checking specific users ---")
emails = ['admin@lms.com', 'trainer@lms.com', 'student@lms.com']
for email in emails:
    user = User.objects.filter(email=email).first()
    if user:
        print(f"Found {email}: Role={user.role}, Active={user.is_active}, PwCheck={user.check_password('admin123' if 'admin' in email else 'trainer123' if 'trainer' in email else 'password123')}")
    else:
        print(f"NOT FOUND: {email}")
