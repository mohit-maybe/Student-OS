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

def add_notification(db, user_id, message, n_type='info'):
    db.execute('INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)',
               (user_id, message, n_type))
    db.commit()


