import os
import django
from django.contrib.auth import authenticate

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

def verify_login():
    print("Verifying student logins...")
    print("-" * 50)
    
    test_cases = [
        ('shalu@gmail.com', 'password123'),
        ('Shalu@gmail.com', 'password123'), # Case variation
        ('ashok@gmail.com', 'password123'),
        ('john@gmail.com', 'password123'),
        ('anil@gmail.com', 'password123'),
        ('admin@lms.com', 'admin123'), # Should still work
    ]

    for email, password in test_cases:
        # Note: We need to emulate the logic in the view (lowercase email)
        # since authenticate() is case-sensitive for the USERNAME_FIELD
        normalized_email = email.lower()
        user = authenticate(username=normalized_email, password=password)
        
        if user:
            print(f"[SUCCESS] Login successful for: {email}")
        else:
            # Check if user exists but auth failed
            try:
                u = User.objects.get(email=normalized_email)
                print(f"[FAILED] Auth failed for: {email} (User exists but password/auth rejected)")
            except User.DoesNotExist:
                print(f"[FAILED] User not found: {normalized_email}")
        print("-" * 50)

if __name__ == "__main__":
    verify_login()
