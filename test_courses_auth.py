import urllib.request
import urllib.error
import json

base_url = "http://localhost:8000/api"
login_url = f"{base_url}/users/login/"
courses_url = f"{base_url}/courses/"

login_data = json.dumps({
    "username": "admin@lms.com",
    "password": "admin123"
}).encode('utf-8')

# 1. Login to get token
req_login = urllib.request.Request(
    login_url, 
    data=login_data, 
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req_login) as response:
        res_data = json.loads(response.read().decode())
        token = res_data.get('access')
        print(f"Login successful. Token obtained.")

    # 2. Call courses endpoint with token
    headers = {
        "Authorization": f"Bearer {token}",
        "Origin": "http://localhost:5173",
    }
    req_courses = urllib.request.Request(courses_url, headers=headers)
    
    with urllib.request.urlopen(req_courses) as response:
        print(f"Courses Status Code: {response.getcode()}")
        print(f"Headers: {dict(response.info())}")
        print(f"Response Body: {response.read().decode()[:100]}")

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Headers: {dict(e.info())}")
    print(f"Body: {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
