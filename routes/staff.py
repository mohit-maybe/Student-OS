import secrets
import string
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from flask_mail import Message
from werkzeug.security import generate_password_hash
from db import get_db, db_cursor
from extensions import mail

staff_bp = Blueprint('staff', __name__)

def _require_admin():
    if current_user.role != 'admin':
        flash('Unauthorized access. Admin only.', 'error')
        return redirect(url_for('dashboard.dashboard'))
    return None

def generate_teacher_credentials(full_name):
    # Base username: first letter + last name (cleaned)
    parts = full_name.split()
    first = parts[0][0].lower() if parts else "t"
    last = parts[-1].lower() if len(parts) > 1 else "teacher"
    base = f"{first}{last}"[:10]
    random_suffix = "".join(secrets.choice(string.digits) for _ in range(3))
    username = f"{base}_{random_suffix}"
    
    # Strong random password
    alphabet = string.ascii_letters + string.digits + "@#$%"
    password = "".join(secrets.choice(alphabet) for _ in range(12))
    
    return username, password

@staff_bp.route('/admin/staff')
@login_required
def list_staff():
    redir = _require_admin()
    if redir: return redir

    db = get_db()
    with db_cursor(db) as cursor:
        cursor.execute('''
            SELECT u.id, u.username, td.full_name, td.email, td.mobile, td.department, td.joined_at
            FROM users u
            JOIN teacher_details td ON u.id = td.user_id
            WHERE u.role = 'teacher'
            ORDER BY td.full_name ASC
        ''')
        teachers = cursor.fetchall()
    
    return render_template('staff.html', teachers=teachers, user=current_user)

@staff_bp.route('/admin/staff/add', methods=['POST'])
@login_required
def add_teacher():
    redir = _require_admin()
    if redir: return redir

    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip()
    mobile = request.form.get('mobile', '').strip()
    department = request.form.get('department', '').strip()

    if not full_name or not email:
        flash('Name and Email are required.', 'error')
        return redirect(url_for('staff.list_staff'))

    username, password = generate_teacher_credentials(full_name)
    hashed_pwd = generate_password_hash(password)

    db = get_db()
    try:
        with db_cursor(db) as cursor:
            # 1. Create User
            cursor.execute(
                'INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s) RETURNING id',
                (username, hashed_pwd, 'teacher')
            )
            user_id = cursor.fetchone()[0]

            # 2. Add Teacher Details
            cursor.execute(
                '''INSERT INTO teacher_details (user_id, full_name, email, mobile, department)
                   VALUES (%s, %s, %s, %s, %s)''',
                (user_id, full_name, email, mobile, department)
            )
        db.commit()

        # 3. Send Email
        msg = Message(
            'Welcome to the Faculty - Your OS Credentials',
            recipients=[email]
        )
        msg.body = f"""
        Hello {full_name},

        Welcome to the team! Your teacher account for the Student OS platform has been created.

        Your Login Credentials:
        -----------------------
        Portal: {request.host_url}
        Username: {username}
        Password: {password}

        Please login and update your profile settings once you have verified access.

        Best Regards,
        Admin Team
        """
        try:
            mail.send(msg)
            flash(f'Teacher {full_name} added! Credentials sent to {email}.', 'success')
        except Exception as mail_err:
            flash(f'Teacher added, but email notification failed: {str(mail_err)}', 'warning')

    except Exception as e:
        db.rollback()
        flash(f'Error adding teacher: {str(e)}', 'error')

    return redirect(url_for('staff.list_staff'))

@staff_bp.route('/admin/staff/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_teacher(user_id):
    redir = _require_admin()
    if redir: return redir

    db = get_db()
    try:
        with db_cursor(db) as cursor:
            # Unlink from classrooms first
            cursor.execute('UPDATE classrooms SET teacher_id = NULL WHERE teacher_id = %s', (user_id,))
            cursor.execute('DELETE FROM teacher_details WHERE user_id = %s', (user_id,))
            cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        db.commit()
        flash('Staff member removed successfully.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error deleting staff: {str(e)}', 'error')

    return redirect(url_for('staff.list_staff'))
