from threading import Thread

from flask_mail import Mail
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

mail = Mail()
babel = Babel()
csrf = CSRFProtect()
login_manager = LoginManager()


def send_async(app, msg):
    """Send a Flask-Mail Message in a background thread so the request that
    triggered it (e.g. a form submission) doesn't have to wait on the SMTP
    round-trip to finish before it can respond to the user.
    """
    def _send(app, msg):
        with app.app_context():
            try:
                mail.send(msg)
            except Exception as e:
                print(f"[Async Mail] Failed to send '{msg.subject}' to {msg.recipients}: {e}")

    Thread(target=_send, args=(app, msg), daemon=True).start()
