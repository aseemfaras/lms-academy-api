
import requests

BASE_URL = 'http://localhost:8000/api'
EMAIL = 'admin@lms.com'
PASSWORD = 'admin123'

def test_flow():
    # 1. Login
    print(f"Attempting login for {EMAIL}...")
    login_url = f"{BASE_URL}/users/login/"
    login_data = {"username": EMAIL, "password": PASSWORD}
    response = requests.post(login_url, json=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        print(response.json())
        return

    data = response.json()
    access_token = data.get('access')
    print("Login successful.")
    # print(f"Access Token: {access_token[:20]}...")

    # 2. Fetch Courses
    print("\nAttempting to fetch courses...")
    courses_url = f"{BASE_URL}/courses/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(courses_url, headers=headers)
    
    print(f"Fetch courses status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error detail: {response.json()}")
    else:
        print(f"Successfully fetched {len(response.json())} courses.")

if __name__ == "__main__":
    test_flow()
