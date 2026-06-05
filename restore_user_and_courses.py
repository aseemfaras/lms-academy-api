import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User
from trainers.models import Course, Module
from django.db import transaction

def restore_data():
    print("Starting data restoration...")
    
    with transaction.atomic():
        # 1. Create or update Anitha's account
        anitha_email = 'anithakommoji78@gmail.com'
        anitha, created = User.objects.get_or_create(
            email=anitha_email,
            defaults={
                'username': anitha_email,
                'role': User.Role.STUDENT,
                'full_name': 'Anitha Kommoji',
                'is_active': True
            }
        )
        anitha.set_password('password123')
        anitha.save()
        print(f"{'Created' if created else 'Updated'} user: {anitha_email}")

        # 2. Get Trainer (Admin)
        trainer = User.objects.filter(role=User.Role.ADMIN).first()
        if not trainer:
            print("No admin user found to assign as trainer.")
            return

        # 3. Restore AI Course
        ai_course, created = Course.objects.get_or_create(
            title="AI",
            defaults={
                'description': 'Comprehensive Artificial Intelligence Course',
                'trainer': trainer,
                'image': 'courses/react-card.png' # Using the image I found
            }
        )
        if created:
            print("Restored Course: AI")
            Module.objects.create(course=ai_course, title="Introduction to AI", order=1)
            Module.objects.create(course=ai_course, title="Neural Networks Basics", order=2)

        # 4. Restore React Course
        react_course, created = Course.objects.get_or_create(
            title="React JS",
            defaults={
                'description': 'Modern Frontend Development with React',
                'trainer': trainer,
                'image': 'courses/react-card.png'
            }
        )
        if created:
            print("Created Course: React JS")
            Module.objects.create(course=react_course, title="React Fundamentals", order=1)
            Module.objects.create(course=react_course, title="Hooks and Context API", order=2)

    print("Data restoration complete.")

if __name__ == "__main__":
    restore_data()
