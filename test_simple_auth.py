import subprocess
import time
import requests
import threading

def start_server():
    # Start the server
    process = subprocess.Popen(['python', 'main.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Wait for server to start
    time.sleep(8)
    return process

def test_simple_auth():
    time.sleep(3)  # Give some extra time
    
    print("=== Testing Super Simple Authentication ===")
    
    # Test health
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        print(f"[OK] Health: {response.status_code}, {response.json()}")
    except Exception as e:
        print(f"[FAIL] Health check failed: {e}")
        return

    # Test registration
    try:
        response = requests.post('http://localhost:8000/api/auth/register',
                                json={
                                    "email": "simpleuser@example.com",
                                    "name": "Simple User",
                                    "password": "simplepass",
                                    "grade_level": "Beginner"
                                },
                                timeout=10)
        print(f"[OK] Registration: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"  User created: {user_data['name']} ({user_data['email']})")
    except Exception as e:
        print(f"[FAIL] Registration failed: {e}")
        return

    # Test login
    try:
        response = requests.post('http://localhost:8000/api/auth/login',
                                json={
                                    "email": "simpleuser@example.com",
                                    "password": "simplepass"
                                },
                                timeout=10)
        print(f"[OK] Login: {response.status_code}")
        if response.status_code == 200:
            login_data = response.json()
            print(f"  Logged in user: {login_data['email']}, ID: {login_data['user_id']}")
            print(f"  Access token: {login_data['access_token']}")
    except Exception as e:
        print(f"[FAIL] Login failed: {e}")

if __name__ == "__main__":
    print("Starting server...")
    # Start server in background
    server_process = start_server()
    
    print("Waiting for server to start...")
    # Test endpoints after a delay
    test_simple_auth()
    
    # Terminate server
    server_process.terminate()
    print("\nDone!")