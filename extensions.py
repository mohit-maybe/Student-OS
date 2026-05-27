from flask_mail import Mail
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

mail = Mail()
babel = Babel()
csrf = CSRFProtect()
login_manager = LoginManager()
