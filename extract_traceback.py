
import requests
import re

BASE_URL = 'http://localhost:8000/api'
EMAIL = 'ashok@gmail.com'
PASSWORD = 'admin123'

def extract_traceback():
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
    
    # Look for the traceback section in Django's error page
    # It usually starts with "Traceback (most recent call last):" or is inside a <div id="traceback">
    match = re.search(r"<pre class=\"exception_value\">(.*?)<\/pre>", content, re.DOTALL)
    if match:
        print(f"Exception Value: {match.group(1)}")

    # Try to find the actual traceback lines
    match = re.search(r"<div id=\"browserTraceback\"(.*?)<\/div>", content, re.DOTALL)
    if match:
        # Strip HTML tags
        traceback_html = match.group(0)
        clean_tb = re.sub(r'<[^>]+>', '', traceback_html)
        print("\n--- Traceback ---")
        print(clean_tb[:2000]) # Print first 2000 chars
    else:
        print("Could not find browserTraceback div.")
        # Try to find any pre tags with code
        pre_tags = re.findall(r"<pre>(.*?)<\/pre>", content, re.DOTALL)
        for tag in pre_tags:
            if "File" in tag and "line" in tag:
                print("\n--- Potential Traceback Fragment ---")
                print(tag[:1000])

if __name__ == "__main__":
    extract_traceback()
