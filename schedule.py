from flask import Blueprint, jsonify, request
from database import get_db_connection
from mysql.connector import Error
from datetime import datetime

schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route("/api/<user_id>/tasks/all")
def get_all_tasks(user_id):
    """Fetches ALL tasks (pending and completed) for the logged-in user."""
    # Stateless: user_id comes from path
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
        
    try:
        cursor = conn.cursor(dictionary=True)
        # Fetches all tasks and orders them by date and time
        query = """
            SELECT id, title, description, category, date, time, done, reminder_setting 
            FROM events 
            WHERE user_id = %s
            ORDER BY date, time
        """
        cursor.execute(query, (user_id,))
        tasks = cursor.fetchall()
        return jsonify(tasks)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@schedule_bp.route("/api/<user_id>/schedule/events/month_view")
def get_events_for_month(user_id):
    """
    Fetches days with pending tasks and days with only completed tasks 
    for a given month and year.
    """
    # Stateless: user_id comes from path
    year = request.args.get('year')
    month = request.args.get('month')

    if not year or not month:
        return jsonify({"error": "Year and month parameters are required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        date_pattern = f"{year}-{int(month):02d}-%"
        cursor.execute("SELECT date, done FROM events WHERE user_id = %s AND date LIKE %s", (user_id, date_pattern))
        events = cursor.fetchall()

        events_by_day = {}
        for event in events:
            day = int(event['date'].split('-')[2])
            if day not in events_by_day:
                events_by_day[day] = {'hasPending': False, 'hasCompleted': False}
            if event['done']:
                events_by_day[day]['hasCompleted'] = True
            else:
                events_by_day[day]['hasPending'] = True

        return jsonify(events_by_day)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()