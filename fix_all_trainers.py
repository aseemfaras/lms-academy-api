
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

# Reset all trainer passwords to consistent values
trainers_to_fix = [
    ('trainer@lms.com', 'trainer123'),
    ('shoubhik@lms.com', 'trainer123'),
    ('vikram@gmail.com', 'trainer123'),
]

for email, new_pw in trainers_to_fix:
    user = User.objects.filter(email=email).first()
    if user:
        user.set_password(new_pw)
        user.save()
        print(f"Fixed: {email} -> password: {new_pw}")
    else:
        print(f"Not found: {email}")

print("\nAll trainer passwords reset successfully.")
