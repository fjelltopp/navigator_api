import os

import ckanapi
from flask import current_app

from navigator_api.app import create_app


def init_ckan(apikey=None):
    return ckanapi.RemoteCKAN(current_app.config['CKAN_URL'], apikey=apikey)


def fetch_country_estimates_datasets(ckan_cli):
    response = ckan_cli.action.package_search(q="type:country-estimates-22", rows=100000, hide_inaccessible_resources=True)
    return response["results"]

def fetch_users_organization_ids(ckan_cli):
    response = ckan_cli.action.organization_list_for_user(permission="read")
    return [org['id'] for org in response]

def fetch_dataset_details(ckan_cli, dataset_id):
    response = ckan_cli.action.package_show(id=dataset_id)
    return response


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        ckan_cli = init_ckan(apikey=os.getenv('CKAN_APIKEY'))
        pass
