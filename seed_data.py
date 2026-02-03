import sqlite3
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta

DATABASE = 'student_os.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def seed():
    db = get_db()
    
    print("Clearing existing data (except admin)...")
    # clear tables but keep admin if you want, or just clear all. 
    # Let's clear all to be clean, but re-create admin at the end or verify.
    db.execute('DELETE FROM grades')
    db.execute('DELETE FROM attendance')
    db.execute('DELETE FROM enrollments')
    db.execute('DELETE FROM courses')
    db.execute('DELETE FROM users WHERE username != "admin"')
    db.commit()

    print("Creating Users...")
    users = []
    
    # Teachers
    teachers = [
        ('mr_smith', 'password', 'teacher'),
        ('ms_jones', 'password', 'teacher'),
        ('dr_brown', 'password', 'teacher')
    ]
    
    created_teachers = []
    for username, password, role in teachers:
        pwd_hash = generate_password_hash(password)
        cur = db.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?) RETURNING id',
                   (username, pwd_hash, role))
        user_id = cur.fetchone()['id']
        created_teachers.append({'id': user_id, 'username': username})
        print(f"Created Teacher: {username}")

    # Students
    students_data = [
        ('alice', 'password'),
        ('bob', 'password'),
        ('charlie', 'password'),
        ('david', 'password'),
        ('eve', 'password')
    ]
    
    created_students = []
    for username, password in students_data:
        pwd_hash = generate_password_hash(password)
        cur = db.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?) RETURNING id',
                   (username, pwd_hash, 'student'))
        user_id = cur.fetchone()['id']
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
        cur = db.execute('INSERT INTO courses (name, teacher_id, schedule) VALUES (?, ?, ?) RETURNING id',
                         (name, teacher_id, schedule))
        course_id = cur.fetchone()['id']
        created_courses.append({'id': course_id, 'name': name, 'teacher_id': teacher_id})
        print(f"Created Course: {name}")

    print("Enrolling Students...")
    for student in created_students:
        # Enroll each student in 2 random courses
        enrolled_courses = random.sample(created_courses, 2)
        for course in enrolled_courses:
            db.execute('INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)',
                       (student['id'], course['id']))
            print(f"Enrolled {student['username']} in {course['name']}")

    print("Adding Sample Grades & Attendance...")
    grade_types = ['Homework', 'Quiz', 'Midterm']
    
    for student in created_students:
        # Get their enrolled courses
        cur = db.execute('SELECT course_id FROM enrollments WHERE student_id = ?', (student['id'],))
        my_courses = [row['course_id'] for row in cur.fetchall()]
        
        for course_id in my_courses:
            # Add a grade
            score = random.randint(60, 100)
            g_type = random.choice(grade_types)
            db.execute('INSERT INTO grades (student_id, course_id, score, grade_type) VALUES (?, ?, ?, ?)',
                       (student['id'], course_id, score, g_type))
            
            # Add some attendance
            for i in range(3):
                date = (datetime.now() - timedelta(days=i*2)).strftime('%Y-%m-%d')
                status = random.choice(['Present', 'Present', 'Present', 'Absent', 'Late'])
                db.execute('INSERT INTO attendance (student_id, course_id, date, status) VALUES (?, ?, ?, ?)',
                           (student['id'], course_id, date, status))

    db.commit()
    print("Database seeded successfully!")
    db.close()

if __name__ == '__main__':
    seed()
