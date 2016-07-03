import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    UPLOAD_FOLDER = 'uploads/'
    ML_FOLDER = os.environ.get('ML_FOLDER')
    SECURITY_REGISTERABLE = True
    SECURITY_POST_LOGIN_VIEW = 'dashboard'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_CHANGEABLE = True
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
    SECURITY_RECOVERABLE = True

    SECURITY_EMAIL_SENDER = 'sumsarizer@gmail.com'

    SMTP_SERVER = os.environ.get('MAIL_SERVER')
    SMTP_LOGIN = os.environ.get('MAIL_USERNAME')
    SMTP_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = True
    MAIL_PORT = os.environ.get('MAIL_PORT')


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://sums:sums@localhost/sums'

class TestingConfig(Config):
    TESTING = True
