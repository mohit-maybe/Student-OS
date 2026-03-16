import os
import psycopg2
from psycopg2.extras import DictCursor
from flask import g, current_app

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db_url = os.getenv('DATABASE_URL')
        if db_url and db_url.startswith('postgresql'):
            try:
                import psycopg2
                from psycopg2.extras import DictCursor
                db = g._database = psycopg2.connect(db_url, cursor_factory=DictCursor)
            except (ImportError, Exception) as e:
                print(f"Postgres connection failed, falling back to SQLite: {e}")
                db_url = None
        
        if not db_url:
            import sqlite3
            db_path = current_app.config.get('DATABASE', 'student_os.db')
            db = g._database = sqlite3.connect(db_path)
            db.row_factory = sqlite3.Row
            
    return db

from contextlib import contextmanager

@contextmanager
def db_cursor(db):
    cursor = db.cursor()
    # Check if we're using SQLite (it won't have the extras or specific connection attributes of psycopg2)
    is_sqlite = hasattr(db, 'row_factory') 
    
    class CursorWrapper:
        def __init__(self, cursor, is_sqlite):
            self.cursor = cursor
            self.is_sqlite = is_sqlite
        
        def execute(self, query, params=None):
            if self.is_sqlite:
                import re
                # 1. Translate %s to ?
                if params is not None:
                    query = query.replace('%s', '?')
                
                # 2. Case-insensitive translation of ILIKE to LIKE
                query = re.sub(r'\s+ILIKE\s+', ' LIKE ', query, flags=re.IGNORECASE)
                
                # 3. Robustly handle RETURNING id (remove for SQLite, use lastrowid)
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
            # If we stripped 'RETURNING id' for SQLite, we need to mock the result
            if self.is_sqlite and hasattr(self, 'last_row_id'):
                row_id = self.last_row_id
                delattr(self, 'last_row_id')
                # Return a dict-like object for compatibility with ['id'] or [0]
                class MockRow(dict):
                    def __getitem__(self, key):
                        if key == 0 or key == 'id':
                            return row_id
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
    with app.app_context():
        db = get_db()
        is_sqlite = hasattr(db, 'row_factory')
        with app.open_resource('schema.sql', mode='r') as f:
            sql_script = f.read()
            if is_sqlite:
                # SQLite compatibility fixes
                sql_script = sql_script.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
                # Split and execute individually since SQLite's executescript can be picky with certain syntax
                from db import db_cursor
                with db_cursor(db) as cursor:
                    for statement in sql_script.split(';'):
                        if statement.strip():
                            try:
                                cursor.execute(statement)
                            except Exception as e:
                                print(f"Schema statement skipped: {e}")
            else:
                with db.cursor() as cursor:
                    cursor.execute(sql_script)
        db.commit()
        
        # Migration: add classroom_id to student_details if it doesn't exist
        try:
            with db_cursor(db) as cursor:
                if is_sqlite:
                    cursor.execute("PRAGMA table_info(student_details)")
                    cols = [row[1] for row in cursor.fetchall()]
                    if 'classroom_id' not in cols:
                        cursor.execute("ALTER TABLE student_details ADD COLUMN classroom_id INTEGER REFERENCES classrooms(id)")
                else:
                    cursor.execute("""
                        ALTER TABLE student_details 
                        ADD COLUMN IF NOT EXISTS classroom_id INTEGER REFERENCES classrooms(id)
                    """)
            db.commit()
        except Exception as e:
            print(f"Migration warning (classroom_id): {e}")
