import os

import ckanapi
from flask import current_app

from navigator_api.app import create_app


def init_ckan(apikey=None):
    return ckanapi.RemoteCKAN(current_app.config['CKAN_URL'], apikey=apikey)


def fetch_country_estimates_datasets(ckan_cli):
    response = ckan_cli.action.package_search(q="type:country-estimates-22", rows=100000, hide_inaccessible_resources=True)
    return response["results"]


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        ckan = init_ckan(apikey=os.getenv('CKAN_APIKEY'))
        pass
