import os

import logging
from redis import Redis
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    ENV_TYPE = os.getenv("ENV_TYPE")
    DEBUG = True
    TESTING = False
    PRODUCTION = False
    JSON_LOGGING = (os.getenv("ENABLE_JSON_LOGGING", 'false').lower() == 'true')
    LOGGING_LEVEL = logging.DEBUG
    SECRET_KEY = 'tJNJzExKtefVbTj32sbg35'
    SESSION_TYPE = 'redis'
    SESSION_KEY_PREFIX = 'session_api:'
    SESSION_REDIS = Redis(host='redis-navigator', port=6379, db=0, socket_connect_timeout=5)
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CKAN_URL = os.getenv("CKAN_URL", "http://adr.local")
    ENGINE_URL = os.getenv("ENGINE_URL", "http://navigator-engine:5001")
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    LANGUAGES = os.getenv('NAVIGATOR_LANGUAGES', 'en,fr,pt_PT').split(',')
    DEFAULT_LANGUAGE = os.getenv('NAVIGATOR_DEFAULT_LANGUAGE', 'en')


class Testing(Config):
    TESTING = True
    DEBUG = False
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(basedir, 'test_session.cache')
    SESSION_FILE_THRESHOLD = 500
    SESSION_FILE_MODE = 384

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
    LOGGING_LEVEL = logging.WARNING


class Production(Config):
    PRODUCTION = True
    DEBUG = False
    LOGGING_LEVEL = logging.ERROR
    JSON_LOGGING = (os.getenv("ENABLE_JSON_LOGGING", 'true').lower() == 'true')
