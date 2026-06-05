
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

try:
    u = User.objects.get(email='ashokkommoji4@gmail.com')
    print(f"User Found: {u.email}, Active: {u.is_active}")
    u.set_password('password123')
    u.save()
    print("Password reset to: password123")
except User.DoesNotExist:
    print("User NOT FOUND")
except Exception as e:
    print(f"Error: {e}")
