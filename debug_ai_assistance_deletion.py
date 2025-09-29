#!/usr/bin/env python3
"""
Debug script to check AI assistance tasks and deletion functionality
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def check_ai_tasks():
    """Check for AI assistance related tasks in database"""
    
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_DATABASE')
        )
        
        cursor = conn.cursor()
        
        # Check all tasks/events that might contain 'ai_assistance' or similar
        print('🔍 Searching for ai_assistance related tasks...')
        query = """
        SELECT id, user_id, title, description, category, date, time, done 
        FROM events 
        WHERE title LIKE '%ai%' OR description LIKE '%ai%' OR title LIKE '%assistance%'
        ORDER BY date DESC, time DESC
        LIMIT 10
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f'✅ Found {len(results)} AI-related tasks:')
            for i, row in enumerate(results, 1):
                print(f'{i}. ID: {row[0]}, User: {row[1]}, Title: "{row[2]}", Category: {row[4]}, Date: {row[5]}, Done: {row[7]}')
                print(f'   Description: "{row[3][:100]}..."')
                print()
        else:
            print('❌ No AI-related tasks found')
            
            # Check all recent tasks
            print('\n🔍 Showing recent tasks instead:')
            cursor.execute('SELECT id, user_id, title, description, category, date, time, done FROM events ORDER BY date DESC, time DESC LIMIT 10')
            recent_tasks = cursor.fetchall()
            
            if recent_tasks:
                print(f'Found {len(recent_tasks)} recent tasks:')
                for i, row in enumerate(recent_tasks, 1):
                    print(f'{i}. ID: {row[0]}, User: {row[1]}, Title: "{row[2]}", Category: {row[4]}, Date: {row[5]}, Done: {row[7]}')
            else:
                print('No tasks found in database')
        
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f'❌ Database error: {e}')
    except Exception as e:
        print(f'❌ Error: {e}')

def test_deletion_endpoints():
    """Test different deletion endpoints available"""
    
    print('\n🔧 Available deletion endpoints:')
    print('1. AI Chat Deletion: POST /api/ai/chat (with delete message)')
    print('2. AI Scheduler Chat: POST /api/ai/scheduler/chat (with delete message)')  
    print('3. Direct Task Deletion: DELETE /api/{user_id}/task/{task_id}')
    print('4. Collaboration Deletion: DELETE /api/{user_id}/task/{task_id}')
    
    print('\n📋 To delete AI assistance tasks, you can:')
    print('• Use natural language: "delete my ai assistance task" or "cancel ai assistance"')
    print('• Use specific deletion: DELETE /api/{user_id}/task/{task_id} with the task ID')
    print('• Use AI chat deletion: POST to /api/ai/chat with deletion request')

if __name__ == "__main__":
    print("🚀 AI Assistance Task Deletion Debug")
    print("=" * 40)
    
    check_ai_tasks()
    test_deletion_endpoints()
    
    print("\n✅ Debug complete!")