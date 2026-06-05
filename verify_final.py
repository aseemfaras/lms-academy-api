
import requests
import os

BASE_URL = 'http://localhost:8000/api'
EMAIL = 'admin@lms.com'
PASSWORD = 'admin123'

def verify_upload():
    # 1. Login
    print("Logging in...")
    login_url = f"{BASE_URL}/users/login/"
    response = requests.post(login_url, json={"username": EMAIL, "password": PASSWORD})
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 2. Prepare dummy image
    img_path = 'final_test.png'
    with open(img_path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')

    # 3. Create course with image
    print("\nCreating course with image upload (FormData test)...")
    url = f"{BASE_URL}/trainers/courses/"
    data = {
        "title": f"Final Test Course {os.getpid()}",
        "description": "Testing ImageField upload fix"
    }
    with open(img_path, 'rb') as img:
        files = {'image': img}
        # Note: requests sets the correct Content-Type: multipart/form-data with boundary automatically
        response = requests.post(url, data=data, files=files, headers=headers)
    
    print(f"Create status: {response.status_code}")
    if response.status_code in [200, 201]:
        print("Course created successfully.")
    else:
        print(f"Error: {response.json()}")

    # Cleanup
    if os.path.exists(img_path):
        os.remove(img_path)

if __name__ == "__main__":
    verify_upload()
