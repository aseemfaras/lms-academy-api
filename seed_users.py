import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

def create_users():
    # 1. Create Admin
    admin_email = "admin@lms.com"
    admin_pass = "admin123"
    if not User.objects.filter(email=admin_email).exists():
        User.objects.create_superuser(
            username="admin",
            email=admin_email,
            password=admin_pass,
            role=User.Role.ADMIN
        )
        print(f"[SUCCESS] Admin Created: {admin_email} | {admin_pass}")
    else:
        print(f"[INFO] Admin already exists: {admin_email}")

    # 2. Create Student
    student_email = "student@lms.com"
    student_pass = "student123"
    if not User.objects.filter(email=student_email).exists():
        User.objects.create_user(
            username="student",
            email=student_email,
            password=student_pass,
            role=User.Role.STUDENT
        )
        print(f"[SUCCESS] Student Created: {student_email} | {student_pass}")
    else:
        print(f"[INFO] Student already exists: {student_email}")

if __name__ == "__main__":
    create_users()
