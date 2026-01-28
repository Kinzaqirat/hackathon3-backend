import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_teacher_login():
    """Test teacher login endpoint"""
    url = f"{BASE_URL}/api/auth/login/teacher"
    
    # Test data
    login_data = {
        "email": "teacher@example.com",
        "password": "password123"
    }
    
    print("Testing teacher login endpoint...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(login_data, indent=2)}")
    
    try:
        # First, try a simple POST request
        response = requests.post(url, json=login_data)
        print(f"POST Response Status: {response.status_code}")
        print(f"POST Response Body: {response.text}")
        
        # Then try an OPTIONS request to see if it's handled properly
        options_response = requests.options(url)
        print(f"OPTIONS Response Status: {options_response.status_code}")
        print(f"OPTIONS Response Headers: {dict(options_response.headers)}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_cors_headers():
    """Check if CORS headers are properly set"""
    url = f"{BASE_URL}/api/auth/login/teacher"
    
    # Send an OPTIONS request to check CORS headers
    headers = {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    print("\nTesting CORS headers...")
    response = requests.options(url, headers=headers)
    print(f"OPTIONS Response Status: {response.status_code}")
    print(f"CORS Headers: {dict(response.headers)}")

if __name__ == "__main__":
    test_teacher_login()
    test_cors_headers()