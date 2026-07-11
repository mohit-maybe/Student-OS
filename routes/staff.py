from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, Response
from flask_login import login_required, current_user
from flask_mail import Message
from werkzeug.security import generate_password_hash
from db import get_db, db_cursor
from extensions import mail
from helpers import generate_credentials
import io
import csv

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/staff/sample_csv')
@login_required
def download_sample_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['full_name', 'email', 'department', 'mobile', 'status'])
    writer.writerow(['Professor Xavier', 'charles@example.com', 'Technology', '9876543210', 'Active'])
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=staff_import_sample.csv"}
    )

def _require_admin():
    if current_user.role != 'admin':
        flash('Unauthorized access. Admin only.', 'error')
        return redirect(url_for('dashboard.dashboard'))
    return None

# Moved to helpers.py

@staff_bp.route('/admin/staff')
@login_required
def list_staff():
    redir = _require_admin()
    if redir: return redir

    db = get_db()
    
    # Super-admin override
    target_school_id = current_user.school_id
    is_superadmin = (current_user.id == 1)
    if is_superadmin and request.args.get('school_id'):
        target_school_id = int(request.args.get('school_id'))

    with db_cursor(db) as cursor:
        cursor.execute('''
            SELECT u.id, u.username, u.role, td.full_name, td.email, td.mobile, td.department, td.joined_at, td.status
            FROM users u
            JOIN teacher_details td ON u.id = td.user_id
            WHERE u.role IN ('teacher', 'principal') AND u.school_id = %s
            ORDER BY td.full_name ASC
        ''', (target_school_id,))
        raw_teachers = cursor.fetchall()
        # Convert rows to dicts for JSON serialization in template
        teachers = [dict(row) for row in raw_teachers]
        
        all_schools = []
        if is_superadmin:
            cursor.execute('SELECT id, name FROM schools ORDER BY name ASC')
            all_schools = cursor.fetchall()
    
    return render_template('staff.html', 
                           teachers=teachers, 
                           user=current_user, 
                           all_schools=all_schools, 
                           current_view_school_id=target_school_id,
                           is_superadmin=is_superadmin)

@staff_bp.route('/admin/staff/add', methods=['POST'])
@login_required
def add_teacher():
    redir = _require_admin()
    if redir: return redir

    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip()
    mobile = request.form.get('mobile', '').strip()
    department = request.form.get('department', '').strip()
    role = request.form.get('role', 'teacher') # Default to teacher
    target_school_id = request.form.get('school_id', current_user.school_id)

    if not full_name or not email:
        flash('Name and Email are required.', 'error')
        return redirect(url_for('staff.list_staff', school_id=target_school_id))

    username, password = generate_credentials(full_name, role=role)
    hashed_pwd = generate_password_hash(password)

    db = get_db()
    try:
        with db_cursor(db) as cursor:
            # 1. Create User
            cursor.execute(
                'INSERT INTO users (username, password_hash, role, school_id) VALUES (%s, %s, %s, %s) RETURNING id',
                (username, hashed_pwd, role, target_school_id)
            )
            user_id = cursor.fetchone()[0]

            # 2. Add Teacher Details
            cursor.execute(
                '''INSERT INTO teacher_details (user_id, full_name, email, mobile, department, school_id)
                   VALUES (%s, %s, %s, %s, %s, %s)''',
                (user_id, full_name, email, mobile, department, target_school_id)
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

    return redirect(url_for('staff.list_staff', school_id=target_school_id))

@staff_bp.route('/admin/staff/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_teacher(user_id):
    redir = _require_admin()
    if redir: return redir

    db = get_db()
    try:
        with db_cursor(db) as cursor:
            # Unlink from classrooms first (ensure school isolation)
            cursor.execute('UPDATE classrooms SET teacher_id = NULL WHERE teacher_id = %s AND school_id = %s', (user_id, current_user.school_id))
            cursor.execute('DELETE FROM teacher_details WHERE user_id = %s AND school_id = %s', (user_id, current_user.school_id))
            cursor.execute('DELETE FROM users WHERE id = %s AND school_id = %s', (user_id, current_user.school_id))
        db.commit()
        flash('Staff member removed successfully.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error deleting staff: {str(e)}', 'error')

    return redirect(url_for('staff.list_staff'))
@staff_bp.route('/staff/import', methods=['POST'])
@login_required
def import_teachers():
    if current_user.role != 'admin':
        flash('Only admins can bulk import staff.', 'error')
        return redirect(url_for('dashboard.dashboard'))
    
    target_school_id = request.form.get('school_id', current_user.school_id)

    file = request.files.get('file')
    if not file or not file.filename.endswith('.csv'):
        flash('Please upload a valid CSV file.', 'error')
        return redirect(url_for('staff.list_staff', school_id=target_school_id))

    # Use io.StringIO to read the uploaded file as text
    try:
        content = file.stream.read().decode("UTF-8")
    except UnicodeDecodeError:
        file.stream.seek(0)
        content = file.stream.read().decode("latin-1")
    
    stream = io.StringIO(content, newline=None)
    csv_input = csv.DictReader(stream)
    
    db = get_db()
    count = 0
    errors = []
    
    try:
        from db import db_cursor
        with db_cursor(db) as cursor:
            for row in csv_input:
                full_name = row.get('full_name', '').strip()
                email = row.get('email', '').strip()
                department = row.get('department', 'General').strip()
                mobile = row.get('mobile', '').strip()
                status = row.get('status', 'Active').strip()
                
                if not full_name or not email:
                    continue
                
                username, password = generate_credentials(full_name)
                hashed_password = generate_password_hash(password)
                
                try:
                    # 1. Create User
                    cursor.execute(
                        'INSERT INTO users (username, password_hash, role, school_id) VALUES (%s, %s, %s, %s) RETURNING id',
                        (username, hashed_password, 'teacher', target_school_id)
                    )
                    user_id = cursor.fetchone()[0]
                    
                    # 2. Create Teacher Details
                    cursor.execute(
                        'INSERT INTO teacher_details (user_id, full_name, email, mobile, department, status, school_id) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        (user_id, full_name, email, mobile or None, department, status, target_school_id)
                    )
                    
                    # 3. Send Credentials Email
                    msg = Message('Student OS - Faculty Credentials', recipients=[email])
                    msg.body = f"Welcome Professor {full_name}!\n\nYour faculty account is ready.\nUsername: {username}\nPassword: {password}\n\nLogin: {request.host_url}"
                    try:
                        mail.send(msg)
                    except: pass
                    
                    count += 1
                except Exception as e:
                    errors.append(f"Row {count+2}: {str(e)}")
                    
        db.commit()
        if errors:
            flash(f'Imported {count} teachers with {len(errors)} errors.', 'warning')
        else:
            flash(f'Successfully imported {count} teachers!', 'success')
            
    except Exception as e:
        db.rollback()
        flash(f'Import failed: {str(e)}', 'error')
        
    return redirect(url_for('staff.list_staff', school_id=target_school_id))

@staff_bp.route('/admin/staff/update/<int:user_id>', methods=['POST'])
@login_required
def update_staff(user_id):
    redir = _require_admin()
    if redir: return redir
    
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    mobile = request.form.get('mobile')
    department = request.form.get('department')
    role = request.form.get('role')
    status = request.form.get('status')
    target_school_id = request.form.get('school_id', current_user.school_id)
    
    db = get_db()
    try:
        with db_cursor(db) as cursor:
            cursor.execute('UPDATE users SET role = %s WHERE id = %s AND school_id = %s', (role, user_id, target_school_id))
            cursor.execute('''
                UPDATE teacher_details SET full_name = %s, email = %s, mobile = %s, department = %s, status = %s
                WHERE user_id = %s AND school_id = %s
            ''', (full_name, email, mobile, department, status, user_id, target_school_id))
        db.commit()
        flash('Staff details updated successfully.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error updating staff: {str(e)}', 'error')
        
    return redirect(url_for('staff.list_staff', school_id=target_school_id))

@staff_bp.route('/admin/staff/toggle/<int:user_id>', methods=['POST'])
@login_required
def toggle_staff_status(user_id):
    redir = _require_admin()
    if redir: return redir
    
    new_status = request.form.get('status')
    target_school_id = request.form.get('school_id', current_user.school_id)
    db = get_db()
    try:
        with db_cursor(db) as cursor:
            cursor.execute('UPDATE teacher_details SET status = %s WHERE user_id = %s AND school_id = %s', (new_status, user_id, target_school_id))
        db.commit()
        flash(f'Staff status updated to {new_status}.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error updating status: {str(e)}', 'error')
        
    return redirect(url_for('staff.list_staff', school_id=target_school_id))
