"""
Simple script to call the seed endpoint
"""
import urllib.request
import json

try:
    # Call the seed endpoint
    req = urllib.request.Request(
        'http://localhost:8000/seed',
        method='POST'
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print(f"[SUCCESS] {result['message']}")
        print("\nNow refresh your browser at http://localhost:3000 to see the content!")
        
except urllib.error.HTTPError as e:
    error_body = e.read().decode()
    print(f"[ERROR] Error: {error_body}")
except Exception as e:
    print(f"[ERROR] Error: {str(e)}")
