import dotenv
import os
# import redis

dotenv.load_dotenv()
environment_values = dotenv.dotenv_values()
basedir = os.path.abspath(os.path.dirname(__file__))

class ApplicationConfig:
    SECRET_KEY = "aldkfjalsdjflaskdjflasjfdldas"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = (
        'sqlite:///'
        + os.path.join(basedir, 'database.db')
    )

    # SESSION_TYPE = "redis"
    # SESSION_PERMANENT = False
    # SESSION_USE_SIGNER = True
    # SESSION_REDIS = redis.from_url("redis::127.0.0.01:6379")