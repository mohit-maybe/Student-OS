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
