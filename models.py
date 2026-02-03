from flask_login import UserMixin
from werkzeug.security import check_password_hash
import sqlite3

class User(UserMixin):
    def __init__(self, id, username, password_hash, role):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get(user_id):
        from db import get_db
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if user:
            return User(user['id'], user['username'], user['password_hash'], user['role'])
        return None

    @staticmethod
    def get_by_username(username):
        from db import get_db
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user:
            return User(user['id'], user['username'], user['password_hash'], user['role'])
        return None

