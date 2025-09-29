import os
import re
import json
from flask import Blueprint, request, jsonify, session
from dotenv import load_dotenv

# Optional imports
try:
    import google.generativeai as genai
except ImportError:
    genai = None
    print("Warning: google.generativeai not available")

try:
    import cohere
except ImportError:
    cohere = None
    print("Warning: cohere not available")

from database import get_db_connection # Make sure you can import your DB connection
from mysql.connector import Error
from datetime import datetime, timedelta
import pytz

try:
    from groq import Groq
except ImportError:
    Groq = None
    print("Warning: groq not available")

load_dotenv()

class AIScheduler:
    """
    AI-powered task scheduler for generating calendar events
    """
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        self.cohere_api_key = os.getenv("COHERE_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        # Initialize AI clients
        if self.api_key and genai:
            genai.configure(api_key=self.api_key)
            
        self.co = None
        self.groq_client = None
        
        if self.cohere_api_key and cohere:
            try:
                self.co = cohere.Client(self.cohere_api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Cohere client in AIScheduler: {e}")
                self.co = None
        else:
            self.co = None
            
        if self.groq_api_key and Groq:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Groq client in AIScheduler: {e}")
                self.groq_client = None
    
    def generate_tasks(self, prompt):
        """
        Generate tasks from a natural language prompt with intelligent reminder settings
        """
        try:
            # Use IST timezone
            ist_tz = pytz.timezone('Asia/Kolkata')
            today = datetime.now(ist_tz).strftime('%A, %Y-%m-%d')
            current_time = datetime.now(ist_tz).strftime('%H:%M')
            
            task_prompt = f"""
            You are an intelligent task scheduler. Today is {today} and current time is {current_time} IST.
            
            Based on this user prompt: "{prompt}"
            
            Generate a comprehensive list of calendar events/tasks in JSON format. Each task MUST have ALL these fields:
            - title: Clear, concise task title
            - description: Detailed, actionable description with context
            - date: Date in YYYY-MM-DD format (use {today} if not specified)
            - time: Time in HH:MM format (24-hour, use appropriate default times)
            - category: Choose from: work, personal, health, fitness, education, shopping, social, travel, maintenance, finance
            - reminder_setting: Intelligent reminder based on task importance and type
            
            REMINDER SETTING RULES (AI should decide intelligently):
            - Important meetings/appointments: "1 hour" or "2 hours"
            - Medical appointments: "2 hours" (need time to prepare/travel)
            - Work tasks/deadlines: "1 day" or "4 hours" 
            - Gym/fitness: "30 minutes" (time to prepare/change)
            - Social events: "1 hour" or "30 minutes"
            - Travel/flights: "4 hours" or "1 day" (critical timing)
            - Education/learning: "30 minutes" (prepare materials)
            - Shopping/errands: "1 hour" (plan route/list)
            - Personal tasks: "15 minutes" or "30 minutes"
            - Maintenance/repairs: "2 hours" (arrange time/materials)
            
            TIME DEFAULTS if not specified:
            - Morning activities: 09:00
            - Work meetings: 10:00, 14:00
            - Lunch: 12:30
            - Gym/fitness: 07:00 or 18:00
            - Dinner: 19:30
            - Medical appointments: 10:00 or 15:00
            - Social events: 19:00
            
            EXAMPLE OUTPUT:
            [
                {{
                    "title": "Team Meeting",
                    "description": "Weekly team standup to discuss project progress and upcoming deadlines",
                    "date": "{today}",
                    "time": "10:00",
                    "category": "work",
                    "reminder_setting": "1 hour"
                }},
                {{
                    "title": "Gym Session",
                    "description": "Full body workout including cardio and strength training",
                    "date": "{today}",
                    "time": "18:00", 
                    "category": "fitness",
                    "reminder_setting": "30 minutes"
                }}
            ]
            
            CRITICAL: Return ONLY the JSON array, no additional text or formatting.
            """
            
            # Try Groq first (fastest and most reliable)
            if self.groq_client:
                try:
                    chat_completion = self.groq_client.chat.completions.create(
                        messages=[{"role": "user", "content": task_prompt}],
                        model="llama-3.1-8b-instant",
                        temperature=0.4,
                        max_tokens=1000
                    )
                    response_text = chat_completion.choices[0].message.content.strip()
                    
                    # Try to parse JSON
                    try:
                        tasks = json.loads(response_text)
                        # Enhance tasks with fallback reminder settings if missing
                        enhanced_tasks = self._ensure_reminder_settings(tasks)
                        return {"success": True, "tasks": enhanced_tasks}
                    except json.JSONDecodeError:
                        print("Groq returned non-JSON response, trying next service...")
                except Exception as e:
                    print(f"Groq failed: {e}")
            
            # Fallback to Gemini if Groq fails
            if self.api_key and genai:
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(task_prompt)
                    response_text = response.text.strip()
                    
                    # Clean up response
                    if response_text.startswith('```json'):
                        response_text = response_text.replace('```json', '').replace('```', '').strip()
                    elif response_text.startswith('```'):
                        response_text = response_text.replace('```', '').strip()
                    
                    # Try to parse JSON
                    try:
                        tasks = json.loads(response_text)
                        # Enhance tasks with fallback reminder settings if missing
                        enhanced_tasks = self._ensure_reminder_settings(tasks)
                        return {"success": True, "tasks": enhanced_tasks}
                    except json.JSONDecodeError:
                        print("Gemini returned non-JSON response, trying next service...")
                except Exception as e:
                    print(f"Gemini failed: {e}")
            
            # Final fallback to Cohere
            if self.cohere_api_key and self.co:
                try:
                    response = self.co.chat(
                        message=task_prompt,
                        max_tokens=1000,
                        temperature=0.4
                    )
                    response_text = response.text.strip()
                    
                    # Clean up response
                    if response_text.startswith('```json'):
                        response_text = response_text.replace('```json', '').replace('```', '').strip()
                    
                    # Try to parse JSON
                    try:
                        tasks = json.loads(response_text)
                        # Enhance tasks with fallback reminder settings if missing
                        enhanced_tasks = self._ensure_reminder_settings(tasks)
                        return {"success": True, "tasks": enhanced_tasks}
                    except json.JSONDecodeError:
                        return {"success": False, "message": "Failed to parse AI response"}
                except Exception as e:
                    print(f"Cohere failed: {e}")
            
            return {"success": False, "message": "All AI services unavailable"}
            
        except Exception as e:
            return {"success": False, "message": f"Error generating tasks: {str(e)}"}
    
    def _ensure_reminder_settings(self, tasks):
        """
        Ensure all tasks have appropriate reminder settings based on their category and type
        """
        enhanced_tasks = []
        
        for task in tasks:
            # Make sure task has all required fields
            if not isinstance(task, dict):
                continue
                
            # Add missing fields with defaults
            task.setdefault('title', 'Untitled Task')
            task.setdefault('description', 'No description provided')
            task.setdefault('category', 'personal')
            task.setdefault('date', datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d'))
            task.setdefault('time', '09:00')
            
            # Intelligently set reminder_setting if missing
            if 'reminder_setting' not in task or not task.get('reminder_setting'):
                task['reminder_setting'] = self._get_smart_reminder(task['title'], task['description'], task['category'])
            
            enhanced_tasks.append(task)
        
        return enhanced_tasks
    
    def _get_smart_reminder(self, title, description, category):
        """
        Intelligently determine appropriate reminder setting based on task details
        """
        title_lower = title.lower()
        description_lower = description.lower()
        category_lower = category.lower()
        
        # Critical/Important events - longer reminders
        critical_keywords = ['flight', 'interview', 'exam', 'surgery', 'wedding', 'deadline', 'presentation']
        if any(keyword in title_lower or keyword in description_lower for keyword in critical_keywords):
            return "1 day"
        
        # Medical/Health appointments
        if category_lower == 'health' or any(word in title_lower for word in ['doctor', 'dentist', 'hospital', 'clinic', 'appointment']):
            return "2 hours"
        
        # Work-related tasks
        if category_lower == 'work' or any(word in title_lower for word in ['meeting', 'conference', 'call', 'standup']):
            if 'important' in description_lower or 'urgent' in description_lower:
                return "2 hours"
            return "1 hour"
        
        # Travel related
        if category_lower == 'travel' or any(word in title_lower for word in ['flight', 'train', 'bus', 'trip', 'travel']):
            return "4 hours"
        
        # Fitness/Gym
        if category_lower == 'fitness' or any(word in title_lower for word in ['gym', 'workout', 'exercise', 'run', 'yoga']):
            return "30 minutes"
        
        # Education/Learning
        if category_lower == 'education' or any(word in title_lower for word in ['class', 'course', 'study', 'learn', 'training']):
            return "30 minutes"
        
        # Social events
        if category_lower == 'social' or any(word in title_lower for word in ['party', 'dinner', 'lunch', 'hangout', 'date']):
            return "1 hour"
        
        # Shopping/Errands
        if category_lower == 'shopping' or any(word in title_lower for word in ['shop', 'buy', 'grocery', 'market']):
            return "1 hour"
        
        # Maintenance/Repairs
        if category_lower == 'maintenance' or any(word in title_lower for word in ['repair', 'fix', 'service', 'maintenance']):
            return "2 hours"
        
        # Finance related
        if category_lower == 'finance' or any(word in title_lower for word in ['bank', 'payment', 'tax', 'budget']):
            return "1 hour"
        
        # Default for personal and everything else
        return "15 minutes"

ai_scheduler_bp = Blueprint('ai_scheduler', __name__)

# API configurations
api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
cohere_api_key = os.getenv("COHERE_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

if api_key and genai:
    genai.configure(api_key=api_key)
else:
    print("Warning: GOOGLE_GEMINI_API_KEY not found in .env file or genai not available.")

# Initialize backup AI clients
co = None
groq_client = None

if cohere_api_key and cohere:
    try:
        co = cohere.Client(cohere_api_key)
    except Exception as e:
        print(f"Warning: Failed to initialize Cohere client: {e}")
        co = None
else:
    co = None
    
if groq_api_key and Groq:
    try:
        groq_client = Groq(api_key=groq_api_key)
    except Exception as e:
        print(f"Warning: Failed to initialize Groq client: {e}")
        groq_client = None

# --- SMART AI EVENT DETECTION AND CREATION ---
def detect_and_create_events(user_message, user_id):
    """
    Uses AI to intelligently detect if the user message contains events
    and automatically creates them. Only returns JSON when events are found.
    """
    
    # First, use AI to determine if this message contains events
    # Use IST timezone
    ist_tz = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ist_tz).strftime('%A, %Y-%m-%d')
    
    detection_prompt = f"""
    You are an AI assistant that determines if a user message contains calendar events or event operations.
    
    Today is {today}.
    
    User message: "{user_message}"
    
    Analyze this message and determine:
    1. Does it contain one or more calendar events to be scheduled?
    2. Does it contain requests to delete/cancel/remove events?
    3. Is it asking for event creation/scheduling?
    4. Is it asking for event deletion/cancellation?
    
    Events include: meetings, appointments, calls, lunch, dinner, workouts, classes, etc.
    Deletion keywords: cancel, delete, remove, clear, cancel my, remove my, delete my, etc.
    
    NOT events: questions, help requests, general conversation, reminders without specific events
    
    Respond with ONLY one of these:
    - "EVENTS_FOUND" if the message contains events to schedule
    - "DELETE_EVENTS" if the message contains requests to delete/cancel events
    - "NO_EVENTS" if no events are found
    - "QUESTION" if it's a question or help request
    """
    
    # Try different AI services to detect events
    event_detection_result = None
    
    try:
        # Try Groq first (fastest and most reliable)
        if groq_client:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": detection_prompt}],
                max_tokens=20,
                temperature=0.1
            )
            event_detection_result = response.choices[0].message.content.strip()
            print(f"Groq detection result: {event_detection_result}")
    except Exception as groq_error:
        print(f"Groq detection failed: {groq_error}")
        
        try:
            # Fallback to Cohere
            if co:
                response = co.chat(
                    message=detection_prompt,
                    max_tokens=20,
                    temperature=0.1
                )
                event_detection_result = response.text.strip()
                print(f"Cohere detection result: {event_detection_result}")
        except Exception as cohere_error:
            print(f"Cohere detection failed: {cohere_error}")
            
            try:
                # Final fallback to Gemini (if working)
                if api_key and genai:
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(detection_prompt)
                    event_detection_result = response.text.strip()
                    print(f"Gemini detection result: {event_detection_result}")
            except Exception as gemini_error:
                print(f"All AI detection failed: {gemini_error}")
                return False, "AI detection services unavailable"
    
    # If no events detected, check for deletion requests
    if not event_detection_result or "NO_EVENTS" in event_detection_result or "QUESTION" in event_detection_result:
        return False, f"AI determined: {event_detection_result or 'No clear result'}"
    
    # If deletion request detected, handle event deletion
    if "DELETE_EVENTS" in event_detection_result:
        return handle_event_deletion(user_message, user_id)
    
    # If events found, extract them with AI
    if "EVENTS_FOUND" in event_detection_result:
        extraction_prompt = f"""
        You are an AI assistant that extracts event details from user messages.
        
        Today is {today}.
        Current time: {datetime.now(ist_tz).strftime('%H:%M')} IST
        
        User message: "{user_message}"
        
        Extract ALL events mentioned in this message. For each event determine:
        1. Title (what is the event)
        2. Description (brief relevant description with context)
        3. Category (from allowed categories only)
        4. Date (convert relative dates like "tomorrow", "next week" to YYYY-MM-DD format)
        5. Time (MUST be in HH:MM format, NEVER use "TBD")
        6. Reminder setting (default "15 minutes" unless specified)
        
        ALLOWED CATEGORIES (choose most appropriate):
        work, home, sports, fun, health, fitness, personal, learning, finance, errands, cleaning, gardening, cooking, pets, meeting, commute, networking, admin, social, entertainment, travel, hobby, volunteering, important, to-do, later, family
        
        TIME REQUIREMENTS:
        - ALWAYS provide a time in HH:MM format (e.g. "09:00", "14:30")
        - NEVER use "TBD", "unknown", or empty time
        - Default times: morning events "09:00", afternoon "14:00", evening "19:00"
        - For school/learning events, use "09:00" as default
        
        DATE INTERPRETATION EXAMPLES:
        - Current date: {datetime.now(ist_tz).strftime('%Y-%m-%d')} (IST)
        this is only example
        - "on 1" → "2025-10-01" (October 1st)
        - "on 2" → "2025-10-02" (October 2nd)  
        - "on 5" → "2025-10-05" (October 5th)
        - "on 7" → "2025-10-07" (October 7th)
        - "on 15" → "2025-10-15" (October 15th)
        - "on 25" → "2025-10-25" (October 25th)
        - "tomorrow" → {(datetime.now(ist_tz) + timedelta(days=1)).strftime('%Y-%m-%d')}
        - "today" → {datetime.now(ist_tz).strftime('%Y-%m-%d')}
        
        CRITICAL RULE: Match the EXACT day number from user input!
        
        VALIDATION: 
        - If user says "on 7", the date MUST be "2025-10-07"
        - If user says "on 15", the date MUST be "2025-10-15"  
        - NEVER use today's date unless user says "today"
        - NEVER use "2025-09-29" unless user specifically mentions today
        
        Rules:
        - If no date specified, assume today
        - If no time specified, ALWAYS use "09:00" as default (NEVER use "TBD" or empty time)
        - Handle multiple events in one message
        - Convert times like "2pm" to "14:00"
        - For "on [number]", interpret as that EXACT day number of current/next month
        - NEVER change the day number: "on 5" = day 5, "on 15" = day 15, etc.
        - Use "meeting" category for meetings, calls, appointments
        - Use "health" for doctor/dentist appointments
        - Use "fitness" for gym/workout activities
        - Use "learning" for school, class, education events
        
        Respond with ONLY this JSON format:
        {{
            "events": [
                {{
                    "title": "Event Title",
                    "description": "Detailed description with context",
                    "category": "meeting",
                    "date": "YYYY-MM-DD",
                    "time": "HH:MM",
                    "reminder_setting": "15 minutes"
                }}
            ]
        }}
        """
        
        # Extract events using AI
        events_json = None
        
        try:
            # Try Groq for extraction
            if groq_client:
                print(f"[DEBUG] Extraction prompt for '{user_message}':")
                print(f"[DEBUG] Date interpretation should map 'on 5' to October 5th")
                response = groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": extraction_prompt}],
                    max_tokens=500,
                    temperature=0.1
                )
                events_json = response.choices[0].message.content.strip()
                print(f"Groq extraction result: {events_json}")
        except Exception as groq_error:
            print(f"Groq extraction failed: {groq_error}")
            
            try:
                # Fallback to Cohere for extraction
                if co:
                    response = co.chat(
                        message=extraction_prompt,
                        max_tokens=500,
                        temperature=0.1
                    )
                    events_json = response.text.strip()
                    print(f"Cohere extraction result: {events_json}")
            except Exception as cohere_error:
                print(f"Cohere extraction failed: {cohere_error}")
                
                try:
                    # Final fallback to Gemini for extraction
                    if api_key:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(extraction_prompt)
                        events_json = response.text.strip()
                        print(f"Gemini extraction result: {events_json}")
                except Exception as gemini_error:
                    print(f"All AI extraction failed: {gemini_error}")
                    return False, "AI extraction services unavailable"
        
        # Parse and save events
        if events_json:
            try:
                # Extract JSON from response
                json_start = events_json.find('{')
                json_end = events_json.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    clean_json = events_json[json_start:json_end]
                    events_data = json.loads(clean_json)
                    
                    if 'events' in events_data and events_data['events']:
                        # Validate and fix date interpretation
                        for event in events_data['events']:
                            # Fix common date interpretation errors
                            original_date = event.get('date', '')
                            fixed_date = fix_date_interpretation(user_message, original_date)
                            if fixed_date != original_date:
                                print(f"[DATE FIX] Changed {original_date} → {fixed_date} based on '{user_message}'")
                                event['date'] = fixed_date
                        
                        # Check for conflicts before creating events
                        all_conflicts = []
                        events_to_create = []
                        
                        for event in events_data['events']:
                            if all(key in event for key in ['title', 'date', 'time']):
                                # Check for conflicts
                                conflicts = check_event_conflicts(
                                    user_id, 
                                    event['date'], 
                                    event['time'], 
                                    event['title']
                                )
                                
                                if conflicts:
                                    # Store the pending event in session for later confirmation
                                    from flask import session
                                    session['pending_event_with_conflict'] = event
                                    
                                    # Generate conflict warning
                                    warning_msg = create_conflict_warning_message(
                                        conflicts, 
                                        event['title'], 
                                        event['date'], 
                                        event['time']
                                    )
                                    return False, warning_msg
                                else:
                                    events_to_create.append(event)
                        
                        # No conflicts found, create all events
                        created_count = 0
                        for event in events_to_create:
                            if create_event_in_db(user_id, event):
                                created_count += 1
                        
                        if created_count > 0:
                            return True, f"✅ Successfully created {created_count} event(s) automatically!"
                        else:
                            return False, "Failed to save events to database"
                    else:
                        return False, "No valid events found in AI response"
                else:
                    return False, "Could not parse JSON from AI response"
                    
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                return False, "Invalid JSON format from AI"
            except Exception as e:
                print(f"Event creation error: {e}")
                return False, f"Error creating events: {str(e)}"
    
    return False, "No events detected by AI"


def handle_event_deletion(user_message, user_id):
    """
    Handles event deletion requests using AI to identify which events to delete.
    """
    # Use IST timezone
    ist_tz = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ist_tz).strftime('%A, %Y-%m-%d')
    
    # First, get user's current events to help with deletion
    current_events = get_user_events_for_deletion(user_id)
    
    if not current_events:
        return False, "No events found to delete"
    
    # Create context of current events for AI with ACTUAL database IDs
    events_context = "Current events:\n"
    for event in current_events:
        events_context += f"ID {event['id']}: {event['title']} - {event['date']} at {event['time']}\n"
    
    deletion_prompt = f"""
    You are an AI assistant that identifies which events to delete based on user requests.
    
    Today is {today}.
    Current time: {datetime.now(ist_tz).strftime('%H:%M')} IST
    
    User message: "{user_message}"
    
    {events_context}
    
    The user wants to delete/cancel events. Based on their message, determine which events should be deleted.
    
    IMPORTANT: Use the actual database ID numbers shown above (like "ID 35", "ID 40", etc.)
    
    Consider:
    - Specific titles mentioned
    - Time references (today, tomorrow, this week)  
    - Event types (meeting, appointment, etc.)
    - Partial matches (user says "cancel meeting" matches any event with "meeting" in title)
    
    Respond with ONLY this JSON format using the ACTUAL database IDs:
    {{
        "delete_events": [
            {{
                "id": actual_database_id_number,
                "title": "Event Title",
                "reason": "Why this event matches the deletion request"
            }}
        ]
    }}
    
    If no events match the deletion criteria, respond with:
    {{"delete_events": []}}
    """
    
    # Get AI analysis for which events to delete
    deletion_analysis = None
    
    try:
        # Try Groq first (fastest and working model)
        if groq_client:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": deletion_prompt}],
                max_tokens=500,
                temperature=0.1
            )
            deletion_analysis = response.choices[0].message.content.strip()
            print(f"Groq deletion analysis: {deletion_analysis}")
    except Exception as groq_error:
        print(f"Groq deletion analysis failed: {groq_error}")
        
        try:
            # Fallback to Cohere
            if co and not deletion_analysis:
                response = co.chat(
                    message=deletion_prompt,
                    max_tokens=500,
                    temperature=0.1
                )
                deletion_analysis = response.text.strip()
                print(f"Cohere deletion analysis: {deletion_analysis}")
        except Exception as cohere_error:
            print(f"Cohere deletion analysis failed: {cohere_error}")
            
            try:
                # Final fallback to Gemini (if working)
                if api_key and not deletion_analysis:
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(deletion_prompt)
                    deletion_analysis = response.text.strip()
                    print(f"Gemini deletion analysis: {deletion_analysis}")
            except Exception as gemini_error:
                print(f"All AI deletion analysis failed: {gemini_error}")
                return False, "AI deletion analysis services unavailable"
    
    # Parse deletion analysis
    if deletion_analysis:
        try:
            # Extract JSON from response
            json_start = deletion_analysis.find('{')
            json_end = deletion_analysis.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                clean_json = deletion_analysis[json_start:json_end]
                deletion_data = json.loads(clean_json)
                
                if 'delete_events' in deletion_data and deletion_data['delete_events']:
                    deleted_count = 0
                    deleted_titles = []
                    
                    for event_to_delete in deletion_data['delete_events']:
                        event_id = event_to_delete.get('id')
                        if event_id and delete_event_from_db(user_id, event_id):
                            deleted_count += 1
                            deleted_titles.append(event_to_delete.get('title', 'Unknown'))
                    
                    if deleted_count > 0:
                        titles_text = ', '.join(deleted_titles)
                        return True, f"✅ Successfully deleted {deleted_count} event(s): {titles_text}"
                    else:
                        return False, "Failed to delete events from database"
                else:
                    return False, "No matching events found to delete"
                    
        except json.JSONDecodeError as e:
            print(f"JSON parsing error in deletion: {e}")
            return False, "Could not parse deletion analysis"
        except Exception as e:
            print(f"Event deletion error: {e}")
            return False, f"Error processing deletion: {str(e)}"
    
    return False, "Could not analyze deletion request"


def fix_date_interpretation(user_message, ai_date):
    """
    Fix common date interpretation errors by the AI
    Enhanced to handle multiple months and date patterns
    """
    import re
    from datetime import datetime, timedelta
    import pytz
    
    # Use IST timezone
    ist_tz = pytz.timezone('Asia/Kolkata')
    current_date = datetime.now(ist_tz)
    today = current_date.strftime('%Y-%m-%d')
    current_day = current_date.day
    current_month = current_date.month
    
    # Extract "on X" patterns from user message
    on_pattern = re.search(r'\bon\s+(\d+)\b', user_message.lower())
    
    if on_pattern:
        day_number = int(on_pattern.group(1))
        
        # If AI used today's date but user said "on X", fix it
        if ai_date == today and day_number != current_day:
            if 1 <= day_number <= 31:
                # Determine the target month based on context
                target_month = current_month
                target_year = current_date.year
                
                from calendar import monthrange
                current_month_max_day = monthrange(target_year, target_month)[1]
                
                # Check if the day makes sense in the current month context
                if day_number < current_day or day_number > current_month_max_day:
                    # Move to next month
                    target_month += 1
                    if target_month > 12:
                        target_month = 1
                        target_year += 1
                
                # Ensure day exists in target month
                max_day_in_month = monthrange(target_year, target_month)[1]
                
                if day_number <= max_day_in_month:
                    return f"{target_year}-{target_month:02d}-{day_number:02d}"
                else:
                    # Day doesn't exist in target month, try next month
                    target_month += 1
                    if target_month > 12:
                        target_month = 1
                        target_year += 1
                    max_day_in_month = monthrange(target_year, target_month)[1]
                    if day_number <= max_day_in_month:
                        return f"{target_year}-{target_month:02d}-{day_number:02d}"
    
    # Extract month + day patterns (e.g., "October 7", "Nov 15", "December 25")
    month_day_pattern = re.search(
        r'\b(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d+)\b',
        user_message.lower()
    )
    
    if month_day_pattern:
        month_name = month_day_pattern.group(1).lower()
        day_number = int(month_day_pattern.group(2))
        
        # Month name to number mapping
        month_map = {
            'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
            'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6,
            'july': 7, 'jul': 7, 'august': 8, 'aug': 8, 'september': 9, 'sep': 9,
            'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12
        }
        
        if month_name in month_map:
            target_month = month_map[month_name]
            target_year = current_date.year
            
            # If the month has passed, use next year
            if target_month < current_month or (target_month == current_month and day_number < current_day):
                target_year += 1
            
            # Validate day exists in target month
            from calendar import monthrange
            max_day_in_month = monthrange(target_year, target_month)[1]
            
            if 1 <= day_number <= max_day_in_month:
                return f"{target_year}-{target_month:02d}-{day_number:02d}"
    
    return ai_date


def check_event_conflicts(user_id, new_event_date, new_event_time, new_event_title):
    """
    Check for potential conflicts with existing events on the same date/time
    """
    try:
        conn = get_db_connection()
        if not conn:
            return []
            
        cursor = conn.cursor(dictionary=True)
        
        # Check for events on the same date
        query = """
        SELECT id, title, date, time, category 
        FROM events 
        WHERE user_id = %s AND date = %s AND done = FALSE
        ORDER BY time
        """
        
        cursor.execute(query, (user_id, new_event_date))
        existing_events = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        conflicts = []
        
        if existing_events:
            # Parse new event time
            new_hour, new_min = map(int, new_event_time.split(':'))
            new_minutes_total = new_hour * 60 + new_min
            
            for event in existing_events:
                existing_time = event['time']
                existing_hour, existing_min = map(int, existing_time.split(':'))
                existing_minutes_total = existing_hour * 60 + existing_min
                
                # Check if times are close (within 2 hours)
                time_diff = abs(new_minutes_total - existing_minutes_total)
                
                if time_diff <= 120:  # Within 2 hours
                    conflicts.append({
                        'id': event['id'],
                        'title': event['title'],
                        'time': existing_time,
                        'category': event['category'],
                        'time_diff_minutes': time_diff
                    })
        
        return conflicts
        
    except Exception as e:
        print(f"Error checking conflicts: {e}")
        return []


def create_conflict_warning_message(conflicts, new_event_title, new_event_date, new_event_time):
    """
    Generate a user-friendly conflict warning message
    """
    if not conflicts:
        return None
        
    warning = f"⚠️ **SCHEDULING CONFLICT DETECTED**\n\n"
    warning += f"You want to add: **{new_event_title}** on {new_event_date} at {new_event_time}\n\n"
    warning += f"But you already have:\n"
    
    for conflict in conflicts:
        time_diff = conflict['time_diff_minutes']
        if time_diff == 0:
            warning += f"• **{conflict['title']}** at {conflict['time']} (EXACT SAME TIME!)\n"
        elif time_diff <= 30:
            warning += f"• **{conflict['title']}** at {conflict['time']} (only {time_diff} minutes apart)\n"
        else:
            hours = time_diff // 60
            minutes = time_diff % 60
            if hours > 0:
                warning += f"• **{conflict['title']}** at {conflict['time']} ({hours}h {minutes}m apart)\n"
            else:
                warning += f"• **{conflict['title']}** at {conflict['time']} ({minutes} minutes apart)\n"
    
    warning += f"\n🤔 **Are you sure you want to add this event?**\n"
    warning += f"Reply 'yes' to confirm or 'no' to cancel."
    
    return warning


def get_user_events_for_deletion(user_id):
    """Get user's upcoming events for deletion analysis."""
    try:
        conn = get_db_connection()
        if not conn:
            return []
            
        cursor = conn.cursor()
        
        # Get events from today onwards (using IST)
        ist_tz = pytz.timezone('Asia/Kolkata')
        today = datetime.now(ist_tz).strftime('%Y-%m-%d')
        query = """
        SELECT id, title, description, date, time, category 
        FROM events 
        WHERE user_id = %s AND date >= %s AND done = 0
        ORDER BY date, time
        LIMIT 20
        """
        
        cursor.execute(query, (user_id, today))
        events = []
        
        for row in cursor.fetchall():
            events.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'date': row[3],
                'time': row[4],
                'category': row[5]
            })
        
        cursor.close()
        conn.close()
        
        return events
        
    except Error as e:
        print(f"Database error getting events for deletion: {e}")
        return []
    except Exception as e:
        print(f"Error getting events for deletion: {e}")
        return []


def delete_event_from_db(user_id, event_id):
    """Delete a specific event from the database."""
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Delete the event (with user_id check for security)
        query = "DELETE FROM events WHERE id = %s AND user_id = %s"
        cursor.execute(query, (event_id, user_id))
        
        deleted_rows = cursor.rowcount
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print(f"✅ Deleted event ID {event_id} for user {user_id}")
        return deleted_rows > 0
        
    except Error as e:
        print(f"Database error deleting event: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"Error deleting event: {e}")
        return False


def create_event_in_db(user_id, event_data):
    """Helper function to create a single event in the database with exact JSON format."""
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Validate and fix time format
        event_time = event_data.get('time', '09:00')
        if event_time == 'TBD' or not event_time or ':' not in event_time:
            event_time = '09:00'  # Default time
        
        # Ensure time is in HH:MM format
        if len(event_time.split(':')[0]) == 1:
            event_time = '0' + event_time  # Convert "9:00" to "09:00"
        
        event_data['time'] = event_time  # Update the event data
        
        # Calculate reminder_datetime based on reminder_setting using IST
        ist_tz = pytz.timezone('Asia/Kolkata')
        event_datetime_str = f"{event_data['date']} {event_time}"
        naive_event_datetime = datetime.strptime(event_datetime_str, '%Y-%m-%d %H:%M')
        event_datetime = ist_tz.localize(naive_event_datetime)
        
        # Parse reminder setting and calculate reminder_datetime
        reminder_setting = event_data.get('reminder_setting', '15 minutes')
        reminder_datetime = None
        
        if reminder_setting and reminder_setting != "No Reminder":
            if "minute" in reminder_setting:
                minutes = int(reminder_setting.split()[0])
                reminder_datetime = event_datetime - timedelta(minutes=minutes)
            elif "hour" in reminder_setting:
                hours = int(reminder_setting.split()[0])
                reminder_datetime = event_datetime - timedelta(hours=hours)
            elif "day" in reminder_setting:
                days = int(reminder_setting.split()[0])
                reminder_datetime = event_datetime - timedelta(days=days)
            else:
                # Default to 15 minutes
                reminder_datetime = event_datetime - timedelta(minutes=15)
        
        # Insert event into database
        query = """
        INSERT INTO events (user_id, title, description, category, date, time, done, reminder_setting, reminder_datetime)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            user_id,
            event_data['title'],
            event_data.get('description', ''),
            event_data.get('category', 'personal'),  # Default to personal if not specified
            event_data['date'],
            event_data['time'],
            0,  # done = False (0)
            reminder_setting,
            reminder_datetime.strftime('%Y-%m-%d %H:%M:%S') if reminder_datetime else None
        )
        
        cursor.execute(query, values)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print(f"✅ Event created (IST): {event_data['title']} on {event_data['date']} at {event_data['time']}")
        print(f"   Category: {event_data.get('category', 'personal')}")
        print(f"   Reminder: {reminder_setting} -> {reminder_datetime}")
        
        return True
        
    except Error as e:
        print(f"Database error creating event: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"Error creating event: {e}")
        return False


# --- PATTERN-BASED FALLBACK FUNCTIONS (Kept for backup) ---
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "user", "content": extraction_prompt}
                ],
                model="llama3-8b-8192",  # Try standard model if available
                temperature=0.1
            )
            response_text = chat_completion.choices[0].message.content.strip()
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                event_details = json.loads(json_match.group())
        except Exception as e:
            print(f"Groq extraction failed: {e}")
            # If Groq fails too, try another model
            try:
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {"role": "user", "content": extraction_prompt}
                    ],
                    model="llama-3.1-8b-instant",  # Alternative Groq model
                    temperature=0.1
                )
                response_text = chat_completion.choices[0].message.content.strip()
                
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    event_details = json.loads(json_match.group())
            except Exception as e2:
                print(f"Groq alternative model also failed: {e2}")
    
    if not event_details or 'events' not in event_details:
        # PATTERN-BASED FALLBACK: Create events even when AI APIs fail
        print("AI APIs failed - attempting pattern-based event extraction")
        event_details = extract_events_with_patterns(user_message)
        
        if not event_details or 'events' not in event_details or len(event_details['events']) == 0:
            return False, "Could not extract event details"
    
    # Create all events in the database
    created_events = []
    conn = get_db_connection()
    
    if not conn:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        
        for event in event_details['events']:
            if all(key in event for key in ['title', 'date', 'time']):
                query = "INSERT INTO events (user_id, title, description, date, time, done) VALUES (%s, %s, %s, %s, %s, %s)"
                values = (
                    user_id,
                    event['title'],
                    event.get('description', ''),
                    event['date'],
                    event['time'],
                    0
                )
                cursor.execute(query, values)
                created_events.append(event['title'])
        
        conn.commit()
        
        if created_events:
            return True, f"Created {len(created_events)} events: {', '.join(created_events)}"
        else:
            return False, "No valid events to create"
            
    except Error as e:
        print(f"Database error creating events: {e}")
        return False, f"Database error: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def extract_events_with_patterns(user_message):
    """
    Pattern-based event extraction as fallback when AI APIs are unavailable.
    Extracts events using regex patterns and basic natural language processing.
    """
    from datetime import datetime, timedelta
    import re
    
    # Normalize the message
    message_lower = user_message.lower()
    
    # Date extraction and parsing (using IST)
    ist_tz = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ist_tz)
    date_map = {
        'today': today.strftime('%Y-%m-%d'),
        'tomorrow': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
        'monday': get_next_weekday(today, 0).strftime('%Y-%m-%d'),
        'tuesday': get_next_weekday(today, 1).strftime('%Y-%m-%d'),
        'wednesday': get_next_weekday(today, 2).strftime('%Y-%m-%d'),
        'thursday': get_next_weekday(today, 3).strftime('%Y-%m-%d'),
        'friday': get_next_weekday(today, 4).strftime('%Y-%m-%d'),
        'saturday': get_next_weekday(today, 5).strftime('%Y-%m-%d'),
        'sunday': get_next_weekday(today, 6).strftime('%Y-%m-%d'),
    }
    
    # Extract date
    event_date = today.strftime('%Y-%m-%d')  # Default to today
    for day_word, day_date in date_map.items():
        if day_word in message_lower:
            event_date = day_date
            break
    
    events = []
    
    # Pattern 1: Look for multiple events with "and" - "meeting at 10am and lunch at 1pm"
    and_pattern = r'(\w+(?:\s+\w+)*?)\s+at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s+and\s+(\w+(?:\s+\w+)*?)\s+at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)'
    and_matches = re.findall(and_pattern, message_lower)
    
    if and_matches:
        for match in and_matches:
            title1, time1, title2, time2 = match
            
            # Parse first event
            parsed_time1 = parse_time(time1)
            if parsed_time1:
                events.append({
                    "title": clean_title(title1),
                    "date": event_date,
                    "time": parsed_time1,
                    "description": f"Event created from: {user_message}"
                })
            
            # Parse second event
            parsed_time2 = parse_time(time2)
            if parsed_time2:
                events.append({
                    "title": clean_title(title2),
                    "date": event_date,
                    "time": parsed_time2,
                    "description": f"Event created from: {user_message}"
                })
    
    # Pattern 2: Look for comma-separated events - "gym at 7am, dentist at 9am, call at 2pm"
    if not events:
        comma_pattern = r'(\w+(?:\s+\w+)*?)\s+at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)'
        comma_matches = re.findall(comma_pattern, message_lower)
        
        if len(comma_matches) > 1:
            for title, time in comma_matches:
                parsed_time = parse_time(time)
                if parsed_time:
                    events.append({
                        "title": clean_title(title),
                        "date": event_date,
                        "time": parsed_time,
                        "description": f"Event created from: {user_message}"
                    })
    
    # Pattern 3: Single event patterns
    if not events:
        single_patterns = [
            r'(?:i have|got|scheduled|planning)\s+(?:a\s+)?(\w+(?:\s+\w+)*?)\s+at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',
            r'(\w+(?:\s+\w+)*?)\s+(?:appointment|meeting|call|session)\s+at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',
            r'(\w+(?:\s+\w+)*?)\s+at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',
        ]
        
        for pattern in single_patterns:
            matches = re.findall(pattern, message_lower)
            if matches:
                for match in matches:
                    if isinstance(match, tuple) and len(match) == 2:
                        title, time = match
                        parsed_time = parse_time(time)
                        if parsed_time:
                            clean_event_title = clean_title(title)
                            # Avoid duplicates
                            if not any(event['title'] == clean_event_title and event['time'] == parsed_time for event in events):
                                events.append({
                                    "title": clean_event_title,
                                    "date": event_date,
                                    "time": parsed_time,
                                    "description": f"Event created from: {user_message}"
                                })
                break  # Found matches, don't try other patterns
    
    return {"events": events} if events else {"events": []}

def parse_time(time_str):
    """Parse time string and return formatted 24-hour time"""
    import re
    
    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', time_str.lower())
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        period = time_match.group(3)
        
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
        elif not period and hour < 8:  # Assume PM for times before 8 without AM/PM
            hour += 12
            
        return f"{hour:02d}:{minute:02d}"
    return None

def clean_title(title):
    """Clean and format the event title"""
    # Remove common filler words
    title = re.sub(r'\b(i have|got|scheduled|planning|a|an|the|and|then|also)\b', '', title.lower()).strip()
    
    # Handle special cases
    title_mappings = {
        'meeting': 'Meeting',
        'lunch': 'Lunch',
        'dinner': 'Dinner',
        'gym': 'Gym workout',
        'dentist': 'Dentist appointment',
        'doctor': 'Doctor appointment',
        'call': 'Phone call',
        'conference': 'Conference',
        'appointment': 'Appointment',
    }
    
    # Check if title matches common event types
    for key, value in title_mappings.items():
        if key in title.lower():
            return value
    
    # Otherwise capitalize words
    return ' '.join(word.capitalize() for word in title.split() if word)

def get_next_weekday(current_date, weekday):
    """Get the next occurrence of a weekday (0=Monday, 6=Sunday)"""
    days_ahead = weekday - current_date.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return current_date + timedelta(days_ahead)


@ai_scheduler_bp.route("/api/ai/scheduler/test", methods=['POST'])
def ai_test_no_auth():
    """
    TEST ENDPOINT: AI chat without authentication (for debugging)
    Remove this in production!
    """
    user_message = request.json.get("message")
    user_id = request.json.get("user_id")
    if not user_message or not user_id:
        return jsonify({"error": "No message or user_id provided"}), 400

    try:
        print(f"[DEBUG] Testing message: '{user_message}' for user: {user_id}")
        result = detect_and_create_events(user_message, user_id)
        if isinstance(result, tuple):
            success, message = result
            response_data = {
                "success": success,
                "message": message,
                "user_message": user_message,
                "user_id": user_id,
                "test_mode": True,
                "timestamp": datetime.now().isoformat()
            }
            if success:
                if "deleted" in message.lower():
                    response_data["action"] = "deletion"
                    response_data["events_deleted"] = message
                elif "created" in message.lower() or "event" in message.lower():
                    response_data["action"] = "creation" 
                    response_data["events_created"] = message
            
            return jsonify(response_data)
        else:
            return jsonify({
                "success": True,
                "message": "Events processed",
                "events_created": result,
                "user_message": user_message,
                "user_id": user_id,
                "test_mode": True
            })

    except Exception as e:
        print(f"An error occurred in ai_test_no_auth: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Debug error: {str(e)}"}), 500


# --- HELPER FUNCTION TO GET SCHEDULE ---
def _get_user_schedule(user_id):
    """Fetches the user's upcoming events for the next 7 days from the database."""
    conn = get_db_connection()
    if not conn:
        return "Database connection failed."
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Get events from today onwards for the next 7 days
        today = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        query = "SELECT title, date, time FROM events WHERE user_id = %s AND date >= %s AND date <= %s AND done = FALSE ORDER BY date, time"
        cursor.execute(query, (user_id, today, end_date))
        events = cursor.fetchall()
        
        if not events:
            return "The user's schedule for the next 7 days is clear."
            
        # Format the events into a clean string for the AI
        schedule_string = "Here is the user's schedule for the next 7 days:\n"
        for event in events:
            schedule_string += f"- On {event['date']} at {event['time']}: {event['title']}\n"
        return schedule_string
        
    except Error as e:
        print(f"Database error fetching schedule: {e}")
        return "Could not retrieve schedule due to a database error."
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@ai_scheduler_bp.route("/api/ai/scheduler/chat", methods=['POST'])
def ai_chat_automatic():
    """
    Enhanced AI chat with AUTOMATIC multiple event detection and creation.
    This route processes messages and automatically creates calendar events when detected.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        user_id = data.get("user_id")
        user_message = data.get("message")

        if not user_message or not user_id:
            return jsonify({"error": "No message or user_id provided"}), 400

        # Note: Conflict handling removed for stateless operation
        
        # 1. FIRST: Check for automatic event creation (including multiple events)
        event_created, creation_message = detect_and_create_events(user_message, user_id)
        
        # Handle conflict warnings
        if not event_created and "SCHEDULING CONFLICT DETECTED" in creation_message:
            # This is a conflict warning - we need to store the pending event for user confirmation
            # For now, just return the conflict message
            return jsonify({
                "reply": creation_message,
                "events_created": False,
                "conflict_detected": True
            })
        
        # 2. Get updated schedule after potential event creation
        schedule_context = _get_user_schedule(user_id)
        
        # 3. Prepare chat history
        history = session.get('chat_history', [])
        history.append({'role': 'user', 'parts': [{'text': user_message}]})

        # 4. Create enhanced system prompt
        system_prompt = f"""
        You are Scout, a friendly and professional AI assistant integrated into the HelpScout application.
        Your goal is to help users organize their work, plan tasks, and manage schedules effectively.
        
        IMPORTANT: You have AUTOMATIC event detection enabled. When users mention events naturally in conversation 
        (like "I have a meeting at 10am and lunch at 1pm tomorrow"), you automatically create them in their calendar.
        
        - Be concise, encouraging, and clear in your responses.
        - When asked to generate lists, always use markdown bullet points.
        - Use the current date of {datetime.now().strftime('%A, %Y-%m-%d')} for any time-related questions.
        - You can handle multiple events in a single message automatically.

        ---
        CURRENT SCHEDULE:
        {schedule_context}
        ---
        """
        
        # 5. Generate AI response with 3-tier fallback (Groq first since it's working)
        ai_response_text = None
        
        # Try Groq first (fastest and currently working)
        if groq_client:
            try:
                # Convert history to Groq format
                groq_messages = [{"role": "system", "content": system_prompt}]
                for msg in history:
                    if msg['role'] == 'user':
                        groq_messages.append({"role": "user", "content": msg['parts'][0]['text']})
                    elif msg['role'] == 'model':
                        groq_messages.append({"role": "assistant", "content": msg['parts'][0]['text']})
                
                chat_completion = groq_client.chat.completions.create(
                    messages=groq_messages,
                    model="llama-3.1-8b-instant",  # Using the working model
                    temperature=0.3,
                    max_tokens=1000
                )
                ai_response_text = chat_completion.choices[0].message.content
                print("✓ Used Groq API for chat response")
            except Exception as e:
                print(f"Groq API failed: {e}")
        
        # Fallback to Gemini if Groq fails
        if not ai_response_text:
            try:
                if api_key:
                    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)
                    chat = model.start_chat(history=history)
                    response = chat.send_message(user_message)
                    ai_response_text = response.text
                    print("✓ Used Gemini API as fallback for chat response")
            except Exception as e:
                print(f"Gemini API failed: {e}")
        
        # Final fallback to Cohere if both fail
        if not ai_response_text and co:
            try:
                # Prepare chat history for Cohere
                cohere_messages = []
                for msg in history:
                    if msg['role'] == 'user':
                        cohere_messages.append({"role": "user", "content": msg['parts'][0]['text']})
                    elif msg['role'] == 'model':
                        cohere_messages.append({"role": "assistant", "content": msg['parts'][0]['text']})
                
                response = co.chat(
                    message=f"{system_prompt}\n\nUser: {user_message}\n\nAssistant:",
                    max_tokens=1000,
                    temperature=0.3
                )
                ai_response_text = response.text.strip()
                print("✓ Used Cohere API as final fallback for chat response")
            except Exception as e:
                print(f"Cohere API failed: {e}")
        
        # If all APIs failed
        if not ai_response_text:
            return jsonify({"error": "All AI services are currently unavailable. Please try again later."}), 503

        # 6. Add event creation confirmation to response if events were created
        if event_created:
            ai_response_text = f"✅ {creation_message}\n\n{ai_response_text}"

        # 7. Update chat history
        history.append({'role': 'model', 'parts': [{'text': ai_response_text}]})
        session['chat_history'] = history
        session.modified = True

        return jsonify({
            "reply": ai_response_text,
            "events_created": event_created,
            "creation_message": creation_message if event_created else None
        })

    except Exception as e:
        print(f"An error occurred in ai_chat_automatic: {e}")
        return jsonify({"error": "An error occurred while processing your message."}), 500


@ai_scheduler_bp.route("/api/<user_id>/ai/add-task", methods=['POST'])
def ai_add_task(user_id):
    """
    AI-powered task creation endpoint that intelligently processes and enhances task data
    before saving it to the database. Auto-generates reminder datetime based on reminder_setting.
    """
    try:
        # Check if request has JSON data
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.json
        
        # Check if JSON data is empty
        if not data:
            return jsonify({"error": "Request body cannot be empty"}), 400
        
        # Validate required fields with detailed messages
        required_fields = ['title', 'description', 'category', 'date', 'time', 'reminder_setting']
        missing_fields = []
        
        for field in required_fields:
            if field not in data or not data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "missing_fields": missing_fields,
                "required_fields": required_fields,
                "message": f"Please provide: {', '.join(missing_fields)}"
            }), 400
        
        # Extract task data
        title = data.get('title')
        description = data.get('description') 
        category = data.get('category')
        date = data.get('date')
        time = data.get('time')
        reminder_setting = data.get('reminder_setting')
        done = data.get('done', False)
        
        # Validate date and time format and localize to IST
        try:
            ist_tz = pytz.timezone('Asia/Kolkata')
            naive_task_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            task_datetime = ist_tz.localize(naive_task_datetime)
        except ValueError:
            return jsonify({"error": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time (IST)"}), 400
        
        # AI Enhancement: Use AI to enhance task description and category if needed
        enhanced_data = ai_enhance_task_data(title, description, category)
        
        if enhanced_data.get('success'):
            description = enhanced_data.get('enhanced_description', description)
            category = enhanced_data.get('enhanced_category', category)
        
        # Calculate reminder datetime based on reminder_setting
        reminder_datetime = calculate_reminder_datetime(date, time, reminder_setting)
        
        if not reminder_datetime:
            return jsonify({"error": "Invalid reminder_setting format. Use format like '15 minutes', '1 hour', '2 days'"}), 400
        
        # Save to database
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        
        query = """
            INSERT INTO events 
            (user_id, title, description, category, date, time, done, 
             reminder_setting, reminder_datetime, reminde1, reminde2, reminde3, reminde4)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            user_id, title, description, category, date, time, done,
            reminder_setting, reminder_datetime, False, False, False, False
        )
        
        cursor.execute(query, values)
        conn.commit()
        task_id = cursor.lastrowid
        
        # Return success response with generated reminder datetime
        return jsonify({
            "success": True,
            "message": "AI task added successfully!",
            "task_id": task_id,
            "task_data": {
                "user_id": user_id,
                "title": title,
                "description": description,
                "category": category,
                "date": date,
                "time": time,
                "done": done,
                "reminder_setting": reminder_setting,
                "reminder_datetime": reminder_datetime
            },
            "ai_enhanced": enhanced_data.get('success', False)
        }), 201
        
    except Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        if 'conn' in locals() and conn and conn.is_connected():
            cursor.close()
            conn.close()


def calculate_reminder_datetime(date, time, reminder_setting):
    """
    Calculate reminder datetime based on task datetime and reminder setting.
    Uses Indian Standard Time (IST) for all calculations.
    
    Args:
        date (str): Task date in YYYY-MM-DD format
        time (str): Task time in HH:MM format
        reminder_setting (str): Reminder setting like "15 minutes", "1 hour", "2 days"
    
    Returns:
        str: Formatted reminder datetime string in IST or None if invalid
    """
    try:
        # Parse task datetime and localize to IST
        ist_tz = pytz.timezone('Asia/Kolkata')
        naive_task_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        task_datetime = ist_tz.localize(naive_task_datetime)
        
        # Parse reminder setting
        parts = reminder_setting.lower().split()
        if len(parts) != 2:
            return None
            
        value_str, unit = parts
        try:
            value = int(value_str)
        except ValueError:
            return None
        
        # Calculate time delta
        delta = timedelta()
        if "minute" in unit:
            delta = timedelta(minutes=value)
        elif "hour" in unit:
            delta = timedelta(hours=value)
        elif "day" in unit:
            delta = timedelta(days=value)
        elif "week" in unit:
            delta = timedelta(weeks=value)
        else:
            return None
        
        # Calculate reminder datetime (subtract delta from task datetime)
        reminder_datetime = task_datetime - delta
        
        # Return formatted string
        return reminder_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
    except Exception as e:
        print(f"Error calculating reminder datetime: {e}")
        return None


def ai_enhance_task_data(title, description, category):
    """
    Use AI to enhance task data - improve description and validate/suggest category.
    
    Args:
        title (str): Task title
        description (str): Task description
        category (str): Task category
    
    Returns:
        dict: Enhancement results with enhanced_description and enhanced_category
    """
    try:
        enhancement_prompt = f"""
        You are a professional productivity assistant. Enhance this task data to make it extremely useful, actionable, and well-organized:
        
        Title: "{title}"
        Description: "{description}"
        Category: "{category}"
        
        TASK: Create an enhanced version that is:
        1. MORE DETAILED: Add specific, actionable details that make the task clearer
        2. MORE PROFESSIONAL: Use clear, concise, professional language
        3. MORE HELPFUL: Include context, tips, or important reminders when relevant
        4. MORE STRUCTURED: Organize information logically
        
        ENHANCEMENT RULES:
        - For gym/fitness: Include workout type, duration, body parts, or specific exercises
        - For meetings: Include purpose, attendees, agenda items, or preparation needed
        - For appointments: Include location, what to bring, preparation required
        - For work tasks: Include deliverables, deadlines, priority level, or next steps
        - For personal tasks: Include specific steps, materials needed, or time estimates
        - For health tasks: Include preparation, what to expect, or follow-up needed
        - For shopping: Include specific items, budget, store locations, or alternatives
        - For travel: Include booking details, documents needed, or itinerary items
        
        CATEGORY VALIDATION:
        Choose the MOST APPROPRIATE category from these options:
        - "work" - Professional tasks, meetings, projects, deadlines
        - "personal" - General personal activities, self-care, hobbies
        - "health" - Medical appointments, wellness, mental health
        - "fitness" - Exercise, gym, sports, physical activities
        - "education" - Learning, courses, training, skill development
        - "shopping" - Purchasing items, errands, market visits
        - "social" - Friends, family time, parties, social events
        - "travel" - Trips, bookings, itinerary planning
        - "maintenance" - Home repair, vehicle service, equipment care
        - "finance" - Banking, investments, bill payments, budgeting
        
        EXAMPLES OF GOOD ENHANCEMENTS:
        
        Input: "Gym Session" / "Go to gym" / "fitness"
        Output: "Complete 60-minute full-body workout including 20 minutes cardio warm-up, strength training focusing on major muscle groups (chest, back, legs), and 10 minutes cool-down stretching. Bring water bottle, towel, and workout playlist."
        
        Input: "Doctor Appointment" / "See doctor" / "health"  
        Output: "Annual health checkup with Dr. Smith including blood work review, vital signs check, and discussion of any health concerns. Arrive 15 minutes early, bring insurance card, current medications list, and prepared questions about health goals."
        
        Input: "Team Meeting" / "Meeting with team" / "work"
        Output: "Weekly team standup meeting to review project progress, discuss blockers, and align on upcoming sprint goals. Review previous week's deliverables, prepare status updates, and come with questions or concerns to address with the team."
        
        Return ONLY a JSON object with this exact format:
        {{
            "enhanced_description": "detailed, actionable, and professional description here",
            "enhanced_category": "most_appropriate_category_here"
        }}
        """
        
        enhanced_data = None
        
        # Try Groq first (fastest and reliable)
        if groq_client:
            try:
                chat_completion = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": enhancement_prompt}],
                    model="llama-3.1-8b-instant",
                    temperature=0.4,  # Slightly higher for more creativity
                    max_tokens=500    # More tokens for detailed descriptions
                )
                response_text = chat_completion.choices[0].message.content.strip()
                
                # Clean up response (remove markdown formatting if present)
                if response_text.startswith('```json'):
                    response_text = response_text.replace('```json', '').replace('```', '').strip()
                
                enhanced_data = json.loads(response_text)
                print("✓ Used Groq API for enhanced task description")
            except Exception as e:
                print(f"Groq enhancement failed: {e}")
        
        # Fallback to Gemini
        if not enhanced_data and api_key and genai:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(enhancement_prompt)
                response_text = response.text.strip()
                
                # Clean up response (remove markdown formatting if present)
                if response_text.startswith('```json'):
                    response_text = response_text.replace('```json', '').replace('```', '').strip()
                elif response_text.startswith('```'):
                    response_text = response_text.replace('```', '').strip()
                
                enhanced_data = json.loads(response_text)
                print("✓ Used Gemini API for enhanced task description")
            except Exception as e:
                print(f"Gemini enhancement failed: {e}")
        
        # Fallback to Cohere
        if not enhanced_data and co:
            try:
                response = co.chat(
                    message=enhancement_prompt,
                    max_tokens=500,
                    temperature=0.4
                )
                response_text = response.text.strip()
                
                # Clean up response
                if response_text.startswith('```json'):
                    response_text = response_text.replace('```json', '').replace('```', '').strip()
                
                enhanced_data = json.loads(response_text)
                print("✓ Used Cohere API for enhanced task description")
            except Exception as e:
                print(f"Cohere enhancement failed: {e}")
        
        # Validate the enhanced data
        if enhanced_data and 'enhanced_description' in enhanced_data and 'enhanced_category' in enhanced_data:
            # Ensure description is significantly better than original
            original_length = len(description.split())
            enhanced_length = len(enhanced_data['enhanced_description'].split())
            
            # If enhancement is much better, use it
            if enhanced_length >= original_length and len(enhanced_data['enhanced_description']) > len(description):
                return {
                    "success": True,
                    "enhanced_description": enhanced_data['enhanced_description'],
                    "enhanced_category": enhanced_data['enhanced_category'],
                    "improvement_ratio": enhanced_length / max(original_length, 1)
                }
            else:
                # Fallback to basic enhancement if AI didn't improve much
                fallback_description = create_fallback_enhancement(title, description, category)
                return {
                    "success": True,
                    "enhanced_description": fallback_description,
                    "enhanced_category": validate_category(category),
                    "fallback_used": True
                }
        else:
            # Use fallback enhancement if AI completely failed
            fallback_description = create_fallback_enhancement(title, description, category)
            return {
                "success": True,
                "enhanced_description": fallback_description,
                "enhanced_category": validate_category(category),
                "fallback_used": True
            }
            
    except Exception as e:
        print(f"AI enhancement error: {e}")
        # Always provide some enhancement, even if AI fails
        fallback_description = create_fallback_enhancement(title, description, category)
        return {
            "success": True,
            "enhanced_description": fallback_description,
            "enhanced_category": validate_category(category),
            "error": str(e),
            "fallback_used": True
        }


def create_fallback_enhancement(title, description, category):
    """
    Create a basic enhancement when AI fails
    """
    enhanced = description
    
    # Add title context if description doesn't include it
    if title.lower() not in description.lower():
        enhanced = f"{title}: {description}"
    
    # Add category-specific enhancements
    category_lower = category.lower()
    
    if category_lower in ['gym', 'fitness', 'workout']:
        if 'workout' not in enhanced.lower() and 'exercise' not in enhanced.lower():
            enhanced = f"{enhanced}. Remember to bring water bottle and towel for the workout session."
    
    elif category_lower in ['meeting', 'work']:
        if 'meeting' in title.lower() or 'meeting' in enhanced.lower():
            enhanced = f"{enhanced}. Prepare agenda items and review relevant materials beforehand."
    
    elif category_lower in ['doctor', 'health', 'appointment']:
        if 'appointment' in enhanced.lower():
            enhanced = f"{enhanced}. Bring insurance card and list of current medications."
    
    elif category_lower in ['shopping', 'grocery']:
        enhanced = f"{enhanced}. Make a list of needed items and check for any available discounts."
    
    elif category_lower in ['travel', 'trip']:
        enhanced = f"{enhanced}. Verify all necessary documents and bookings are ready."
    
    # Add time estimate if not present
    if 'minute' not in enhanced and 'hour' not in enhanced:
        if category_lower in ['gym', 'fitness']:
            enhanced = f"{enhanced} (Estimated duration: 1 hour)"
        elif category_lower in ['meeting']:
            enhanced = f"{enhanced} (Estimated duration: 30-60 minutes)"
        elif category_lower in ['appointment']:
            enhanced = f"{enhanced} (Plan for 30 minutes plus travel time)"
    
    return enhanced


def validate_category(category):
    """
    Validate and potentially correct the category
    """
    valid_categories = {
        'work', 'personal', 'health', 'fitness', 'education', 
        'shopping', 'social', 'travel', 'maintenance', 'finance'
    }
    
    category_lower = category.lower()
    
    # Direct matches
    if category_lower in valid_categories:
        return category_lower
    
    # Category mappings
    category_mappings = {
        'gym': 'fitness',
        'workout': 'fitness',
        'exercise': 'fitness',
        'doctor': 'health',
        'medical': 'health',
        'appointment': 'health',
        'meeting': 'work',
        'business': 'work',
        'office': 'work',
        'project': 'work',
        'grocery': 'shopping',
        'market': 'shopping',
        'buy': 'shopping',
        'purchase': 'shopping',
        'friend': 'social',
        'family': 'social',
        'party': 'social',
        'vacation': 'travel',
        'trip': 'travel',
        'flight': 'travel',
        'hotel': 'travel',
        'repair': 'maintenance',
        'fix': 'maintenance',
        'service': 'maintenance',
        'bank': 'finance',
        'money': 'finance',
        'bill': 'finance',
        'payment': 'finance',
        'learn': 'education',
        'study': 'education',
        'course': 'education',
        'training': 'education'
    }
    
    # Check if category matches any mapping
    for key, value in category_mappings.items():
        if key in category_lower:
            return value
    
    # Default to personal if no match found
    return 'personal'