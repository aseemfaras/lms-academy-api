
import requests
import re

BASE_URL = 'http://localhost:8000/api'
EMAIL = 'ashok@gmail.com'
PASSWORD = 'admin123'

def extract_error():
    print(f"Logging in...")
    login_url = f"{BASE_URL}/users/login/"
    response = requests.post(login_url, json={"username": EMAIL, "password": PASSWORD})
    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}

    print("Fetching courses...")
    url = f"{BASE_URL}/trainers/courses/"
    response = requests.get(url, headers=headers)
    
    content = response.text
    # Look for the title which usually contains the exception name
    match = re.search(r"<title>(.*?)<\/title>", content)
    if match:
        error_title = match.group(1)
        print(f"Error Title: {error_title}")
        with open("error_name.txt", "w") as f:
            f.write(error_title)
    else:
        print("No title found.")

if __name__ == "__main__":
    extract_error()
