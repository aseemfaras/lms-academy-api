from django.db import models
from django.conf import settings

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    trainers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        through='TrainerAssignment',
        related_name='courses_teaching', 
        blank=True
    )

    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'

    def __str__(self):
        return self.title

class Batch(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='batches')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'course_batches'
        unique_together = ('course', 'name')

    def __str__(self):
        return f"{self.course.title} - {self.name}"

class TrainerAssignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    batch = models.CharField(max_length=50, default="Batch 1")
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'trainer_assignments'
        unique_together = ('course', 'trainer', 'batch')

    def __str__(self):
        return f"{self.trainer.email} in {self.course.title} ({'Active' if self.is_active else 'Inactive'})"

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    video_url = models.URLField(max_length=500, blank=True, null=True)
    notes_url = models.URLField(max_length=500, blank=True, null=True)
    notes_binary = models.BinaryField(blank=True, null=True)
    notes_filename = models.CharField(max_length=255, blank=True, null=True)
    notes_content_type = models.CharField(max_length=100, blank=True, null=True)
    batch = models.CharField(max_length=50, default="Batch 1")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        db_table = 'modules'
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class LiveSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='live_sessions', null=True, blank=True)
    batch = models.CharField(max_length=50, default="Batch 1")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scheduled_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    meeting_link = models.URLField()
    recording_url = models.URLField(blank=True, null=True)
    notes_url = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_sessions')


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'live_sessions'
        ordering = ['scheduled_date', 'start_time']

    @property
    def is_completed(self):
        from django.utils import timezone
        import datetime
        now = timezone.now()
        end_dt = timezone.make_aware(datetime.datetime.combine(self.scheduled_date, self.end_time))
        return now > end_dt

    def __str__(self):
        return f"{self.title} ({self.scheduled_date} {self.start_time})"



class ActivityLog(models.Model):
    ACTIVITY_TYPES = (
        ('ENROLLMENT', 'Enrollment'),
        ('SESSION_SCHEDULED', 'Live Session Scheduled'),
        ('MATERIAL_UPLOADED', 'Material Uploaded'),
        ('TRAINER_ASSIGNED', 'Trainer Assigned'),
        ('SYSTEM_UPDATE', 'System Update'),
    )
    
    related_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='activity_logs', null=True, blank=True)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activity_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.activity_type}] {self.message}"
