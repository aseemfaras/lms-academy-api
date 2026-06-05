
import requests
import re

BASE_URL = 'http://localhost:8000/api'
EMAIL = 'shalu@gmail.com'
PASSWORD = 'admin123'

def extract_error():
    print(f"Logging in as {EMAIL}...")
    login_url = f"{BASE_URL}/users/login/"
    response = requests.post(login_url, json={"username": EMAIL, "password": PASSWORD})
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}

    print("Fetching courses...")
    url = f"{BASE_URL}/trainers/courses/"
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    content = response.text
    # Look for the title which usually contains the exception name
    match = re.search(r"<title>(.*?)<\/title>", content)
    if match:
        error_title = match.group(1)
        print(f"Error Title: {error_title}")
        with open("error_name_list.txt", "w") as f:
            f.write(error_title)
            
    # Also look for the specific traceback line if possible
    match = re.search(r"name &#x27;(.*?)&#x27; is not defined", content)
    if match:
        print(f"Specific NameError: {match.group(1)}")

if __name__ == "__main__":
    extract_error()
