import os
import django
import requests
import json

def reproduce_error():
    url = "http://127.0.0.1:8000/api/users/login/"
    data = {
        "email": "admin@lms.com",
        "password": "admin123"
    }
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    reproduce_error()
