
import os
import django
import sys
import traceback

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.users.views import UserDeleteView

User = get_user_model()

def reproduce_error():
    # Create a dummy user to delete
    try:
        user, created = User.objects.get_or_create(email='delete_me@example.com', username='delete_me')
        if created:
            user.set_password('password')
            user.save()
            print(f"Created user: {user.email} (ID: {user.id})")
        else:
            print(f"Using existing user: {user.email} (ID: {user.id})")
            
        # Create an admin user to perform the deletion
        admin, _ = User.objects.get_or_create(email='admin_repro@example.com', username='admin_repro')
        admin.is_staff = True
        admin.is_superuser = True
        admin.role = 'ADMIN'
        admin.save()
        
        factory = APIRequestFactory()
        view = UserDeleteView.as_view()
        
        request = factory.delete(f'/api/users/{user.id}/')
        force_authenticate(request, user=admin)
        
        response = view(request, pk=user.id)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Data: {response.data}")
        
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    reproduce_error()
