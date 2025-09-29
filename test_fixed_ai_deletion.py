#!/usr/bin/env python3
"""
Test AI deletion after fixing timeout issues
"""

import requests
import json
from datetime import datetime

def test_fixed_ai_deletion():
    """Test AI deletion with the fixed model priority"""
    
    print("🔧 TESTING FIXED AI DELETION")
    print("=" * 30)
    
    # Test case for AI assistance deletion
    test_data = {
        'message': 'delete ai assistance task',
        'user_id': '8620b861-ea55-478a-b1b4-f266cb6a999d'  # User with Mom's Task
    }
    
    endpoints_to_test = [
        '/api/ai/test',  # No auth endpoint (faster)
        '/api/ai/scheduler/test'  # Scheduler test endpoint
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n📤 Testing: {endpoint}")
        
        try:
            url = f'http://127.0.0.1:5000{endpoint}'
            print(f"🌐 POST {url}")
            print(f"💬 Message: '{test_data['message']}'")
            
            response = requests.post(url,
                                   headers={'Content-Type': 'application/json'},
                                   json=test_data,
                                   timeout=15)  # Shorter timeout
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS!")
                print(f"🤖 AI Response: {result.get('message', 'No message')}")
                
                # Check for deletion
                response_text = str(result).lower()
                if 'deleted' in response_text or 'removed' in response_text or 'cancel' in response_text:
                    print("🗑️ DELETION DETECTED!")
                    return True
                else:
                    print("ℹ️ Response received but no deletion detected")
            else:
                print(f"❌ FAILED with status {response.status_code}")
                try:
                    error = response.json()
                    print(f"❌ Error: {error}")
                except:
                    print(f"❌ Raw error: {response.text}")
                    
        except requests.exceptions.Timeout:
            print("❌ Still timing out after fixes")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False

def create_test_ai_task():
    """Create a test AI assistance task to delete"""
    
    print(f"\n➕ CREATING TEST AI ASSISTANCE TASK")
    print("-" * 35)
    
    try:
        url = 'http://127.0.0.1:5000/api/test-user-999/ai/add-task'
        
        task_data = {
            'title': 'AI Assistance Task',
            'description': 'Test AI assistance task for deletion testing',
            'category': 'work',
            'date': '2025-09-30',
            'time': '10:00'
        }
        
        print(f"📤 POST {url}")
        print(f"📋 Task: {task_data['title']}")
        
        response = requests.post(url,
                               headers={'Content-Type': 'application/json'},
                               json=task_data,
                               timeout=10)
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Test AI task created successfully!")
            print(f"🆔 Task ID: {result.get('task_id', 'Unknown')}")
            return result.get('task_id')
        else:
            print(f"❌ Failed to create test task: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error creating test task: {e}")
    
    return None

def test_deletion_with_created_task(task_id):
    """Test deletion with the newly created task"""
    
    print(f"\n🗑️ TESTING DELETION OF CREATED TASK")
    print("-" * 35)
    
    try:
        # Try AI deletion
        test_data = {
            'message': 'delete my ai assistance task',
            'user_id': 'test-user-999'
        }
        
        url = 'http://127.0.0.1:5000/api/ai/test'
        response = requests.post(url,
                               headers={'Content-Type': 'application/json'},
                               json=test_data,
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI deletion request processed!")
            print(f"🤖 Response: {result.get('message', 'No message')}")
            
            if 'deleted' in str(result).lower():
                print("🎉 DELETION SUCCESSFUL!")
                return True
        
        # If AI deletion didn't work, try direct deletion
        print("\n🔧 Trying direct deletion as fallback...")
        delete_url = f'http://127.0.0.1:5000/api/test-user-999/task/{task_id}'
        delete_response = requests.delete(delete_url, timeout=5)
        
        if delete_response.status_code == 200:
            print("✅ Direct deletion successful!")
            return True
        else:
            print(f"❌ Direct deletion failed: {delete_response.status_code}")
            
    except Exception as e:
        print(f"❌ Deletion test error: {e}")
    
    return False

if __name__ == "__main__":
    print(f"🚀 Testing Fixed AI Deletion at {datetime.now()}")
    print()
    
    # Test 1: Try deletion with existing tasks
    deletion_worked = test_fixed_ai_deletion()
    
    # Test 2: Create and delete a specific AI task
    if not deletion_worked:
        print("\n🔄 Testing with newly created task...")
        task_id = create_test_ai_task()
        if task_id:
            test_deletion_with_created_task(task_id)
    
    print(f"\n✅ AI Deletion Testing Complete!")
    print()
    print("💡 If deletion is still not working:")
    print("1. Check server logs for AI errors")
    print("2. Verify API keys are valid") 
    print("3. Use direct DELETE endpoint as fallback")
    print("4. Try shorter/simpler deletion messages")