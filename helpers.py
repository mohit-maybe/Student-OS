import os
from werkzeug.utils import secure_filename
import time

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload(file, upload_folder, prefix=""):
    if file and file.filename != '' and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{prefix}{int(time.time())}_{filename}"
        file.save(os.path.join(upload_folder, unique_filename))
        return unique_filename
    return None

def calculate_gpa(score):
    if score >= 90: return 4.0
    if score >= 80: return 3.0
    if score >= 70: return 2.0
    if score >= 60: return 1.0
    return 0.0

def add_notification(db, user_id, message, n_type='info', school_id=1):
    from db import db_cursor
    with db_cursor(db) as cursor:
        cursor.execute('INSERT INTO notifications (user_id, message, type, school_id) VALUES (%s, %s, %s, %s)',
                   (user_id, message, n_type, school_id))
    db.commit()
    
def generate_credentials(full_name, role='student'):
    import secrets
    import string
    # Base username from name
    base = "".join(full_name.split()).lower()[:8]
    random_suffix = "".join(secrets.choice(string.digits) for _ in range(4))
    prefix = "s" if role == 'student' else "t"
    username = f"{prefix}_{base}_{random_suffix}"
    
    # Strong random password
    alphabet = string.ascii_letters + string.digits
    password = "".join(secrets.choice(alphabet) for _ in range(10))
    
    return username, password
