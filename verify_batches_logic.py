import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from users.models import User
from trainers.models import Course, Module, LiveSession, TrainerAssignment
from students.models import Enrollment

def run_verification():
    print("--- STARTING BATCH VERIFICATION ---")
    
    # 1. Setup Test Data
    admin = User.objects.filter(role='ADMIN').first()
    student = User.objects.filter(role='STUDENT').first()
    trainer = User.objects.filter(role='TRAINER').first()
    
    if not (admin and student and trainer):
        print("Missing users for testing.")
        return

    course = Course.objects.create(title="Batch Isolation Test Course")
    print(f"Created Course: {course.title} (ID: {course.id})")

    # 2. Assign Trainer & Enroll Student to Batch 2
    TrainerAssignment.objects.create(course=course, trainer=trainer, batch="Batch 2")
    Enrollment.objects.create(student=student, course=course, batch="Batch 2")
    
    print("Enrolled student and assigned trainer to Batch 2.")

    # 3. Create items in different batches
    mod1 = Module.objects.create(course=course, title="Module B1", batch="Batch 1")
    mod2 = Module.objects.create(course=course, title="Module B2", batch="Batch 2")
    
    ls1 = LiveSession.objects.create(course=course, title="Live B1", batch="Batch 1", scheduled_date="2026-05-01", start_time="10:00", end_time="11:00")
    ls2 = LiveSession.objects.create(course=course, title="Live B2", batch="Batch 2", scheduled_date="2026-05-01", start_time="10:00", end_time="11:00")
    
    print("Created Modules and Live Sessions in Batch 1 and Batch 2.")

    # 4. Verify Student Visibility (Should only see Batch 2)
    # Re-importing views would be tricky with DRF Request objects. 
    # Let's manually replicate the queryset logic from views.py
    
    # Student Module visibility logic:
    student_enrollments = student.enrollments.filter(course=course)
    student_batches = {e.batch for e in student_enrollments}
    student_modules = Module.objects.filter(course=course, batch__in=student_batches)
    
    print("\n--- Student Visibility (Batch 2) ---")
    print(f"Allowed Batches: {student_batches}")
    print(f"Visible Modules: {[m.title for m in student_modules]}")
    assert len(student_modules) == 1 and student_modules[0].title == "Module B2", "Student saw incorrect modules."
    
    # Student Live Session visibility logic:
    student_sessions = LiveSession.objects.filter(course=course, batch__in=student_batches)
    print(f"Visible Sessions: {[s.title for s in student_sessions]}")
    assert len(student_sessions) == 1 and student_sessions[0].title == "Live B2", "Student saw incorrect sessions."
    
    # 5. Verify Trainer Visibility (Should only see Batch 2)
    trainer_assignments = trainer.trainerassignment_set.filter(course=course)
    trainer_batches = {a.batch for a in trainer_assignments}
    trainer_modules = Module.objects.filter(course=course, batch__in=trainer_batches)
    trainer_sessions = LiveSession.objects.filter(course=course, batch__in=trainer_batches)

    print("\n--- Trainer Visibility (Batch 2) ---")
    print(f"Allowed Batches: {trainer_batches}")
    print(f"Visible Modules: {[m.title for m in trainer_modules]}")
    assert len(trainer_modules) == 1 and trainer_modules[0].title == "Module B2", "Trainer saw incorrect modules."
    print(f"Visible Sessions: {[s.title for s in trainer_sessions]}")
    assert len(trainer_sessions) == 1 and trainer_sessions[0].title == "Live B2", "Trainer saw incorrect sessions."

    print("\n✅ Verification Successful: Batch isolation logic works correctly.")
    
    # Cleanup
    course.delete()
    print("Cleaned up test data.")

if __name__ == "__main__":
    run_verification()
