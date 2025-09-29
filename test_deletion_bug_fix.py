#!/usr/bin/env python3
"""
Test AI Deletion After Bug Fix
"""

import requests
import json

def test_deletion_fix():
    """Test the fixed AI deletion functionality"""
    
    BASE_URL = "http://localhost:5000"
    TEST_ENDPOINT = f"{BASE_URL}/api/ai/test"
    
    print("🚀 Testing AI Deletion After Bug Fix")
    print("=" * 50)
    
    # Test with the exact same message from your logs
    test_cases = [
        {
            "name": "Delete that (from logs)",
            "message": "delete that",
            "user_id": "8620b861-ea55-478a-b1b4-f266cb6a999d"  # Using the UUID from your logs
        },
        {
            "name": "Simple deletion",
            "message": "delete my task", 
            "user_id": 1
        },
        {
            "name": "Cancel meeting",
            "message": "cancel meeting",
            "user_id": 1
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test['name']}")
        print(f"📝 Message: '{test['message']}'")
        
        try:
            response = requests.post(TEST_ENDPOINT, 
                json={
                    "message": test["message"],
                    "user_id": test["user_id"]
                },
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            print(f"🌐 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {data.get('success', False)}")
                message = data.get('message', '')
                print(f"📄 Message: {message}")
                
                if 'deleted' in message.lower():
                    print("🎉 DELETION SUCCESSFUL!")
                elif 'no events found' in message.lower():
                    print("⚠️  No events to delete (create some first)")
                elif 'error' in message.lower():
                    print(f"❌ Error in deletion: {message}")
                else:
                    print("❓ Unclear result")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Start your Flask server first")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 Bug Fixes Applied:")
    print("1. ✅ Fixed 're' module reference error")
    print("2. ✅ Added proper error handling in regex fallback")
    print("3. ✅ Fixed missing return statement in conflict detection")
    print("\n💡 If deletion still fails, check:")
    print("- Database has events to delete")
    print("- User ID exists in database")
    print("- AI services are responding")

if __name__ == "__main__":
    test_deletion_fix()