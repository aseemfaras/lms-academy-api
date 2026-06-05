
import requests

BASE_URL = 'http://localhost:8000/api'
EMAIL = 'admin@lms.com'
PASSWORD = 'admin123'

def verify_routes():
    # 1. Login to get token
    print("Logging in...")
    login_url = f"{BASE_URL}/users/login/"
    response = requests.post(login_url, json={"username": EMAIL, "password": PASSWORD})
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 2. Test Trainers Route (Courses)
    print("\nTesting /api/trainers/courses/ ...")
    courses_url = f"{BASE_URL}/trainers/courses/"
    response = requests.get(courses_url, headers=headers)
    print(f"Courses status: {response.status_code}")
    if response.status_code == 200:
        print(f"Successfully fetched {len(response.json())} courses.")
    else:
        print(f"Error: {response.json()}")

    # 3. Test Students Route (Enrollments)
    print("\nTesting /api/students/enrollments/ ...")
    # First, list enrollments
    enroll_url = f"{BASE_URL}/students/enrollments/"
    response = requests.get(enroll_url, headers=headers)
    print(f"Enrollments status: {response.status_code}")
    if response.status_code == 200:
        print(f"Successfully fetched {len(response.json())} enrollments.")
    else:
        print(f"Error: {response.json()}")

    # 4. Test creating an enrollment
    print("\nTesting POST to /api/students/enrollments/ ...")
    # Get first course ID
    course_id = requests.get(courses_url, headers=headers).json()[0]['id']
    enroll_data = {
        "course": course_id,
        "email": "shalu@gmail.com"
    }
    response = requests.post(enroll_url, json=enroll_data, headers=headers)
    print(f"Create enrollment status: {response.status_code}")
    if response.status_code in [200, 201]:
        print("Enrollment created successfully.")
    else:
        print(f"Error: {response.json()}")

if __name__ == "__main__":
    verify_routes()
