import subprocess
import time
import requests
import threading
import sys

def start_server_with_logging():
    # Start the server with output to file
    with open('detailed_server_log.txt', 'w') as log_file:
        process = subprocess.Popen(['python', 'main.py'], 
                                 stdout=log_file, 
                                 stderr=log_file,
                                 text=True)
        # Wait for server to start
        time.sleep(8)
        return process

def test_registration():
    time.sleep(3)  # Give some extra time
    
    # Test registration
    try:
        response = requests.post('http://localhost:8000/api/auth/register', 
                                json={
                                    "email": "testuser5@example.com",
                                    "name": "Test User 5", 
                                    "password": "password123",
                                    "grade_level": "Beginner"
                                }, 
                                timeout=10)
        print(f"Registration: {response.status_code}, {response.json()}")
        
        # Also try login to see if user was created
        if response.status_code == 500:
            print("Trying login to see if user was created despite error...")
            login_response = requests.post('http://localhost:8000/api/auth/login', 
                                         json={
                                             "email": "testuser5@example.com",
                                             "password": "password123"
                                         }, 
                                         timeout=10)
            print(f"Login: {login_response.status_code}, {login_response.json()}")
    except Exception as e:
        print(f"Registration failed: {e}")

if __name__ == "__main__":
    print("Starting server...")
    # Start server in background with logging
    server_process = start_server_with_logging()
    
    print("Waiting for server to start...")
    # Test registration after a delay
    test_thread = threading.Thread(target=test_registration)
    test_thread.start()
    test_thread.join()
    
    print("Terminating server...")
    # Terminate server
    server_process.terminate()
    
    print("Checking server logs...")
    try:
        with open('detailed_server_log.txt', 'r') as f:
            logs = f.read()
            print("\nServer Logs:")
            print(logs[-2000:])  # Print last 2000 chars of logs
    except Exception as e:
        print(f"Could not read logs: {e}")