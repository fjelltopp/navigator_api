import logging

import json
import os
import requests
from urllib.parse import urljoin
from flask import current_app

from clients import ckan_client

log = logging.getLogger(__name__)


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
    resp = requests.post(urljoin(_engine_url(), "decide/"), data=json.dumps(body))
    if resp.status_code != 200:
        log.error("Non 200 response from engine: %s", resp.text)
        raise EngineError(f"Failed to get decision for dataset {dataset_id} from the engine")
    try:
        data = resp.json()
    except json.decoder.JSONDecodeError:
        log.exception("Failed to get json response from engine: %s", resp.text)
        raise EngineError(f"Failed to get decision for dataset {dataset_id} from the engine")
    return data


def get_workflow_tasks(ckan_cli, dataset_id, skip_actions=None):
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
    resp = requests.post(urljoin(_engine_url(), "decide/list"), data=json.dumps(body))
    if resp.status_code != 200:
        log.error("Non 200 response from engine: %s", resp.text)
        raise EngineError(f"Failed to get decision list for dataset {dataset_id} from the engine")
    try:
        data = resp.json()
    except json.decoder.JSONDecodeError:
        log.exception("Failed to get json response from engine: %s", resp.text)
        raise EngineError(f"Failed to get decision list for dataset {dataset_id} from the engine")
    return data


def get_action(action_id):
    resp = requests.get(urljoin(_engine_url(), f"action/{action_id}"))
    if resp.status_code != 200:
        log.error("Non 200 response from engine: %s", resp.text)
        raise EngineError(f"Failed to get action details {action_id} from the engine")
    try:
        data = resp.json()
    except json.decoder.JSONDecodeError:
        log.exception("Failed to get json response from engine: %s", resp.text)
        raise EngineError(f"Failed to get action details {action_id} from the engine")
    return data


def _engine_url():
    return urljoin(current_app.config['ENGINE_URL'], "api/")


class EngineError(Exception):
    pass


if __name__ == '__main__':
    from app import create_app
    dataset_id = "3963fdf5-8915-448d-b8dd-9beca9c04a35"
    app = create_app()
    with app.app_context():
        ckan_cli = ckan_client.init_ckan(apikey=os.getenv('CKAN_APIKEY'))
        get_decision(ckan_cli, dataset_id)
        pass
