from trainers.models import LiveSession
from django.utils import timezone
import datetime

sessions = LiveSession.objects.filter(title__icontains='gen ai') | LiveSession.objects.filter(title__icontains='neural')
now = timezone.now()
print(f"Current Time (timezone.now()): {now}")
for s in sessions:
    start_dt = timezone.make_aware(datetime.datetime.combine(s.scheduled_date, s.start_time))
    end_dt = timezone.make_aware(datetime.datetime.combine(s.scheduled_date, s.end_time))
    
    print("-" * 50)
    print(f"Session: {s.title}")
    print(f"Start Data: {s.scheduled_date} {s.start_time}")
    print(f"End Data: {s.scheduled_date} {s.end_time}")
    print(f"Aware Start: {start_dt}")
    print(f"Aware End: {end_dt}")
    print(f"Backend calculation is_completed (now > end_dt): {now > end_dt}")
    if now > end_dt:
        print("Status: COMPLETED")
    elif now < start_dt:
        print("Status: UPCOMING")
    else:
        print("Status: LIVE")
