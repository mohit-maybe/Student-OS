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


# --- Account email linking & verification -------------------------------

def get_token_serializer(salt):
    """Shared signed-token helper used for both email verification and password resets."""
    from itsdangerous import URLSafeTimedSerializer
    from flask import current_app
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt=salt)


def get_account_email(cursor, user_id):
    """Return (email, is_verified) for a user's linked account email, or (None, False)."""
    cursor.execute('SELECT email, is_verified FROM user_emails WHERE user_id = %s', (user_id,))
    row = cursor.fetchone()
    if row:
        return row['email'], bool(row['is_verified'])
    return None, False


def link_email_and_send_verification(db, user, email):
    """
    Link/update a user's account email and send a verification link.
    Any previous link for this user is overwritten and marked unverified again,
    since we can't assume the new address is the same person's inbox.
    """
    from db import db_cursor
    import secrets

    token = get_token_serializer('email-verify').dumps({'user_id': user.id, 'email': email})

    with db_cursor(db) as cursor:
        cursor.execute('SELECT user_id FROM user_emails WHERE user_id = %s', (user.id,))
        exists = cursor.fetchone()
        if exists:
            cursor.execute(
                'UPDATE user_emails SET email = %s, is_verified = %s, verification_token = %s, token_created_at = CURRENT_TIMESTAMP, verified_at = NULL WHERE user_id = %s',
                (email, False, token, user.id)
            )
        else:
            cursor.execute(
                'INSERT INTO user_emails (user_id, email, is_verified, verification_token, token_created_at) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)',
                (user.id, email, False, token)
            )
    db.commit()
    send_verification_email(user, email, token)
    return token


def send_verification_email(user, email, token):
    from flask import url_for, current_app
    from flask_mail import Message
    from extensions import send_async

    verify_url = url_for('auth.verify_email', token=token, _external=True)
    try:
        msg = Message('Verify your email — Student OS', recipients=[email])
        msg.body = (
            f"Hi {user.username},\n\n"
            f"Confirm this email is linked to your Student OS account by clicking the link below "
            f"(expires in 24 hours):\n\n{verify_url}\n\n"
            f"If you didn't request this, you can safely ignore this email."
        )
        send_async(current_app._get_current_object(), msg)
    except Exception as e:
        print(f"[Email Verification] Failed to send email to {email}: {e}")
