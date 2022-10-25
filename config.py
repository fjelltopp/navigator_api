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
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CKAN_URL = os.getenv("CKAN_URL", "http://adr.local")
    ENGINE_URL = os.getenv("ENGINE_URL", "http://navigator-engine:5001")
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    LANGUAGES = os.getenv('NAVIGATOR_LANGUAGES', 'en,fr,pt').split(',')
    DEFAULT_LANGUAGE = os.getenv('NAVIGATOR_DEFAULT_LANGUAGE', 'en')
    AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'hivtools.eu.auth0.com')
    AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE', 'http://navigator.minikube')
    AUTH0_EMAIL_NAMESPACE = os.getenv('AUTH0_EMAIL_NAMESPACE', 'http://navigator.minikube/email')
    CKAN_API = os.getenv('CKAN_API_SECRET', '6011357f-a7f8-4367-a47d-8c2ab8059520')


class Testing(Config):
    TESTING = True
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
    LOGGING_LEVEL = logging.WARNING


class Production(Config):
    PRODUCTION = True
    DEBUG = False
    LOGGING_LEVEL = logging.ERROR
    JSON_LOGGING = (os.getenv("ENABLE_JSON_LOGGING", 'true').lower() == 'true')
