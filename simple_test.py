from flask import Flask, request, jsonify
from ai_scheduler import AIScheduler

app = Flask(__name__)

@app.route('/test-ai', methods=['POST'])
def test_ai():
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'Create a simple task')
        
        scheduler = AIScheduler()
        result = scheduler.generate_tasks(prompt)
        return jsonify({"success": True, "tasks": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "error_type": type(e).__name__}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)