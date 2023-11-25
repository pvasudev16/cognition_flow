import dotenv
import os
from models import db
from datetime import timedelta

dotenv.load_dotenv()
environment_values = dotenv.dotenv_values()
basedir = os.path.abspath(os.path.dirname(__file__))

class ApplicationConfig:
    SECRET_KEY = "a very secret key"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = (
        'sqlite:///'
        + os.path.join(basedir, 'database.db')
    )

    SESSION_TYPE = "sqlalchemy"
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    SESSION_SQLALCHEMY_TABLE="sessions"
    SESSION_SQLALCHEMY=db
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)

    # SESSION_COOKIE_SECURE = "True" # or True?
    # SESSION_COOKIE_SAMESITE = "None" # or None?
    # SESSION_COOKIE_HTTPONLY = "False" # or False? Do I even need this