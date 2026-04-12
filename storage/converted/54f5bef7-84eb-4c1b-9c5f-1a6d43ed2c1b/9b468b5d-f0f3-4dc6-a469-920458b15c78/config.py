import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-l94ryb(ydgm+ia59483b*k!x7)j)6ou@d!tp1qse2ig*s1nktj')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'db.sqlite3'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
