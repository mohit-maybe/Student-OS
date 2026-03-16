import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from db import get_db
from werkzeug.utils import secure_filename
from utils.ai_engine import ExamAIEngine
from datetime import datetime

exam_predictor_bp = Blueprint('exam_predictor', __name__)
ai_engine = ExamAIEngine()

@exam_predictor_bp.route('/exam-predictor')
@login_required
def dashboard():
    db = get_db()
    from db import db_cursor
    with db_cursor(db) as cursor:
        # Fetch uploaded docs
        cursor.execute('SELECT * FROM exam_assets WHERE student_id = %s ORDER BY created_at DESC', (current_user.id,))
        assets = cursor.fetchall()
        
        # Fetch predicted topics
        cursor.execute('SELECT * FROM predicted_topics WHERE student_id = %s ORDER BY probability DESC', (current_user.id,))
        topics = cursor.fetchall()
        
        # Fetch questions
        questions = []
        if topics:
            topic_ids = [t['id'] for t in topics]
            cursor.execute('SELECT q.*, t.topic_name FROM predicted_questions q JOIN predicted_topics t ON q.topic_id = t.id WHERE t.student_id = %s', (current_user.id,))
            questions = cursor.fetchall()
            
        # Fetch revision plan
        cursor.execute('SELECT r.*, t.topic_name FROM revision_plans r JOIN predicted_topics t ON r.topic_id = t.id WHERE r.student_id = %s ORDER BY scheduled_date', (current_user.id,))
        revision_plan = cursor.fetchall()

    return render_template('exam_predictor/dashboard.html', 
                           assets=assets, 
                           topics=topics, 
                           questions=questions, 
                           revision_plan=revision_plan,
                           user=current_user)

@exam_predictor_bp.route('/exam-predictor/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    asset_type = request.form.get('asset_type', 'Past Paper')
    exam_year = request.form.get('exam_year')
    class_level = request.form.get('class_level')

    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'exam_docs')
        os.makedirs(upload_path, exist_ok=True)
        
        file_save_path = os.path.join(upload_path, filename)
        file.save(file_save_path)
        
        db = get_db()
        from db import db_cursor
        with db_cursor(db) as cursor:
            cursor.execute('''
                INSERT INTO exam_assets (student_id, file_path, asset_type, exam_year, class_level)
                VALUES (%s, %s, %s, %s, %s)
            ''', (current_user.id, file_save_path, asset_type, exam_year, class_level))
        db.commit()
        
        flash('File uploaded successfully! Analyzing documents...', 'success')
        # In a real app, this should be a background task (e.g. Celery)
        # For this demo, we'll trigger analysis immediately
        success = run_analysis(current_user.id)
        if success:
            flash('Analysis completed successfully!', 'success')
        else:
            flash('Document analysis failed. Please ensure you upload PDFs with selectable text (not scans or images).', 'warning')
        
        return redirect(url_for('exam_predictor.dashboard'))

def run_analysis(student_id):
    """Internal function to process docs and update predictions."""
    print(f"DEBUG: Starting analysis for student ID {student_id}")
    db = get_db()
    from db import db_cursor
    try:
        with db_cursor(db) as cursor:
            cursor.execute('SELECT * FROM exam_assets WHERE student_id = %s', (student_id,))
            assets = cursor.fetchall()
            
            if not assets:
                print("DEBUG: No assets found for this student.")
                return False

            docs_metadata = []
            for asset in assets:
                print(f"DEBUG: Analyzing file: {asset['file_path']}")
                text = ai_engine.extract_text_from_file(asset['file_path'])
                if text and len(text) > 50:
                    print(f"DEBUG: Successfully extracted {len(text)} text context.")
                    docs_metadata.append({
                        'text': text,
                        'year': asset['exam_year'] or datetime.now().year,
                        'type': asset['asset_type']
                    })
                else:
                    print(f"DEBUG: Warning - skipping file {asset['file_path']} due to empty/short text.")
            
            if not docs_metadata:
                print("DEBUG: Analysis aborted - no readable text found in any files.")
                return False

            # Perform Analysis
            topics = ai_engine.analyze_topics(docs_metadata)
            if not topics:
                print("DEBUG: AI Engine returned no topics.")
                return False
            
            print(f"DEBUG: Detected {len(topics)} topics. Updating database...")

            # Clear old predictions for this student
            cursor.execute('DELETE FROM predicted_topics WHERE student_id = %s', (student_id,))
            
            # Insert new predictions
            for t in topics:
                cursor.execute('''
                    INSERT INTO predicted_topics (student_id, topic_name, probability, importance_level)
                    VALUES (%s, %s, %s, %s) RETURNING id
                ''', (student_id, t['topic'], t['probability'], t['importance']))
                topic_id = cursor.fetchone()[0]
                
                # Generate and insert questions for this topic
                questions = ai_engine.generate_questions([t])
                for q in questions:
                    cursor.execute('''
                        INSERT INTO predicted_questions (topic_id, question_text)
                        VALUES (%s, %s)
                    ''', (topic_id, q['question']))
            
            # Generate Revision Plan (default 7 days)
            plan = ai_engine.generate_revision_plan(topics, 7)
            cursor.execute('DELETE FROM revision_plans WHERE student_id = %s', (student_id,))
            for p in plan:
                # Find the topic_id for this topic name
                cursor.execute('SELECT id FROM predicted_topics WHERE student_id = %s AND topic_name = %s', (student_id, p['topic']))
                row = cursor.fetchone()
                if row:
                    cursor.execute('''
                        INSERT INTO revision_plans (student_id, topic_id, scheduled_date)
                        VALUES (%s, %s, %s)
                    ''', (student_id, row[0], p['date']))
            
            db.commit()
            print("DEBUG: Analysis completed successfully.")
            return True
            
    except Exception as e:
        print(f"DEBUG: Analysis failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
