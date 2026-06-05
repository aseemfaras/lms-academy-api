import os
import django
import sys

# Add the project directory to the sys.path
sys.path.insert(0, r'c:\aideas\lms-backend')
sys.path.insert(0, os.path.join(r'c:\aideas\lms-backend', 'apps'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from trainers.models import LiveSession
from trainers.serializers import LiveSessionSerializer

sessions = LiveSession.objects.all()
print(f"Total sessions: {sessions.count()}")

for s in sessions:
    print(f"--- Session ID: {s.id} ---")
    print(f"Title: {s.title}")
    print(f"Course: {s.course}")
    print(f"Batch: {s.batch}")
    print(f"Date: {s.scheduled_date}")
    print(f"Start: {s.start_time}")
    print(f"End: {s.end_time}")
    
    try:
        serializer = LiveSessionSerializer(s)
        data = serializer.data
        print(f"Serialized Status: {data.get('status')}")
        print(f"Serialized Trainer: {data.get('trainer_name')}")
    except Exception as e:
        print(f"Error serializing: {e}")
