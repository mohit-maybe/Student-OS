from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import User
import time

auth_bp = Blueprint('auth', __name__)

# Simple in-memory brute-force guard: tracks failed attempts per (username, ip).
# Not distributed-safe (fine for a single-dyno deployment); resets on restart.
_failed_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 300  # 5 minutes

def _attempt_key():
    return f"{request.form.get('username', '').lower()}:{request.remote_addr}"

def _is_locked_out(key):
    entry = _failed_attempts.get(key)
    if not entry:
        return False
    count, first_failed_at = entry
    if count < MAX_ATTEMPTS:
        return False
    if time.time() - first_failed_at > LOCKOUT_SECONDS:
        _failed_attempts.pop(key, None)
        return False
    return True

def _record_failure(key):
    count, first_failed_at = _failed_attempts.get(key, (0, time.time()))
    _failed_attempts[key] = (count + 1, first_failed_at)

def _clear_failures(key):
    _failed_attempts.pop(key, None)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        key = _attempt_key()
        if _is_locked_out(key):
            flash('Too many failed attempts. Please try again in a few minutes.', 'error')
            return render_template('login.html'), 429

        username = request.form.get('username')
        password = request.form.get('password')
        selected_role = request.form.get('role', 'student')  # Get selected role from form
        remember = request.form.get('remember') == 'on'  # Check if remember me is checked
        
        user = User.get_by_username(username)
        
        if user and user.check_password(password):
            # Validate that the selected role matches the user's actual role
            # Allow principal to login as teacher
            is_valid_role = (user.role.lower() == selected_role.lower()) or \
                           (user.role.lower() == 'principal' and selected_role.lower() == 'teacher')
            
            if not is_valid_role:
                _record_failure(key)
                flash(f'Invalid login. This account is registered as a {user.role.title()}, not a {selected_role.title()}.', 'error')
                return render_template('login.html')
            
            _clear_failures(key)
            # Login user with remember me option (30 days if checked)
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            _record_failure(key)
            flash('Invalid username or password', 'error')
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


def _get_reset_serializer():
    from itsdangerous import URLSafeTimedSerializer
    from flask import current_app
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='password-reset')


def _find_email_for_user(cursor, user_id):
    """Look up the email on file for a user, checking student then teacher records."""
    cursor.execute('SELECT email FROM student_details WHERE user_id = %s', (user_id,))
    row = cursor.fetchone()
    if row and row['email']:
        return row['email']
    cursor.execute('SELECT email FROM teacher_details WHERE user_id = %s', (user_id,))
    row = cursor.fetchone()
    if row and row['email']:
        return row['email']
    return None


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        from db import get_db, db_cursor
        username = request.form.get('username', '').strip()

        db = get_db()
        with db_cursor(db) as cursor:
            user = User.get_by_username(username)
            email = _find_email_for_user(cursor, user.id) if user else None

        # Always show the same message, whether or not the account/email was found,
        # so this endpoint can't be used to enumerate valid usernames.
        if user and email:
            try:
                from extensions import mail
                from flask_mail import Message
                token = _get_reset_serializer().dumps({'user_id': user.id})
                reset_url = url_for('auth.reset_password', token=token, _external=True)
                msg = Message('Reset your Student OS password', recipients=[email])
                msg.body = (
                    f"Hi,\n\nA password reset was requested for the account '{user.username}'.\n"
                    f"Reset your password here (this link expires in 1 hour):\n{reset_url}\n\n"
                    f"If you didn't request this, you can safely ignore this email."
                )
                mail.send(msg)
            except Exception as e:
                print(f"[Password Reset] Failed to send email: {e}")

        flash('If an account with that username has an email on file, a reset link has been sent.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    from itsdangerous import SignatureExpired, BadSignature
    try:
        data = _get_reset_serializer().loads(token, max_age=3600)  # 1 hour expiry
    except SignatureExpired:
        flash('This reset link has expired. Please request a new one.', 'error')
        return redirect(url_for('auth.forgot_password'))
    except BadSignature:
        flash('This reset link is invalid.', 'error')
        return redirect(url_for('auth.forgot_password'))

    user = User.get(data.get('user_id'))
    if not user:
        flash('This reset link is no longer valid.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('reset_password.html', token=token)
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)

        from db import get_db, db_cursor
        from werkzeug.security import generate_password_hash
        db = get_db()
        with db_cursor(db) as cursor:
            cursor.execute('UPDATE users SET password_hash = %s WHERE id = %s',
                       (generate_password_hash(password), user.id))
        db.commit()

        flash('Your password has been updated. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)
