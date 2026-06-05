
import requests

BASE_URL = 'http://localhost:8000/api'

def test_login(email, password):
    login_url = f"{BASE_URL}/users/login/"
    login_data = {"username": email, "password": password}
    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        data = response.json()
        user = data.get('user', {})
        print(f"LOGIN SUCCESS: {email} | Role: {user.get('role')} | Name: {user.get('full_name')}")
        return True
    else:
        print(f"LOGIN FAILED: {email} | Status: {response.status_code} | Detail: {response.text[:100]}")
        return False

print("Testing ALL trainer logins after password reset...\n")
test_login('hadasha@gmail.com', 'trainer123')
test_login('trainer@lms.com', 'trainer123')
test_login('shoubhik@lms.com', 'trainer123')
test_login('vikram@gmail.com', 'trainer123')
test_login('admin@lms.com', 'admin123')
