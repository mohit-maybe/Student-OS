from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, current_app, send_file
from flask_login import login_required, current_user
from db import get_db
from helpers import add_notification
from reports import generate_student_report_card
import io
import zipfile



academic_bp = Blueprint('academic', __name__)

@academic_bp.route('/grades', methods=['GET', 'POST'])
@login_required
def grades():
    db = get_db()
    from db import db_cursor
    with db_cursor(db) as cursor:
        if request.method == 'POST' and current_user.role == 'teacher':
            score = float(request.form.get('score', 0))
            if not (0 <= score <= 100):
                flash('Score must be between 0 and 100.', 'error')
                return redirect(url_for('academic.grades'))
                
            cursor.execute('INSERT INTO grades (student_id, course_id, score, grade_type, school_id) VALUES (%s, %s, %s, %s, %s)',
                       (request.form.get('student_id'), request.form.get('course_id'), 
                        request.form.get('score'), request.form.get('grade_type'), current_user.school_id))
            db.commit()
            flash('Grade added!', 'success')
            
            if request.form.get('redirect_to_course') == 'true':
                return redirect(url_for('courses.course_details', course_id=request.form.get('course_id')))
            return redirect(url_for('academic.grades'))

        elif current_user.role == 'student':
            cursor.execute('''
                SELECT g.*, c.name as course_name FROM grades g 
                JOIN courses c ON g.course_id = c.id WHERE g.student_id = %s AND g.school_id = %s
            ''', (current_user.id, current_user.school_id))
            grades = cursor.fetchall()
        elif current_user.role in ['admin', 'principal']:
            cursor.execute('''
                SELECT g.*, u.username as student_name, c.name as course_name
                FROM grades g JOIN users u ON g.student_id = u.id JOIN courses c ON g.course_id = c.id
                WHERE g.school_id = %s
            ''', (current_user.school_id,))
            grades = cursor.fetchall()
        else:
            # Teacher only sees their course grades
            cursor.execute('''
                SELECT g.*, u.username as student_name, c.name as course_name
                FROM grades g JOIN users u ON g.student_id = u.id JOIN courses c ON g.course_id = c.id
                WHERE c.teacher_id = %s AND g.school_id = %s
            ''', (current_user.id, current_user.school_id))
            grades = cursor.fetchall()
            
        cursor.execute("SELECT * FROM users WHERE role = 'student' AND school_id = %s", (current_user.school_id,))
        students = cursor.fetchall()
        cursor.execute('SELECT * FROM courses WHERE teacher_id = %s AND school_id = %s', (current_user.id, current_user.school_id))
        my_courses = cursor.fetchall()
    return render_template('grades.html', grades=grades, courses=my_courses, students=students, user=current_user)

@academic_bp.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    db = get_db()
    from db import db_cursor
    with db_cursor(db) as cursor:
        if request.method == 'POST' and current_user.role == 'teacher':
            cursor.execute('INSERT INTO attendance (student_id, course_id, date, status, school_id) VALUES (%s, %s, %s, %s, %s)',
                       (request.form.get('student_id'), request.form.get('course_id'), 
                        request.form.get('date'), request.form.get('status'), current_user.school_id))
            db.commit()
            flash('Log updated!', 'success')
            return redirect(url_for('academic.attendance'))

        elif current_user.role == 'student':
            cursor.execute('''
                SELECT a.*, c.name as course_name FROM attendance a 
                JOIN courses c ON a.course_id = c.id WHERE a.student_id = %s AND a.school_id = %s ORDER BY a.date DESC
            ''', (current_user.id, current_user.school_id))
            logs = cursor.fetchall()
        elif current_user.role in ['admin', 'principal']:
            cursor.execute('''
                SELECT a.*, u.username as student_name, c.name as course_name
                FROM attendance a 
                JOIN users u ON a.student_id = u.id 
                JOIN courses c ON a.course_id = c.id
                WHERE a.school_id = %s ORDER BY a.date DESC
            ''', (current_user.school_id,))
            logs = cursor.fetchall()
        else:
            cursor.execute('''
                SELECT a.*, u.username as student_name, c.name as course_name
                FROM attendance a 
                JOIN users u ON a.student_id = u.id 
                JOIN courses c ON a.course_id = c.id
                WHERE c.teacher_id = %s AND a.school_id = %s ORDER BY a.date DESC
            ''', (current_user.id, current_user.school_id))
            logs = cursor.fetchall()

            
        cursor.execute("SELECT * FROM users WHERE role = 'student' AND school_id = %s", (current_user.school_id,))
        students = cursor.fetchall()
        cursor.execute('SELECT * FROM courses WHERE teacher_id = %s AND school_id = %s', (current_user.id, current_user.school_id))
        my_courses = cursor.fetchall()
    return render_template('attendance.html', attendance=logs, courses=my_courses, students=students, user=current_user)

@academic_bp.route('/assignment/<int:assignment_id>/grade', methods=['GET'])
@login_required
def view_submissions(assignment_id):
    if current_user.role not in ['teacher', 'admin', 'principal']: return redirect(url_for('dashboard.dashboard'))
    db = get_db()
    from db import db_cursor
    with db_cursor(db) as cursor:
        cursor.execute('SELECT * FROM assignments WHERE id = %s AND school_id = %s', (assignment_id, current_user.school_id))
        assignment = cursor.fetchone()
        cursor.execute('SELECT * FROM courses WHERE id = %s AND school_id = %s', (assignment['course_id'], current_user.school_id))
        course = cursor.fetchone()
        cursor.execute('''
            SELECT s.*, u.username as student_name FROM submissions s 
            JOIN users u ON s.student_id = u.id WHERE s.assignment_id = %s AND s.school_id = %s
        ''', (assignment_id, current_user.school_id))
        submissions = cursor.fetchall()
    return render_template('grading_view.html', assignment=assignment, course=course, submissions=submissions, user=current_user)

@academic_bp.route('/assignment/<int:assignment_id>/submission/<int:submission_id>/grade', methods=['POST'])
@login_required
def grade_submission(assignment_id, submission_id):
    if current_user.role not in ['teacher', 'admin', 'principal']: return redirect(url_for('dashboard.dashboard'))
    
    db = get_db()
    from db import db_cursor
    with db_cursor(db) as cursor:
        cursor.execute('SELECT * FROM submissions WHERE id = %s', (submission_id,))
        sub = cursor.fetchone()
        cursor.execute('SELECT * FROM assignments WHERE id = %s', (assignment_id,))
        assign = cursor.fetchone()
        
        grade = float(request.form.get('grade', 0))
        if not (0 <= grade <= 100):
            flash('Grade must be between 0 and 100.', 'error')
            return redirect(url_for('academic.view_submissions', assignment_id=assignment_id))

        feedback = request.form.get('feedback')

        
        cursor.execute('UPDATE submissions SET grade = %s, feedback = %s WHERE id = %s AND school_id = %s', (grade, feedback, submission_id, current_user.school_id))
        
        # Sync to main grades table
        cursor.execute('SELECT id FROM grades WHERE student_id = %s AND course_id = %s AND grade_type = %s AND school_id = %s',
                               (sub['student_id'], assign['course_id'], f"Assignment: {assign['title']}", current_user.school_id))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('UPDATE grades SET score = %s WHERE id = %s AND school_id = %s', (grade, existing['id'], current_user.school_id))
        else:
            cursor.execute('INSERT INTO grades (student_id, course_id, score, grade_type, school_id) VALUES (%s, %s, %s, %s, %s)',
                       (sub['student_id'], assign['course_id'], grade, f"Assignment: {assign['title']}", current_user.school_id))
        
        # Add Notification
        add_notification(db, sub['student_id'], f"Your work for '{assign['title']}' has been graded: {grade}%", 'success', current_user.school_id)
        
        db.commit()
    flash('Grade assigned and student notified!', 'success')
    return redirect(url_for('academic.view_submissions', assignment_id=assignment_id))


@academic_bp.route('/report/student/<int:student_id>')
@login_required
def download_student_report(student_id):
    if current_user.role not in ['teacher', 'admin', 'principal']: return redirect(url_for('dashboard.dashboard'))
    
    db = get_db()
    from db import db_cursor
    with db_cursor(db) as cursor:
        cursor.execute('SELECT * FROM users WHERE id = %s', (student_id,))
        student = cursor.fetchone()
        
        # Get Grades
        cursor.execute('''
            SELECT c.name, AVG(g.score) as avg_score 
            FROM grades g JOIN courses c ON g.course_id = c.id 
            WHERE g.student_id = %s AND g.school_id = %s GROUP BY c.id, c.name
        ''', (student_id, current_user.school_id))
        grades_data = cursor.fetchall()
        
        # Get Attendance
        cursor.execute('''
            SELECT status, COUNT(*) as count FROM attendance WHERE student_id = %s AND school_id = %s GROUP BY status
        ''', (student_id, current_user.school_id))
        attendance_summary = cursor.fetchall()
        
        # Get Remarks
        cursor.execute('SELECT * FROM remarks WHERE student_id = %s AND school_id = %s ORDER BY created_at DESC', (student_id, current_user.school_id))
        remarks_row = cursor.fetchone()
        remarks_data = dict(remarks_row) if remarks_row else {}

    pdf_buffer = generate_student_report_card(current_app.config['UNIVERSITY_NAME'], student, grades_data, attendance_summary, remarks_data)

    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Report_Card_{student['username']}.pdf",
        mimetype='application/pdf'
    )

@academic_bp.route('/report/batch')
@login_required
def download_batch_reports():
    if current_user.role not in ['teacher', 'admin', 'principal']: return redirect(url_for('dashboard.dashboard'))
    
    db = get_db()
    from db import db_cursor
    with db_cursor(db) as cursor:
        cursor.execute("SELECT * FROM users WHERE role = 'student' AND school_id = %s", (current_user.school_id,))
        students = cursor.fetchall()
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            for student in students:
                # Re-fetch data for each
                cursor.execute('''
                    SELECT c.name, AVG(g.score) as avg_score 
                    FROM grades g JOIN courses c ON g.course_id = c.id 
                    WHERE g.student_id = %s AND g.school_id = %s GROUP BY c.id, c.name
                ''', (student['id'], current_user.school_id))
                grades_data = cursor.fetchall()
                
                cursor.execute('''
                    SELECT status, COUNT(*) as count FROM attendance WHERE student_id = %s AND school_id = %s GROUP BY status
                ''', (student['id'], current_user.school_id))
                attendance_summary = cursor.fetchall()
                
                cursor.execute('SELECT * FROM remarks WHERE student_id = %s AND school_id = %s ORDER BY created_at DESC', (student['id'], current_user.school_id))
                remarks_row = cursor.fetchone()
                remarks_data = dict(remarks_row) if remarks_row else {}

                pdf_buffer = generate_student_report_card(current_app.config['UNIVERSITY_NAME'], student, grades_data, attendance_summary, remarks_data)
                zf.writestr(f"Report_Card_{student['username']}.pdf", pdf_buffer.getvalue())

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name="PTM_Batch_Reports.zip",
        mimetype='application/zip'
    )

@academic_bp.route('/remarks/save', methods=['POST'])
@login_required
def save_remarks():
    if current_user.role not in ['teacher', 'admin', 'principal']: return redirect(url_for('dashboard.dashboard'))
    
    student_id = request.form.get('student_id')
    term = request.form.get('term', 'Term 1')
    remarks = request.form.get('remarks')
    improvement = request.form.get('improvement_areas')
    
    db = get_db()
    from db import db_cursor
    with db_cursor(db) as cursor:
        cursor.execute('SELECT id FROM remarks WHERE student_id = %s AND term = %s AND school_id = %s', (student_id, term, current_user.school_id))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('UPDATE remarks SET remarks = %s, improvement_areas = %s WHERE id = %s AND school_id = %s',
                       (remarks, improvement, existing['id'], current_user.school_id))
        else:
            cursor.execute('INSERT INTO remarks (student_id, teacher_id, term, remarks, improvement_areas, school_id) VALUES (%s, %s, %s, %s, %s, %s)',
                       (student_id, current_user.id, term, remarks, improvement, current_user.school_id))
        
        db.commit()
    flash('Performance evaluation updated!', 'success')
    return redirect(request.referrer)

@academic_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

