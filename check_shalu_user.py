import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

emails_to_check = ['shalu@gmail.com', 'Shalu@gmail.com']
passwords_to_try = ['admin123', 'admin@123', 'password123', '12345']

for email in emails_to_check:
    try:
        user = User.objects.get(email=email)
        print(f"User found: '{user.email}' (ID: {user.id})")
        print(f"Role: {user.role}, Active: {user.is_active}")
        for pwd in passwords_to_try:
            if user.check_password(pwd):
                print(f"  [CORRECT] Password '{pwd}' for {email}")
            else:
                pass # print(f"  [INCORRECT] Password '{pwd}' for {email}")
    except User.DoesNotExist:
        print(f"User '{email}' NOT found")
    print("-" * 30)

# Also check how many users have this email if we ignore case
all_shas = User.objects.filter(email__iexact='shalu@gmail.com')
print(f"Total users with email 'shalu@gmail.com' (case-insensitive): {all_shas.count()}")
for u in all_shas:
    print(f"  - {u.email} (ID: {u.id})")

