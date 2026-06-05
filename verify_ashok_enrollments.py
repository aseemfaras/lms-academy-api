import requests

BASE_URL = 'http://localhost:8000/api'
EMAIL = 'ashok@gmail.com'
PASSWORD = 'admin123'

def check_user_courses():
    # Login
    print(f"Logging in as {EMAIL}...")
    login_url = f"{BASE_URL}/users/login/"
    response = requests.post(login_url, json={"username": EMAIL, "password": PASSWORD})
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json()['access']
    user_id = response.json()['user']['id']
    headers = {"Authorization": f"Bearer {token}"}

    # Get enrollments
    print(f"Fetching enrollments for user {user_id}...")
    enroll_url = f"{BASE_URL}/students/enrollments/?student={user_id}"
    response = requests.get(enroll_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch enrollments: {response.status_code} - {response.text}")
        return
        
    enrollments = response.json()
    print(f"Found {len(enrollments)} enrollment(s)")
    
    for enrollment in enrollments:
        course = enrollment.get('course')
        if isinstance(course, dict):
            course_id = course['id']
            course_title = course['title']
        else:
            course_id = course
            course_title = f"ID {course_id}"
            
        print(f"\nEnrollment {enrollment['id']}: Course {course_id} ({course_title})")
        
        # Try to access the course detail
        course_url = f"{BASE_URL}/courses/{course_id}/"
        course_response = requests.get(course_url, headers=headers)
        print(f"  Course detail API: {course_response.status_code}")
        if course_response.status_code != 200:
            print(f"  Error: {course_response.text[:200]}")

if __name__ == "__main__":
    check_user_courses()
