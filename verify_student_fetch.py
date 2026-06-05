
import requests

BASE_URL = 'http://localhost:8000/api'
STUDENT_EMAIL = 'shalu@gmail.com'
PASSWORD = 'admin123'
COURSE_ID = 7

def verify_student():
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

    # 2. Fetch Course Detail
    print(f"Fetching Course {COURSE_ID} details as Student...")
    url = f"{BASE_URL}/trainers/courses/{COURSE_ID}/"
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS! Data received:")
        print(response.json())
    else:
        print("FAILED! Response preview:")
        print(response.text[:500])

if __name__ == "__main__":
    verify_student()
