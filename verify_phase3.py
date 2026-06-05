
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from trainers.models import Course, Module
from students.models import Enrollment
from trainers.views import CourseViewSet
from users.views import CustomTokenObtainPairView

User = get_user_model()
factory = APIRequestFactory()

# 1. Test Login with 'username' payload
print("Testing Login with 'username' payload...")
admin_email = 'admin@lms.com'
login_view = CustomTokenObtainPairView.as_view()
request = factory.post('/api/users/login/', {'username': admin_email, 'password': 'admin'}, format='json')
response = login_view(request)
print(f"Login Response: {response.status_code}")
if response.status_code == 200:
    print("Tokens received:", response.data.keys())
else:
    print("Login FAILED")

# 2. Test Course Detail with enrolled_students and modules
print("\nTesting Course Detail with enrolled_students...")
course = Course.objects.first()
if not course:
    print("No courses found. Creating one...")
    admin = User.objects.get(email=admin_email)
    course = Course.objects.create(title="Master Python", description="Adv Python", instructor=admin)
    Module.objects.create(course=course, title="Module 1", content="Intro", order=1)
    student = User.objects.filter(role=User.Role.STUDENT).first()
    if student:
        Enrollment.objects.create(student=student, course=course)

course_view = CourseViewSet.as_view({'get': 'retrieve'})
request = factory.get(f'/api/courses/{course.id}/')
force_authenticate(request, user=User.objects.get(email=admin_email))
response = course_view(request, pk=course.id)

print(f"Course Detail Response: {response.status_code}")
if response.status_code == 200:
    print("Data keys:", response.data.keys())
    print(f"Modules count: {len(response.data.get('modules', []))}")
    print(f"Enrolled Students count: {len(response.data.get('enrolled_students', []))}")
    if len(response.data.get('enrolled_students', [])) > 0:
        print("First student name:", response.data['enrolled_students'][0]['username'])
else:
    print("Course retrieval FAILED")

print("\nFinal Verification Complete!")
