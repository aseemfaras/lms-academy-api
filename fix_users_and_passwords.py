import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User
from django.db import transaction

def cleanup_users():
    print("Starting SAFE user cleanup...")
    
    with transaction.atomic():
        # 1. Get all students
        students = User.objects.filter(role=User.Role.STUDENT)
        processed_emails = set()

        for student in students:
            email_lower = student.email.lower()
            if email_lower in processed_emails:
                continue
            
            # Find all accounts with this email (case-insensitive)
            # We use email__iexact to find all variations
            duplicates = User.objects.filter(email__iexact=email_lower).order_by('id')
            
            if duplicates.count() > 1:
                print(f"Merging duplicates for: {email_lower}")
                canonical = None
                # Prefer exact lowercase match if it exists
                for d in duplicates:
                    if d.email == email_lower:
                        canonical = d
                        break
                if not canonical:
                    canonical = duplicates[0]
                
                # Deactivate others instead of deleting to avoid integrity issues with missing tables
                for d in duplicates:
                    if d.id != canonical.id:
                        print(f"  Deactivating and renaming duplicate ID: {d.id} ({d.email})")
                        d.email = f"merged_{d.id}_{d.email}"
                        d.username = f"merged_{d.id}_{d.username}"
                        d.is_active = False
                        d.save()
                
                # Update canonical
                canonical.email = email_lower
                canonical.username = email_lower
                canonical.set_password('password123')
                canonical.is_active = True
                canonical.save()
                print(f"  Canonical Cleaned: {canonical.email} (Password: password123)")
            else:
                # Just reset password and lowercase email
                student.email = email_lower
                student.username = email_lower
                student.set_password('password123')
                # Ensure active since we want students to be able to login
                student.is_active = True 
                student.save()
                print(f"  Updated: {student.email} (Password: password123)")
            
            processed_emails.add(email_lower)

    print("User cleanup complete.")

if __name__ == "__main__":
    cleanup_users()
