# Packages
import os
from flask              import Flask
from flask_sqlalchemy   import SQLAlchemy
from flask_migrate      import Migrate
from dotenv             import load_dotenv
from flask_login        import LoginManager
import logging
from logging.handlers   import SMTPHandler, RotatingFileHandler

# Local imports
from config import Config

# Load environment variables from .env file using python-dotenv package
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

login = LoginManager(app)
login.login_view = 'login'  # type: ignore[attr-defined]


# Initialize database and migration objects
db      = SQLAlchemy(app)
migrate = Migrate(app, db)


# Set up email error logging if mail server is configured and not in debug mode
if not app.debug:

    # Send error logs to email
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Mega Flask Tutorial Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    # Log errors to a file with rotation
    if not os.path.exists('logs'): # if logs directory does not exist create it
        os.mkdir('logs')

    file_handler = RotatingFileHandler(
            'logs/mega_flask_tutorial.log', maxBytes=10240, backupCount=10
            )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Mega Flask Tutorial startup')


from app import routes, models, errors

# Shell context for flask shell command
@app.shell_context_processor
def make_shell_context():
    from app.models import User, Post
    import sqlalchemy as sa
    import sqlalchemy.orm as orm 
    return {
            'sa': sa, 
            'orm': orm, 
            'db': db, 
            'session': db.session,
            'User': User, 
            'Post': Post
            }
