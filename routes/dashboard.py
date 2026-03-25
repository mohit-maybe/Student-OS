from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user
from flask_babel import _
from db import get_db
from helpers import calculate_gpa


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
    
    from db import db_cursor
    with db_cursor(db) as cursor:
        # Fetch Notifications
        cursor.execute('''
            SELECT * FROM notifications 
            WHERE user_id = %s AND school_id = %s
            ORDER BY created_at DESC LIMIT 5
        ''', (current_user.id, current_user.school_id))
        notifications = cursor.fetchall()

        
        if current_user.role == 'student':
            # Grade performance
            cursor.execute('''
                SELECT c.name, AVG(g.score) as avg_score 
                FROM grades g 
                JOIN courses c ON g.course_id = c.id 
                WHERE g.student_id = %s AND g.school_id = %s
                GROUP BY c.id, c.name
            ''', (current_user.id, current_user.school_id))
            grades = cursor.fetchall()

            # Classroom Info
            cursor.execute('''
                SELECT cl.name 
                FROM classrooms cl
                JOIN student_details sd ON sd.classroom_id = cl.id
                WHERE sd.user_id = %s AND sd.school_id = %s
            ''', (current_user.id, current_user.school_id))
            classroom_row = cursor.fetchone()
            stats['classroom_name'] = classroom_row['name'] if classroom_row else "Not Assigned"
            
            for g in grades:
                chart_data['grade_labels'].append(g['name'])
                chart_data['grade_values'].append(round(g['avg_score'], 1))
                
            # Attendance
            cursor.execute('''
                SELECT status, COUNT(*) as count 
                FROM attendance WHERE student_id = %s AND school_id = %s GROUP BY status
            ''', (current_user.id, current_user.school_id))
            attendance = cursor.fetchall()
            
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

            cursor.execute('''
                SELECT a.title, c.name as course_name, a.due_date 
                FROM assignments a
                JOIN courses c ON a.course_id = c.id
                JOIN enrollments e ON c.id = e.course_id
                WHERE e.student_id = %s AND a.school_id = %s
                ORDER BY a.created_at DESC LIMIT 5
            ''', (current_user.id, current_user.school_id))
            recent_activity = cursor.fetchall()

        elif current_user.role == 'teacher':
            cursor.execute('''
                SELECT c.name, AVG(g.score) as avg_score 
                FROM grades g 
                JOIN courses c ON g.course_id = c.id 
                WHERE c.teacher_id = %s AND c.school_id = %s
                GROUP BY c.id, c.name
            ''', (current_user.id, current_user.school_id))
            grades = cursor.fetchall()
            
            for g in grades:
                chart_data['grade_labels'].append(g['name'])
                chart_data['grade_values'].append(round(g['avg_score'], 1))
                
            cursor.execute('''
                SELECT a.status, COUNT(*) as count 
                FROM attendance a 
                JOIN courses c ON a.course_id = c.id 
                WHERE c.teacher_id = %s AND c.school_id = %s GROUP BY a.status
            ''', (current_user.id, current_user.school_id))
            attendance = cursor.fetchall()
            
            att_dict = {row['status']: row['count'] for row in attendance}
            chart_data['attendance_values'] = [att_dict.get('Present', 0), att_dict.get('Absent', 0), att_dict.get('Late', 0)]

            cursor.execute('''
                SELECT COUNT(DISTINCT e.student_id) 
                FROM enrollments e JOIN courses c ON e.course_id = c.id WHERE c.teacher_id = %s AND c.school_id = %s
            ''', (current_user.id, current_user.school_id))
            total_students = cursor.fetchone()[0]
            
            avg_grade = f"{round(sum(chart_data['grade_values'])/len(chart_data['grade_values']), 1)}%" if chart_data['grade_values'] else "0%"

            stats = {
                'card1_label': _('Class Average'), 'card1_value': avg_grade,
                'card2_label': _('My Courses'), 'card2_value': len(chart_data['grade_labels']),
                'card3_label': _('Total Students'), 'card3_value': total_students,
                'card4_label': _('Status'), 'card4_value': _('Teacher Profile')
            }

            cursor.execute('''
                SELECT u.username as student_name, a.title as assignment_title, s.submission_date
                FROM submissions s
                JOIN assignments a ON s.assignment_id = a.id
                JOIN courses c ON a.course_id = c.id
                JOIN users u ON s.student_id = u.id
                WHERE c.teacher_id = %s AND c.school_id = %s
                ORDER BY s.submission_date DESC LIMIT 5
            ''', (current_user.id, current_user.school_id))
            recent_activity = cursor.fetchall()

        elif current_user.role == 'principal':
            # 1. School-wide grade average
            cursor.execute('''
                SELECT AVG(score) FROM grades WHERE school_id = %s
            ''', (current_user.school_id,))
            avg_score = cursor.fetchone()[0] or 0
            
            # 2. School-wide attendance distribution
            cursor.execute('''
                SELECT status, COUNT(*) as count 
                FROM attendance WHERE school_id = %s GROUP BY status
            ''', (current_user.school_id,))
            attendance = cursor.fetchall()
            att_dict = {row['status']: row['count'] for row in attendance}
            chart_data['attendance_values'] = [att_dict.get('Present', 0), att_dict.get('Absent', 0), att_dict.get('Late', 0)]
            
            # 3. Faculty count
            cursor.execute('''
                SELECT COUNT(*) FROM users WHERE school_id = %s AND role = 'teacher'
            ''', (current_user.school_id,))
            teacher_count = cursor.fetchone()[0]
            
            # 4. Student count
            cursor.execute('''
                SELECT COUNT(*) FROM users WHERE school_id = %s AND role = 'student'
            ''', (current_user.school_id,))
            student_count = cursor.fetchone()[0]

            stats = {
                'card1_label': _('School Average'), 'card1_value': f"{round(avg_score, 1)}%",
                'card2_label': _('Total Faculty'), 'card2_value': teacher_count,
                'card3_label': _('Total Students'), 'card3_value': student_count,
                'card4_label': _('Status'), 'card4_value': _('Active Monitoring')
            }
            
            # Recent school activity
            cursor.execute('''
                SELECT 'New Admission' as type, full_name as detail, created_at as ts
                FROM student_details WHERE school_id = %s
                UNION ALL
                SELECT 'Grade Posted' as type, 'Classwide' as detail, date_recorded as ts
                FROM grades WHERE school_id = %s
                ORDER BY ts DESC LIMIT 5
            ''', (current_user.school_id, current_user.school_id))
            recent_activity = cursor.fetchall()

        else:
            cursor.execute('SELECT COUNT(*) FROM users WHERE school_id = %s', (current_user.school_id,))
            user_count = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM courses WHERE school_id = %s', (current_user.school_id,))
            course_count = cursor.fetchone()[0]
            stats = {
                'card1_label': _('System'), 'card1_value': _('Online'),
                'card2_label': _('Users'), 'card2_value': user_count,
                'card3_label': _('Courses'), 'card3_value': course_count,
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
