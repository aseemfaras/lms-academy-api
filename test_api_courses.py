import urllib.request
import json

def test_courses_api():
    # 1. Test Courses
    url_courses = "http://localhost:8000/api/courses/"
    print(f"Testing GET {url_courses}...")
    try:
        urllib.request.urlopen(url_courses)
    except urllib.error.HTTPError as e:
        print(f"Status: {e.code} ({'OK' if e.code == 401 else 'FAILED'})")

    # 2. Test Modules
    url_modules = "http://localhost:8000/api/modules/"
    print(f"Testing GET {url_modules}...")
    try:
        urllib.request.urlopen(url_modules)
    except urllib.error.HTTPError as e:
        print(f"Status: {e.code} ({'OK' if e.code == 401 else 'FAILED'})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_courses_api()
