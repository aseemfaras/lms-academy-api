
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from trainers.models import Course

def fix_images():
    # Fix the Python course image
    courses = Course.objects.filter(title__icontains='Python')
    for course in courses:
        print(f"Fixing course: {course.title}")
        # Clear the URL string so it doesn't break the ImageField property
        # and defaults to empty or can be re-uploaded.
        # Alternatively, we could point it to a local static placeholder if needed.
        course.image = None
        course.save()
        print("Image field cleared. You can now upload a fresh thumbnail from the dashboard.")

if __name__ == "__main__":
    fix_images()
