import io
import logging
import os
from urllib.parse import urljoin
from flask import current_app
import ckanapi
import requests

import logic

WORKFLOW_RESOURCE_TYPE = 'navigator-workflow-state'
log = logging.getLogger(__name__)


def get_user_details_for_email(email):
    ckan = init_ckan()
    ret = ckan.action.user_list(email=email)
    if not ret or len(ret) != 1:
        log.error(f'Incorrect user email ({email}), found {len(ret)} candidates')
        raise NotFound(f"User with email {email} not found in CKAN")
    return ret[0]


def get_username_from_email(email):
    return get_user_details_for_email(email)['name']


def get_ckan_client_with_username_for_substitution_from_email(email):
    username = get_username_from_email(email)
    return init_ckan(apikey=current_app.config['CKAN_API'], username_for_substitution=username)


def init_ckan(apikey=None, username_for_substitution=None):
    apikey = apikey or current_app.config['CKAN_APIKEY']
    session = requests.Session()
    if username_for_substitution:
        session.headers.update({'CKAN-Substitute-User': username_for_substitution})
    return ckanapi.RemoteCKAN(current_app.config['CKAN_URL'], apikey=apikey, session=session)


def fetch_country_estimates_datasets(ckan_cli, include_private=True):
    response = ckan_cli.action.package_search(
        q="type:country-estimates-23",
        rows=100000,
        hide_inaccessible_resources=True,
        include_private=include_private
    )
    return response["results"]


def fetch_user_organization_ids(ckan_cli, capacity="create_dataset"):
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
    state_r = requests.get(json_url, headers={'Authorization': ckan_cli.apikey})
    state_json = logic.json_loads(state_r.text)
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
            upload=io.StringIO(logic.json_dumps(workflow_state))
        )
    else:
        ckan_cli.action.resource_patch(
            id=workflow_state_resource['id'],
            upload=io.StringIO(logic.json_dumps(workflow_state))
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


class CkanError(Exception):
    pass


if __name__ == '__main__':
    from app import create_app

    app = create_app()
    with app.app_context():
        ckan_cli = init_ckan(apikey=os.getenv('CKAN_APIKEY'))
        dataset_id = "switzerland-country-estimates-2022"
        state = fetch_workflow_state(ckan_cli, dataset_id)
        push_workflow_state(ckan_cli, dataset_id, {"completedTasks": ["Tomek"]})
        pass
