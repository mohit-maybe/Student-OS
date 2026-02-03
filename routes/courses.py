import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from db import get_db
from utils import save_upload, add_notification


courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/courses')
@login_required
def courses():
    db = get_db()
    if current_user.role == 'teacher':
        courses = db.execute('SELECT * FROM courses WHERE teacher_id = ?', (current_user.id,)).fetchall()
    elif current_user.role == 'student':
        courses = db.execute('''
            SELECT c.*, u.username as teacher_name 
            FROM courses c 
            JOIN enrollments e ON c.id = e.course_id 
            JOIN users u ON c.teacher_id = u.id
            WHERE e.student_id = ?
        ''', (current_user.id,)).fetchall()
    else: # Admin sees all
        courses = db.execute('''
            SELECT c.*, u.username as teacher_name 
            FROM courses c 
            LEFT JOIN users u ON c.teacher_id = u.id
        ''').fetchall()
    
    return render_template('courses.html', courses=courses, user=current_user)

@courses_bp.route('/api/courses/search')
@login_required
def search_courses():
    query = request.args.get('q', '')
    db = get_db()
    
    if current_user.role == 'teacher':
        courses = db.execute('''
            SELECT * FROM courses 
            WHERE teacher_id = ? AND name LIKE ?
        ''', (current_user.id, f'%{query}%')).fetchall()
    elif current_user.role == 'student':
        courses = db.execute('''
            SELECT c.*, u.username as teacher_name 
            FROM courses c 
            JOIN enrollments e ON c.id = e.course_id 
            JOIN users u ON c.teacher_id = u.id
            WHERE e.student_id = ? AND c.name LIKE ?
        ''', (current_user.id, f'%{query}%')).fetchall()
    else:
        courses = db.execute('''
            SELECT c.*, u.username as teacher_name 
            FROM courses c 
            LEFT JOIN users u ON c.teacher_id = u.id
            WHERE c.name LIKE ?
        ''', (f'%{query}%',)).fetchall()
        
    return {'courses': [dict(c) for c in courses]}


@courses_bp.route('/course/<int:course_id>')
@login_required
def course_details(course_id):
    db = get_db()
    course = db.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
    if not course:
        flash('Course not found.', 'error')
        return redirect(url_for('courses.courses'))
        
    if current_user.role == 'teacher' and course['teacher_id'] != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('courses.courses'))
    
    assignments = db.execute('SELECT * FROM assignments WHERE course_id = ? ORDER BY due_date', (course_id,)).fetchall()
    students = db.execute('''
        SELECT u.*, sd.full_name 
        FROM users u 
        JOIN enrollments e ON u.id = e.student_id 
        LEFT JOIN student_details sd ON u.id = sd.user_id
        WHERE e.course_id = ?
    ''', (course_id,)).fetchall()
    
    # Fetch students NOT enrolled in this course for the selection list
    available_students = db.execute('''
        SELECT u.id, u.username, sd.full_name 
        FROM users u
        LEFT JOIN student_details sd ON u.id = sd.user_id
        WHERE u.role = 'student' 
        AND u.id NOT IN (SELECT student_id FROM enrollments WHERE course_id = ?)
        ORDER BY u.username
    ''', (course_id,)).fetchall()
    
    return render_template('course_details.html', 
                         course=course, 
                         students=students, 
                         available_students=[dict(s) for s in available_students],
                         user=current_user, 
                         assignments=assignments)

@courses_bp.route('/course/new', methods=['GET', 'POST'])
@login_required
def new_course():
    if current_user.role == 'student':
        flash('Permission denied.', 'error')
        return redirect(url_for('courses.courses'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        schedule = request.form.get('schedule')
        db = get_db()
        db.execute('INSERT INTO courses (name, teacher_id, schedule) VALUES (?, ?, ?)',
                   (name, current_user.id, schedule))
        db.commit()
        flash('Course created!', 'success')
        return redirect(url_for('courses.courses'))
    return render_template('course_form.html', user=current_user, course=None)

@courses_bp.route('/course/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    db = get_db()
    course = db.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
    if not course or (current_user.role != 'admin' and course['teacher_id'] != current_user.id):
        flash('Access denied.', 'error')
        return redirect(url_for('courses.courses'))
        
    if request.method == 'POST':
        db.execute('UPDATE courses SET name = ?, schedule = ? WHERE id = ?',
                   (request.form.get('name'), request.form.get('schedule'), course_id))
        db.commit()
        flash('Course updated!', 'success')
        return redirect(url_for('courses.courses'))
    return render_template('course_form.html', user=current_user, course=course)

@courses_bp.route('/course/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    db = get_db()
    course = db.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
    if not course or (current_user.role != 'admin' and course['teacher_id'] != current_user.id):
        flash('Access denied.', 'error')
        return redirect(url_for('courses.courses'))
        
    db.execute('DELETE FROM courses WHERE id = ?', (course_id,))
    db.commit()
    flash('Course deleted.', 'success')
    return redirect(url_for('courses.courses'))

@courses_bp.route('/course/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_student(course_id):
    if current_user.role not in ['teacher', 'admin']:
        return redirect(url_for('courses.course_details', course_id=course_id))

    username = request.form.get('username')
    db = get_db()
    student = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if not student or student['role'] != 'student':
        flash('Student not found.', 'error')
        return redirect(url_for('courses.course_details', course_id=course_id))
        
    db.execute('INSERT OR IGNORE INTO enrollments (student_id, course_id) VALUES (?, ?)',
               (student['id'], course_id))
    db.commit()
    flash(f'{username} enrolled!', 'success')
    return redirect(url_for('courses.course_details', course_id=course_id))

@courses_bp.route('/course/<int:course_id>/assignment/new', methods=['GET', 'POST'])
@login_required
def new_assignment(course_id):
    if current_user.role not in ['teacher', 'admin']:
        return redirect(url_for('courses.course_details', course_id=course_id))

    if request.method == 'POST':
        path = save_upload(request.files.get('attachment'), current_app.config['UPLOAD_FOLDER'])
        db = get_db()
        db.execute('INSERT INTO assignments (course_id, title, description, due_date, attachment_path) VALUES (?, ?, ?, ?, ?)',
                   (course_id, request.form.get('title'), request.form.get('description'), request.form.get('due_date'), path))
        db.commit()
        flash('Assignment posted!', 'success')
        return redirect(url_for('courses.course_details', course_id=course_id))
    return render_template('assignment_form.html', course_id=course_id, user=current_user)

@courses_bp.route('/course/<int:course_id>/assignment/<int:assignment_id>/submit', methods=['GET', 'POST'])
@login_required
def submit_assignment(course_id, assignment_id):
    if current_user.role != 'student':
        flash('Permission denied.', 'error')
        return redirect(url_for('courses.course_details', course_id=course_id))

    if request.method == 'POST':
        path = save_upload(request.files.get('attachment'), current_app.config['UPLOAD_FOLDER'])
        db = get_db()
        db.execute('''
            INSERT INTO submissions (assignment_id, student_id, content, attachment_path)
            VALUES (?, ?, ?, ?)
        ''', (assignment_id, current_user.id, request.form.get('content'), path))
        
        # Notify Teacher
        course = db.execute('SELECT teacher_id FROM courses WHERE id = ?', (course_id,)).fetchone()
        assign = db.execute('SELECT title FROM assignments WHERE id = ?', (assignment_id,)).fetchone()
        add_notification(db, course['teacher_id'], f"New submission from {current_user.username} for {assign['title']}", 'info')
        
        db.commit()
        flash('Work submitted!', 'success')
        return redirect(url_for('courses.course_details', course_id=course_id))

    # For GET request, render a submission form
    db = get_db()
    assignment = db.execute('SELECT * FROM assignments WHERE id = ?', (assignment_id,)).fetchone()
    if not assignment:
        flash('Assignment not found.', 'error')
        return redirect(url_for('courses.course_details', course_id=course_id))
    
    return render_template('submit_assignment.html', course_id=course_id, assignment=assignment, user=current_user)
