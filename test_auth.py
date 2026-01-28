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

def test_endpoints():
    time.sleep(3)  # Give some extra time
    
    # Test health
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        print(f"Health: {response.status_code}, {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test registration
    try:
        response = requests.post('http://localhost:8000/api/auth/register', 
                                json={
                                    "email": "testuser4@example.com",
                                    "name": "Test User 4", 
                                    "password": "password123",
                                    "grade_level": "Beginner"
                                }, 
                                timeout=10)
        print(f"Registration: {response.status_code}, {response.json()}")
    except Exception as e:
        print(f"Registration failed: {e}")

if __name__ == "__main__":
    # Start server in background
    server_process = start_server()
    
    # Test endpoints after a delay
    test_thread = threading.Thread(target=test_endpoints)
    test_thread.start()
    test_thread.join()
    
    # Terminate server
    server_process.terminate()