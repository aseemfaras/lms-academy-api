
import requests
import re

BASE_URL = 'http://localhost:8000/api'
EMAIL = 'ashok@gmail.com'
PASSWORD = 'admin123'

def extract_error():
    print(f"Logging in as {EMAIL}...")
    login_url = f"{BASE_URL}/users/login/"
    response = requests.post(login_url, json={"username": EMAIL, "password": PASSWORD})
    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}

    print("Fetching courses...")
    url = f"{BASE_URL}/trainers/courses/"
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    content = response.text
    match = re.search(r"<title>(.*?)<\/title>", content)
    if match:
        print(f"Error Title: {match.group(1)}")
    
    match = re.search(r"name &#x27;(.*?)&#x27; is not defined", content)
    if match:
        print(f"NameError: {match.group(1)}")
    else:
        # Check for other common error patterns
        if "AttributeError" in content:
            print("AttributeError found.")
        if "TypeError" in content:
            print("TypeError found.")

if __name__ == "__main__":
    extract_error()
