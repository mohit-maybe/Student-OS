import os
from dotenv import load_dotenv

load_dotenv()

from datetime import timedelta
from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from models import User
from db import close_connection, init_db, get_db
from werkzeug.security import generate_password_hash
# Blueprint Imports
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.courses import courses_bp
from routes.academic import academic_bp
from routes.messages import messages_bp
from routes.admissions import admissions_bp
from flask_mail import Mail
from flask_babel import Babel, _
from flask import session, request
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE'] = 'student_os.db'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UNIVERSITY_NAME'] = 'GLOBAL UNIVERSITY OF OS'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)  # Remember me for 30 days

# Mail Configuration (Gmail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Auth Setup
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def get_locale():
    # If the user has a preferred language in their session, use it
    if 'language' in session:
        return session['language']
    # Fallback to the best match from the browser languages
    return request.accept_languages.best_match(['en', 'hi', 'bn', 'te', 'mr', 'ta', 'gu', 'kn', 'ml'])

babel = Babel(app, locale_selector=get_locale)
csrf = CSRFProtect(app)

# Teardown
app.teardown_appcontext(close_connection)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(courses_bp)
app.register_blueprint(academic_bp)
app.register_blueprint(messages_bp)
app.register_blueprint(admissions_bp)

@app.context_processor
def inject_unread_count():
    if current_user.is_authenticated:
        db = get_db()
        count = db.execute('SELECT COUNT(*) FROM messages WHERE recipient_id = ? AND is_read = 0', (current_user.id,)).fetchone()[0]
        return dict(unread_messages_count=count)
    return dict(unread_messages_count=0)

from datetime import datetime
@app.template_filter('pretty_date')
def pretty_date_filter(date_str):
    if not date_str:
        return ''
    try:
        # Handle both list (if someone passed rows) and string
        if isinstance(date_str, datetime):
            dt = date_str
        else:
            # SQLite might return slightly different formats
            formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']
            dt = None
            for fmt in formats:
                try:
                    dt = datetime.strptime(str(date_str), fmt)
                    break
                except ValueError:
                    continue
            if not dt:
                return str(date_str)
        
        now = datetime.now()
        diff = now - dt
        
        if diff.days == 0:
            if diff.seconds < 60:
                return "Just now"
            if diff.seconds < 3600:
                return f"{diff.seconds // 60}m ago"
            return f"Today at {dt.strftime('%I:%M %p')}"
        elif diff.days == 1:
            return f"Yesterday at {dt.strftime('%I:%M %p')}"
        elif diff.days < 7:
            return dt.strftime('%a at %I:%M %p')
        return dt.strftime('%b %d, %Y')
    except Exception as e:
        print(f"Date error: {e}")
        return str(date_str)

@app.route('/')

def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize DB modularly
    init_db(app)
    
    with app.app_context():
        db = get_db()
        # Create default admin if not exists
        if not db.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone():
            db.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                       ('admin', generate_password_hash('admin123'), 'admin'))
            db.commit()

        # Create Group Chat system user (ID 0) to satisfy FK constraints
        try:
            if not db.execute('SELECT * FROM users WHERE id = 0').fetchone():
                db.execute("INSERT INTO users (id, username, password_hash, role) VALUES (0, 'Group Chat', 'system', 'group')")
                db.commit()
        except Exception as e:
            print(f"Group chat setup warning: {e}")

    app.run(host='0.0.0.0', debug=True)

