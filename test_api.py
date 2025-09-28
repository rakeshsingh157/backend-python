import requests
import json

# Test the actual API endpoint
url = "http://127.0.0.1:5001/test-ai"
data = {
    "prompt": "Create a task for tomorrow to buy groceries"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Request Error: {e}")
    try:
        print(f"Response text: {response.text}")
    except:
        print("Could not get response text")