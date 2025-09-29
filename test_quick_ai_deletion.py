#!/usr/bin/env python3
"""
Quick test for AI deletion functionality with simpler approach
"""

import requests
import json

def test_simple_ai_deletion():
    """Test AI deletion with a simple approach"""
    
    print("🔍 TESTING SIMPLE AI DELETION")
    print("=" * 30)
    
    try:
        # Test the debug endpoint first (no auth, faster response)
        url = 'http://127.0.0.1:5000/api/ai/debug'
        print(f"📤 Testing debug endpoint: {url}")
        
        response = requests.post(url, 
                               headers={'Content-Type': 'application/json'},
                               json={'test': 'debug'},
                               timeout=5)
        
        print(f"📊 Debug Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ AI Blueprint is working!")
            result = response.json()
            print(f"Response: {result}")
        else:
            print("❌ AI Blueprint issue")
            
    except Exception as e:
        print(f"❌ Debug test error: {e}")
        
    # Test the test endpoint without authentication
    try:
        url = 'http://127.0.0.1:5000/api/ai/test'
        data = {
            'message': 'delete test ai meeting',
            'user_id': '2de79958-cd03-4407-8fa3-fe20bed3660c'
        }
        
        print(f"\n📤 Testing AI deletion via test endpoint...")
        response = requests.post(url,
                               headers={'Content-Type': 'application/json'},
                               json=data,
                               timeout=10)
        
        print(f"📊 Test Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ AI Test endpoint working!")
            print(f"🤖 Response: {json.dumps(result, indent=2)}")
            
            # Check for deletion success
            if 'deleted' in str(result).lower():
                print("🗑️ DELETION SUCCESSFUL!")
            else:
                print("⚠️ No deletion detected")
        else:
            print("❌ AI test failed")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ AI test error: {e}")

def test_direct_database_check():
    """Check what tasks exist after deletion attempts"""
    
    print(f"\n📊 CHECKING DATABASE AFTER DELETION ATTEMPTS")
    print("=" * 45)
    
    try:
        import mysql.connector
        from mysql.connector import Error
        import os
        from dotenv import load_dotenv

        load_dotenv()
        
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_DATABASE')
        )
        
        cursor = conn.cursor()
        
        # Check Test AI Meeting tasks
        user_id = '2de79958-cd03-4407-8fa3-fe20bed3660c'
        query = "SELECT id, title, description FROM events WHERE user_id = %s AND title LIKE '%test%ai%'"
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        
        if results:
            print(f"🔍 Found {len(results)} 'Test AI' tasks for user:")
            for row in results:
                print(f"   ID {row[0]}: {row[1]}")
        else:
            print("✅ No 'Test AI' tasks found - they may have been deleted!")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check error: {e}")

if __name__ == "__main__":
    print("🚀 Quick AI Deletion Test")
    print()
    
    test_simple_ai_deletion()
    test_direct_database_check()
    
    print("\n✅ Quick test complete!")