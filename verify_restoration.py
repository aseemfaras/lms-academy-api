import os
import django
from django.contrib.auth import authenticate

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User
from trainers.models import Course

def verify_restoration():
    print("Verifying Restoration...")
    print("-" * 50)
    
    # 1. Verify User
    email = 'anithakommoji78@gmail.com'
    password = 'password123'
    user = authenticate(username=email, password=password)
    
    if user:
        print(f"[SUCCESS] Login successful for: {email}")
    else:
        print(f"[FAILED] Login failed for: {email}")

    # 2. Verify Courses
    courses = Course.objects.all()
    print(f"\nTotal courses in DB: {courses.count()}")
    for c in courses:
        print(f" - {c.title} (Trainer: {c.trainer.email})")
    
    print("-" * 50)

if __name__ == "__main__":
    verify_restoration()
