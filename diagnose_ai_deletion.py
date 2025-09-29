#!/usr/bin/env python3
"""
AI Deletion Diagnostic Script - Comprehensive Testing
"""

import json
import re
from datetime import datetime

def test_deletion_detection():
    """Test the deletion keyword detection logic"""
    
    print("🔍 Testing Deletion Keyword Detection")
    print("=" * 50)
    
    # Test messages that should trigger deletion
    deletion_messages = [
        "delete my task",
        "cancel my meeting", 
        "remove ai assistance",
        "delete ai_assistance task",
        "cancel all my events",
        "remove my appointment",
        "delete the gym session",
        "cancel today's meeting",
        "remove all tasks",
        "clear my schedule"
    ]
    
    # Simulate the detection logic from your code
    for message in deletion_messages:
        message_lower = message.lower()
        
        # Check for deletion keywords
        deletion_keywords = ['cancel', 'delete', 'remove', 'clear']
        has_deletion_keyword = any(keyword in message_lower for keyword in deletion_keywords)
        
        print(f"📝 Message: '{message}'")
        print(f"🎯 Has deletion keyword: {has_deletion_keyword}")
        
        if has_deletion_keyword:
            print("✅ Should trigger DELETE_EVENTS")
        else:
            print("❌ Might not trigger DELETE_EVENTS")
        print()

def test_json_parsing():
    """Test JSON parsing for deletion responses"""
    
    print("🔧 Testing JSON Parsing for Deletion")
    print("=" * 50)
    
    # Simulate AI responses that might cause parsing issues
    test_responses = [
        '''{"delete_events": [{"id": 123, "title": "Test Task", "reason": "User requested deletion"}]}''',
        '''
        Here are the events to delete:
        {"delete_events": [{"id": 456, "title": "Meeting", "reason": "Cancel requested"}]}
        ''',
        '''{"delete_events": []}''',  # Empty deletion
        '''delete_events: [{"id": 789, "title": "Broken JSON"}]''',  # Malformed
    ]
    
    for i, response in enumerate(test_responses, 1):
        print(f"🧪 Test Response {i}:")
        print(f"Raw: {response[:100]}...")
        
        try:
            # Extract JSON like in your code
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                clean_json = response[json_start:json_end]
                
                # Clean JSON like in your code
                clean_json = clean_json.replace('\n', ' ').replace('\t', ' ')
                clean_json = re.sub(r'}\s*{', '}, {', clean_json)
                clean_json = re.sub(r',\s*}', '}', clean_json)
                clean_json = re.sub(r',\s*]', ']', clean_json)
                
                print(f"Cleaned: {clean_json}")
                
                deletion_data = json.loads(clean_json)
                
                if 'delete_events' in deletion_data and deletion_data['delete_events']:
                    print(f"✅ Found {len(deletion_data['delete_events'])} events to delete")
                    for event in deletion_data['delete_events']:
                        print(f"   - ID: {event.get('id')}, Title: {event.get('title')}")
                else:
                    print("⚠️  No events to delete")
                    
            else:
                print("❌ No valid JSON structure found")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON Error: {e}")
            
            # Test regex fallback
            id_matches = re.findall(r'"id":\s*(\d+)', response)
            if id_matches:
                print(f"🔄 Regex fallback found IDs: {id_matches}")
            else:
                print("❌ Regex fallback also failed")
        
        print()

def check_database_schema():
    """Show expected database schema for events table"""
    
    print("🗄️  Expected Database Schema")
    print("=" * 50)
    
    expected_schema = """
    CREATE TABLE events (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        category VARCHAR(100),
        date DATE NOT NULL,
        time TIME NOT NULL,
        done BOOLEAN DEFAULT FALSE,
        reminder_setting VARCHAR(100),
        reminder_datetime DATETIME,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    print(expected_schema)
    print("🔍 Make sure your events table matches this structure")
    print("🎯 The deletion query uses: DELETE FROM events WHERE id = %s AND user_id = %s")

def main():
    """Run all diagnostic tests"""
    
    print("🚀 AI Deletion Diagnostic Tool")
    print("=" * 60)
    print(f"📅 Running at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_deletion_detection()
    print()
    test_json_parsing()
    print()
    check_database_schema()
    
    print("=" * 60)
    print("🔧 Troubleshooting Tips:")
    print("1. Check if AI services (Groq/Cohere/Gemini) are working")
    print("2. Verify database connection and events table structure")
    print("3. Test with simple deletion messages like 'delete my task'")
    print("4. Check server logs for detailed error messages")
    print("5. Ensure user_id exists and has events to delete")

if __name__ == "__main__":
    main()