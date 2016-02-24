import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    STORMPATH_API_KEY_ID = os.environ.get('STORMPATH_API_KEY_ID')
    STORMPATH_API_KEY_SECRET = os.environ.get('STORMPATH_API_KEY_SECRET')
    STORMPATH_APPLICATION = os.environ.get('STORMPATH_APPLICATION')
    STORMPATH_ENABLE_REGISTRATION = False
    STORMPATH_ENABLE_LOGIN = False
    STORMPATH_ENABLE_LOGOUT = False
    UPLOAD_FOLDER = 'uploads/'


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql:///sums'


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('HEROKU_POSTGRESQL_MAROON_URL')


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://sums:sums@localhost/sums'

class TestingConfig(Config):
    TESTING = True
