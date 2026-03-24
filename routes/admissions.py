import secrets
import string
import io
import qrcode
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from flask_mail import Message
from werkzeug.security import generate_password_hash
from db import get_db, db_cursor
from helpers import generate_credentials

admissions_bp = Blueprint('admissions', __name__)


@admissions_bp.route('/students/<int:student_id>/qr')
@login_required
def student_qr(student_id):
    """Generate and return a QR code image for a student."""
    db = get_db()
    with db_cursor(db) as cursor:
        cursor.execute(
            'SELECT full_name, admission_number FROM student_details WHERE user_id = %s AND school_id = %s',
            (student_id, current_user.school_id)
        )
        student = cursor.fetchone()

    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('admissions.enroll'))

    # Only the student themselves, or staff, can view the QR
    if current_user.role not in ['admin', 'teacher'] and current_user.id != student_id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('dashboard.dashboard'))

    # Encode: "student:<user_id>:<admission_number>"
    qr_data = f"student:{student_id}:{student['admission_number']}"

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1E1B4B", back_color="white")

    # Stream it as PNG
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return send_file(img_buffer, mimetype='image/png')

# credentials helper moved to helpers.py

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
        classroom_id = request.form.get('classroom_id') or None
        
        username, password = generate_credentials(full_name)
        hashed_password = generate_password_hash(password)
        
        try:
            from db import db_cursor
            with db_cursor(db) as cursor:
                # 1. Create User
                cursor.execute(
                    'INSERT INTO users (username, password_hash, role, school_id) VALUES (%s, %s, %s, %s) RETURNING id',
                    (username, hashed_password, 'student', current_user.school_id)
                )
                user_id = cursor.fetchone()[0]
                
                # 2. Create Student Details
                admission_number = f"ADM{user_id:04d}"
                cursor.execute(
                    '''INSERT INTO student_details 
                    (user_id, full_name, email, mobile, dob, gender, address, parent_name, parent_mobile, parent_email, admission_number, classroom_id, school_id) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                    (user_id, full_name, email, mobile, dob, gender, address, parent_name, parent_mobile, parent_email, admission_number, classroom_id, current_user.school_id)
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
    from db import db_cursor
    with db_cursor(db) as cursor:
        cursor.execute('''
            SELECT u.id as user_id, u.username, sd.full_name, sd.email, sd.mobile, 
                   sd.dob, sd.gender, sd.address, sd.parent_name, sd.parent_mobile, 
                   sd.parent_email, sd.admission_number, sd.classroom_id,
                   cl.name as classroom_name
            FROM users u
            LEFT JOIN student_details sd ON u.id = sd.user_id
            LEFT JOIN classrooms cl ON sd.classroom_id = cl.id
            WHERE u.role = 'student' AND u.school_id = %s
            ORDER BY cl.name ASC, sd.full_name ASC
        ''', (current_user.school_id,))
        rows = cursor.fetchall()
        
        # Fetch classrooms for dropdown (filtered by school)
        cursor.execute("SELECT id, name, section FROM classrooms WHERE school_id = %s ORDER BY name", (current_user.school_id,))
        classrooms = [dict(row) for row in cursor.fetchall()]
    
    students = [dict(row) for row in rows]
    
    return render_template('enroll.html', user=current_user, students=students, classrooms=classrooms)

@admissions_bp.route('/admissions/edit/<int:user_id>', methods=['POST'])
@login_required
def edit_student(user_id):
    if current_user.role not in ['teacher', 'admin']:
        return {"success": False, "message": "Unauthorized"}, 403
    
    db = get_db()
    data = request.form
    try:
        from db import db_cursor
        with db_cursor(db) as cursor:
            cursor.execute('''
                UPDATE student_details SET 
                full_name = %%s, email = %%s, mobile = %%s, dob = %%s, 
                gender = %%s, address = %%s, parent_name = %%s, 
                parent_mobile = %%s, parent_email = %%s, classroom_id = %%s
                WHERE user_id = %%s AND school_id = %%s
            '''.replace('%%', '%'), (
                data.get('full_name'), data.get('email'), data.get('mobile'), 
                data.get('dob'), data.get('gender'), data.get('address'),
                data.get('parent_name'), data.get('parent_mobile'), 
                data.get('parent_email'), data.get('classroom_id') or None, user_id, current_user.school_id
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
        from db import db_cursor
        with db_cursor(db) as cursor:
            cursor.execute('DELETE FROM student_details WHERE user_id = %s AND school_id = %s', (user_id, current_user.school_id))
            cursor.execute('DELETE FROM users WHERE id = %s AND school_id = %s', (user_id, current_user.school_id))
            cursor.execute('DELETE FROM enrollments WHERE student_id = %s AND school_id = %s', (user_id, current_user.school_id))
        db.commit()
        flash('Student account deleted successfully.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error deleting student: {str(e)}', 'error')
        
    return redirect(url_for('admissions.enroll'))
@admissions_bp.route('/admissions/import', methods=['POST'])
@login_required
def import_students():
    if current_user.role not in ['teacher', 'admin']:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('dashboard.dashboard'))
    
    file = request.files.get('file')
    if not file or not file.filename.endswith('.csv'):
        flash('Please upload a valid CSV file.', 'error')
        return redirect(url_for('admissions.enroll'))

    # Use io.StringIO to read the uploaded file as text
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.DictReader(stream)
    
    db = get_db()
    count = 0
    errors = []
    
    try:
        from extensions import mail
        with db_cursor(db) as cursor:
            for row in csv_input:
                full_name = row.get('full_name', '').strip()
                email = row.get('email', '').strip()
                
                if not full_name or not email:
                    continue
                
                username, password = generate_credentials(full_name)
                hashed_password = generate_password_hash(password)
                
                try:
                    # 1. Create User
                    cursor.execute(
                        'INSERT INTO users (username, password_hash, role, school_id) VALUES (%s, %s, %s, %s) RETURNING id',
                        (username, hashed_password, 'student', current_user.school_id)
                    )
                    user_id = cursor.fetchone()[0]
                    
                    # 2. Create Student Details
                    admission_number = f"ADM{user_id:04d}"
                    cursor.execute(
                        '''INSERT INTO student_details 
                        (user_id, full_name, email, admission_number, school_id) 
                        VALUES (%s, %s, %s, %s, %s)''',
                        (user_id, full_name, email, admission_number, current_user.school_id)
                    )
                    
                    # 3. Send Credentials Email
                    msg = Message(
                        'Student OS - Your Login Credentials',
                        recipients=[email]
                    )
                    msg.body = f"Welcome {full_name}!\n\nYour account is ready.\nUsername: {username}\nPassword: {password}\n\nLogin: {request.host_url}"
                    # Try sending but don't fail the whole import if one fails
                    try:
                        mail.send(msg)
                    except: pass
                    
                    count += 1
                except Exception as e:
                    errors.append(f"Row {count+2}: {str(e)}")
                    
        db.commit()
        if errors:
            flash(f'Imported {count} students with {len(errors)} errors: {", ".join(errors[:3])}...', 'warning')
        else:
            flash(f'Successfully imported {count} students!', 'success')
            
    except Exception as e:
        db.rollback()
        flash(f'Import failed: {str(e)}', 'error')
        
    return redirect(url_for('admissions.enroll'))
