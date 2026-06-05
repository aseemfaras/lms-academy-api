import os
import django
import sys
from django.utils import timezone

# Set up Django environment
sys.path.append('c:/aideas/lms-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from trainers.models import Course, Module, LiveSession
from students.models import Enrollment
from django.contrib.auth import get_user_model

User = get_user_model()

def verify_content_isolation():
    print("--- Starting Verification: Course Content Isolation ---")
    
    # Setup test data
    python_course, _ = Course.objects.get_or_create(title="Python")
    java_course, _ = Course.objects.get_or_create(title="Java")
    
    student_ashok, _ = User.objects.get_or_create(email="ashok@test.com", defaults={"username": "ashok", "role": "STUDENT"})
    
    # Enroll Ashok only in Python
    Enrollment.objects.get_or_create(student=student_ashok, course=python_course)
    
    # Create modules for both
    Module.objects.get_or_create(course=python_course, title="Intro to Python", video_url="http://youtube.com/python", order=1)
    Module.objects.get_or_create(course=java_course, title="Intro to Java", video_url="http://youtube.com/java", order=1)
    
    # Mock Request
    class MockRequest:
        def __init__(self, user, params):
            self.user = user
            self.query_params = params

    from trainers.views import ModuleViewSet
    
    # Test case: Student Ashok viewing Python modules
    print(f"\nTesting Ashok (Enrolled in Python) viewing Python modules...")
    viewset = ModuleViewSet()
    viewset.request = MockRequest(student_ashok, {"course": str(python_course.id)})
    qs = viewset.get_queryset()
    print(f"Found {qs.count()} modules.")
    for m in qs:
        print(f" - {m.title} (Course: {m.course.title})")
        if m.course != python_course:
            print("❌ FAILURE: Found module from different course!")
    
    # Test case: Student Ashok viewing Java modules (should be empty or filtered)
    print(f"\nTesting Ashok (NOT Enrolled in Java) viewing Java modules...")
    viewset.request = MockRequest(student_ashok, {"course": str(java_course.id)})
    qs = viewset.get_queryset()
    print(f"Found {qs.count()} modules.")
    if qs.count() == 0:
        print("✅ SUCCESS: Properly isolated Java content from Ashok.")
    else:
        for m in qs:
            print(f" - {m.title} (Course: {m.course.title})")
        print("❌ FAILURE: Ashok saw Java modules even though not enrolled or incorrectly filtered!")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    verify_content_isolation()
