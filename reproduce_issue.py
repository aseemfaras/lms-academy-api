
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from apps.users.serializers import CustomTokenObtainPairSerializer

User = get_user_model()
email = 'admin@lms.com'
password = 'admin'

print(f"Checking user: {email}")

try:
    user = User.objects.get(email=email)
    print(f"User found: {user}")
    print(f"Password correct? {user.check_password(password)}")
    print(f"Is active? {user.is_active}")
except User.DoesNotExist:
    print("User not found!")
    exit()

# Test Authentication directly
user_auth = authenticate(email=email, password=password) # Trying with email kwarg
print(f"Authenticate(email=...): {user_auth}")

user_auth_username = authenticate(username=email, password=password) # Trying with username kwarg
print(f"Authenticate(username=...): {user_auth_username}")

# Test Serializer
print("\nTesting Serializer with 'email' field:")
data_email = {'email': email, 'password': password}
serializer = CustomTokenObtainPairSerializer(data=data_email)
try:
    if serializer.is_valid():
        print("Serializer valid!")
    else:
        print(f"Serializer invalid: {serializer.errors}")
except Exception as e:
    print(f"Serializer error: {e}")

print("\nTesting Serializer with 'username' field (value is email):")
data_username = {'username': email, 'password': password}
serializer = CustomTokenObtainPairSerializer(data=data_username)
try:
    if serializer.is_valid():
        print("Serializer valid!")
    else:
        print(f"Serializer invalid: {serializer.errors}")
except Exception as e:
    print(f"Serializer error: {e}")
