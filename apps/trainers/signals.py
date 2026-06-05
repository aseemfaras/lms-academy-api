from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import ActivityLog, Module, LiveSession, TrainerAssignment
from students.models import Enrollment

User = get_user_model()

@receiver(post_save, sender=Enrollment)
def log_student_enrollment(sender, instance, created, **kwargs):
    if created and instance.course:
        student_name = instance.student.full_name or instance.student.username
        course_title = instance.course.title
        ActivityLog.objects.create(
            related_course=instance.course,
            activity_type='ENROLLMENT',
            message=f"New student {student_name} enrolled in {course_title}"
        )

@receiver(post_save, sender=LiveSession)
def log_live_session_scheduled(sender, instance, created, **kwargs):
    if created and instance.course:
        course_title = instance.course.title
        ActivityLog.objects.create(
            related_course=instance.course,
            activity_type='SESSION_SCHEDULED',
            message=f"Live session '{instance.title}' scheduled for {course_title}"
        )

@receiver(post_save, sender=Module)
def log_module_uploaded(sender, instance, created, **kwargs):
    if created and instance.course:
        course_title = instance.course.title
        # Defensive check for both old and new field names to prevent AttributeError if server is stale
        has_notes = (
            getattr(instance, 'notes_binary', None) or 
            getattr(instance, 'notes_file', None) or 
            getattr(instance, 'notes_url', None)
        )
        item_type = "Notes/Materials" if has_notes else ("Recording" if getattr(instance, 'video_url', None) else "Module")
        ActivityLog.objects.create(
            related_course=instance.course,
            activity_type='MATERIAL_UPLOADED',
            message=f"New {item_type.lower()} uploaded for {course_title}"
        )

@receiver(post_save, sender=TrainerAssignment)
def log_trainer_assigned(sender, instance, created, **kwargs):
    if created and instance.course:
        trainer_name = instance.trainer.full_name or instance.trainer.username
        course_title = instance.course.title
        ActivityLog.objects.create(
            related_course=instance.course,
            activity_type='TRAINER_ASSIGNED',
            message=f"Trainer {trainer_name} assigned to {course_title}"
        )
