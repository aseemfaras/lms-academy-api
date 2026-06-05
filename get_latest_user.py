import os
import django
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

def get_latest_user():
    try:
        user = User.objects.order_by('-date_joined').first()
        if user:
            print(f"Latest user email: {user.email}")
        else:
            print("No users found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_latest_user()
