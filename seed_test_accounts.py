import os
import django
import sys
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "apps"))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

def create_users():
    # 1. Create Admin
    admin_email = "admin@lms.com"
    admin_pass = "admin123"
    if not User.objects.filter(email=admin_email).exists():
        User.objects.create_superuser(
            username=admin_email,
            email=admin_email,
            password=admin_pass,
            role=User.Role.ADMIN
        )
        print(f"[SUCCESS] Admin Created: {admin_email} | {admin_pass}")
    else:
        user = User.objects.get(email=admin_email)
        user.set_password(admin_pass)
        user.role = User.Role.ADMIN
        user.is_active = True
        user.save()
        print(f"[INFO] Admin updated: {admin_email}")

    # 2. Create Trainer
    trainer_email = "trainer@lms.com"
    trainer_pass = "trainer123"
    if not User.objects.filter(email=trainer_email).exists():
        User.objects.create_user(
            username=trainer_email,
            email=trainer_email,
            password=trainer_pass,
            role=User.Role.TRAINER
        )
        print(f"[SUCCESS] Trainer Created: {trainer_email} | {trainer_pass}")
    else:
        user = User.objects.get(email=trainer_email)
        user.set_password(trainer_pass)
        user.role = User.Role.TRAINER
        user.is_active = True
        user.save()
        print(f"[INFO] Trainer updated: {trainer_email}")

    # 3. Create Student
    student_email = "student@lms.com"
    student_pass = "password123"
    if not User.objects.filter(email=student_email).exists():
        User.objects.create_user(
            username=student_email,
            email=student_email,
            password=student_pass,
            role=User.Role.STUDENT
        )
        print(f"[SUCCESS] Student Created: {student_email} | {student_pass}")
    else:
        user = User.objects.get(email=student_email)
        user.set_password(student_pass)
        user.role = User.Role.STUDENT
        user.is_active = True
        user.save()
        print(f"[INFO] Student updated: {student_email}")

if __name__ == "__main__":
    create_users()
