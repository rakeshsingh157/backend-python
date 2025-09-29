"""
Simple test to check if our endpoint is accessible
"""
import json

try:
    import requests
    
    # Test the specific endpoint with minimal data
    url = "http://127.0.0.1:5000/api/8620b861-ea55-478a-b1b4-f266cb6a999d/ai/add-task"
    
    # Minimal test data
    test_data = {
        "title": "Test Task",
        "description": "Test Description", 
        "category": "test",
        "date": "2025-09-30",
        "time": "09:00",
        "reminder_setting": "15 minutes"
    }
    
    print("Testing AI add-task endpoint...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    
    response = requests.post(url, json=test_data, timeout=10)
    print(f"\nStatus Code: {response.status_code}")
    
    try:
        response_json = response.json()
        print(f"Response: {json.dumps(response_json, indent=2)}")
    except:
        print(f"Raw Response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
    print("\nAlso testing a simple endpoint to see if Flask is running...")
    try:
        simple_response = requests.get("http://127.0.0.1:5000/")
        print(f"Simple GET / status: {simple_response.status_code}")
    except Exception as simple_error:
        print(f"Simple request also failed: {simple_error}")