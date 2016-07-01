import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    UPLOAD_FOLDER = 'uploads/'
    ML_FOLDER = '/vagrant/ml_labeler'
    SECURITY_REGISTERABLE = True
    SECURITY_POST_LOGIN_VIEW = 'dashboard'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_CHANGEABLE = True
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql:///sums'
    ML_FOLDER = '/home/www/SUMSarizer/ml_labeler'

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://sums:sums@localhost/sums'

class TestingConfig(Config):
    TESTING = True
