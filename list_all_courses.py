import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from trainers.models import Course

courses = Course.objects.all()
print(f"Total courses: {courses.count()}")
print("-" * 50)
for course in courses:
    print(f"ID: {course.id}")
    print(f"Title: {course.title}")
    print(f"Category: {course.category}")
    print(f"Trainer: {course.trainer}")
    print(f"Created At: {course.created_at}")
    print("-" * 50)
