import logging
from redis import Redis


class Config(object):
    DEBUG = True
    TESTING = False
    PRODUCTION = False
    LOGGING_LEVEL = logging.DEBUG
    SECRET_KEY = 'tJNJzExKtefVbTj32sbg35'
    SESSION_TYPE = 'redis'
    SESSION_REDIS = Redis(host='navigator.minikube', port=6379, db=1)


class Testing(Config):
    TESTING = True
    DEBUG = False
    LOGGING_LEVEL = logging.WARNING


class Production(Config):
    PRODUCTION = True
    DEBUG = False
    LOGGING_LEVEL = logging.ERROR
