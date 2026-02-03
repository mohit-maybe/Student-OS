from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from db import get_db

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/messages')
@login_required
def inbox():
    db = get_db()
    
    # Get distinct conversations (latest message from each unique user we're talking to)
    # This is a bit complex for SQLite but we can approximate:
    conversations = db.execute('''
        SELECT 
            u.id as other_user_id,
            u.username as other_username,
            m.content as last_message,
            m.created_at,
            m.is_read,
            m.sender_id
        FROM users u
        JOIN messages m ON (m.sender_id = u.id AND m.recipient_id = ?) 
                        OR (m.recipient_id = u.id AND m.sender_id = ?)
        WHERE m.id IN (
            SELECT MAX(id) FROM messages 
            WHERE sender_id = ? OR recipient_id = ? 
            GROUP BY CASE WHEN sender_id = ? THEN recipient_id ELSE sender_id END
        )
        ORDER BY m.created_at DESC
    ''', (current_user.id, current_user.id, current_user.id, current_user.id, current_user.id)).fetchall()

    # Get unread count
    unread_total = db.execute('SELECT COUNT(*) FROM messages WHERE recipient_id = ? AND is_read = 0', (current_user.id,)).fetchone()[0]

    return render_template('messages/inbox.html', conversations=conversations, unread_total=unread_total, user=current_user)

@messages_bp.route('/messages/chat/<int:other_user_id>')
@login_required
def chat(other_user_id):
    db = get_db()
    
    if other_user_id == 0:
        # Group Chat Logic
        other_user = {'id': 0, 'username': 'Group Chat', 'role': 'Everyone'}
        
        # Fetch group history with sender info
        history = db.execute('''
            SELECT m.*, u.username as sender_name, u.role as sender_role
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.recipient_id = 0
            ORDER BY m.created_at ASC
        ''').fetchall()
    else:
        # Direct Message Logic
        other_user = db.execute('SELECT * FROM users WHERE id = ?', (other_user_id,)).fetchone()
        if not other_user:
            flash('User not found.', 'error')
            return redirect(url_for('messages.inbox'))

        # Mark as read
        db.execute('UPDATE messages SET is_read = 1 WHERE sender_id = ? AND recipient_id = ?', (other_user_id, current_user.id))
        db.commit()

        # Fetch history
        history = db.execute('''
            SELECT m.*, u.username as sender_name 
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE (m.sender_id = ? AND m.recipient_id = ?) 
               OR (m.sender_id = ? AND m.recipient_id = ?)
            ORDER BY m.created_at ASC
        ''', (current_user.id, other_user_id, other_user_id, current_user.id)).fetchall()

    return render_template('messages/chat.html', other_user=other_user, history=history, user=current_user)

@messages_bp.route('/messages/send', methods=['POST'])
@login_required
def send_message():
    recipient_id = request.form.get('recipient_id')
    content = request.form.get('content')
    
    if not content:
        flash('Message cannot be empty.', 'error')
        return redirect(request.referrer)

    db = get_db()
    db.execute('INSERT INTO messages (sender_id, recipient_id, content) VALUES (?, ?, ?)',
               (current_user.id, recipient_id, content))
    db.commit()
    
    return redirect(url_for('messages.chat', other_user_id=recipient_id))

@messages_bp.route('/messages/new')
@login_required
def new_conversation():
    # Simple list of users we can chat with
    db = get_db()
    users = db.execute('SELECT id, username, role FROM users WHERE id != ?', (current_user.id,)).fetchall()
    return render_template('messages/new.html', users=users, user=current_user)
