
import requests
import re

BASE_URL = 'http://localhost:8000/api'
EMAIL = 'ashok@gmail.com'
PASSWORD = 'admin123'

def extract_login_error():
    print(f"Logging in as {EMAIL}...")
    login_url = f"{BASE_URL}/users/login/"
    response = requests.post(login_url, json={"username": EMAIL, "password": PASSWORD})
    print(f"Status: {response.status_code}")
    content = response.text
    
    match = re.search(r"<title>(.*?)<\/title>", content)
    if match:
        print(f"Login Error Title: {match.group(1)}")
    
    match = re.search(r"name &#x27;(.*?)&#x27; is not defined", content)
    if match:
        print(f"NameError: {match.group(1)}")
    else:
        # Check for other common error patterns
        match = re.search(r"Traceback.*?<pre.*?>(.*?)<\/pre>", content, re.DOTALL)
        if match:
            print("\n--- Traceback Fragment ---")
            print(match.group(1)[:1000])
        else:
            with open("ashok_login_error.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("Looked at HTML, no obvious traceback. Saved to ashok_login_error.html")

if __name__ == "__main__":
    extract_login_error()
