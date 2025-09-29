"""
Test script for the AI ADD TASK endpoint
"""
import requests
import json

# Test data matching your example
test_data = {
    "user_id": "8620b861-ea55-478a-b1b4-f266cb6a999d",
    "title": "Gym Session",
    "description": "Scheduled gym session at the gym",
    "category": "fitness",
    "date": "2025-09-30",
    "time": "07:00",
    "done": False,
    "reminder_setting": "15 minutes"
}

def test_ai_add_task():
    url = "http://127.0.0.1:5000/api/8620b861-ea55-478a-b1b4-f266cb6a999d/ai/add-task"
    
    try:
        response = requests.post(url, json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ Test PASSED - Task created successfully!")
            
            # Check if reminder_datetime was calculated correctly
            response_data = response.json()
            if 'task_data' in response_data and 'reminder_datetime' in response_data['task_data']:
                reminder_dt = response_data['task_data']['reminder_datetime']
                print(f"📅 Generated reminder datetime: {reminder_dt}")
                print("Expected: 2025-09-30 06:45:00 (15 minutes before 07:00)")
        else:
            print("❌ Test FAILED")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - Make sure your Flask server is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Test Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing AI ADD TASK endpoint...")
    test_ai_add_task()