
import requests
import json

BASE_URL = 'http://localhost:8000/api'
EMAIL = 'ashok@gmail.com'
PASSWORD = 'admin123'

def debug_500():
    print(f"Logging in as: {EMAIL}...")
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
    if "NameError" in content:
        import re
        match = re.search(r"NameError: (.*?)<", content)
        if match:
            print(f"Server-side NameError identified: {match.group(1)}")
        else:
            # Try to find it in the context of the traceback
            # Look for "The name '...' is not defined"
            match = re.search(r"name &#x27;(.*?)&#x27; is not defined", content)
            if match:
                print(f"Server-side NameError identified: name '{match.group(1)}' is not defined")
            else:
                print("Could not parse specific NameError from HTML. Full response saved to debug.html")
                with open("debug.html", "w", encoding="utf-8") as f:
                    f.write(content)
    else:
        print("No NameError found in response. First 500 chars:")
        print(content[:500])

if __name__ == "__main__":
    debug_500()
