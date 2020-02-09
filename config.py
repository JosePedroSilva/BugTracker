import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'guess-it'
    SQLALCHEMY_DATABASE_URI = os.environ['postgresql://postgres:2427@localhost/bugTracker']
    SQLALCHEMY_TRACK_MODIFICATIONS = False