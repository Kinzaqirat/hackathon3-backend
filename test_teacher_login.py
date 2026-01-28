import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Test teacher login
url = f"{BASE_URL}/api/auth/login/teacher"
login_data = {
    "email": "teachertest@example.com",
    "password": "password123"
}

print(f"Testing teacher login to: {url}")
print(f"Payload: {json.dumps(login_data, indent=2)}")

try:
    response = requests.post(url, json=login_data)
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nLogin successful!")
        print(f"Token: {data.get('access_token')}")
        print(f"User ID: {data.get('user_id')}")
        print(f"Role: {data.get('role')}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
