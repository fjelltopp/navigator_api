import logging

from authlib.integrations.flask_oauth2 import current_token
from flask import Blueprint, jsonify, session
from flask_login import login_required

import logic
from api.validator import require_auth, extract_username_from_token
from clients import ckan_client

api_bp = Blueprint('api', __name__)
log = logging.getLogger(__name__)


@api_bp.route('/')
def index():
    return jsonify({"app": "navigator_api"})


@api_bp.route('/user')
@require_auth(None)
def user_details():
    return jsonify({'message': 'Hello!', 'email': extract_username_from_token(current_token)})
    _user_details = session['ckan_user']
    return jsonify(
        {
            "fullname": _user_details["fullname"],
            "email": _user_details["email"],
        }
    )


@api_bp.route('/datasets')
@require_auth(None)
def datasets():
    ckan_user = session['ckan_user']
    ckan_cli = logic.get_ckan_client_from_session()
    dataset_list = ckan_client.fetch_country_estimates_datasets(ckan_cli)
    orgs = set(ckan_client.fetch_user_organization_ids(ckan_cli, capacity='create_dataset'))
    collab_datasets = set(
        ckan_client.fetch_user_collabolator_ids(ckan_cli, ckan_user_id=ckan_user['id'], capacity='editor')
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
