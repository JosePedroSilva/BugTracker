import os

class Config(object):
<<<<<<< HEAD
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'guess-it'
    SQLALCHEMY_DATABASE_URI = os.environ['postgresql://postgres:2427@localhost/bugTracker']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
=======
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-secret-key'
>>>>>>> parent of b38ccec... sqlite and alembic migration setup
