"""
Test script for AI Generate Schedule with Intelligent Reminder Settings
"""
import requests
import json

def test_ai_generate_schedule():
    """Test the AI generate schedule endpoint with various prompts"""
    
    base_url = "http://127.0.0.1:5000"
    user_id = "8620b861-ea55-478a-b1b4-f266cb6a999d"
    url = f"{base_url}/api/{user_id}/ai/generate-schedule"
    
    test_prompts = [
        {
            "name": "Medical Appointments",
            "prompt": "I need to schedule a doctor appointment for next week and a dentist cleaning"
        },
        {
            "name": "Work Schedule", 
            "prompt": "Schedule team meeting tomorrow at 10am, important client presentation on Friday, and project deadline review"
        },
        {
            "name": "Fitness Routine",
            "prompt": "Plan my gym sessions for this week - cardio on Monday, strength training Wednesday, yoga Friday"
        },
        {
            "name": "Travel Planning",
            "prompt": "I have a flight to Mumbai next Monday at 2pm, need to pack the night before"
        },
        {
            "name": "Mixed Activities",
            "prompt": "Schedule grocery shopping tomorrow, dinner with friends on Saturday, and study session for exam on Sunday"
        },
        {
            "name": "Urgent Tasks",
            "prompt": "Important job interview on Thursday at 11am, bank appointment to discuss loan, car service urgent repair"
        }
    ]
    
    print("🤖 TESTING AI GENERATE SCHEDULE WITH INTELLIGENT REMINDERS")
    print("=" * 80)
    print("🎯 The AI will automatically generate appropriate reminder_setting values!")
    print("=" * 80)
    
    for i, test_case in enumerate(test_prompts, 1):
        print(f"\n📝 TEST {i}: {test_case['name']}")
        print("-" * 60)
        print(f"📥 PROMPT: '{test_case['prompt']}'")
        
        try:
            response = requests.post(url, json={"prompt": test_case['prompt']}, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success') and 'tasks' in result:
                    tasks = result['tasks']
                    print(f"✅ SUCCESS - Generated {len(tasks)} task(s)")
                    print()
                    
                    for j, task in enumerate(tasks, 1):
                        print(f"   🔹 TASK {j}:")
                        print(f"      📋 Title: {task.get('title', 'N/A')}")
                        print(f"      📝 Description: {task.get('description', 'N/A')}")
                        print(f"      🏷️ Category: {task.get('category', 'N/A')}")
                        print(f"      📅 Date: {task.get('date', 'N/A')}")
                        print(f"      ⏰ Time: {task.get('time', 'N/A')}")
                        
                        # Highlight the AI-generated reminder setting
                        reminder = task.get('reminder_setting', 'Not set')
                        print(f"      🔔 AI Smart Reminder: {reminder}")
                        
                        # Show why this reminder was chosen
                        category = task.get('category', '').lower()
                        title_lower = task.get('title', '').lower()
                        
                        reason = get_reminder_reason(title_lower, category, reminder)
                        print(f"      💡 Why this reminder: {reason}")
                        print()
                        
                else:
                    print("❌ ERROR - No tasks generated")
                    print(f"Response: {json.dumps(result, indent=2)}")
                    
            else:
                print(f"❌ HTTP ERROR: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Raw error: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print("❌ CONNECTION ERROR - Make sure Flask server is running")
            break
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
    
    print("\n" + "=" * 80)
    print("🎯 AI REMINDER INTELLIGENCE SUMMARY:")
    print("✨ Medical appointments → 2 hours (preparation/travel time)")
    print("💼 Work meetings → 1 hour (standard business reminder)")  
    print("🏋️ Gym/fitness → 30 minutes (time to change/prepare)")
    print("✈️ Travel/flights → 4 hours (critical timing)")
    print("📚 Study/education → 30 minutes (prepare materials)")
    print("🛍️ Shopping → 1 hour (plan route/list)")
    print("👥 Social events → 1 hour (prepare/travel)")
    print("🔧 Repairs/maintenance → 2 hours (arrange time/materials)")
    print("💰 Finance/banking → 1 hour (gather documents)")
    print("📱 Personal tasks → 15 minutes (quick reminder)")
    print("🚨 Urgent/critical → 1 day (maximum advance notice)")
    print("=" * 80)

def get_reminder_reason(title, category, reminder):
    """Explain why a specific reminder was chosen"""
    if '1 day' in reminder or '4 hours' in reminder:
        return "Critical/important event needs advance planning"
    elif '2 hours' in reminder:
        if 'health' in category or any(word in title for word in ['doctor', 'dentist']):
            return "Medical appointments need preparation and travel time"
        else:
            return "Important task requiring significant preparation"
    elif '1 hour' in reminder:
        if 'work' in category:
            return "Standard business meeting reminder"
        else:
            return "Adequate time for preparation and travel"
    elif '30 minutes' in reminder:
        if 'fitness' in category:
            return "Time to change clothes and prepare for workout"
        else:
            return "Quick preparation for learning/education activity"
    else:
        return "Standard reminder for routine personal tasks"

if __name__ == "__main__":
    test_ai_generate_schedule()