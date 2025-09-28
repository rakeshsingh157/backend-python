from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/api/ai/test', methods=['POST'])
def ai_test():
    """Simple test endpoint without AI dependencies"""
    try:
        data = request.get_json()
        user_message = data.get('message')
        user_id = data.get('user_id')
        
        if not user_message or not user_id:
            return jsonify({"error": "No message or user_id provided"}), 400
        
        return jsonify({
            "success": True,
            "message": f"✅ Received message: '{user_message}' from user: {user_id}",
            "user_message": user_message,
            "user_id": user_id,
            "test_mode": True
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/<user_id>/ai/generate-schedule', methods=['POST'])
def generate_schedule_simple(user_id):
    """Simple schedule generation without AI"""
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({'message': 'Prompt is required'}), 400
        
        # Mock response for testing
        mock_tasks = [
            {
                "title": f"Task from: {prompt[:30]}...",
                "description": "Generated from your prompt",
                "date": "2025-09-30",
                "time": "10:00",
                "category": "generated"
            }
        ]
        
        return jsonify({
            "success": True,
            "tasks": mock_tasks,
            "user_id": user_id,
            "prompt": prompt
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting simple AI test server...")
    app.run(debug=True, port=5001)