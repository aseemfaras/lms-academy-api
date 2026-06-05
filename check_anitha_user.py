import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

email = 'anithakommoji78@gmail.com'
try:
    user = User.objects.get(email=email)
    print(f"User found: '{user.email}' (ID: {user.id})")
    print(f"Role: {user.role}, Active: {user.is_active}")
    
    passwords_to_try = ['password123', 'admin123', 'admin@123', '12345']
    for pwd in passwords_to_try:
        if user.check_password(pwd):
            print(f"  [CORRECT] Password '{pwd}' for {email}")
        else:
            print(f"  [INCORRECT] Password '{pwd}' for {email}")

except User.DoesNotExist:
    print(f"User '{email}' NOT found in database.")
except Exception as e:
    print(f"Error: {e}")
