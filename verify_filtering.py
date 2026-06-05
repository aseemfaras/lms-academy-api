
import requests

BASE_URL = 'http://localhost:8000/api'
PASSWORD = 'admin123'

def test_student_filtering(email, expected_ids):
    print(f"\nTesting filtering for: {email}")
    login_url = f"{BASE_URL}/users/login/"
    response = requests.post(login_url, json={"username": email, "password": PASSWORD})
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}

    url = f"{BASE_URL}/trainers/courses/"
    response = requests.get(url, headers=headers)
    print(f"Status for {email}: {response.status_code}")
    if response.status_code == 200:
        courses = response.json()
        received_ids = [c['id'] for c in courses]
        print(f"Received IDs: {received_ids}")
        print(f"Expected IDs: {expected_ids}")
        if set(received_ids) == set(expected_ids):
            print("SUCCESS: Filtering works correctly.")
        else:
            print("FAILURE: IDs do not match expectations.")
    else:
        print(f"Error fetching courses: {response.text}")

if __name__ == "__main__":
    # ashok@gmail.com enrolled in 6 (Java)
    test_student_filtering('ashok@gmail.com', [6])
    
    # shalu@gmail.com enrolled in 7 (Python)
    test_student_filtering('shalu@gmail.com', [7])
    
    # Admin should see all
    test_student_filtering('admin@lms.com', [6, 7])
