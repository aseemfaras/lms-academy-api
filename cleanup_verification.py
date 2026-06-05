import os
import django
import sys

# Set up Django environment
sys.path.append('c:/aideas/lms-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from trainers.models import Course

def cleanup_verification_course():
    print("--- Starting Cleanup ---")
    
    course_title = "Verification Course"
    try:
        courses = Course.objects.filter(title=course_title)
        count = courses.count()
        if count > 0:
            courses.delete()
            print(f"✅ SUCCESS: Deleted {count} instance(s) of '{course_title}'.")
        else:
            print(f"ℹ️ INFO: No course found with title '{course_title}'.")
    except Exception as e:
        print(f"❌ ERROR: Failed to delete course: {e}")

    print("--- Cleanup Complete ---")

if __name__ == "__main__":
    cleanup_verification_course()
