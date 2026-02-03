from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        selected_role = request.form.get('role', 'student')  # Get selected role from form
        remember = request.form.get('remember') == 'on'  # Check if remember me is checked
        
        user = User.get_by_username(username)
        
        if user and user.check_password(password):
            # Validate that the selected role matches the user's actual role
            if user.role.lower() != selected_role.lower():
                flash(f'Invalid login. This account is registered as a {user.role.title()}, not a {selected_role.title()}.', 'error')
                return render_template('login.html')
            
            # Login user with remember me option (30 days if checked)
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
