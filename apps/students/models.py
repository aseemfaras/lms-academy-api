from django.db import models
from django.conf import settings

class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey('trainers.Course', on_delete=models.CASCADE, related_name='enrollments', null=True, blank=True)
    batch = models.CharField(max_length=50, default="Batch 1")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='ACTIVE', choices=[('ACTIVE', 'Active'), ('COMPLETED', 'Completed'), ('DROPPED', 'Dropped')])

    class Meta:
        db_table = 'enrollments'

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
