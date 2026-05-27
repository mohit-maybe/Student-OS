import os
from db import get_db, db_cursor
from flask import Flask

app = Flask(__name__)
try:
    with app.app_context():
        db = get_db()
        print("DEBUG: DB connected")
        with db_cursor(db) as cursor:
            cursor.execute("SELECT * FROM exam_assets")
            assets = cursor.fetchall()
            for asset in assets:
                print(f"DEBUG: Asset ID: {asset['id']} | Student ID: {asset['student_id']} | File: {asset['file_path']}")
            
            cursor.execute("SELECT id, username FROM users")
            users = cursor.fetchall()
            for u in users:
                print(f"DEBUG: User ID: {u['id']} | Username: {u['username']}")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
