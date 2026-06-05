
import os
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from users.views import CustomTokenObtainPairView

factory = APIRequestFactory()
view = CustomTokenObtainPairView.as_view()

# Simulate frontend payload with MISSING fields
payload_empty = {}
print("\nTesting login with EMPTY payload:", payload_empty)
request_empty = factory.post('/api/users/login/', payload_empty, format='json')
response_empty = view(request_empty)
print("Response Status (Empty):", response_empty.status_code)
print("Response Data (Empty):", json.dumps(response_empty.data, indent=2))

if response.status_code == 400:
    print("\nDetailed Validation Errors:")
    for field, errors in response.data.items():
        print(f" - {field}: {errors}")
