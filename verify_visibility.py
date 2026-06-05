
import requests

BASE_URL = 'http://localhost:8000/api'
STUDENT_EMAIL = 'shalu@gmail.com' # Existing student
PASSWORD = 'admin123' # Assuming standard password from seed
COURSE_ID = 2 # Python course

def verify_visibility():
    # 1. Login as Student
    print(f"Logging in as student: {STUDENT_EMAIL}...")
    login_url = f"{BASE_URL}/users/login/"
    response = requests.post(login_url, json={"username": STUDENT_EMAIL, "password": PASSWORD})
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 2. Get Course Detail
    print(f"\nFetching Course Detail (ID: {COURSE_ID}) as Student...")
    url = f"{BASE_URL}/trainers/courses/{COURSE_ID}/"
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Course: {data['title']}")
        modules = data.get('modules', [])
        print(f"Modules found: {len(modules)}")
        for m in modules:
            print(f"- {m['title']} (URL: {m['video_url']})")
    else:
        print(f"Error: {response.text}")

    # 3. Try to add a module (should fail)
    print("\nAttempting to add module as Student (should fail)...")
    url = f"{BASE_URL}/trainers/modules/"
    data = {"course": COURSE_ID, "title": "Hacker Module"}
    response = requests.post(url, json=data, headers=headers)
    print(f"Post status: {response.status_code} (Expected: 403)")

if __name__ == "__main__":
    verify_visibility()
