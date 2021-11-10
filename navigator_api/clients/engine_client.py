import requests
from urllib.parse import urljoin
from flask import current_app

from navigator_api.app import create_app


def get_decision_engine(dataset_id, user_id):
    return {"id": "foobar"}


def get_decision(dataset_id):
    # get CKAN dataset dict for data_url
    # get nav Workflow obj for skipped steps
    # send engine POST request /api/decide
    pass


def get_action(action_id):
    return requests.get(urljoin(_engine_url(), f"action/{action_id}")).json()["content"]


def _engine_url():
    return urljoin(current_app.config['ENGINE_URL'], "api/")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        get_action("2")
        pass