import os, sys
sys.path.append('c:/aideas/lms-backend')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()
tests = [
    ('admin@lms.com', 'admin123'),
    ('trainer@lms.com', 'trainer123'),
    ('anithakommoji78@gmail.com', 'password123'),
]
for email, pwd in tests:
    user = authenticate(username=email, password=pwd)
    print(email + ': ' + ('OK - role=' + user.role if user else 'FAIL'))
