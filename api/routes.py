import logging

from flask import Blueprint, jsonify

from api.auth import auth0_service
from clients import ckan_client

api_bp = Blueprint('api', __name__)
log = logging.getLogger(__name__)


@api_bp.route('/')
def index():
    return jsonify({"app": "navigator_api"})


@api_bp.route('/user')
@auth0_service.require_auth(None)
def user_details():
    _user_details = ckan_client.get_user_details_for_email_or_404(
        auth0_service.current_user_email()
    )
    return jsonify(
        {
            "fullname": _user_details["fullname"],
            "email": _user_details["email"]
        }
    )


@api_bp.route('/datasets')
@auth0_service.require_auth(None)
def datasets():
    ckan_username = ckan_client.get_username_from_email_or_404(auth0_service.current_user_email())
    ckan_cli = ckan_client.init_ckan(username_for_substitution=ckan_username)
    dataset_list = ckan_client.fetch_country_estimates_datasets(ckan_cli)
    orgs = set(ckan_client.fetch_user_organization_ids(ckan_cli, capacity='create_dataset'))
    collab_datasets = set(
        ckan_client.fetch_user_collabolator_ids(ckan_cli, ckan_username, capacity='editor')
    )
    result = []
    for dataset in dataset_list:
        if dataset['organization']['id'] in orgs or dataset['id'] in collab_datasets:
            result.append({
                "id": dataset['id'],
                "organizationName": dataset['organization']['title'],
                "name": dataset["title"]
            })
    return jsonify({
        "datasets": result
    })


if __name__ == '__main__':
    from app import create_app

    app = create_app()
    with app.app_context():
        pass
