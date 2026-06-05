import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

users = User.objects.all().order_by('-date_joined')
print(f"Total users: {users.count()}")
print("-" * 50)
for user in users:
    print(f"Email: {user.email}")
    print(f"Username: {user.username}")
    print(f"Role: {user.role}")
    print(f"Active: {user.is_active}")
    print(f"Last Login: {user.last_login}")
    print(f"Date Joined: {user.date_joined}")
    print("-" * 50)
