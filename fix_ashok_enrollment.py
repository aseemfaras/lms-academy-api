"""
Script to clean up orphaned enrollments and fix ashok@gmail.com's access
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from students.models import Enrollment
from trainers.models import Course
from users.models import User

# Get ashok
try:
    ashok = User.objects.get(email='ashok@gmail.com')
    print(f"Found user: {ashok.email} (ID: {ashok.id})")
except User.DoesNotExist:
    print("User ashok@gmail.com not found!")
    exit(1)

# Check current enrollments
print(f"\nCurrent enrollments for {ashok.email}:")
for enrollment in Enrollment.objects.filter(student=ashok):
    course = enrollment.course
    if course:
        print(f"  - Enrollment {enrollment.id}: Course {course.id} ({course.title})")
        # Try to verify if the course is accessible
        accessible = Course.objects.filter(id=course.id, enrollments__student=ashok).exists()
        print(f"    Accessible via CourseViewSet: {accessible}")
    else:
        print(f"  - Enrollment {enrollment.id}: Course is NULL (orphaned)")

# Get all available courses
print("\nAvailable courses:")
all_courses = Course.objects.all()
for course in all_courses:
    print(f"  - Course {course.id}: {course.title}")

# Delete enrollment for course 6 if it exists and problematic
problematic = Enrollment.objects.filter(student=ashok, course_id=6)
if problematic.exists():
    print(f"\nDeleting problematic enrollment for course 6...")
    count = problematic.delete()[0]
    print(f"Deleted {count} enrollment(s)")

# Enroll ashok in Python course (ID 7) if not already enrolled
python_course = Course.objects.filter(id=7).first()
if python_course:
    enrollment, created = Enrollment.objects.get_or_create(
        student=ashok,
        course=python_course,
        defaults={'status': 'ACTIVE'}
    )
    if created:
        print(f"\n✓ Enrolled {ashok.email} in '{python_course.title}' (ID: {python_course.id})")
    else:
        print(f"\n✓ {ashok.email} already enrolled in '{python_course.title}' (ID: {python_course.id})")
else:
    print("\n⚠ Python course (ID 7) not found!")

# Show final enrollments
print(f"\nFinal enrollments for {ashok.email}:")
for enrollment in Enrollment.objects.filter(student=ashok):
    course = enrollment.course
    if course:
        print(f"  - Course {course.id}: {course.title}")
