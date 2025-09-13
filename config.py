import os

base_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-in-production'

    # Here i diviate from the tutorial for the name of the database file
    # just for convinience i didnt want a folder named 'app' and a file named 'app.db'
    # duo to auto completion in the terminal
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(base_dir, '.app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
