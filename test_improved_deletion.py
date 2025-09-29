#!/usr/bin/env python3
"""
Test the improved AI deletion JSON parsing
"""

import requests
import json
import time

def test_improved_json_parsing():
    """Test the improved JSON parsing for AI deletion"""
    
    print("🔧 TESTING IMPROVED JSON PARSING")
    print("=" * 35)
    
    # Wait for server to be ready
    time.sleep(2)
    
    try:
        # Test deletion with a message that should find multiple tasks
        test_data = {
            'message': 'delete all my tasks',  # This might trigger multiple deletions
            'user_id': '8620b861-ea55-478a-b1b4-f266cb6a999d'
        }
        
        print(f"💬 Testing message: '{test_data['message']}'")
        print(f"👤 User ID: {test_data['user_id']}")
        
        url = 'http://127.0.0.1:5000/api/ai/test'
        response = requests.post(url,
                               headers={'Content-Type': 'application/json'},
                               json=test_data,
                               timeout=12)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RESPONSE RECEIVED!")
            print(f"📝 Full Response:")
            print(json.dumps(result, indent=2))
            
            # Check for success indicators
            if result.get('success'):
                print("🎉 SUCCESS FLAG SET!")
            
            # Check for deletion message
            message = result.get('message', '')
            if 'deleted' in message.lower():
                print("🗑️ DELETION SUCCESSFUL!")
            elif 'no events found' in message.lower():
                print("ℹ️ No tasks found to delete (expected if no tasks exist)")
            else:
                print("⚠️ Unclear deletion status")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw error response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask is running.")
    except requests.exceptions.Timeout:
        print("❌ Request timed out. This might still be a JSON parsing issue.")
    except Exception as e:
        print(f"❌ Test error: {e}")

def test_specific_task_deletion():
    """Test deletion of a specific task type"""
    
    print(f"\n🎯 TESTING SPECIFIC TASK DELETION")
    print("-" * 35)
    
    try:
        # Test deletion of meeting tasks specifically
        test_data = {
            'message': 'delete meeting tasks',
            'user_id': '8620b861-ea55-478a-b1b4-f266cb6a999d'
        }
        
        print(f"💬 Testing: '{test_data['message']}'")
        
        url = 'http://127.0.0.1:5000/api/ai/scheduler/test'  # Try scheduler endpoint
        response = requests.post(url,
                               headers={'Content-Type': 'application/json'},
                               json=test_data,
                               timeout=10)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SCHEDULER ENDPOINT WORKING!")
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Scheduler test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Specific deletion test error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Improved AI Deletion JSON Parsing")
    print()
    
    test_improved_json_parsing()
    test_specific_task_deletion()
    
    print(f"\n✅ Testing Complete!")
    print()
    print("💡 Summary of fixes applied:")
    print("1. ✅ Fixed all gemini-1.5-flash → gemini-pro")
    print("2. ✅ Removed system_instruction parameter issues") 
    print("3. ✅ Added robust JSON parsing with regex fallback")
    print("4. ✅ Improved AI prompts for better JSON formatting")
    print("5. ✅ Added comma/bracket fixing for malformed JSON")