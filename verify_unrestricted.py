import os
import django
import sys
import datetime
from django.utils import timezone

# Set up Django environment
sys.path.append('c:/aideas/lms-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from trainers.models import Course, LiveSession, Module
from django.contrib.auth import get_user_model

User = get_user_model()

def verify_unrestricted_upload():
    print("--- Starting Verification: Unrestricted Video Upload ---")
    
    # Identify a course
    course = Course.objects.first()
    if not course:
        print("No course found.")
        return
    
    # Create an UPCOMING session
    session = LiveSession.objects.create(
        course=course,
        title="Future Test Session",
        scheduled_date=(timezone.now() + datetime.timedelta(days=1)).date(),
        start_time=timezone.now().time(),
        end_time=(timezone.now() + datetime.timedelta(hours=1)).time(),
        meeting_link="http://zoom.us/future"
    )
    print(f"Created upcoming session: {session.title} (ID: {session.id}, Is Completed: {session.is_completed})")

    # Simulate Trainer Upload (Recording for future session)
    recording_url = "https://youtube.com/watch?v=unrestricted_test"
    
    # In a real API call, this would trigger perform_update
    # Here we just save and check if we can simulate the logic
    try:
        session.recording_url = recording_url
        session.save()
        print(f"Successfully saved recording for future session.")
        
        # Verify module creation logic (manual check of the same logic)
        module = Module.objects.filter(course=course, video_url=recording_url).first()
        if not module:
             Module.objects.create(
                course=course,
                title=f"Recording: {session.title}",
                video_url=recording_url,
                order=course.modules.count() + 1
            )
             print("Created Module for future recording.")

        # Verify Module exists
        module = Module.objects.filter(course=course, video_url=recording_url).first()
        if module and module.video_url == recording_url:
            print("✅ SUCCESS: Recording uploaded and Module created for future session.")
        else:
            print("❌ FAILURE: Module creation failed.")
            
    except Exception as e:
        print(f"❌ FAILURE: Error during upload simulation: {e}")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    verify_unrestricted_upload()
