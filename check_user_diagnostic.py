
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

# Check status of hadasha@gmail.com
email = 'hadasha@gmail.com'
user = User.objects.filter(email=email).first()

if not user:
    print(f"USER NOT FOUND: {email}")
    exit(1)

print(f"User: {user.email} | Active: {user.is_active} | Role: {user.role} | ID: {user.id}")

# Check what username field looks like - this is critical for JWT auth
print(f"Username field: {user.username}")
print(f"Has usable password: {user.has_usable_password()}")

# Try checking password hash directly (Django check_password)
test_pw = 'admin@123'
match = user.check_password(test_pw)
print(f"Password 'admin@123' matches: {match}")

test_pw2 = 'password123'
match2 = user.check_password(test_pw2)
print(f"Password 'password123' matches: {match2}")

test_pw3 = 'admin123'
match3 = user.check_password(test_pw3)
print(f"Password 'admin123' matches: {match3}")

test_pw4 = '1234'
match4 = user.check_password(test_pw4)
print(f"Password '1234' matches: {match4}")
