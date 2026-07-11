CREATE TABLE IF NOT EXISTS schools (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    logo_path TEXT,
    primary_color TEXT DEFAULT '#4f46e5',
    enabled_features TEXT DEFAULT 'classrooms,admissions,staff_management,courses,grades,attendance,exam_predictor,messages,group_chat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    school_id INTEGER DEFAULT 1,
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    teacher_id INTEGER NOT NULL,
    schedule TEXT,
    school_id INTEGER DEFAULT 1,
    FOREIGN KEY (teacher_id) REFERENCES users (id),
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

CREATE TABLE IF NOT EXISTS enrollments (
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    school_id INTEGER DEFAULT 1,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES users (id),
    FOREIGN KEY (course_id) REFERENCES courses (id),
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

CREATE TABLE IF NOT EXISTS grades (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    score REAL NOT NULL,
    max_score REAL NOT NULL DEFAULT 100,
    grade_type TEXT NOT NULL, -- e.g., 'Exam', 'Homework'
    school_id INTEGER DEFAULT 1,
    date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users (id),
    FOREIGN KEY (course_id) REFERENCES courses (id),
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    date DATE NOT NULL,
    status TEXT NOT NULL, -- 'Present', 'Absent', 'Late'
    school_id INTEGER DEFAULT 1,
    FOREIGN KEY (student_id) REFERENCES users (id),
    FOREIGN KEY (course_id) REFERENCES courses (id),
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

CREATE TABLE IF NOT EXISTS assignments (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT, -- HTML content from Quill
    due_date TIMESTAMP,
    attachment_path TEXT, -- Path to uploaded file
    school_id INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses (id),
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    content TEXT, -- HTML content from Quill
    attachment_path TEXT, -- Path to uploaded file
    grade REAL,
    feedback TEXT,
    school_id INTEGER DEFAULT 1,
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES assignments (id),
    FOREIGN KEY (student_id) REFERENCES users (id),
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY, 
    user_id INTEGER NOT NULL, 
    message TEXT NOT NULL, 
    type TEXT DEFAULT 'info', 
    is_read BOOLEAN DEFAULT FALSE, 
    school_id INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY, 
    sender_id INTEGER NOT NULL, 
    recipient_id INTEGER NOT NULL, 
    content TEXT NOT NULL, 
    is_read BOOLEAN DEFAULT FALSE, 
    school_id INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (sender_id) REFERENCES users (id), 
    FOREIGN KEY (recipient_id) REFERENCES users (id),
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

CREATE TABLE IF NOT EXISTS remarks (
    id SERIAL PRIMARY KEY, 
    student_id INTEGER NOT NULL, 
    teacher_id INTEGER NOT NULL, 
    term TEXT, 
    remarks TEXT, 
    improvement_areas TEXT, 
    school_id INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (student_id) REFERENCES users (id), 
    FOREIGN KEY (teacher_id) REFERENCES users (id),
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

CREATE TABLE IF NOT EXISTS student_details (
    user_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT,
    mobile TEXT,
    dob TEXT,
    gender TEXT,
    address TEXT,
    parent_name TEXT,
    parent_mobile TEXT,
    parent_email TEXT,
    admission_number TEXT UNIQUE,
    classroom_id INTEGER,
    school_id INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (classroom_id) REFERENCES classrooms (id),
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

CREATE TABLE IF NOT EXISTS classrooms (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    section TEXT,
    teacher_id INTEGER,
    academic_year TEXT DEFAULT '2025-2026',
    school_id INTEGER DEFAULT 1,
    UNIQUE(name, school_id),
    FOREIGN KEY (teacher_id) REFERENCES users (id),
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

-- AI Exam Predictor Tables
CREATE TABLE IF NOT EXISTS exam_assets (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER,
    file_path TEXT NOT NULL,
    asset_type TEXT NOT NULL, -- 'Past Paper', 'Syllabus', 'Notes'
    exam_year INTEGER,
    class_level TEXT, -- 'Class 10', 'Class 11', 'Class 12'
    school_id INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users (id),
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

CREATE TABLE IF NOT EXISTS predicted_topics (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER,
    topic_name TEXT NOT NULL,
    probability REAL NOT NULL,
    frequency_score REAL,
    importance_level TEXT, -- 'High', 'Medium', 'Low'
    school_id INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users (id),
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

CREATE TABLE IF NOT EXISTS predicted_questions (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_type TEXT, -- 'Theory', 'Numerical', 'Derivation'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES predicted_topics (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS revision_plans (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    scheduled_date DATE NOT NULL,
    status TEXT DEFAULT 'Pending', -- 'Pending', 'Completed'
    school_id INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users (id),
    FOREIGN KEY (topic_id) REFERENCES predicted_topics (id) ON DELETE CASCADE,
    FOREIGN KEY (school_id) REFERENCES schools (id)
);

CREATE TABLE IF NOT EXISTS teacher_details (
    user_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    mobile TEXT,
    department TEXT,
    school_id INTEGER DEFAULT 1,
    status TEXT DEFAULT 'Active', -- 'Active', 'On Leave', 'Inactive'
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (school_id) REFERENCES schools (id)
);
