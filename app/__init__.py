# Packages
from flask              import Flask
from flask_sqlalchemy   import SQLAlchemy
from flask_migrate      import Migrate
from dotenv             import load_dotenv
from flask_login        import LoginManager

# Local imports
from config import Config

# Load environment variables from .env file using python-dotenv package
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

login = LoginManager(app)
login.login_view = 'login'  # Specify the login view for @login_required


# Initialize database and migration objects
db      = SQLAlchemy(app)
migrate = Migrate(app, db)


from app import routes, models

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
