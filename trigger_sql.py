import os
import django
from django.conf import settings

# This script manually triggers a DB query to see if SQL logging works
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User

print("Fetching users...")
users = list(User.objects.all())
print(f"Found {len(users)} users.")
