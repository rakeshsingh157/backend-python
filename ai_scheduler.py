import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import re
from datetime import datetime

load_dotenv()

class AIScheduler:
    def __init__(self):
        google_gemini_api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        if not google_gemini_api_key:
            raise ValueError("GOOGLE_GEMINI_API_KEY not found in environment variables")
        
        # Configure API key (no Client object required)
        genai.configure(api_key=google_gemini_api_key)
        
        # Load Gemini model
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate_tasks(self, user_input):
        try:
            prompt = f"""
            Analyze the following user input and generate a list of tasks with specific details.
            The user said: "{user_input}"
            
            Return ONLY a JSON array with tasks in this exact format:
            [
                {{
                    "title": "Task title",
                    "description": "Task description",
                    "category": "Category (work, home, sports, fun, health, fitness, personal, learning, finance, errands, cleaning, gardening, cooking, pets, meeting, commute, networking, admin, social, entertainment, travel, hobby, volunteering, important, to-do, later, family)",
                    "date": "YYYY-MM-DD",
                    "time": "HH:MM",
                    "reminder": "15 minutes"
                }}
            ]
            
            Rules:
            1. Extract or infer dates and times from the input
            2. If no specific date is mentioned, use today's date: {datetime.now().strftime('%Y-%m-%d')}
            3. If no specific time is mentioned, use a reasonable time like "09:00"
            4. Categorize each task appropriately
            5. Generate at least 1 task and at most 5 tasks
            6. For reminder field, use values like "15 minutes", "30 minutes", "1 hour", "2 hours", "1 day"
            """

            response = self.model.generate_content(prompt)

            # Extract JSON from response text
            response_text = response.text
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            
            if json_match:
                tasks_json = json_match.group(0)
                tasks = json.loads(tasks_json)
                
                # Ensure reminder field exists
                for task in tasks:
                    if 'reminder' not in task:
                        task['reminder'] = '15 minutes'
                        
                return tasks
            else:
                return [{
                    "title": "Complete your task",
                    "description": user_input,
                    "category": "personal",
                    "date": datetime.now().strftime('%Y-%m-%d'),
                    "time": "09:00",
                    "reminder": "15 minutes"
                }]
                
        except Exception as e:
            print(f"Error generating tasks: {e}")
            return [{
                "title": "Complete your task",
                "description": user_input,
                "category": "personal",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "time": "09:00",
                "reminder": "15 minutes"
            }]
