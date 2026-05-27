from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
import os
from flask_login import login_required, current_user
from db import get_db, db_cursor

schools_bp = Blueprint('schools', __name__)

def _require_superadmin():
    # Only user with ID 1 (original admin) or role 'superadmin' can manage schools
    if current_user.role != 'admin' or current_user.id != 1:
        flash('Unauthorized access. Super-admin only.', 'error')
        return redirect(url_for('dashboard.dashboard'))
    return None

@schools_bp.route('/superadmin/schools')
@login_required
def list_schools():
    redir = _require_superadmin()
    if redir: return redir

    db = get_db()
    with db_cursor(db) as cursor:
        cursor.execute('SELECT * FROM schools ORDER BY id ASC')
        schools = cursor.fetchall()
        
    return render_template('superadmin_schools.html', schools=schools, user=current_user)

@schools_bp.route('/superadmin/schools/add', methods=['POST'])
@login_required
def add_school():
    redir = _require_superadmin()
    if redir: return redir

    name = request.form.get('name', '').strip()
    slug = request.form.get('slug', '').strip().lower()
    primary_color = request.form.get('primary_color', '#4f46e5')

    if not name or not slug:
        flash('Name and Slug are required.', 'error')
        return redirect(url_for('schools.list_schools'))

    db = get_db()
    try:
        with db_cursor(db) as cursor:
            cursor.execute(
                'INSERT INTO schools (name, slug, primary_color) VALUES (%s, %s, %s)',
                (name, slug, primary_color)
            )
        db.commit()
        flash(f'School "{name}" created successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error creating school: {str(e)}', 'error')

    return redirect(url_for('schools.list_schools'))
@schools_bp.route('/superadmin/schools/details/<int:school_id>')
@login_required
def school_details(school_id):
    redir = _require_superadmin()
    if redir: return redir

    db = get_db()
    with db_cursor(db) as cursor:
        # Get basic school info
        cursor.execute('SELECT * FROM schools WHERE id = %s', (school_id,))
        school = cursor.fetchone()
        if not school:
            return {"error": "School not found"}, 404

        # Get counts
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE school_id = %s AND role = %s', (school_id, 'student'))
        student_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE school_id = %s AND role = %s', (school_id, 'teacher'))
        teacher_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM courses WHERE school_id = %s', (school_id,))
        course_count = cursor.fetchone()['count']

        # Estimate DB usage (mocked for now based on record weights)
        # In a real app, you might query pg_database_size or similar
        total_records = student_count + teacher_count + course_count
        db_usage_kb = total_records * 2.5 # 2.5KB per major record estimate
        
        # Simulate profit
        profit = student_count * 15 # $15/student estimate

        return {
            "id": school['id'],
            "name": school['name'],
            "slug": school['slug'],
            "students": student_count,
            "teachers": teacher_count,
            "courses": course_count,
            "db_usage": f"{db_usage_kb:.2f} KB",
            "profit": f"${profit:,}"
        }

@schools_bp.route('/superadmin/schools/export/<int:school_id>')
@login_required
def export_school_data(school_id):
    redir = _require_superadmin()
    if redir: return redir

    from utils.reports import generate_school_excel
    from flask import send_file
    
    filepath = generate_school_excel(school_id)
    if not filepath:
        flash('Failed to generate report.', 'error')
        return redirect(url_for('schools.list_schools'))
    
    return send_file(filepath, as_attachment=True)

@schools_bp.route('/settings/school', methods=['GET', 'POST'])
@login_required
def school_settings():
    if current_user.role != 'admin':
        flash('Unauthorized. Only school admins can modify settings.', 'error')
        return redirect(url_for('dashboard.dashboard'))
    
    db = get_db()
    
    # Super-admin override: allow viewing/editing any school via query param
    target_school_id = current_user.school_id
    is_superadmin = (current_user.id == 1)
    
    if is_superadmin and request.args.get('school_id'):
        target_school_id = int(request.args.get('school_id'))

    if request.method == 'POST':
        name = request.form.get('name')
        academic_session = request.form.get('academic_session', '2023-24')
        support_email = request.form.get('support_email')
        
        # Allow superadmin to change school_id they are editing
        submitted_school_id = request.form.get('school_id', target_school_id)
        
        # Handle Logo Upload
        logo = request.files.get('logo')
        logo_path = None
        if logo and logo.filename:
            filename = f"logo_{submitted_school_id}_{logo.filename}"
            logo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            logo_path = filename

        with db_cursor(db) as cursor:
            # Superadmin can update features
            if is_superadmin:
                features_list = request.form.getlist('features')
                enabled_features = ",".join(features_list)
                
                if logo_path:
                    cursor.execute(
                        'UPDATE schools SET name = %s, academic_session = %s, support_email = %s, logo_path = %s, enabled_features = %s WHERE id = %s',
                        (name, academic_session, support_email, logo_path, enabled_features, submitted_school_id)
                    )
                else:
                    cursor.execute(
                        'UPDATE schools SET name = %s, academic_session = %s, support_email = %s, enabled_features = %s WHERE id = %s',
                        (name, academic_session, support_email, enabled_features, submitted_school_id)
                    )
            else:
                if logo_path:
                    cursor.execute(
                        'UPDATE schools SET name = %s, academic_session = %s, support_email = %s, logo_path = %s WHERE id = %s',
                        (name, academic_session, support_email, logo_path, submitted_school_id)
                    )
                else:
                    cursor.execute(
                        'UPDATE schools SET name = %s, academic_session = %s, support_email = %s WHERE id = %s',
                        (name, academic_session, support_email, submitted_school_id)
                    )
        db.commit()
        flash('School settings updated successfully!', 'success')
        return redirect(url_for('schools.school_settings', school_id=submitted_school_id))

    with db_cursor(db) as cursor:
        cursor.execute('SELECT * FROM schools WHERE id = %s', (target_school_id,))
        school = cursor.fetchone()
        
        all_schools = []
        if is_superadmin:
            cursor.execute('SELECT id, name FROM schools ORDER BY name ASC')
            all_schools = cursor.fetchall()
        
    return render_template('school_settings.html', 
                          school=school, 
                          user=current_user, 
                          all_schools=all_schools,
                          is_superadmin=is_superadmin)
