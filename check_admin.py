
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()
email = 'admin@lms.com'
password = 'admin'

print(f"--- Verifying Admin User: {email} ---")
try:
    user = User.objects.get(email=email)
    print(f"User found: {user.username} | Role: {user.role}")
    print(f"Password 'admin' correct? {user.check_password(password)}")
    
    # Try authenticating
    auth_user = authenticate(email=email, password=password)
    print(f"Authenticate(email={email}): {auth_user}")
    
    auth_user_username = authenticate(username=email, password=password)
    print(f"Authenticate(username={email}): {auth_user_username}")

except User.DoesNotExist:
    print("User NOT found!")
    # Create the user if it doesn't exist to be sure
    User.objects.create_superuser(username='admin', email=email, password=password, role='ADMIN')
    print(f"Admin user {email} created with password 'admin'.")

except Exception as e:
    print(f"Error: {e}")

print("--- End of Verification ---")
