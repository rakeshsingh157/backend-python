import os
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
from database import get_db_connection # Make sure you can import your DB connection
from mysql.connector import Error
from datetime import datetime, timedelta

# Load environment variables with explicit path
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

ai_assistant_bp = Blueprint('ai_assistant', __name__)

# Try to load API key from environment, with fallback
api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
if not api_key:
    # Fallback API key
    api_key = "AIzaSyDV4XXwema9MvK0r5Knkhh_GDudB9cU7Io"

if api_key:
    genai.configure(api_key=api_key)

# --- NEW HELPER FUNCTION TO GET SCHEDULE ---
def _get_user_schedule(user_id):
    """Fetches the user's upcoming events for the next 7 days from the database."""
    conn = get_db_connection()
    if not conn:
        return "Database connection failed."
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Get events from today onwards for the next 7 days with more details
        today = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        query = """SELECT title, description, date, time, category, reminder_setting 
                   FROM events 
                   WHERE user_id = %s AND date >= %s AND date <= %s AND done = FALSE 
                   ORDER BY date, time"""
        cursor.execute(query, (user_id, today, end_date))
        events = cursor.fetchall()
        
        if not events:
            return "The user's schedule for the next 7 days is completely clear - perfect for planning new activities!"
            
        # Format the events into a detailed string for the AI
        schedule_string = "📅 USER'S CURRENT SCHEDULE (Next 7 Days):\n\n"
        current_date = None
        
        for event in events:
            # Group by date for better readability
            if event['date'] != current_date:
                current_date = event['date']
                # Format date nicely
                event_date = datetime.strptime(str(event['date']), '%Y-%m-%d')
                day_name = event_date.strftime('%A')
                formatted_date = event_date.strftime('%B %d, %Y')
                schedule_string += f"**{day_name}, {formatted_date}:**\n"
            
            # Format time
            time_str = str(event['time'])
            category = event.get('category', 'general')
            description = event.get('description', '')
            
            schedule_string += f"  • {time_str} - {event['title']}"
            if category and category != 'general':
                schedule_string += f" [{category}]"
            if description and len(description.strip()) > 0:
                schedule_string += f"\n    Description: {description[:100]}{'...' if len(description) > 100 else ''}"
            schedule_string += "\n"
        
        schedule_string += f"\n💡 Schedule Analysis: {len(events)} events planned. Look for gaps and potential conflicts when suggesting new activities."
        return schedule_string
        
    except Error as e:
        print(f"Database error fetching schedule: {e}")
        return "Could not retrieve schedule due to a database error."
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@ai_assistant_bp.route("/api/<user_id>/ai/chat", methods=['POST'])
def ai_chat(user_id):
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        # 1. Get the user's schedule from the database
        schedule_context = _get_user_schedule(user_id)

        # Stateless: omit server-side chat history; clients should manage context
        history = []
        history.append({'role': 'user', 'parts': [{'text': user_message}]})

        # 2. Create a dynamic system prompt including the schedule context
        system_prompt = f"""
        You are Scout, a highly intelligent project management assistant integrated into the HelpScout application.
        Your goal is to help users organize their work, plan tasks, and manage schedules effectively.

        CORE CAPABILITIES:
        - Analyze user schedules for conflicts and overlaps
        - Suggest optimal timing for new events
        - Provide smart recommendations based on existing commitments
        - Help resolve scheduling conflicts with creative solutions
        - Be proactive about time management and productivity

        CONFLICT DETECTION & RESOLUTION:
        - Always check for time conflicts when users mention new events
        - If conflicts exist, suggest alternative times or solutions
        - Consider travel time between events when relevant
        - Warn about back-to-back scheduling issues
        - Suggest buffer time for important meetings

        SMART SUGGESTIONS:
        - Recommend best times for different types of activities
        - Group similar tasks together for efficiency
        - Suggest breaks and rest periods
        - Consider user's energy levels throughout the day
        - Propose realistic time estimates for tasks

        RESPONSE STYLE:
        - Be concise, encouraging, and actionable
        - Use markdown bullet points for lists
        - Highlight conflicts with ⚠️ warnings
        - Use ✅ for good scheduling choices
        - Use 💡 for smart suggestions
        - Current date reference: {datetime.now().strftime('%A, %Y-%m-%d')}

        ---
        CURRENT SCHEDULE CONTEXT:
        {schedule_context}
        ---

        INSTRUCTIONS:
        - Always reference the user's existing schedule when making suggestions
        - Proactively identify potential conflicts in your responses
        - Offer multiple alternatives when conflicts are detected
        - Be specific about timing and duration recommendations
        """
        
        model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=system_prompt)
        chat = model.start_chat(history=history)
        response = chat.send_message(user_message)
        ai_response_text = response.text

        history.append({'role': 'model', 'parts': [{'text': ai_response_text}]})

        return jsonify({"reply": ai_response_text})

    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        return jsonify({"error": "An error occurred while communicating with the AI assistant."}), 500
