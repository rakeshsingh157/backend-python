from flask import Flask, Blueprint, request, jsonify

# Create a minimal AI blueprint for testing
ai_bp = Blueprint('ai', __name__)

class SimpleAIScheduler:
    """Simple mock AI scheduler for testing"""
    
    def generate_tasks(self, prompt):
        """Generate mock tasks"""
        return {
            "success": True,
            "tasks": [
                {
                    "title": f"Task from: {prompt[:30]}...",
                    "description": "Mock generated task",
                    "date": "2025-09-30",
                    "time": "10:00",
                    "category": "generated"
                }
            ]
        }

@ai_bp.route('/api/<string:user_id>/ai/generate-schedule', methods=['POST'])
def generate_schedule(user_id):
    try:
        data = request.json
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({'message': 'Prompt is required'}), 400

        ai_scheduler = SimpleAIScheduler()
        tasks = ai_scheduler.generate_tasks(prompt)
        return jsonify(tasks), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@ai_bp.route('/api/<string:user_id>/ai/add-task', methods=['POST'])
def add_ai_task_to_schedule(user_id):
    try:
        data = request.json
        title = data.get('title')
        description = data.get('description')
        category = data.get('category')
        date = data.get('date')
        time = data.get('time')
        reminder_setting = data.get('reminder')

        if not all([title, description, category, date, time, reminder_setting]):
            return jsonify({'message': 'All task fields are required'}), 400

        # Mock successful response
        return jsonify({'message': f'Task "{title}" added successfully for user {user_id}'}), 201
    except Exception as e:
        return jsonify({'message': f'Failed to add task: {e}'}), 500

# Test app
app = Flask(__name__)
app.register_blueprint(ai_bp)

if __name__ == '__main__':
    print("🚀 Starting minimal AI test server on port 5003...")
    app.run(debug=True, port=5003)