import urllib.request
import urllib.error

url = "http://localhost:8000/api/courses/"
try:
    with urllib.request.urlopen(url) as response:
        print(f"Status Code: {response.getcode()}")
        print(f"Response Body: {response.read().decode()[:500]}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Reason: {e.reason}")
    print(f"Body: {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
