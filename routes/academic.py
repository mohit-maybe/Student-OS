from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, current_app, send_file
from flask_login import login_required, current_user
from db import get_db
from utils import add_notification
from reports import generate_student_report_card
import io
import zipfile



academic_bp = Blueprint('academic', __name__)

@academic_bp.route('/grades', methods=['GET', 'POST'])
@login_required
def grades():
    db = get_db()
    if request.method == 'POST' and current_user.role == 'teacher':
        score = float(request.form.get('score', 0))
        if not (0 <= score <= 100):
            flash('Score must be between 0 and 100.', 'error')
            return redirect(url_for('academic.grades'))
            
        db.execute('INSERT INTO grades (student_id, course_id, score, grade_type) VALUES (?, ?, ?, ?)',
                   (request.form.get('student_id'), request.form.get('course_id'), 
                    request.form.get('score'), request.form.get('grade_type')))
        db.commit()
        flash('Grade added!', 'success')
        
        if request.form.get('redirect_to_course') == 'true':
            return redirect(url_for('courses.course_details', course_id=request.form.get('course_id')))
        return redirect(url_for('academic.grades'))

    if current_user.role == 'student':
        grades = db.execute('''
            SELECT g.*, c.name as course_name FROM grades g 
            JOIN courses c ON g.course_id = c.id WHERE g.student_id = ?
        ''', (current_user.id,)).fetchall()
    else:
        grades = db.execute('''
            SELECT g.*, u.username as student_name, c.name as course_name
            FROM grades g JOIN users u ON g.student_id = u.id JOIN courses c ON g.course_id = c.id
            WHERE c.teacher_id = ?
        ''', (current_user.id,)).fetchall()
        
    students = db.execute("SELECT * FROM users WHERE role = 'student'").fetchall()
    my_courses = db.execute('SELECT * FROM courses WHERE teacher_id = ?', (current_user.id,)).fetchall()
    return render_template('grades.html', grades=grades, courses=my_courses, students=students, user=current_user)

@academic_bp.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    db = get_db()
    if request.method == 'POST' and current_user.role == 'teacher':
        db.execute('INSERT INTO attendance (student_id, course_id, date, status) VALUES (?, ?, ?, ?)',
                   (request.form.get('student_id'), request.form.get('course_id'), 
                    request.form.get('date'), request.form.get('status')))
        db.commit()
        flash('Log updated!', 'success')
        return redirect(url_for('academic.attendance'))

    if current_user.role == 'student':
        logs = db.execute('''
            SELECT a.*, c.name as course_name FROM attendance a 
            JOIN courses c ON a.course_id = c.id WHERE a.student_id = ? ORDER BY a.date DESC
        ''', (current_user.id,)).fetchall()
    else:
        logs = db.execute('''
            SELECT a.*, u.username as student_name, c.name as course_name
            FROM attendance a 
            JOIN users u ON a.student_id = u.id 
            JOIN courses c ON a.course_id = c.id
            WHERE c.teacher_id = ? ORDER BY a.date DESC
        ''', (current_user.id,)).fetchall()

        
    students = db.execute("SELECT * FROM users WHERE role = 'student'").fetchall()
    my_courses = db.execute('SELECT * FROM courses WHERE teacher_id = ?', (current_user.id,)).fetchall()
    return render_template('attendance.html', attendance=logs, courses=my_courses, students=students, user=current_user)

@academic_bp.route('/assignment/<int:assignment_id>/grade', methods=['GET'])
@login_required
def view_submissions(assignment_id):
    if current_user.role not in ['teacher', 'admin']: return redirect(url_for('dashboard.dashboard'))
    db = get_db()
    assignment = db.execute('SELECT * FROM assignments WHERE id = ?', (assignment_id,)).fetchone()
    course = db.execute('SELECT * FROM courses WHERE id = ?', (assignment['course_id'],)).fetchone()
    submissions = db.execute('''
        SELECT s.*, u.username as student_name FROM submissions s 
        JOIN users u ON s.student_id = u.id WHERE s.assignment_id = ?
    ''', (assignment_id,)).fetchall()
    return render_template('grading_view.html', assignment=assignment, course=course, submissions=submissions, user=current_user)

@academic_bp.route('/assignment/<int:assignment_id>/submission/<int:submission_id>/grade', methods=['POST'])
@login_required
def grade_submission(assignment_id, submission_id):
    if current_user.role not in ['teacher', 'admin']: return redirect(url_for('dashboard.dashboard'))
    
    db = get_db()
    sub = db.execute('SELECT * FROM submissions WHERE id = ?', (submission_id,)).fetchone()
    assign = db.execute('SELECT * FROM assignments WHERE id = ?', (assignment_id,)).fetchone()
    
    grade = float(request.form.get('grade', 0))
    if not (0 <= grade <= 100):
        flash('Grade must be between 0 and 100.', 'error')
        return redirect(url_for('academic.view_submissions', assignment_id=assignment_id))

    feedback = request.form.get('feedback')

    
    db.execute('UPDATE submissions SET grade = ?, feedback = ? WHERE id = ?', (grade, feedback, submission_id))
    
    # Sync to main grades table
    existing = db.execute('SELECT id FROM grades WHERE student_id = ? AND course_id = ? AND grade_type = ?',
                           (sub['student_id'], assign['course_id'], f"Assignment: {assign['title']}")).fetchone()
    
    if existing:
        db.execute('UPDATE grades SET score = ? WHERE id = ?', (grade, existing['id']))
    else:
        db.execute('INSERT INTO grades (student_id, course_id, score, grade_type) VALUES (?, ?, ?, ?)',
                   (sub['student_id'], assign['course_id'], grade, f"Assignment: {assign['title']}"))
    
    # Add Notification
    add_notification(db, sub['student_id'], f"Your work for '{assign['title']}' has been graded: {grade}%", 'success')
    
    db.commit()
    flash('Grade assigned and student notified!', 'success')
    return redirect(url_for('academic.view_submissions', assignment_id=assignment_id))


@academic_bp.route('/report/student/<int:student_id>')
@login_required
def download_student_report(student_id):
    if current_user.role not in ['teacher', 'admin']: return redirect(url_for('dashboard.dashboard'))
    
    db = get_db()
    student = db.execute('SELECT * FROM users WHERE id = ?', (student_id,)).fetchone()
    
    # Get Grades
    grades_data = db.execute('''
        SELECT c.name, AVG(g.score) as avg_score 
        FROM grades g JOIN courses c ON g.course_id = c.id 
        WHERE g.student_id = ? GROUP BY c.id
    ''', (student_id,)).fetchall()
    
    # Get Attendance
    attendance_summary = db.execute('''
        SELECT status, COUNT(*) as count FROM attendance WHERE student_id = ? GROUP BY status
    ''', (student_id,)).fetchall()
    
    # Get Remarks
    remarks_row = db.execute('SELECT * FROM remarks WHERE student_id = ? ORDER BY created_at DESC', (student_id,)).fetchone()
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
    if current_user.role not in ['teacher', 'admin']: return redirect(url_for('dashboard.dashboard'))
    
    db = get_db()
    students = db.execute("SELECT * FROM users WHERE role = 'student'").fetchall()
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        for student in students:
            # Re-fetch data for each
            grades_data = db.execute('''
                SELECT c.name, AVG(g.score) as avg_score 
                FROM grades g JOIN courses c ON g.course_id = c.id 
                WHERE g.student_id = ? GROUP BY c.id
            ''', (student['id'],)).fetchall()
            
            attendance_summary = db.execute('''
                SELECT status, COUNT(*) as count FROM attendance WHERE student_id = ? GROUP BY status
            ''', (student['id'],)).fetchall()
            
            remarks_row = db.execute('SELECT * FROM remarks WHERE student_id = ? ORDER BY created_at DESC', (student['id'],)).fetchone()
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
    if current_user.role not in ['teacher', 'admin']: return redirect(url_for('dashboard.dashboard'))
    
    student_id = request.form.get('student_id')
    term = request.form.get('term', 'Term 1')
    remarks = request.form.get('remarks')
    improvement = request.form.get('improvement_areas')
    
    db = get_db()
    existing = db.execute('SELECT id FROM remarks WHERE student_id = ? AND term = ?', (student_id, term)).fetchone()
    
    if existing:
        db.execute('UPDATE remarks SET remarks = ?, improvement_areas = ? WHERE id = ?',
                   (remarks, improvement, existing['id']))
    else:
        db.execute('INSERT INTO remarks (student_id, teacher_id, term, remarks, improvement_areas) VALUES (?, ?, ?, ?, ?)',
                   (student_id, current_user.id, term, remarks, improvement))
    
    db.commit()
    flash('Performance evaluation updated!', 'success')
    return redirect(request.referrer)

@academic_bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

