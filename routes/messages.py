from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from db import get_db

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/messages')
@login_required
def inbox():
    db = get_db()
    
    from db import db_cursor
    with db_cursor(db) as cursor:
        # Get distinct conversations (latest message from each unique user we're talking to)
        cursor.execute('''
            SELECT 
                u.id as other_user_id,
                u.username as other_username,
                m.content as last_message,
                m.created_at,
                m.is_read,
                m.sender_id
            FROM users u
            JOIN messages m ON (m.sender_id = u.id AND m.recipient_id = %s) 
                            OR (m.recipient_id = u.id AND m.sender_id = %s)
            WHERE m.id IN (
                SELECT MAX(id) FROM messages 
                WHERE (sender_id = %s OR recipient_id = %s) AND school_id = %s
                GROUP BY CASE WHEN sender_id = %s THEN recipient_id ELSE sender_id END
            )
            ORDER BY m.created_at DESC
        ''', (current_user.id, current_user.id, current_user.id, current_user.id, current_user.school_id, current_user.id))
        conversations = cursor.fetchall()

        # Get unread count
        cursor.execute('SELECT COUNT(*) FROM messages WHERE recipient_id = %s AND is_read = 0 AND school_id = %s', (current_user.id, current_user.school_id))
        unread_total = cursor.fetchone()[0]

    return render_template('messages/inbox.html', conversations=conversations, unread_total=unread_total, user=current_user)

@messages_bp.route('/messages/chat/<int:other_user_id>')
@login_required
def chat(other_user_id):
    db = get_db()
    
    from db import db_cursor
    with db_cursor(db) as cursor:
        if other_user_id == 0:
            # Group Chat Logic
            other_user = {'id': 0, 'username': 'Group Chat', 'role': 'Everyone'}
            
            # Fetch group history with sender info
            cursor.execute('''
                SELECT m.*, u.username as sender_name, u.role as sender_role
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.recipient_id = 0 AND m.school_id = %s
                ORDER BY m.created_at ASC
            ''', (current_user.school_id,))
            history = cursor.fetchall()
        else:
            # Direct Message Logic
            cursor.execute('SELECT * FROM users WHERE id = %s AND school_id = %s', (other_user_id, current_user.school_id))
            other_user = cursor.fetchone()
            if not other_user:
                flash('User not found.', 'error')
                return redirect(url_for('messages.inbox'))

            # Mark as read
            cursor.execute('UPDATE messages SET is_read = 1 WHERE sender_id = %s AND recipient_id = %s AND school_id = %s', (other_user_id, current_user.id, current_user.school_id))
            db.commit()

            # Fetch history
            cursor.execute('''
                SELECT m.*, u.username as sender_name 
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE ((m.sender_id = %s AND m.recipient_id = %s) 
                   OR (m.sender_id = %s AND m.recipient_id = %s))
                   AND m.school_id = %s
                ORDER BY m.created_at ASC
            ''', (current_user.id, other_user_id, other_user_id, current_user.id, current_user.school_id))
            history = cursor.fetchall()

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
    from db import db_cursor
    with db_cursor(db) as cursor:
        # Security: Verify recipient belongs to the same school
        if recipient_id != '0': # Skip check for group chat
            cursor.execute('SELECT id FROM users WHERE id = %s AND school_id = %s', (recipient_id, current_user.school_id))
            if not cursor.fetchone():
                flash('Invalid recipient.', 'error')
                return redirect(url_for('messages.inbox'))

        cursor.execute('INSERT INTO messages (sender_id, recipient_id, content, school_id) VALUES (%s, %s, %s, %s)',
                   (current_user.id, recipient_id, content, current_user.school_id))
    db.commit()
    
    return redirect(url_for('messages.chat', other_user_id=recipient_id))

@messages_bp.route('/messages/new')
@login_required
def new_conversation():
    # Simple list of users we can chat with
    db = get_db()
    from db import db_cursor
    with db_cursor(db) as cursor:
        cursor.execute('SELECT id, username, role FROM users WHERE id != %s AND school_id = %s', (current_user.id, current_user.school_id))
        users = cursor.fetchall()
    return render_template('messages/new.html', users=users, user=current_user)
