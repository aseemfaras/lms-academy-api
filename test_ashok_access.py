import requests

BASE_URL = 'http://localhost:8000/api'
EMAIL = 'ashok@gmail.com'
PASSWORD = 'admin123'

def test_course_access():
    # Login
    print(f"Logging in as {EMAIL}...")
    response = requests.post(f"{BASE_URL}/users/login/", json={"username": EMAIL, "password": PASSWORD})
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json()['access']
    user_id = response.json()['user']['id']
    headers = {"Authorization": f"Bearer {token}"}

    # Get enrollments
    print(f"\nFetching enrollments for user {user_id}...")
    response = requests.get(f"{BASE_URL}/students/enrollments/?student={user_id}", headers=headers)
    
    if response.status_code != 200:
        print(f"Failed: {response.status_code} - {response.text[:200]}")
        return
        
    enrollments = response.json()
    print(f"✓ Found {len(enrollments)} enrollment(s)")
    
    for enrollment in enrollments:
        course = enrollment.get('course')
        if isinstance(course, dict):
            course_id = course['id']
            course_title = course['title']
            print(f"\n✓ Enrolled in: Course {course_id} - {course_title}")
            
            # Try to access the course detail
            print(f"  Testing course detail API...")
            course_response = requests.get(f"{BASE_URL}/courses/{course_id}/", headers=headers)
            if course_response.status_code == 200:
                print(f"  ✓ Course detail accessible (200 OK)")
            else:
                print(f"  ✗ Course detail failed: {course_response.status_code}")
        else:
            print(f"\n⚠ Enrollment {enrollment['id']}: Course not nested (got {type(course)})")

if __name__ == "__main__":
    test_course_access()
