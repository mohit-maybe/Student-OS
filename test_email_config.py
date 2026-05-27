#!/usr/bin/env python3
"""Test email configuration"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=== Email Configuration Test ===")
print(f"MAIL_USERNAME: {os.getenv('MAIL_USERNAME')}")
print(f"MAIL_PASSWORD configured: {'Yes' if os.getenv('MAIL_PASSWORD') else 'No'}")
print(f"SECRET_KEY configured: {'Yes' if os.getenv('SECRET_KEY') else 'No'}")

# Test Flask mail configuration
try:
    from flask import Flask
    from flask_mail import Mail, Message
    
    app = Flask(__name__)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']
    
    mail = Mail(app)
    
    with app.app_context():
        # Test connection
        print("\n=== Testing Mail Connection ===")
        try:
            # Try to send a test email
            msg = Message(
                'Student OS - Email Configuration Test',
                recipients=[os.getenv('MAIL_USERNAME')]
            )
            msg.html = """
            <h1>Email Configuration Successful!</h1>
            <p>Your Student OS email system is working correctly.</p>
            <p>You will now receive login credentials emails when adding staff members.</p>
            """
            mail.send(msg)
            print("✓ Test email sent successfully!")
            print(f"✓ Check your inbox at {os.getenv('MAIL_USERNAME')}")
        except Exception as e:
            print(f"✗ Email sending failed: {str(e)}")
            print("Note: This could be due to:")
            print("  - Incorrect app password")
            print("  - Gmail security settings")
            print("  - Network connectivity issues")
            
except ImportError as e:
    print(f"✗ Missing dependencies: {str(e)}")
    print("Run: pip install flask-mail python-dotenv")
