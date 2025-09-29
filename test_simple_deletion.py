#!/usr/bin/env python3
"""
Simple test for AI deletion functionality
"""

import requests
import json
import time

def test_simple_deletion():
    """Simple test of AI deletion functionality"""
    
    print("🤖 TESTING SIMPLE AI DELETION")
    print("=" * 30)
    
    # Wait for server to be ready
    time.sleep(2)
    
    try:
        # Test the debug endpoint first
        url = 'http://127.0.0.1:5000/api/ai/debug'
        print(f"📤 Testing debug endpoint...")
        
        response = requests.post(url, 
                               headers={'Content-Type': 'application/json'},
                               json={'test': 'debug'},
                               timeout=3)
        
        if response.status_code == 200:
            print("✅ Server is responding!")
            
            # Now test AI deletion
            deletion_test = {
                'message': 'delete mom\'s task',
                'user_id': '8620b861-ea55-478a-b1b4-f266cb6a999d'
            }
            
            print(f"\n💬 Testing AI deletion message: '{deletion_test['message']}'")
            
            test_url = 'http://127.0.0.1:5000/api/ai/test'
            response = requests.post(test_url,
                                   headers={'Content-Type': 'application/json'},
                                   json=deletion_test,
                                   timeout=8)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ AI DELETION TEST SUCCESS!")
                print(f"🤖 Response: {json.dumps(result, indent=2)}")
                
                if 'deleted' in str(result).lower():
                    print("🎉 DELETION SUCCESSFUL!")
                else:
                    print("ℹ️ No deletion detected in response")
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(f"Error: {response.text}")
        else:
            print(f"❌ Server not responding: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask is running on port 5000.")
    except requests.exceptions.Timeout:
        print("❌ Request timed out. AI might still be slow.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Simple AI Deletion Test")
    print()
    
    test_simple_deletion()
    
    print("\n✅ Test complete!")