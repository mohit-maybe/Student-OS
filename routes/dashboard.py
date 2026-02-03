from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user
from flask_babel import _
from db import get_db
from utils import calculate_gpa


dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    
    chart_data = {
        'grade_labels': [],
        'grade_values': [],
        'attendance_labels': ['Present', 'Absent', 'Late'],
        'attendance_values': [0, 0, 0]
    }
    
    stats = {}
    recent_activity = []
    notifications = []
    
    # Fetch Notifications
    notifications = db.execute('''
        SELECT * FROM notifications 
        WHERE user_id = ? 
        ORDER BY created_at DESC LIMIT 5
    ''', (current_user.id,)).fetchall()

    
    if current_user.role == 'student':
        # Grade performance
        grades = db.execute('''
            SELECT c.name, AVG(g.score) as avg_score 
            FROM grades g 
            JOIN courses c ON g.course_id = c.id 
            WHERE g.student_id = ? 
            GROUP BY c.id
        ''', (current_user.id,)).fetchall()
        
        for g in grades:
            chart_data['grade_labels'].append(g['name'])
            chart_data['grade_values'].append(round(g['avg_score'], 1))
            
        # Attendance
        attendance = db.execute('''
            SELECT status, COUNT(*) as count 
            FROM attendance WHERE student_id = ? GROUP BY status
        ''', (current_user.id,)).fetchall()
        
        att_dict = {row['status']: row['count'] for row in attendance}
        chart_data['attendance_values'] = [att_dict.get('Present', 0), att_dict.get('Absent', 0), att_dict.get('Late', 0)]

        # Student Stats
        total_att = sum(chart_data['attendance_values'])
        att_rate = f"{int((chart_data['attendance_values'][0]/total_att)*100)}%" if total_att > 0 else "0%"
        
        # Calculate Cumulative GPA
        total_points = sum([calculate_gpa(v) for v in chart_data['grade_values']])
        avg_gpa = round(total_points / len(chart_data['grade_values']), 2) if chart_data['grade_values'] else 0.0

        stats = {
            'card1_label': _('Current GPA'), 'card1_value': f"{avg_gpa} / 4.0",
            'card2_label': _('Total Courses'), 'card2_value': len(chart_data['grade_labels']),
            'card3_label': _('Attendance Rate'), 'card3_value': att_rate,
            'card4_label': _('Status'), 'card4_value': _('Academic Honor') if avg_gpa >= 3.5 else _('Active')
        }

        recent_activity = db.execute('''
            SELECT a.title, c.name as course_name, a.due_date 
            FROM assignments a
            JOIN courses c ON a.course_id = c.id
            JOIN enrollments e ON c.id = e.course_id
            WHERE e.student_id = ?
            ORDER BY a.created_at DESC LIMIT 5
        ''', (current_user.id,)).fetchall()

    elif current_user.role == 'teacher':
        grades = db.execute('''
            SELECT c.name, AVG(g.score) as avg_score 
            FROM grades g 
            JOIN courses c ON g.course_id = c.id 
            WHERE c.teacher_id = ? 
            GROUP BY c.id
        ''', (current_user.id,)).fetchall()
        
        for g in grades:
            chart_data['grade_labels'].append(g['name'])
            chart_data['grade_values'].append(round(g['avg_score'], 1))
            
        attendance = db.execute('''
            SELECT a.status, COUNT(*) as count 
            FROM attendance a 
            JOIN courses c ON a.course_id = c.id 
            WHERE c.teacher_id = ? GROUP BY a.status
        ''', (current_user.id,)).fetchall()
        
        att_dict = {row['status']: row['count'] for row in attendance}
        chart_data['attendance_values'] = [att_dict.get('Present', 0), att_dict.get('Absent', 0), att_dict.get('Late', 0)]

        total_students = db.execute('''
            SELECT COUNT(DISTINCT e.student_id) 
            FROM enrollments e JOIN courses c ON e.course_id = c.id WHERE c.teacher_id = ?
        ''', (current_user.id,)).fetchone()[0]
        
        avg_grade = f"{round(sum(chart_data['grade_values'])/len(chart_data['grade_values']), 1)}%" if chart_data['grade_values'] else "0%"

        stats = {
            'card1_label': _('Class Average'), 'card1_value': avg_grade,
            'card2_label': _('My Courses'), 'card2_value': len(chart_data['grade_labels']),
            'card3_label': _('Total Students'), 'card3_value': total_students,
            'card4_label': _('Status'), 'card4_value': _('Teacher Profile')
        }

        recent_activity = db.execute('''
            SELECT u.username as student_name, a.title as assignment_title, s.submission_date
            FROM submissions s
            JOIN assignments a ON s.assignment_id = a.id
            JOIN courses c ON a.course_id = c.id
            JOIN users u ON s.student_id = u.id
            WHERE c.teacher_id = ?
            ORDER BY s.submission_date DESC LIMIT 5
        ''', (current_user.id,)).fetchall()

    else:
        stats = {
            'card1_label': _('System'), 'card1_value': _('Online'),
            'card2_label': _('Users'), 'card2_value': db.execute('SELECT COUNT(*) FROM users').fetchone()[0],
            'card3_label': _('Courses'), 'card3_value': db.execute('SELECT COUNT(*) FROM courses').fetchone()[0],
            'card4_label': _('Role'), 'card4_value': _(current_user.role.capitalize())
        }

    return render_template('dashboard.html', user=current_user, chart_data=chart_data, stats=stats, 
                           recent_activity=recent_activity, notifications=notifications)


@dashboard_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@dashboard_bp.route('/settings')
@login_required
def settings():
    languages = [
        {'code': 'en', 'name': 'English'},
        {'code': 'hi', 'name': 'Hindi (हिन्दी)'},
        {'code': 'bn', 'name': 'Bengali (বাংলা)'},
        {'code': 'te', 'name': 'Telugu (తెలుగు)'},
        {'code': 'mr', 'name': 'Marathi (मराठी)'},
        {'code': 'ta', 'name': 'Tamil (தமிழ்)'},
        {'code': 'gu', 'name': 'Gujarati (ગુજરાતી)'},
        {'code': 'kn', 'name': 'Kannada (ಕನ್ನಡ)'},
        {'code': 'ml', 'name': 'Malayalam (മലയാളം)'}
    ]
    return render_template('settings.html', user=current_user, languages=languages, current_lang=session.get('language', 'en'))

@dashboard_bp.route('/set_language/<lang_code>')
@login_required
def set_language(lang_code):
    valid_langs = ['en', 'hi', 'bn', 'te', 'mr', 'ta', 'gu', 'kn', 'ml']
    if lang_code in valid_langs:
        session['language'] = lang_code
        flash(f'Language changed successfully!', 'success')
    return redirect(request.referrer or url_for('dashboard.settings'))
