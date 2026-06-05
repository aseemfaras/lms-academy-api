
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

# Reset password for hadasha@gmail.com trainer
email = 'hadasha@gmail.com'
new_password = 'trainer123'

user = User.objects.filter(email=email).first()
if user:
    user.set_password(new_password)
    user.save()
    print(f"SUCCESS: Password reset for {user.email} (Role: {user.role}) to '{new_password}'")
else:
    print(f"ERROR: User {email} not found")

# Also check and list all trainer accounts
print("\n--- All Trainer Accounts ---")
trainers = User.objects.filter(role='TRAINER')
for t in trainers:
    print(f"  {t.email} | Active: {t.is_active} | Name: {t.full_name}")
