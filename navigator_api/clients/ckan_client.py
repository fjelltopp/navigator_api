from urllib.parse import urljoin

import json

import io
import os
import ckanapi
import requests
from flask import current_app

from navigator_api.app import create_app

WORKFLOW_RESOURCE_TYPE = 'navigator-workflow-state'


def init_ckan(apikey=None):
    return ckanapi.RemoteCKAN(current_app.config['CKAN_URL'], apikey=apikey)


def authenticate_user(password, username):
    ckan = init_ckan()
    ckan_user = ckan.action.user_login(id=username, password=password)
    return ckan_user


def fetch_country_estimates_datasets(ckan_cli, include_private=True):
    response = ckan_cli.action.package_search(
        q="type:country-estimates-22",
        rows=100000,
        hide_inaccessible_resources=True,
        include_private=include_private
    )
    return response["results"]


def fetch_user_organization_ids(ckan_cli, capacity="editor"):
    response = ckan_cli.action.organization_list_for_user(permission=capacity)
    return [org['id'] for org in response]


def fetch_user_collabolator_ids(ckan_cli, ckan_user_id=None, capacity="editor"):
    response = ckan_cli.action.package_collaborator_list_for_user(id=ckan_user_id, capacity=capacity)
    return [dataset['package_id'] for dataset in response]


def fetch_dataset_details(ckan_cli, dataset_id):
    try:
        response = ckan_cli.action.package_show(id=dataset_id)
    except ckanapi.errors.NotFound:
        raise NotFound(f"Dataset {dataset_id} not found in CKAN")
    return response


def fetch_workflow_state(ckan_cli, dataset_id):
    response = fetch_dataset_details(ckan_cli, dataset_id)
    workflow_state_resource = _get_workflow_state(response)
    if not workflow_state_resource:
        raise NotFound(
            f"Dataset {dataset_id} does not contain navigator workflow state"
        )
    json_url = workflow_state_resource['url']
    state_json = requests.get(json_url, headers={'Authorization': ckan_cli.apikey}).json()
    return state_json


def push_workflow_state(ckan_cli, dataset_id, workflow_state):
    response = fetch_dataset_details(ckan_cli, dataset_id)
    workflow_state_resource = _get_workflow_state(response)
    if not workflow_state_resource:
        ckan_cli.action.resource_create(
            package_id=dataset_id,
            name="Navigator Workflow",
            resource_type=WORKFLOW_RESOURCE_TYPE,
            filename="navigator_workflow.json",
            format="JSON",
            upload=io.StringIO(json.dumps(workflow_state))
        )
    else:
        ckan_cli.action.resource_patch(
            id=workflow_state_resource['id'],
            upload=io.StringIO(json.dumps(workflow_state))
        )


def dataset_show_url(ckan_cli, dataset_id):
    return urljoin(ckan_cli.address, f"api/3/action/package_show?id={dataset_id}")


def _get_workflow_state(response):
    def is_workflow_state(resource):
        return resource['resource_type'] == WORKFLOW_RESOURCE_TYPE
    try:
        workflow_state_resource = list(filter(is_workflow_state, response['resources']))[0]
    except IndexError:
        return None
    return workflow_state_resource


class NotFound(Exception):
    pass


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        ckan_cli = init_ckan(apikey=os.getenv('CKAN_APIKEY'))
        dataset_id = "3963fdf5-8915-448d-b8dd-9beca9c04a35"
        fetch_workflow_state(ckan_cli, dataset_id)
        push_workflow_state(ckan_cli, dataset_id, {"completedTasks": ["Tomek"]})
        pass
