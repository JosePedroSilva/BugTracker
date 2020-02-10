import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-secret-key'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:2427@localhost/bugTracker'
    SQLALCHEMY_TRACK_MODIFICATIONS = False





    #postgresql+psycopg2://postgres:2427@localhost/bugTracker