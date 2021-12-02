import os

import logging
from redis import Redis
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = True
    TESTING = False
    PRODUCTION = False
    JSON_LOGGING = bool(os.getenv("JSON_LOGGING", False))
    LOGGING_LEVEL = logging.DEBUG
    SECRET_KEY = 'tJNJzExKtefVbTj32sbg35'
    SESSION_TYPE = 'redis'
    SESSION_KEY_PREFIX = 'session_api:'
    SESSION_REDIS = Redis(host='redis-navigator', port=6379, db=0)
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CKAN_URL = os.getenv("CKAN_URL", "http://adr.local")
    ENGINE_URL = os.getenv("ENGINE_URL", "http://navigator-engine:5001")


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
    JSON_LOGGING = bool(os.getenv("JSON_LOGGING", True))
