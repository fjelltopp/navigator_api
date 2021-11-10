import json
import os
import requests
from urllib.parse import urljoin
from flask import current_app

from navigator_api.app import create_app
from navigator_api.clients import ckan_client


def get_decision_engine(dataset_id, user_id):
    return {"id": "foobar"}


def get_decision(ckan_cli, dataset_id, skip_actions=None):
    if not skip_actions:
        skip_actions = []
    body = {
        "data":
            {
                "url": ckan_client.dataset_show_url(ckan_cli, dataset_id),
                "authorization_header": ckan_cli.apikey
            },
        "skipActions": skip_actions
    }
    return requests.post(urljoin(_engine_url(), "decide/"), data=json.dumps(body)).json()


def get_action(action_id):
    return requests.get(urljoin(_engine_url(), f"action/{action_id}")).json()["content"]


def _engine_url():
    return urljoin(current_app.config['ENGINE_URL'], "api/")

if __name__ == '__main__':
    dataset_id = "3963fdf5-8915-448d-b8dd-9beca9c04a35"
    app = create_app()
    with app.app_context():
        ckan_cli = ckan_client.init_ckan(apikey=os.getenv('CKAN_APIKEY'))
        get_decision(ckan_cli, dataset_id)
        pass