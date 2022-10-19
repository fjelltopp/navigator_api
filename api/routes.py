import logging

from authlib.integrations.flask_oauth2 import current_token
from flask import Blueprint, jsonify

from api.auth0_integration import require_auth
from clients import ckan_client
from clients.ckan_client import init_ckan, extract_email_from_token, \
    get_user_details_for_email_or_404, get_username_from_token_or_404

api_bp = Blueprint('api', __name__)
log = logging.getLogger(__name__)


@api_bp.route('/')
def index():
    return jsonify({"app": "navigator_api"})


@api_bp.route('/user')
@require_auth(None)
def user_details():
    _user_details = get_user_details_for_email_or_404(extract_email_from_token(current_token))
    return jsonify(
        {
            "fullname": _user_details["fullname"],
            "email": _user_details["email"]
        }
    )


@api_bp.route('/datasets')
@require_auth(None)
def datasets():
    username = get_username_from_token_or_404(current_token)
    ckan_cli = init_ckan(username_for_substitution=username)
    dataset_list = ckan_client.fetch_country_estimates_datasets(ckan_cli)
    orgs = set(ckan_client.fetch_user_organization_ids(ckan_cli, capacity='create_dataset'))
    collab_datasets = set(
        ckan_client.fetch_user_collabolator_ids(ckan_cli, username, capacity='editor')
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
