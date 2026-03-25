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
from routes.exam_predictor import exam_predictor_bp
from routes.classrooms import classrooms_bp
from routes.staff import staff_bp
from routes.schools import schools_bp
from routes.webhooks import webhooks_bp
from flask_mail import Message
from flask_babel import _
from flask import session, request
from extensions import mail, babel, csrf, login_manager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'student_os.db')
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

# Extensions Setup
mail.init_app(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Auth Setup
login_manager.init_app(app)
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

babel.init_app(app, locale_selector=get_locale)
csrf.init_app(app)

# Teardown
app.teardown_appcontext(close_connection)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(courses_bp)
app.register_blueprint(academic_bp)
app.register_blueprint(messages_bp)
app.register_blueprint(admissions_bp)
app.register_blueprint(exam_predictor_bp)
app.register_blueprint(classrooms_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(schools_bp)
app.register_blueprint(webhooks_bp)

@app.context_processor
def inject_school_context():
    from db import get_db, db_cursor
    db = get_db()
    
    # Identify school from subdomain first
    host = request.host.split(':')[0]
    parts = host.split('.')
    
    school = None
    # Check for subdomain (e.g., slug.localhost or slug.studentos.com)
    if len(parts) > 1:
        potential_slug = parts[0]
        # Ignore common prefixes or TLD-only checks if needed
        if potential_slug not in ['www', 'app', 'localhost', '127']:
            with db_cursor(db) as cursor:
                cursor.execute('SELECT * FROM schools WHERE slug = %s', (potential_slug,))
                school = cursor.fetchone()
    
    # If no subdomain match, use the user's school if logged in
    if not school and current_user.is_authenticated:
        with db_cursor(db) as cursor:
            cursor.execute('SELECT * FROM schools WHERE id = %s', (current_user.school_id,))
            school = cursor.fetchone()
            
    # Ultimate fallback to school ID 1
    if not school:
        with db_cursor(db) as cursor:
            cursor.execute('SELECT * FROM schools WHERE id = 1')
            school = cursor.fetchone()
        
    unread_count = 0
    try:
        if current_user.is_authenticated:
            with db_cursor(db) as cursor:
                cursor.execute('SELECT COUNT(*) FROM messages WHERE recipient_id = %s AND is_read = 0 AND school_id = %s', (current_user.id, current_user.school_id))
                unread_count = cursor.fetchone()[0]
    except Exception as e:
        print(f"Unread count error: {e}")
        
    return dict(
        current_school=school,
        unread_messages_count=unread_count,
        current_year=datetime.now().year
    )

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
    return render_template('landing.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    import traceback
    return f"<h1>500 Internal Server Error</h1><pre>{traceback.format_exc()}</pre>", 500

def seed_demo_data(db):
    """Populates the database with sample data if it's empty."""
    print("Seeding demo data...")
    import random
    
    from db import db_cursor
    with db_cursor(db) as cursor:
        # 1. Create Teachers
        teachers = [
            ('mr_smith', 'password', 'Sarah Smith'),
            ('ms_jones', 'password', 'Emily Jones'),
            ('dr_brown', 'password', 'Michael Brown')
        ]
        
        teacher_ids = []
        for username, pwd, name in teachers:
            cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s) RETURNING id',
                       (username, generate_password_hash(pwd), 'teacher'))
            teacher_ids.append(cursor.fetchone()[0])

        # 2. Create Courses
        courses = [
            ('Mathematics 101', teacher_ids[0], 'Mon/Wed 10:00 AM'),
            ('History 201', teacher_ids[1], 'Tue/Thu 2:00 PM'),
            ('Computer Science', teacher_ids[2], 'Fri 1:00 PM')
        ]
        
        course_ids = []
        for name, t_id, schedule in courses:
            cursor.execute('INSERT INTO courses (name, teacher_id, schedule) VALUES (%s, %s, %s) RETURNING id',
                              (name, t_id, schedule))
            course_ids.append(cursor.fetchone()[0])

        # 3. Create Students
        students_data = [
            ('alice', 'Alice Johnson', 'alice@example.com'),
            ('bob', 'Bob Wilson', 'bob@example.com'),
            ('charlie', 'Charlie Davis', 'charlie@example.com'),
            ('david', 'David Miller', 'david@example.com')
        ]
        
        for i, (username, name, email) in enumerate(students_data):
            pwd_hash = generate_password_hash('password')
            cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s) RETURNING id',
                       (username, pwd_hash, 'student'))
            user_id = cursor.fetchone()[0]
            
            # Details
            cursor.execute('''INSERT INTO student_details 
                (user_id, full_name, email, admission_number, gender) 
                VALUES (%s, %s, %s, %s, %s)''',
                (user_id, name, email, f"ADM{user_id:04d}", random.choice(['Male', 'Female'])))
            
            # Random Enrollments (Each student in 2 courses)
            for c_id in random.sample(course_ids, 2):
                cursor.execute('INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s)', (user_id, c_id))
                
                # Add some sample grades
                cursor.execute('INSERT INTO grades (student_id, course_id, score, grade_type) VALUES (%s, %s, %s, %s)',
                           (user_id, c_id, random.randint(75, 98), 'Assignment'))
    
    db.commit()
    print("Demo data seeded successfully.")

# Thread-safe initialization
_db_initialized = False

@app.before_request
def safe_init():
    global _db_initialized
    if not _db_initialized:
        # Avoid running in debug reloader's main process or if already initialized
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
            print("[INIT] Performing one-time startup initialization...")
            startup_init()
        _db_initialized = True

def startup_init():
    """Initializes the database and default data safely."""
    with app.app_context():
        # Create tables
        try:
            init_db(app)
            
            db = get_db()
            from db import db_cursor
            with db_cursor(db) as cursor:
                # 0. Ensure at least one school exists (Genesis School)
                cursor.execute('SELECT id FROM schools WHERE id = 1')
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO schools (id, name, slug) VALUES (%s, %s, %s)",
                        (1, 'Genesis High', 'genesis')
                    )
                    db.commit()

                # 1. Create default admin if not exists
                cursor.execute('SELECT id FROM users WHERE username = %s', ('admin',))
                if not cursor.fetchone():
                    cursor.execute('INSERT INTO users (username, password_hash, role, school_id) VALUES (%s, %s, %s, %s)',
                               ('admin', generate_password_hash('admin123'), 'admin', 1))
                    db.commit()

                # 2. Create Group Chat system user (ID 0)
                try:
                    cursor.execute('SELECT id FROM users WHERE id = %s', (0,))
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO users (id, username, password_hash, role, school_id) VALUES (%s, %s, %s, %s, %s)", 
                                   (0, 'Group Chat', 'system', 'group', 1))
                        db.commit()
                except Exception as e:
                    print(f"Group chat setup warning: {e}")

                # 3. Auto-seed if requested and database has no students
                should_seed = os.getenv('SEED_DEMO', 'true').lower() == 'true'
                if should_seed:
                    cursor.execute("SELECT 1 FROM users WHERE role = 'student' LIMIT 1")
                    if not cursor.fetchone():
                        print("[DATA] Seeding initial demo data...")
                        seed_demo_data(db)
                else:
                    print("[INFO] Auto-seeding is disabled via environment variable.")
            
            print("[OK] Startup initialization complete.")
        except Exception as startup_err:
            print(f"[ERROR] CRITICAL STARTUP ERROR: {startup_err}")
            import traceback
            traceback.print_exc()
    # We let it pass so gunicorn can at least start the app 
    # and we can potentially see the error through the 500 handler if it reaches it.

# Perform one-time initialization before starting the app (Locally)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

