import os
import django
import sys
import io

# Set up Django environment
sys.path.append('c:/aideas/lms-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.urls import reverse
from trainers.models import Course, Module

def verify_db_notes():
    print("--- Starting Verification: Database-only Note Storage ---")
    
    User = get_user_model()
    admin = User.objects.filter(role='ADMIN').first()
    if not admin:
        print("Creating admin user...")
        admin = User.objects.create_superuser(email='admin_test@example.com', password='password', username='admin_test', role='ADMIN')
    
    client = APIClient()
    client.force_authenticate(user=admin)
    
    # 1. Prepare course
    course = Course.objects.first()
    if not course:
        course = Course.objects.create(title="Test Course", description="Test")
    
    # 2. Upload Module with Binary Note
    note_content = b"This is a test note stored in the database."
    note_file = SimpleUploadedFile("test_note.txt", note_content, content_type="text/plain")
    
    data = {
        "course": course.id,
        "title": "Module with DB Note",
        "notes_file": note_file,
        "batch": "Batch 1",
        "order": 1
    }
    
    print("Uploading module with notes...")
    url = reverse('module-list')
    # Use request context for absolute URI in SerializerMethodField
    response = client.post(url, data, format='multipart')
    
    if response.status_code != 201:
        print(f"[FAILURE] Failed to create module. Status: {response.status_code}, Error: {response.data}")
        return

    module_id = response.data['id']
    download_url = response.data['notes_file']
    print(f"[SUCCESS] Module created. ID: {module_id}")
    print(f"Download URL: {download_url}")
    
    # 3. Verify Database
    module = Module.objects.get(id=module_id)
    if module.notes_binary == note_content and module.notes_filename == "test_note.txt":
        print("[SUCCESS] Note content and filename stored correctly in DB.")
    else:
        print("[FAILURE] DB storage verification failed.")
        print(f"DB content length: {len(module.notes_binary) if module.notes_binary else 0}")
        print(f"DB filename: {module.notes_filename}")

    # 4. Verify Download
    print("Testing download...")
    download_response = client.get(download_url)
    
    if download_response.status_code == 200:
        if download_response.content == note_content:
            print("[SUCCESS] Downloaded content matches original.")
        else:
            print("[FAILURE] Downloaded content mismatch.")
        
        if download_response['Content-Disposition'] == 'attachment; filename="test_note.txt"':
            print("[SUCCESS] Content-Disposition header is correct.")
        else:
            print(f"[FAILURE] Content-Disposition header is wrong: {download_response['Content-Disposition']}")
    else:
        print(f"[FAILURE] Download failed. Status: {download_response.status_code}")

    # 5. Verify Filesystem (Ensure no files created)
    media_notes_path = os.path.join('c:/aideas/lms-backend', 'media', 'modules', 'notes')
    if os.path.exists(media_notes_path):
        files = os.listdir(media_notes_path)
        if any("test_note" in f for f in files):
            print(f"[FAILURE] Found file in media directory: {files}")
        else:
            print("[SUCCESS] No matching file found in media directory.")
    else:
        print("[SUCCESS] Media notes directory does not exist or is empty.")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    verify_db_notes()
