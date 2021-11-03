import ckanapi
from flask import current_app


def init_ckan(apikey=None):
    return ckanapi.RemoteCKAN(current_app.config['CKAN_URL'], apikey=apikey)
