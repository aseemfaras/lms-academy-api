import urllib.request
import urllib.error

url = "http://localhost:8000/api/users/"
# This looks like a JWT but is invalid
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
    "Origin": "http://localhost:5177",
    "Referer": "http://localhost:5177/",
}
req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.getcode()}")
        print(f"Headers: {dict(response.info())}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Headers: {dict(e.info())}")
    print(f"Body: {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
