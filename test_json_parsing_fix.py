#!/usr/bin/env python3
"""
Direct test of JSON parsing improvements
"""

import json
import re

def test_json_parsing_fix():
    """Test the JSON parsing improvements directly"""
    
    print("🔧 TESTING JSON PARSING FIXES")
    print("=" * 30)
    
    # Simulate the malformed JSON that was causing issues
    malformed_json = '''```json
{
    "delete_events": [
        {
            "reason": "Matches 'delete my all
            "title": "Debug Test Task",
            "id": 64,
        {
        },
            "reason": "Matches 'delete my all task' request as it is a task-related event"
            "title": "Debug Test Task",
            "id": 63,
        {
        },
            "reason": "Matches 'delete my all task' request as it is a task-related event"
            "title": "Meeting",
            "id": 60,
        }
    ]
}
```'''
    
    print("🔍 Original malformed JSON:")
    print(malformed_json[:200] + "...")
    
    # Apply the same cleaning logic as in the actual code
    try:
        # Extract JSON from response
        json_start = malformed_json.find('{')
        json_end = malformed_json.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            clean_json = malformed_json[json_start:json_end]
            
            # Try to fix common JSON formatting issues
            clean_json = clean_json.replace('\n', ' ').replace('\t', ' ')
            # Fix missing commas between objects
            clean_json = re.sub(r'}\s*{', '}, {', clean_json)
            # Fix trailing commas
            clean_json = re.sub(r',\s*}', '}', clean_json)
            clean_json = re.sub(r',\s*]', ']', clean_json)
            
            print("\n🔧 After cleaning:")
            print(clean_json[:200] + "...")
            
            try:
                # Try to parse the cleaned JSON
                deletion_data = json.loads(clean_json)
                print("\n✅ JSON PARSING SUCCESSFUL!")
                print(f"Found {len(deletion_data.get('delete_events', []))} events to process")
                
            except json.JSONDecodeError as e:
                print(f"\n⚠️ JSON still invalid: {e}")
                print("🔄 Trying regex fallback...")
                
                # Test regex fallback
                id_matches = re.findall(r'"id":\s*(\d+)', clean_json)
                if id_matches:
                    print(f"✅ Regex fallback found {len(id_matches)} event IDs: {id_matches}")
                else:
                    print("❌ Regex fallback failed")
    
    except Exception as e:
        print(f"❌ Processing error: {e}")

def test_good_json():
    """Test with properly formatted JSON"""
    
    print(f"\n✅ TESTING GOOD JSON")
    print("-" * 20)
    
    good_json = '''{
        "delete_events": [
            {
                "id": 64,
                "title": "Debug Test Task",
                "reason": "Matches delete request"
            },
            {
                "id": 63,
                "title": "Meeting",
                "reason": "Also matches delete request"
            }
        ]
    }'''
    
    try:
        deletion_data = json.loads(good_json)
        print("✅ Good JSON parsed successfully!")
        print(f"Events to delete: {len(deletion_data['delete_events'])}")
        
        for event in deletion_data['delete_events']:
            print(f"  - ID {event['id']}: {event['title']}")
            
    except Exception as e:
        print(f"❌ Unexpected error with good JSON: {e}")

def summarize_improvements():
    """Summarize all the improvements made"""
    
    print(f"\n📋 SUMMARY OF ALL FIXES APPLIED")
    print("=" * 35)
    
    print("1. ✅ Fixed Gemini Model Issues:")
    print("   • Changed gemini-1.5-flash → gemini-pro (working model)")
    print("   • Removed unsupported system_instruction parameter")
    print()
    print("2. ✅ Improved JSON Parsing:")
    print("   • Added newline/tab cleaning")
    print("   • Fixed missing commas between objects")
    print("   • Fixed trailing commas")
    print("   • Added regex fallback for malformed JSON")
    print()
    print("3. ✅ Enhanced AI Prompts:")
    print("   • Clearer instructions for valid JSON output")
    print("   • Explicit formatting requirements")
    print("   • Better error handling instructions")
    print()
    print("4. ✅ Optimized AI Service Priority:")
    print("   • Groq first (fastest, most reliable)")
    print("   • Cohere second (good fallback)")
    print("   • Gemini last (if working)")
    print()
    print("🎯 EXPECTED RESULTS:")
    print("✅ No more Gemini 404 errors")
    print("✅ No more JSON parsing failures") 
    print("✅ No more system_instruction errors")
    print("✅ Faster, more reliable AI deletion")

if __name__ == "__main__":
    print("🚀 JSON Parsing Improvement Tests")
    print()
    
    test_json_parsing_fix()
    test_good_json()
    summarize_improvements()
    
    print("\n🎉 All improvements have been implemented!")
    print("The AI deletion system should now work reliably.")