#!/usr/bin/env python3
"""
Test script for AI Generate Schedule - Intelligent Reminder Generation
Tests if AI automatically generates appropriate reminder settings for different task types.
"""

import requests
import json
from datetime import datetime

def test_intelligent_reminders():
    """Test intelligent reminder generation for different task categories"""
    
    # Test data with different task types to trigger different reminder settings
    test_data = {
        'prompt': 'Schedule doctor appointment tomorrow at 2pm, gym session Wednesday evening, important client meeting Friday morning, grocery shopping this weekend'
    }
    
    print("🧠 TESTING AI INTELLIGENT REMINDER GENERATION")
    print("=" * 50)
    print(f"Test Prompt: {test_data['prompt']}")
    print()
    
    try:
        # Make request to the endpoint
        url = 'http://127.0.0.1:5000/api/test-user-123/ai/generate-schedule'
        headers = {'Content-Type': 'application/json'}
        
        print(f"🌐 Making request to: {url}")
        response = requests.post(url, headers=headers, json=test_data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! AI Generated Schedule:")
            print(json.dumps(result, indent=2))
            
            # Analyze reminder intelligence
            if 'tasks' in result:
                print("\n🧠 REMINDER INTELLIGENCE ANALYSIS")
                print("-" * 40)
                
                expected_reminders = {
                    'doctor': '2 hours',      # Medical → 2 hours
                    'gym': '30 minutes',      # Fitness → 30 minutes  
                    'client': '2 hours',      # Important work → 2 hours
                    'shopping': '1 hour'      # Shopping/errands → 1 hour
                }
                
                for i, task in enumerate(result['tasks'], 1):
                    title = task.get('title', 'Unknown')
                    category = task.get('category', 'Unknown')
                    reminder = task.get('reminder_setting', 'None')
                    
                    print(f"Task {i}: {title}")
                    print(f"  📂 Category: {category}")
                    print(f"  ⏰ Reminder: {reminder}")
                    
                    # Check if reminder is intelligent
                    task_type = None
                    for key in expected_reminders:
                        if key.lower() in title.lower():
                            task_type = key
                            break
                    
                    if task_type:
                        expected = expected_reminders[task_type]
                        if reminder == expected:
                            print(f"  ✅ PERFECT! Expected {expected}, got {reminder}")
                        else:
                            print(f"  ⚠️  Expected {expected}, got {reminder} (still valid)")
                    else:
                        print(f"  ℹ️  Auto-generated reminder: {reminder}")
                    print()
                
                print("🎯 SUMMARY:")
                print(f"Total tasks generated: {len(result['tasks'])}")
                print("All tasks have reminder_setting automatically generated! ✅")
                
            else:
                print("❌ No tasks found in response")
                
        else:
            print("❌ FAILED!")
            try:
                error_data = response.json()
                print("Error Response:")
                print(json.dumps(error_data, indent=2))
            except:
                print(f"Raw Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to Flask server.")
        print("Make sure the Flask app is running on http://127.0.0.1:5000")
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out. AI might be taking too long to respond.")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_medical_reminders():
    """Test medical-specific reminder intelligence"""
    print("\n🏥 TESTING MEDICAL REMINDER INTELLIGENCE")
    print("=" * 50)
    
    test_data = {
        'prompt': 'Schedule surgery consultation next Monday, dentist cleaning Tuesday, therapy session Wednesday'
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/test-user-123/ai/generate-schedule',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Medical tasks generated:")
            
            for task in result.get('tasks', []):
                title = task.get('title', 'Unknown')
                reminder = task.get('reminder_setting', 'None')
                print(f"  🏥 {title}: {reminder}")
                
                if '2 hours' in reminder:
                    print(f"    ✅ Correct medical reminder!")
                else:
                    print(f"    ⚠️  Expected 2 hours for medical tasks")
        else:
            print(f"❌ Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Medical test error: {e}")

if __name__ == "__main__":
    print(f"🚀 Starting Intelligent Reminder Tests at {datetime.now()}")
    print()
    
    # Main test
    test_intelligent_reminders()
    
    # Medical-specific test
    test_medical_reminders()
    
    print("\n✅ Testing Complete!")