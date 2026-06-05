
import requests

BASE_URL = 'http://localhost:8000/api'
ADMIN_EMAIL = 'admin@lms.com'
PASSWORD = 'admin123'
COURSE_ID = 7 # UPDATED Python course ID

def verify_fix():
    # 1. Login as Admin
    print("Logging in as Admin...")
    login_url = f"{BASE_URL}/users/login/"
    response = requests.post(login_url, json={"username": ADMIN_EMAIL, "password": PASSWORD})
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 2. Create Module for Course 7
    print(f"\nCreating module for Course {COURSE_ID}...")
    url = f"{BASE_URL}/trainers/modules/"
    data = {
        "course": COURSE_ID,
        "title": "Final Fixed Module",
        "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "notes_url": "https://example.com/notes.pdf",
        "order": 1
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"Create Module Status: {response.status_code}")
    if response.status_code not in [200, 201]:
        print(f"Error: {response.text}")
        return
    
    module_id = response.json()['id']
    print(f"Module created with ID: {module_id}")

    # 3. Check Course Detail (Admin)
    print(f"\nChecking Course {COURSE_ID} details as Admin...")
    url = f"{BASE_URL}/trainers/courses/{COURSE_ID}/"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        modules = response.json().get('modules', [])
        found = any(m['id'] == module_id for m in modules)
        print(f"Module found in course detail: {found}")
    else:
        print(f"Error fetching course detail: {response.text}")

    # 4. Check Course Detail (Student)
    STUDENT_EMAIL = 'shalu@gmail.com'
    print(f"\nLogging in as student: {STUDENT_EMAIL}...")
    response = requests.post(login_url, json={"username": STUDENT_EMAIL, "password": PASSWORD})
    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"Fetching Course {COURSE_ID} details as Student...")
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        modules = response.json().get('modules', [])
        print(f"Modules found for Student: {len(modules)}")
        if len(modules) > 0:
            print("SUCCESS: Student can now see the videos!")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    verify_fix()
