
from flask import Blueprint, request, jsonify
import os
import traceback
import mysql.connector
from mysql.connector import Error
from ai_scheduler import AIScheduler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ai_bp = Blueprint('ai', __name__)

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
    except Error as e:
        print(f"❌ DB Connection Error: {e}")
        return None

@ai_bp.route('/api/<string:user_id>/ai/generate-schedule', methods=['POST'])
def generate_schedule(user_id):
    
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'message': 'Prompt is required'}), 400

    try:
        ai_scheduler = AIScheduler()
        tasks = ai_scheduler.generate_tasks(prompt)
        return jsonify(tasks), 200
    except Exception as e:
        # Temporarily return detailed error for debugging
        return jsonify({'message': 'Failed to generate tasks from AI.', 'error': str(e), 'error_type': type(e).__name__}), 500

@ai_bp.route('/api/<string:user_id>/ai/add-task', methods=['POST'])
def add_ai_task_to_schedule(user_id):

    data = request.json
    title = data.get('title')
    description = data.get('description')
    category = data.get('category')
    date = data.get('date')
    time = data.get('time')
    reminder_setting = data.get('reminder')

    if not all([title, description, category, date, time, reminder_setting]):
        return jsonify({'message': 'All task fields are required'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'message': 'Database connection error'}), 500

    cursor = conn.cursor()
    try:
        query = (
            """
            INSERT INTO events 
            (user_id, title, description, category, date, time, done, reminder_setting)
            VALUES (%s, %s, %s, %s, %s, %s, FALSE, %s)
            """
        )
        values = (user_id, title, description, category, date, time, reminder_setting)
        cursor.execute(query, values)
        conn.commit()
        return jsonify({'message': 'Task added to schedule successfully'}), 201
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'message': f'Failed to add task: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

