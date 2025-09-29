#!/usr/bin/env python3
"""
Test AI model availability and response times
"""

import os
from dotenv import load_dotenv
import time

load_dotenv()

def test_ai_models():
    """Test each AI model individually to identify issues"""
    
    print("🤖 TESTING AI MODEL AVAILABILITY")
    print("=" * 35)
    
    # Test Groq
    print("\n🚀 Testing Groq...")
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key:
            from groq import Groq
            groq_client = Groq(api_key=groq_api_key)
            
            start_time = time.time()
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "Test: respond with 'GROQ_WORKING'"}],
                max_tokens=50,
                temperature=0.1
            )
            end_time = time.time()
            
            result = response.choices[0].message.content.strip()
            print(f"✅ Groq: {result} (Response time: {end_time - start_time:.2f}s)")
        else:
            print("❌ Groq: No API key found")
    except Exception as e:
        print(f"❌ Groq error: {e}")
    
    # Test Gemini
    print("\n🧠 Testing Gemini...")
    try:
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        if api_key:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            start_time = time.time()
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Test: respond with 'GEMINI_WORKING'")
            end_time = time.time()
            
            result = response.text.strip()
            print(f"✅ Gemini: {result} (Response time: {end_time - start_time:.2f}s)")
        else:
            print("❌ Gemini: No API key found")
    except Exception as e:
        print(f"❌ Gemini error: {e}")
    
    # Test Cohere
    print("\n🌊 Testing Cohere...")
    try:
        cohere_api_key = os.getenv("COHERE_API_KEY")
        if cohere_api_key:
            import cohere
            co = cohere.Client(cohere_api_key)
            
            start_time = time.time()
            response = co.chat(
                message="Test: respond with 'COHERE_WORKING'",
                max_tokens=50,
                temperature=0.1
            )
            end_time = time.time()
            
            result = response.text.strip()
            print(f"✅ Cohere: {result} (Response time: {end_time - start_time:.2f}s)")
        else:
            print("❌ Cohere: No API key found")
    except Exception as e:
        print(f"❌ Cohere error: {e}")

def test_deletion_logic():
    """Test the deletion detection logic with simulated data"""
    
    print(f"\n🔍 TESTING DELETION DETECTION LOGIC")
    print("=" * 35)
    
    # Simulate the AI detection step
    test_messages = [
        "delete my ai assistance task",
        "cancel test ai meeting", 
        "remove ai tasks",
        "delete all ai meetings"
    ]
    
    for message in test_messages:
        print(f"\n📝 Message: '{message}'")
        
        # This is what should happen in detect_and_create_events
        detection_keywords = ['delete', 'cancel', 'remove', 'clear']
        
        has_deletion_keyword = any(keyword in message.lower() for keyword in detection_keywords)
        has_ai_reference = any(word in message.lower() for word in ['ai', 'assistance', 'meeting', 'task'])
        
        if has_deletion_keyword and has_ai_reference:
            print("✅ Would trigger DELETE_EVENTS flow")
        else:
            print("❌ Would not trigger deletion")

def provide_fix_suggestions():
    """Provide specific suggestions to fix the AI deletion issue"""
    
    print(f"\n💡 FIX SUGGESTIONS FOR AI DELETION")
    print("=" * 35)
    
    print("Based on the timeout issues, here are fixes:")
    print()
    print("1. 🔧 ADD TIMEOUT HANDLING:")
    print("   • Set shorter timeouts for AI requests (5-10 seconds)")
    print("   • Add fallback logic for timeouts")
    print()
    print("2. 🔧 OPTIMIZE DELETION PROMPT:")
    print("   • Make AI prompts shorter and more specific")
    print("   • Reduce context size sent to AI")
    print()
    print("3. 🔧 ADD CACHING:")
    print("   • Cache user events to avoid repeated DB queries")
    print("   • Cache AI responses for similar requests")
    print()
    print("4. 🔧 IMPLEMENT ASYNC PROCESSING:")
    print("   • Use background tasks for AI deletion")
    print("   • Return immediate response, process deletion async")
    print()
    print("5. 🔧 BETTER ERROR HANDLING:")
    print("   • Catch specific timeout errors")
    print("   • Provide user-friendly error messages")

if __name__ == "__main__":
    print("🚀 AI Model Diagnostics")
    print()
    
    test_ai_models()
    test_deletion_logic()
    provide_fix_suggestions()
    
    print("\n✅ Diagnostics complete!")