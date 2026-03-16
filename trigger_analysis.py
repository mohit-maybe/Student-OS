import os
from flask import Flask
from routes.exam_predictor import run_analysis
from db import get_db

app = Flask(__name__)
# Mock config for upload folder if needed by any imports
app.config['UPLOAD_FOLDER'] = 'uploads'

with app.app_context():
    print("DEBUG: Triggering run_analysis(6)...")
    success = run_analysis(6)
    print(f"DEBUG: run_analysis result: {success}")
    
    if success:
        db = get_db()
        from db import db_cursor
        with db_cursor(db) as cursor:
            cursor.execute("SELECT COUNT(*) FROM predicted_topics WHERE student_id = 6")
            count = cursor.fetchone()[0]
            print(f"DEBUG: Predicted topics for student 1: {count}")
            
            cursor.execute("SELECT * FROM predicted_topics WHERE student_id = 1 LIMIT 5")
            topics = cursor.fetchall()
            for t in topics:
                print(f"DEBUG: Topic: {t['topic_name']} ({t['probability']}%)")
