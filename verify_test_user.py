import os
import django
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

def verify_test_user():
    email = "yashwanth_test@gmail.com"
    try:
        user = User.objects.get(email=email)
        print(f"User found: {user.email}")
        print(f"Full Name: {user.full_name}")
        print(f"Course: {user.course_name}")
        print(f"Portal: {user.portal_link}")
        print(f"Role: {user.role}")
    except User.DoesNotExist:
        print(f"User {email} not found.")

if __name__ == "__main__":
    verify_test_user()
