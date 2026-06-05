import os
import django
import sys
from django.core.mail import send_mail

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

from users.utils import send_welcome_email
from users.models import User

def test_smtp_auth():
    print(f"Testing Welcome Email for {settings.EMAIL_HOST_USER}...")
    try:
        # Create a dummy user object for testing
        class DummyUser:
            full_name = "Test User"
            username = "Test User"
            email = settings.EMAIL_HOST_USER
        
        send_welcome_email(DummyUser(), "testpass123", "Python Full Stack", "https://lms.aideasacademy.com")
        print("Welcome email sent successfully!")
    except Exception as e:
        print(f"SMTP authentication or sending FAILED: {e}")

if __name__ == "__main__":
    test_smtp_auth()
