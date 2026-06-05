
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from trainers.models import Course, Module
from students.models import Enrollment

User = get_user_model()

# 1. Ensure Instructor and Student exist
instructor = User.objects.filter(role=User.Role.ADMIN).first()
if not instructor:
    instructor = User.objects.create_superuser(username='admin_test', email='admin_test@lms.com', password='admin', role=User.Role.ADMIN)

student = User.objects.filter(role=User.Role.STUDENT).first()
if not student:
    student = User.objects.create_user(username='student_test', email='student_test@lms.com', password='admin', role=User.Role.STUDENT)

print(f"Using Instructor: {instructor.email}")
print(f"Using Student: {student.email}")

# 2. Create a Course
course, created = Course.objects.get_or_create(
    title="Python for Beginners",
    defaults={'description': "Learn Python from scratch.", 'instructor': instructor}
)
if created:
    print(f"Course Created: {course.title}")
else:
    print(f"Course already exists: {course.title}")

# 3. Create a Module
module, created = Module.objects.get_or_create(
    course=course,
    title="Introduction to Basics",
    defaults={'content': "Printing Hello World!", 'order': 1}
)
if created:
    print(f"Module Created: {module.title}")
else:
    print(f"Module already exists: {module.title}")

# 4. Enroll Student
enrollment, created = Enrollment.objects.get_or_create(
    student=student,
    course=course
)
if created:
    print(f"Student enrolled in {course.title}")
else:
    print(f"Student already enrolled in {course.title}")

# 5. Verify via Query
print("\nVerifying Data:")
all_courses = Course.objects.all()
for c in all_courses:
    print(f"Course: {c.title} | Modules: {c.modules.count()} | Enrollments: {c.enrollments.count()}")

print("\nVerification Successful!")
