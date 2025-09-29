#!/usr/bin/env python3
"""
Test AI-powered task deletion functionality
Tests if AI can properly delete tasks when given deletion requests
"""

import requests
import json
from datetime import datetime

def test_ai_deletion_functionality():
    """Test AI deletion with different endpoints and messages"""
    
    print("🤖 TESTING AI DELETION FUNCTIONALITY")
    print("=" * 50)
    
    # Test data for deletion requests
    test_cases = [
        {
            'endpoint': '/api/ai/chat',
            'user_id': '2de79958-cd03-4407-8fa3-fe20bed3660c',  # User with Test AI Meeting tasks
            'message': 'delete my ai assistance task',
            'description': 'AI Chat - Delete AI assistance task'
        },
        {
            'endpoint': '/api/ai/scheduler/chat', 
            'user_id': '2de79958-cd03-4407-8fa3-fe20bed3660c',
            'message': 'cancel my test ai meeting',
            'description': 'AI Scheduler - Cancel AI meeting'
        },
        {
            'endpoint': '/api/ai/chat',
            'user_id': '2de79958-cd03-4407-8fa3-fe20bed3660c',
            'message': 'remove test ai meeting from today',
            'description': 'AI Chat - Remove specific meeting'
        },
        {
            'endpoint': '/api/ai/scheduler/chat',
            'user_id': '8620b861-ea55-478a-b1b4-f266cb6a999d',  # User with Mom's Task
            'message': 'delete mom\'s task',
            'description': 'AI Scheduler - Delete Mom\'s task'
        }
    ]
    
    base_url = 'http://127.0.0.1:5000'
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}: {test_case['description']}")
        print("-" * 30)
        
        try:
            url = f"{base_url}{test_case['endpoint']}"
            data = {
                'message': test_case['message'],
                'user_id': test_case['user_id']
            }
            
            print(f"📤 POST {url}")
            print(f"💬 Message: \"{test_case['message']}\"")
            print(f"👤 User ID: {test_case['user_id']}")
            
            response = requests.post(url, 
                                   headers={'Content-Type': 'application/json'},
                                   json=data,
                                   timeout=30)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS!")
                print(f"🤖 AI Response: {result.get('message', 'No message')}")
                
                # Check if deletion was successful
                if 'deleted' in str(result).lower() or 'removed' in str(result).lower():
                    print("🗑️ DELETION DETECTED!")
                else:
                    print("⚠️ No deletion detected in response")
                    
            else:
                print("❌ FAILED!")
                try:
                    error_data = response.json()
                    print(f"❌ Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"❌ Raw Error: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print("❌ ERROR: Could not connect to Flask server.")
            print("Make sure the Flask app is running on http://127.0.0.1:5000")
            break
        except requests.exceptions.Timeout:
            print("❌ ERROR: Request timed out (30s). AI might be processing too long.")
        except Exception as e:
            print(f"❌ ERROR: {e}")

def test_direct_deletion():
    """Test direct task deletion using DELETE endpoint"""
    
    print(f"\n🔧 TESTING DIRECT DELETION")
    print("=" * 30)
    
    # Test deleting one of the Test AI Meeting tasks (ID 27)
    user_id = '2de79958-cd03-4407-8fa3-fe20bed3660c'
    task_id = 27
    
    try:
        url = f'http://127.0.0.1:5000/api/{user_id}/task/{task_id}'
        print(f"📤 DELETE {url}")
        
        response = requests.delete(url, timeout=10)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ DIRECT DELETION SUCCESS!")
            print(f"📝 Message: {result.get('message', 'No message')}")
        else:
            print("❌ DIRECT DELETION FAILED!")
            try:
                error_data = response.json()
                print(f"❌ Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"❌ Raw Error: {response.text}")
                
    except Exception as e:
        print(f"❌ Direct deletion error: {e}")

def provide_solutions():
    """Provide solutions for AI deletion issues"""
    
    print(f"\n💡 SOLUTIONS FOR AI DELETION ISSUES")
    print("=" * 40)
    
    print("🔧 If AI deletion is not working, try these solutions:")
    print()
    print("1. ✅ USE SPECIFIC LANGUAGE:")
    print("   • 'delete my test ai meeting'")
    print("   • 'cancel the ai assistance task'") 
    print("   • 'remove all ai tasks from today'")
    print()
    print("2. ✅ TRY DIFFERENT ENDPOINTS:")
    print("   • POST /api/ai/chat")
    print("   • POST /api/ai/scheduler/chat")
    print()
    print("3. ✅ USE DIRECT DELETION:")
    print("   • DELETE /api/{user_id}/task/{task_id}")
    print("   • First get task ID, then delete directly")
    print()
    print("4. ✅ CHECK AI SERVICE STATUS:")
    print("   • Groq API might be down")
    print("   • Gemini API might be rate limited")
    print("   • Check .env file for API keys")
    print()
    print("5. ✅ DEBUG STEPS:")
    print("   • Check server logs for AI errors")
    print("   • Verify task exists in database") 
    print("   • Test with different user IDs")

if __name__ == "__main__":
    print(f"🚀 Starting AI Deletion Tests at {datetime.now()}")
    print()
    
    # Test AI-powered deletion
    test_ai_deletion_functionality()
    
    # Test direct deletion 
    test_direct_deletion()
    
    # Provide solutions
    provide_solutions()
    
    print("\n✅ All tests complete!")