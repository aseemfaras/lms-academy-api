
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
    
    # Extract the name from "name '...' is not defined"
    match = re.search(r"name &#x27;(.*?)&#x27; is not defined", content)
    if match:
        error_name = match.group(1)
        print(f"FAILED! NameError: name '{error_name}' is not defined")
        with open("critical_error_name.txt", "w") as f:
            f.write(error_name)
    else:
        # Check for other error formats
        match = re.search(r"Traceback.*?<pre.*?>(.*?)<\/pre>", content, re.DOTALL)
        if match:
            print("\n--- Traceback Fragment ---")
            print(match.group(1)[:1000])
        else:
            print("No Traceback found in HTML.")
            with open("ashok_error.html", "w", encoding="utf-8") as f:
                f.write(content)

if __name__ == "__main__":
    extract_error()
