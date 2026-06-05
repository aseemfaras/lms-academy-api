import requests
import sys

def test_login(email, password):
    url = "http://localhost:8000/api/users/login/"
    data = {
        "username": email,
        "password": password
    }
    print(f"Testing login for {email}...")
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Login successful!")
            print(f"Response: {response.json().get('user', {})}")
        else:
            print(f"Login failed: {response.text}")
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    # Test with admin credentials from the logs
    test_login("admin@lms.com", "admin123")
