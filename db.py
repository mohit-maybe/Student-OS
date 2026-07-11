import os
import psycopg2
import sqlite3
import re
from psycopg2.extras import DictCursor
from flask import g, current_app
from contextlib import contextmanager

def get_db():
    if not current_app:
        # Fallback for initialization outside of request context
        db_url = os.getenv('DATABASE_URL')
        if db_url and ('postgres' in db_url):
            try:
                if db_url.startswith('postgres://'):
                    db_url = db_url.replace('postgres://', 'postgresql://', 1)
                return psycopg2.connect(db_url, cursor_factory=DictCursor)
            except: pass
        db_path = os.getenv('DATABASE', 'student_os.db')
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        return db

    db = getattr(g, '_database', None)
    if db is None:
        db_url = os.getenv('DATABASE_URL')
        if db_url and ('postgres' in db_url):
            try:
                if db_url.startswith('postgres://'):
                    db_url = db_url.replace('postgres://', 'postgresql://', 1)
                db = g._database = psycopg2.connect(db_url, cursor_factory=DictCursor, connect_timeout=10)
                print("[OK] Successfully connected to PostgreSQL")
            except Exception as e:
                print(f"[ERROR] Postgres connection failed: {e}")
                db_url = None
        
        if not db_url:
            db_path = current_app.config.get('DATABASE', 'student_os.db')
            db = g._database = sqlite3.connect(db_path)
            db.row_factory = sqlite3.Row
            
    return db

@contextmanager
def db_cursor(db):
    cursor = db.cursor()
    is_sqlite = hasattr(db, 'row_factory') 
    
    class CursorWrapper:
        def __init__(self, cursor, is_sqlite):
            self.cursor = cursor
            self.is_sqlite = is_sqlite
        
        def execute(self, query, params=None):
            if self.is_sqlite:
                if params is not None:
                    query = query.replace('%s', '?')
                query = re.sub(r'\s+ILIKE\s+', ' LIKE ', query, flags=re.IGNORECASE)
                
                returning_id = False
                if re.search(r'\s+RETURNING\s+id', query, flags=re.IGNORECASE):
                    query = re.sub(r'\s+RETURNING\s+id', '', query, flags=re.IGNORECASE)
                    returning_id = True
                
                try:
                    res = self.cursor.execute(query, params or ())
                    if returning_id:
                        self.last_row_id = self.cursor.lastrowid
                    return res
                except Exception as e:
                    print(f"DEBUG: SQLite Execution Error: {e} | Query: {query}")
                    raise e
            
            if params:
                return self.cursor.execute(query, params)
            return self.cursor.execute(query)
            
        def fetchone(self):
            if self.is_sqlite and hasattr(self, 'last_row_id'):
                row_id = self.last_row_id
                delattr(self, 'last_row_id')
                class MockRow(dict):
                    def __getitem__(self, key):
                        if key == 0 or key == 'id': return row_id
                        return super().__getitem__(key)
                return MockRow({'id': row_id})
            return self.cursor.fetchone()
            
        def fetchall(self):
            return self.cursor.fetchall()
            
        def __getattr__(self, name):
            return getattr(self.cursor, name)

    try:
        yield CursorWrapper(cursor, is_sqlite)
    finally:
        cursor.close()

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db(app):
    """Initializes the database and runs migrations if necessary."""
    # Create a dedicated connection for initialization to avoid 'g' outside request context
    db_url = os.getenv('DATABASE_URL')
    db = None
    if db_url and ('postgres' in db_url):
        try:
            if db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', 'postgresql://', 1)
            db = psycopg2.connect(db_url, cursor_factory=DictCursor, connect_timeout=10)
        except Exception as e:
            print(f"[ERROR] Initialization connection failed: {e}")
    
    if not db:
        db_path = app.config.get('DATABASE', 'student_os.db')
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row

    is_sqlite = hasattr(db, 'row_factory')
    
    try:
        # Fast-path check
        with db_cursor(db) as cursor:
            if is_sqlite:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schools'")
            else:
                cursor.execute("SELECT 1 FROM information_schema.tables WHERE table_name='schools'")
            
            if cursor.fetchone():
                print("[INFO] Database schema already exists, skipping full creation.")
            else:
                print("[START] Creating database schema...")
                with app.open_resource('schema.sql', mode='r') as f:
                    sql_script = f.read()
                    if is_sqlite:
                        sql_script = sql_script.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
                        for statement in sql_script.split(';'):
                            if statement.strip():
                                try:
                                    cursor.execute(statement)
                                except Exception as e:
                                    print(f"[WARN] Schema statement skipped: {e}")
                    else:
                        cursor.execute(sql_script)
                db.commit()

        # Migration system
        print("[MIGRATE] Checking for required migrations...")
        with db_cursor(db) as cursor:
            if is_sqlite:
                cursor.execute("PRAGMA table_info(student_details)")
                cols = [row[1] for row in cursor.fetchall()]
                if 'classroom_id' not in cols:
                    cursor.execute("ALTER TABLE student_details ADD COLUMN classroom_id INTEGER REFERENCES classrooms(id)")
                
                tables = ['users', 'courses', 'classrooms', 'enrollments', 'grades', 'attendance', 
                         'assignments', 'submissions', 'notifications', 'messages', 'remarks', 
                         'student_details', 'teacher_details', 'exam_assets', 'predicted_topics', 
                         'predicted_questions', 'revision_plans', 'schools']
                
                for table in tables:
                    cursor.execute(f"PRAGMA table_info({table})")
                    current_cols = [row[1] for row in cursor.fetchall()]
                    if 'school_id' not in current_cols and table != 'schools':
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN school_id INTEGER DEFAULT 1 REFERENCES schools(id)")
                    if 'created_at' not in current_cols:
                        try:
                            cursor.execute(f"ALTER TABLE {table} ADD COLUMN created_at TIMESTAMP")
                            cursor.execute(f"UPDATE {table} SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
                        except: pass
            else:
                tables = ['users', 'courses', 'classrooms', 'enrollments', 'grades', 'attendance', 
                         'assignments', 'submissions', 'notifications', 'messages', 'remarks', 
                         'student_details', 'teacher_details', 'exam_assets', 'predicted_topics', 
                         'predicted_questions', 'revision_plans']
                
                migration_sql = "DO $$ BEGIN "
                migration_sql += "IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='student_details' AND column_name='classroom_id') THEN ALTER TABLE student_details ADD COLUMN classroom_id INTEGER REFERENCES classrooms(id); END IF; "
                for table in tables:
                    migration_sql += f"IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='{table}' AND column_name='school_id') THEN ALTER TABLE {table} ADD COLUMN school_id INTEGER DEFAULT 1 REFERENCES schools(id); END IF; "
                    migration_sql += f"IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='{table}' AND column_name='created_at') THEN ALTER TABLE {table} ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP; END IF; "
                migration_sql += "IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='schools' AND column_name='created_at') THEN ALTER TABLE schools ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP; END IF; "
                migration_sql += "IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='teacher_details' AND column_name='status') THEN ALTER TABLE teacher_details ADD COLUMN status TEXT DEFAULT 'Active'; END IF; "
                migration_sql += "IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='schools' AND column_name='enabled_features') THEN ALTER TABLE schools ADD COLUMN enabled_features TEXT DEFAULT 'classrooms,admissions,staff_management,courses,grades,attendance,exam_predictor,messages,group_chat'; END IF; "
                migration_sql += "IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='schools' AND column_name='academic_session') THEN ALTER TABLE schools ADD COLUMN academic_session TEXT DEFAULT '2023-24'; END IF; "
                migration_sql += "IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='schools' AND column_name='support_email') THEN ALTER TABLE schools ADD COLUMN support_email TEXT; END IF; "
                migration_sql += "UPDATE schools SET enabled_features = 'classrooms,admissions,staff_management,courses,grades,attendance,exam_predictor,messages,group_chat' WHERE enabled_features IS NULL OR enabled_features = 'exam_predictor,group_chat'; "
                migration_sql += " END $$;"
                cursor.execute(migration_sql)
        
        # SQLite migration for enabled_features
        if is_sqlite:
            with db_cursor(db) as cursor:
                cursor.execute("PRAGMA table_info(schools)")
                cols = [row[1] for row in cursor.fetchall()]
                if 'enabled_features' not in cols:
                    cursor.execute("ALTER TABLE schools ADD COLUMN enabled_features TEXT DEFAULT 'classrooms,admissions,staff_management,courses,grades,attendance,exam_predictor,messages,group_chat'")
                if 'academic_session' not in cols:
                    cursor.execute("ALTER TABLE schools ADD COLUMN academic_session TEXT DEFAULT '2023-24'")
                if 'support_email' not in cols:
                    cursor.execute("ALTER TABLE schools ADD COLUMN support_email TEXT")
                
                # Data Migration to ensure existing schools have all features active
                cursor.execute("UPDATE schools SET enabled_features = 'classrooms,admissions,staff_management,courses,grades,attendance,exam_predictor,messages,group_chat' WHERE enabled_features IS NULL OR enabled_features = 'exam_predictor,group_chat'")

        
        db.commit()
        print("[OK] Database migrations complete.")
    except Exception as e:
        print(f"[WARN] Initialization/Migration failed: {e}")
    finally:
        if db:
            db.close()


