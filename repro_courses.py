
import requests
import sys

BASE_URL = "http://localhost:8000/api"

def test_admin_access():
    # 1. Login
    login_url = f"{BASE_URL}/users/login/"
    login_data = {
        "username": "admin@lms.com",
        "password": "admin123" # Updated with correct password from seed_users.py
    }
    
    print(f"Attempting login for {login_data['username']}...")
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            print(response.text)
            return
        
        data = response.json()
        access_token = data.get('access')
        print("Login successful.")
        
        # 2. Fetch courses
        courses_url = f"{BASE_URL}/courses/"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        print("\nAttempting to fetch courses...")
        response = requests.get(courses_url, headers=headers)
        print(f"Fetch Courses Response: {response.status_code}")
        if response.status_code == 200:
            print(response.json())
        else:
            print(response.text)
            
        # 3. Try to add a course
        print("\nAttempting to create a course...")
        course_data = {
            "title": "Test Course from Script",
            "description": "This is a test course description"
        }
        response = requests.post(courses_url, json=course_data, headers=headers)
        print(f"Create Course Response: {response.status_code}")
        if response.status_code == 201:
            print("Course created successfully!")
            print(response.json())
        else:
            print(response.text)
            
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    # Check if we should use different password from command line
    if len(sys.argv) > 1:
        # If user provided a password
        pass 
    test_admin_access()
