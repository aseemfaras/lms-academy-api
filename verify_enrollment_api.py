
import requests

BASE_URL = 'http://localhost:8000/api'
EMAIL = 'shalu@gmail.com'
PASSWORD = 'admin123'

def verify_enrollment_response():
    print(f"Logging in as {EMAIL}...")
    login_url = f"{BASE_URL}/users/login/"
    response = requests.post(login_url, json={"username": EMAIL, "password": PASSWORD})
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json()['access']
    user_id = response.json()['user']['id']
    headers = {"Authorization": f"Bearer {token}"}

    print(f"Fetching enrollments for student {user_id}...")
    url = f"{BASE_URL}/students/enrollments/?student={user_id}"
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data:
            print("First enrollment sample:")
            import json
            print(json.dumps(data[0], indent=2))
        else:
            print("No enrollments found for this student.")
    else:
        print(f"Failed to fetch enrollments: {response.text}")
        with open('error_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)

if __name__ == "__main__":
    verify_enrollment_response()
