import secrets
import string
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from flask_mail import Message
from werkzeug.security import generate_password_hash
from db import get_db

admissions_bp = Blueprint('admissions', __name__)

def generate_credentials(full_name):
    # Base username from name
    base = "".join(full_name.split()).lower()[:8]
    random_suffix = "".join(secrets.choice(string.digits) for _ in range(4))
    username = f"{base}{random_suffix}"
    
    # Strong random password
    alphabet = string.ascii_letters + string.digits
    password = "".join(secrets.choice(alphabet) for _ in range(10))
    
    return username, password

@admissions_bp.route('/admissions/enroll', methods=['GET', 'POST'])
@login_required
def enroll():
    if current_user.role not in ['teacher', 'admin']:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('dashboard.dashboard'))
    
    db = get_db()
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        address = request.form.get('address')
        parent_name = request.form.get('parent_name')
        parent_mobile = request.form.get('parent_mobile')
        parent_email = request.form.get('parent_email')
        
        username, password = generate_credentials(full_name)
        hashed_password = generate_password_hash(password)
        
        try:
            # 1. Create User
            cursor = db.execute(
                'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                (username, hashed_password, 'student')
            )
            user_id = cursor.lastrowid
            
            # 2. Create Student Details
            admission_number = f"ADM{user_id:04d}"
            db.execute(
                '''INSERT INTO student_details 
                (user_id, full_name, email, mobile, dob, gender, address, parent_name, parent_mobile, parent_email, admission_number) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (user_id, full_name, email, mobile, dob, gender, address, parent_name, parent_mobile, parent_email, admission_number)
            )
            
            db.commit()
            
            # 3. Send Email
            from extensions import mail
            msg = Message(
                'Welcome to Student OS - Your Login Credentials',
                recipients=[email]
            )
            msg.body = f"""
            Dear {full_name},

            Welcome to our institution! Your student account has been successfully created.

            Here are your login credentials:
            Username: {username}
            Password: {password}
            Admission Number: {admission_number}

            Please login at: {request.host_url}
            
            Regards,
            Administration
            """
            
            try:
                mail.send(msg)
                flash(f'Student enrolled successfully! Credentials sent to {email}.', 'success')
            except Exception as e:
                flash(f'Student enrolled, but email failed: {str(e)}', 'warning')
                print(f"Mail error: {e}")

            return redirect(url_for('admissions.enroll'))
            
        except Exception as e:
            db.rollback()
            flash(f'Error enrolling student: {str(e)}', 'error')
            print(f"Enroll error: {e}")
            
    # GET: Fetch all students with their courses
    rows = db.execute('''
        SELECT u.id as user_id, u.username, sd.full_name, sd.email, sd.mobile, 
               sd.dob, sd.gender, sd.address, sd.parent_name, sd.parent_mobile, 
               sd.parent_email, sd.admission_number,
        (SELECT GROUP_CONCAT(c.name, ", ") FROM enrollments e 
         JOIN courses c ON e.course_id = c.id 
         WHERE e.student_id = u.id) as courses
        FROM users u
        LEFT JOIN student_details sd ON u.id = sd.user_id
        WHERE u.role = 'student'
        ORDER BY courses ASC, sd.full_name ASC
    ''').fetchall()
    
    students = [dict(row) for row in rows]
    
    return render_template('enroll.html', user=current_user, students=students)

@admissions_bp.route('/admissions/edit/<int:user_id>', methods=['POST'])
@login_required
def edit_student(user_id):
    if current_user.role not in ['teacher', 'admin']:
        return {"success": False, "message": "Unauthorized"}, 403
    
    db = get_db()
    data = request.form
    try:
        db.execute('''
            UPDATE student_details SET 
            full_name = ?, email = ?, mobile = ?, dob = ?, 
            gender = ?, address = ?, parent_name = ?, 
            parent_mobile = ?, parent_email = ?
            WHERE user_id = ?
        ''', (
            data.get('full_name'), data.get('email'), data.get('mobile'), 
            data.get('dob'), data.get('gender'), data.get('address'),
            data.get('parent_name'), data.get('parent_mobile'), 
            data.get('parent_email'), user_id
        ))
        db.commit()
        flash('Student details updated!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error updating student: {str(e)}', 'error')
        
    return redirect(url_for('admissions.enroll'))

@admissions_bp.route('/admissions/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_student(user_id):
    if current_user.role not in ['teacher', 'admin']:
        flash('Unauthorized.', 'error')
        return redirect(url_for('dashboard.dashboard'))
    
    db = get_db()
    try:
        db.execute('DELETE FROM student_details WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM users WHERE id = ?', (user_id,))
        db.execute('DELETE FROM enrollments WHERE student_id = ?', (user_id,))
        db.commit()
        flash('Student account deleted successfully.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error deleting student: {str(e)}', 'error')
        
    return redirect(url_for('admissions.enroll'))
