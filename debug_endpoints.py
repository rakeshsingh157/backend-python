"""
Debug script to test different endpoints and identify the source of the error
"""
import requests
import json

def test_endpoint(url, data, description):
    """Test a single endpoint with given data"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Raw Response: {response.text}")
            
        if response.status_code == 200 or response.status_code == 201:
            print("✅ SUCCESS")
        else:
            print("❌ ERROR")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Server might not be running")
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

def main():
    base_url = "http://127.0.0.1:5000"
    user_id = "8620b861-ea55-478a-b1b4-f266cb6a999d"
    
    # Test data with all required fields
    complete_data = {
        "title": "Debug Test Task",
        "description": "Testing endpoint to debug error",
        "category": "test",
        "date": "2025-10-01",
        "time": "10:00",
        "reminder_setting": "15 minutes"
    }
    
    # Test data with missing fields
    incomplete_data = {
        "title": "Incomplete Task"
    }
    
    print("🔍 ENDPOINT DEBUGGING SCRIPT")
    print("This script will test different endpoints to identify the error source")
    
    # Test 1: Our AI Add Task endpoint with complete data
    test_endpoint(
        f"{base_url}/api/{user_id}/ai/add-task",
        complete_data,
        "AI Add Task - Complete Data"
    )
    
    # Test 2: Our AI Add Task endpoint with incomplete data
    test_endpoint(
        f"{base_url}/api/{user_id}/ai/add-task", 
        incomplete_data,
        "AI Add Task - Missing Fields (Expected Error)"
    )
    
    # Test 3: Regular tasks endpoint with complete data
    test_endpoint(
        f"{base_url}/api/{user_id}/tasks/add",
        complete_data,
        "Regular Tasks Add - Complete Data"
    )
    
    # Test 4: Regular tasks endpoint with incomplete data
    test_endpoint(
        f"{base_url}/api/{user_id}/tasks/add",
        incomplete_data,
        "Regular Tasks Add - Missing Fields"
    )
    
    # Test 5: Check if server is running
    print(f"\n{'='*60}")
    print("Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Server is running - Status: {response.status_code}")
    except:
        print("❌ Server connection failed")
    
    print(f"\n{'='*60}")
    print("DEBUGGING COMPLETE")
    print("Check the results above to identify which endpoint is causing the error.")
    print("Look for the exact error message you're seeing to identify the source.")

if __name__ == "__main__":
    main()