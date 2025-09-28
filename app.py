from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
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
    """Serves the main login/signup page."""
    return render_template("index.html")

@app.route("/home")
def home_redirect():
    """Redirect /home to login page since user_id is required."""
    return redirect(url_for('home'))


@app.route("/profile/<user_id>")
def profile_page(user_id):
    """Serves the user profile page."""
    return render_template("profile.html", user_id=user_id)


@app.route("/home/<user_id>")
def home_page(user_id):
    return render_template("home.html", user_id=user_id)

@app.route("/schedule/<user_id>")
def schedule_page(user_id):
    return render_template("schedule.html", user_id=user_id)

@app.route("/add_event/<user_id>")
def add_event_page(user_id):
    return render_template("add-new-task.html", user_id=user_id)

@app.route("/AI/<user_id>")
def ai_page(user_id):
    return render_template("AI.html", user_id=user_id)
    
@app.route("/aiAssistant/<user_id>")
def ai_assistant_page(user_id):
    return render_template("AiAssistant.html", user_id=user_id)
    
@app.route("/collaboration/<user_id>")
def collaboration_page(user_id):
    return render_template("collabration.html", user_id=user_id)

# Return JSON errors for API routes, with optional stack traces
@app.errorhandler(Exception)
def handle_exception(e):
    try:
        is_api = request.path.startswith('/api/')
    except Exception:
        is_api = False
    if is_api:
        payload = {"error": str(e)}
        if os.getenv('DEBUG_ERRORS') == '1':
            payload["trace"] = traceback.format_exc()
        return jsonify(payload), 500
    # Non-API: fall back to default behavior
    return render_template("index.html"), 500

# --- Main entry point ---
if __name__ == "__main__":
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
        print("🚀 Starting server anyway for API testing...")
    
    app.run(debug=True)

