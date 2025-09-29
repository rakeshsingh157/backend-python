from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sys
import traceback
import mysql.connector
from mysql.connector import Error
from user_profile import profile_bp
import os
from werkzeug.utils import secure_filename
from bcrypt import hashpw, gensalt, checkpw
import uuid
from login_register import auth_bp, init_db
from collaboration import collaboration_bp
from ai import ai_bp
from ai_assistant import ai_assistant_bp
from ai_scheduler import ai_scheduler_bp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from home_routes import home_bp
from tasks import tasks_bp
from schedule import schedule_bp


# Create the Flask application instance
app = Flask(__name__)
app = Flask(__name__, template_folder='../', static_folder='static')
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))




app.register_blueprint(profile_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(collaboration_bp)
app.register_blueprint(ai_assistant_bp)
app.register_blueprint(ai_scheduler_bp)
app.register_blueprint(home_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(schedule_bp)

# --- Database and Uploads Configuration ---
@app.route("/")
def home():
    """API status endpoint."""
    return jsonify({
        "message": "HelpScout API is running",
        "status": "active",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/login, /api/register",
            "tasks": "/api/tasks/*",
            "schedule": "/api/schedule/*",
            "ai": "/api/ai/*",
            "user": "/api/user/*"
        }
    })

@app.route("/health")
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": os.getenv('BUILD_TIMESTAMP', 'unknown'),
        "python_version": os.getenv('PYTHON_VERSION', 'unknown')
    })

@app.route("/home")
def home_redirect():
    """Redirect to main status endpoint."""
    return redirect(url_for('home'))

@app.route("/profile/<user_id>")
def profile_page(user_id):
    """User profile API endpoint."""
    return jsonify({
        "message": "Profile endpoint",
        "user_id": user_id,
        "note": "Use /api/user/profile/<user_id> for profile data"
    })

@app.route("/home/<user_id>")
def home_page(user_id):
    """User home API endpoint."""
    return jsonify({
        "message": "User home endpoint",
        "user_id": user_id,
        "note": "Use /api/tasks/<user_id> for user tasks"
    })

@app.route("/schedule/<user_id>")
def schedule_page(user_id):
    """User schedule API endpoint."""
    return jsonify({
        "message": "Schedule endpoint",
        "user_id": user_id,
        "note": "Use /api/schedule/<user_id> for schedule data"
    })

@app.route("/add_event/<user_id>")
def add_event_page(user_id):
    """Add event API endpoint."""
    return jsonify({
        "message": "Add event endpoint",
        "user_id": user_id,
        "note": "Use POST /api/tasks/<user_id>/add for adding events"
    })

@app.route("/AI/<user_id>")
def ai_page(user_id):
    """AI endpoint."""
    return jsonify({
        "message": "AI endpoint",
        "user_id": user_id,
        "note": "Use /api/ai/chat for AI interactions"
    })
    
@app.route("/aiAssistant/<user_id>")
def ai_assistant_page(user_id):
    """AI Assistant endpoint."""
    return jsonify({
        "message": "AI Assistant endpoint",
        "user_id": user_id,
        "note": "Use /api/ai/scheduler/chat for AI assistant"
    })
    
@app.route("/collaboration/<user_id>")
def collaboration_page(user_id):
    """Collaboration endpoint."""
    return jsonify({
        "message": "Collaboration endpoint",
        "user_id": user_id,
        "note": "Use /api/collaboration/* for collaboration features"
    })

# Return JSON errors for API routes, with optional stack traces
@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all exceptions with JSON responses."""
    payload = {"error": str(e), "type": type(e).__name__}
    
    # Add stack trace in debug mode
    if os.getenv('DEBUG_ERRORS') == '1' or app.debug:
        import traceback
        payload["trace"] = traceback.format_exc()
    
    # Return appropriate status code
    status_code = 500
    if hasattr(e, 'code'):
        status_code = e.code
    
    return jsonify(payload), status_code

# --- Main entry point ---
if __name__ == "__main__":
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
        print("🚀 Starting server anyway for API testing...")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # Running via gunicorn
    print("🚀 Starting HelpScout API via gunicorn")
    print(f"Python version: {sys.version}")
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
        print("🚀 Continuing anyway...")

