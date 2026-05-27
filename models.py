from flask_login import UserMixin
from werkzeug.security import check_password_hash

class User(UserMixin):
    def __init__(self, id, username, password_hash, role, school_id):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.school_id = school_id

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get(user_id):
        from db import get_db, db_cursor
        db = get_db()
        with db_cursor(db) as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            if user:
                return User(user['id'], user['username'], user['password_hash'], user['role'], user['school_id'])
        return None

    @staticmethod
    def get_by_username(username):
        from db import get_db, db_cursor
        db = get_db()
        with db_cursor(db) as cursor:
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = cursor.fetchone()
            if user:
                return User(user['id'], user['username'], user['password_hash'], user['role'], user['school_id'])
        return None
