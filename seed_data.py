import os
import psycopg2
from psycopg2.extras import DictCursor
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_db():
    db_url = os.getenv('DATABASE_URL')
    if db_url and db_url.startswith('postgresql'):
        try:
            conn = psycopg2.connect(db_url, cursor_factory=DictCursor)
            return conn
        except Exception as e:
            print(f"Postgres seed connection failed: {e}")
    
    import sqlite3
    db_path = 'student_os.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def seed():
    from db import db_cursor
    db = get_db()
    with db_cursor(db) as cursor:
        print("Clearing existing data (except admin)...")
        cursor.execute('DELETE FROM grades')
        cursor.execute('DELETE FROM attendance')
        cursor.execute('DELETE FROM enrollments')
        cursor.execute('DELETE FROM markings' if False else 'SELECT 1') # Placeholder cleanup
        cursor.execute('DELETE FROM assignments')
        cursor.execute('DELETE FROM submissions')
        cursor.execute('DELETE FROM notifications')
        cursor.execute('DELETE FROM messages')
        cursor.execute('DELETE FROM remarks')
        cursor.execute('DELETE FROM student_details')
        cursor.execute('DELETE FROM courses')
        cursor.execute('DELETE FROM users WHERE username != %s', ("admin",))
        db.commit()

        print("Creating Users...")
        # Teachers
        teachers = [
            ('mr_smith', 'password', 'teacher'),
            ('ms_jones', 'password', 'teacher'),
            ('dr_brown', 'password', 'teacher')
        ]
        
        created_teachers = []
        for username, password, role in teachers:
            pwd_hash = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s) RETURNING id',
                       (username, pwd_hash, role))
            user_id = cursor.fetchone()['id']
            created_teachers.append({'id': user_id, 'username': username})
            print(f"Created Teacher: {username}")

        # Students
        students_data = [
            ('alice', 'Alice Johnson'),
            ('bob', 'Bob Wilson'),
            ('charlie', 'Charlie Davis'),
            ('david', 'David Miller'),
            ('eve', 'Eve Adams')
        ]
        
        created_students = []
        for username, name in students_data:
            pwd_hash = generate_password_hash('password')
            cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s) RETURNING id',
                       (username, pwd_hash, 'student'))
            user_id = cursor.fetchone()['id']
            
            cursor.execute('''INSERT INTO student_details 
                (user_id, full_name, email, admission_number) 
                VALUES (%s, %s, %s, %s)''',
                (user_id, name, f"{username}@example.com", f"ADM{user_id:04d}"))
            
            created_students.append({'id': user_id, 'username': username})
            print(f"Created Student: {username}")

        print("Creating Courses...")
        courses_data = [
            ('Mathematics 101', created_teachers[0]['id'], 'Mon/Wed 10:00 AM'),
            ('History 201', created_teachers[1]['id'], 'Tue/Thu 2:00 PM'),
            ('Physics 101', created_teachers[2]['id'], 'Fri 9:00 AM'),
            ('Computer Science', created_teachers[0]['id'], 'Mon/Wed 1:00 PM')
        ]
        
        created_courses = []
        for name, teacher_id, schedule in courses_data:
            cursor.execute('INSERT INTO courses (name, teacher_id, schedule) VALUES (%s, %s, %s) RETURNING id',
                             (name, teacher_id, schedule))
            course_id = cursor.fetchone()['id']
            created_courses.append({'id': course_id, 'name': name, 'teacher_id': teacher_id})
            print(f"Created Course: {name}")

        print("Enrolling Students...")
        for student in created_students:
            enrolled_courses = random.sample(created_courses, 2)
            for course in enrolled_courses:
                cursor.execute('INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s)',
                           (student['id'], course['id']))
                print(f"Enrolled {student['username']} in {course['name']}")

        print("Adding Sample Grades & Attendance...")
        grade_types = ['Homework', 'Quiz', 'Midterm']
        
        for student in created_students:
            cursor.execute('SELECT course_id FROM enrollments WHERE student_id = %s', (student['id'],))
            my_courses = [row['course_id'] for row in cursor.fetchall()]
            
            for course_id in my_courses:
                score = random.randint(60, 100)
                g_type = random.choice(grade_types)
                cursor.execute('INSERT INTO grades (student_id, course_id, score, grade_type) VALUES (%s, %s, %s, %s)',
                           (student['id'], course_id, score, g_type))
                
                for i in range(3):
                    date = (datetime.now() - timedelta(days=i*2)).date()
                    status = random.choice(['Present', 'Present', 'Present', 'Absent', 'Late'])
                    cursor.execute('INSERT INTO attendance (student_id, course_id, date, status) VALUES (%s, %s, %s, %s)',
                               (student['id'], course_id, date, status))

        db.commit()
    print("Database seeded successfully!")
    db.close()

if __name__ == '__main__':
    seed()
