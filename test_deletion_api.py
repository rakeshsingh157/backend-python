#!/usr/bin/env python3
"""
Simple AI Deletion Test - Test the actual API endpoint
"""

import requests
import json
import sys

def test_ai_deletion_api():
    """Test the AI deletion via the actual API"""
    
    # Configuration
    BASE_URL = "http://localhost:5000"  # Adjust if your server runs on different port
    TEST_ENDPOINT = f"{BASE_URL}/api/ai/test"
    
    print("🚀 Testing AI Deletion API")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Simple task deletion",
            "message": "delete my task",
            "user_id": 1
        },
        {
            "name": "AI assistance deletion", 
            "message": "delete ai_assistance",
            "user_id": 1
        },
        {
            "name": "Cancel meeting",
            "message": "cancel my meeting", 
            "user_id": 1
        },
        {
            "name": "Remove task",
            "message": "remove my task",
            "user_id": 1
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test['name']}")
        print(f"📝 Message: '{test['message']}'")
        
        try:
            # Make API request
            response = requests.post(TEST_ENDPOINT, 
                json={
                    "message": test["message"],
                    "user_id": test["user_id"]
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"🌐 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {data.get('success', False)}")
                print(f"📄 Message: {data.get('message', 'No message')}")
                
                # Check for deletion indicators
                message_text = data.get('message', '').lower()
                if 'deleted' in message_text or 'successfully' in message_text:
                    print("🎉 DELETION WORKED!")
                elif 'no events found' in message_text:
                    print("⚠️  No events to delete (this might be normal)")
                elif 'ai determined' in message_text:
                    print("❌ AI didn't detect deletion request")
                    print(f"🔍 AI Response: {data.get('message')}")
                else:
                    print("❓ Unclear deletion result")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"📄 Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"📄 Raw Response: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Is your Flask server running?")
            print("🔧 Try: python app.py (in your backend directory)")
            
        except requests.exceptions.Timeout:
            print("❌ Timeout: Request took too long (AI services might be slow)")
            
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 If deletion isn't working:")
    print("1. Make sure your Flask server is running")
    print("2. Check if you have events in your database to delete") 
    print("3. Verify your AI API keys (GROQ_API_KEY, COHERE_API_KEY, GOOGLE_GEMINI_API_KEY)")
    print("4. Check server console for error messages")

if __name__ == "__main__":
    test_ai_deletion_api()