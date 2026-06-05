import requests
import sys

def test_registration_and_email(email, full_name, role, course, portal):
    url = "http://localhost:8000/api/users/register/"
    data = {
        "username": full_name,
        "email": email,
        "password": "Temporary@2025",
        "role": role,
        "course_name": course,
        "portal_link": portal
    }
    print(f"Testing registration and email for {email}...")
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 201 or response.status_code == 200:
            print("Registration successful!")
            print("Check the backend console for the rendered email.")
        else:
            print(f"Registration failed: {response.text}")
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    # Test with a new student
    test_registration_and_email(
        "yashwanth_test@gmail.com", 
        "Yashwanth", 
        "Student", 
        "Python Backend _2601_ 10AM", 
        "https://lms.aideasacademy.com"
    )
