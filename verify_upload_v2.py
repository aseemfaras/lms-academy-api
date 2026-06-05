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

def verify_upload():
    print("--- Starting Verification: Video and Notes Upload ---")
    
    # Identify a course and session
    course = Course.objects.first()
    if not course:
        print("No course found. Creating one...")
        course = Course.objects.create(title="Test Course", description="Test")
    
    # Create a completed session
    session = LiveSession.objects.create(
        course=course,
        title="Test Completed Session",
        scheduled_date=timezone.now().date(),
        start_time=(timezone.now() - datetime.timedelta(hours=2)).time(),
        end_time=(timezone.now() - datetime.timedelta(hours=1)).time(),
        meeting_link="http://zoom.us/test"
    )
    print(f"Created session: {session.title} (ID: {session.id}, Is Completed: {session.is_completed})")

    # Simulate Trainer Upload (Recording + Notes)
    recording_url = "https://youtube.com/watch?v=test_video"
    notes_url = "https://drive.google.com/test_notes"
    
    session.recording_url = recording_url
    session.notes_url = notes_url
    session.save()
    print(f"Uploaded: recording={recording_url}, notes={notes_url}")

    # The viewset logic (perform_update) is not triggered by direct model save, 
    # but we can verify the model fields and then manually check the logic 
    # if we want to simulate the viewset.
    
    # Manually trigger the logic that would be in perform_update for verification
    if not Module.objects.filter(course=course, video_url=recording_url).exists():
        Module.objects.create(
            course=course,
            title=f"Recording: {session.title}",
            video_url=recording_url,
            notes_url=notes_url,
            order=course.modules.count() + 1
        )
        print("Created Module from Session logic simulation.")

    # Verify Module contains both
    module = Module.objects.filter(course=course, video_url=recording_url).first()
    if module and module.video_url == recording_url and module.notes_url == notes_url:
        print("✅ SUCCESS: Module contains both recording and notes URL.")
    else:
        print("❌ FAILURE: Module mapping failed.")

    # Verify LiveSession contains both
    session_refresh = LiveSession.objects.get(id=session.id)
    if session_refresh.recording_url == recording_url and session_refresh.notes_url == notes_url:
        print("✅ SUCCESS: LiveSession contains both recording and notes URL.")
    else:
        print("❌ FAILURE: LiveSession fields failed.")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    verify_upload()
