import os
import django
import sys

# Set up Django environment
sys.path.append('c:/aideas/lms-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from trainers.models import Course, TrainerAssignment, LiveSession
from django.contrib.auth import get_user_model

User = get_user_model()

def verify_trainer_visibility():
    print("--- Starting Verification ---")
    
    # 1. Setup/Identify a trainer and courses
    trainer_email = "shoubhik@lms.com"
    try:
        trainer = User.objects.get(email=trainer_email)
    except User.DoesNotExist:
        print(f"Trainer {trainer_email} not found. Please ensure seed data exists.")
        return

    # Create a dummy course if none exists for this trainer
    course_title = "Verification Course"
    course, created = Course.objects.get_or_create(title=course_title)
    
    # Assign trainer to course
    assignment, created = TrainerAssignment.objects.get_or_create(course=course, trainer=trainer)
    assignment.is_active = False # Set to Inactive for verification
    assignment.save()
    
    print(f"Course: {course.title}, Trainer: {trainer.email}, Active: {assignment.is_active}")

    # Create a live session for this course
    import datetime
    session, created = LiveSession.objects.get_or_create(
        course=course,
        title="Verification Session",
        defaults={
            'scheduled_date': datetime.date.today(),
            'start_time': datetime.time(10, 0),
            'end_time': datetime.time(11, 0),
            'meeting_link': 'http://example.com'
        }
    )

    # 2. Check Course QuerySet (Trainer's view)
    # Simulating get_queryset logic
    courses_view = Course.objects.filter(trainerassignment__trainer=trainer).distinct()
    print(f"Courses visible to trainer: {[c.title for c in courses_view]}")
    
    # Verification: Course should be visible even if inactive
    if course in courses_view:
        print("✅ SUCCESS: Inactive course is visible in trainer's course list.")
    else:
        print("❌ FAILURE: Inactive course is NOT visible in trainer's course list.")

    # 3. Check Live Session QuerySet (Trainer's view)
    # Simulating get_queryset logic for LiveSession
    sessions_view = LiveSession.objects.filter(
        course__trainerassignment__trainer=trainer, 
        course__trainerassignment__is_active=True
    ).distinct()
    print(f"Live sessions visible to trainer: {[s.title for s in sessions_view]}")
    
    # Verification: Session for inactive course should NOT be visible
    if session in sessions_view:
        print("❌ FAILURE: Session from inactive course is visible to trainer.")
    else:
        print("✅ SUCCESS: Session from inactive course is hidden from trainer.")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    verify_trainer_visibility()
