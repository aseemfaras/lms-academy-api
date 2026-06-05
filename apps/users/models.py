from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User Model for LMS.
    Includes role-based access control.
    """
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        TRAINER = 'TRAINER', 'Trainer'
        SUPPORTER = 'SUPPORTER', 'Supporter'
        ADMIN = 'ADMIN', 'Admin'

    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.STUDENT
    )
    
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    portal_link = models.URLField(max_length=500, blank=True, null=True)
    course_name = models.CharField(max_length=255, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
    
    # You can add more fields here if needed (e.g., profile picture, phone number)

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
