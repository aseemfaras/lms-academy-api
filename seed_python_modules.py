
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from trainers.models import Course, Module

def seed_modules():
    python_course = Course.objects.filter(title__icontains="Python").first()
    if not python_course:
        print("Python course not found.")
        return

    modules_data = [
        {
            "title": "Introduction to Python",
            "video_url": "https://www.youtube.com/embed/kqtD5dpn9C8",
            "notes_url": "#",
            "order": 1
        },
        {
            "title": "Python Data Types",
            "video_url": "https://www.youtube.com/embed/rfscVS0vtbw",
            "notes_url": "#",
            "order": 2
        },
        {
            "title": "Control Flow in Python",
            "video_url": "https://www.youtube.com/embed/Zp5MuPOtsSY",
            "notes_url": "#",
            "order": 3
        }
    ]

    for m in modules_data:
        Module.objects.get_or_create(
            course=python_course,
            title=m['title'],
            defaults={
                "video_url": m['video_url'],
                "notes_url": m['notes_url'],
                "order": m['order']
            }
        )
        print(f"Added module: {m['title']}")

if __name__ == "__main__":
    seed_modules()
    print("Seeding completed.")
