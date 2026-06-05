import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

students = User.objects.filter(role=User.Role.STUDENT)
passwords_to_try = ['password123', 'admin123', 'admin@123', 'student123', '12345']

print(f"Checking {students.count()} students...")
print("-" * 50)

for user in students:
    print(f"Email: {user.email}")
    found_any = False
    for pwd in passwords_to_try:
        if user.check_password(pwd):
            print(f"  [CORRECT] Password: {pwd}")
            found_any = True
            break
    if not found_any:
        print("  [ERROR] No known password matches.")
    print("-" * 50)
