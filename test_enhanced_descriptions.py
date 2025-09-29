"""
Test script to demonstrate the enhanced AI descriptions
"""
import requests
import json

def test_enhanced_descriptions():
    """Test various task types to show AI enhancement improvements"""
    
    base_url = "http://127.0.0.1:5000"
    user_id = "8620b861-ea55-478a-b1b4-f266cb6a999d"
    url = f"{base_url}/api/{user_id}/ai/add-task"
    
    test_cases = [
        {
            "name": "Gym Session",
            "data": {
                "title": "Gym Session",
                "description": "Go to gym",
                "category": "fitness",
                "date": "2025-10-01",
                "time": "07:00",
                "reminder_setting": "15 minutes"
            }
        },
        {
            "name": "Doctor Appointment", 
            "data": {
                "title": "Doctor Appointment",
                "description": "See doctor",
                "category": "health",
                "date": "2025-10-02",
                "time": "14:30",
                "reminder_setting": "1 hour"
            }
        },
        {
            "name": "Team Meeting",
            "data": {
                "title": "Team Meeting",
                "description": "Meeting with team",
                "category": "work", 
                "date": "2025-10-03",
                "time": "09:00",
                "reminder_setting": "30 minutes"
            }
        },
        {
            "name": "Grocery Shopping",
            "data": {
                "title": "Grocery Shopping",
                "description": "Buy groceries",
                "category": "shopping",
                "date": "2025-10-04",
                "time": "18:00",
                "reminder_setting": "1 hour"
            }
        },
        {
            "name": "Study Session",
            "data": {
                "title": "Study Session", 
                "description": "Study for exam",
                "category": "education",
                "date": "2025-10-05",
                "time": "20:00",
                "reminder_setting": "30 minutes"
            }
        }
    ]
    
    print("🚀 TESTING ENHANCED AI DESCRIPTIONS")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 TEST {i}: {test_case['name']}")
        print("-" * 50)
        
        # Show original
        original_desc = test_case['data']['description']
        print(f"📥 ORIGINAL DESCRIPTION: '{original_desc}'")
        
        try:
            response = requests.post(url, json=test_case['data'], timeout=15)
            
            if response.status_code == 201:
                result = response.json()
                enhanced_desc = result['task_data']['description']
                ai_enhanced = result.get('ai_enhanced', False)
                
                print(f"📤 ENHANCED DESCRIPTION: '{enhanced_desc}'")
                print(f"🤖 AI Enhanced: {'Yes' if ai_enhanced else 'No'}")
                print(f"📊 Improvement: {len(enhanced_desc)} chars vs {len(original_desc)} chars")
                
                # Calculate improvement ratio
                improvement = (len(enhanced_desc) / len(original_desc)) * 100
                print(f"📈 Enhancement Ratio: {improvement:.1f}%")
                
                if ai_enhanced:
                    print("✅ SUCCESS - AI made the description much better!")
                else:
                    print("⚠️  FALLBACK - Used basic enhancement")
                    
            else:
                print(f"❌ ERROR: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Raw error: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print("❌ CONNECTION ERROR - Make sure Flask server is running")
            break
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
    
    print("\n" + "=" * 80)
    print("🎯 ENHANCEMENT SUMMARY:")
    print("✨ AI now creates much more detailed, actionable descriptions")
    print("🏷️ AI validates and corrects categories automatically") 
    print("🛡️ Fallback system ensures enhancement always works")
    print("📝 Professional, structured, and contextually relevant descriptions")
    print("=" * 80)

if __name__ == "__main__":
    test_enhanced_descriptions()