from flask import Blueprint, jsonify, session, abort
from flask_login import login_required, current_user

import navigator_api.ckan_client as ckan_client
from navigator_api import model
from navigator_api.engine_client import get_decision_engine

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    return jsonify({"app": "navigator_api"})


@main_blueprint.route('/user')
@login_required
def user_details():
    user_details = session['ckan_user']
    return jsonify(
        {
            "fullname": user_details["fullname"],
            "email": user_details["email"],
        }
    )


@main_blueprint.route('/datasets')
@login_required
def datasets():
    ckan_user = session['ckan_user']
    ckan_cli = _get_ckan_client_from_session()
    datasets = ckan_client.fetch_country_estimates_datasets(ckan_cli)
    orgs = set(ckan_client.fetch_user_organization_ids(ckan_cli, capacity='editor'))
    collab_datasets = set(ckan_client.fetch_user_collabolator_ids(ckan_cli, ckan_user_id=ckan_user['id'], capacity='editor'))
    result = []
    for dataset in datasets:
        if dataset['organization']['id'] in orgs or dataset['id'] in collab_datasets:
            result.append({
                "id": dataset['id'],
                "organization_name": dataset['organization']['name'],
                "name": dataset["title"]
            })
    return jsonify({
        "datasets": result
    })


@main_blueprint.route('/workflows')
@login_required
def workflow_list():
    return jsonify({
        "workflows": [
            {
                "id": "dataset-1",
                "name": "Uganda Inputs UNAIDS Estimates 2021"
            },
            {
                "id": "dataset-3",
                "name": "Antarctica Inputs UNAIDS Estimates 2021"
            }
        ]
    })


def get_or_create_workflow(dataset_id, user_id):
    workflow = model.get_workflow(dataset_id, user_id)
    if not workflow:
        try:
            decision_engine = get_decision_engine(dataset_id, user_id)
        except Exception:
            return None
        workflow = model.Workflow(dataset_id=dataset_id, user_id=user_id, decision_engine_id=decision_engine['id'])
        model.db.session.add(workflow)
        model.db.session.commit()

    return workflow


@main_blueprint.route('/workflows/<dataset_id>/state')
@login_required
def workflow_state(dataset_id):
    ckan_cli = _get_ckan_client_from_session()
    dataset = ckan_client.fetch_dataset_details(ckan_cli, dataset_id)
    if not dataset:
        abort(404, f"Could not find dataset with id: {dataset_id}")
    workflow = get_or_create_workflow(dataset['id'], current_user.id)
    if not workflow:
        abort(500, f"Couldn't get decision engine details for dataset {dataset_id}")

    return jsonify({
        "id": f"{workflow.id}",
        "milestones": [
            {
                "id": "xxx",
                "title": "Naomi Data Prep",
                "completed": True,
                "progress": 100
            },
            {
                "id": "yyy",
                "title": "Shiny 90 Data Prep",
                "completed": False,
                "progress": 50
            },
            {
                "id": "zzz",
                "title": "Update Spectrum",
                "completed": False,
                "progress": 0
            }
        ],
        "taskBreadcrumps": [
            "aaabbbbcc",
            "dddeeefff",
            "asdfasdfa",
            "aaabbbbcc",
            "dddeeefff",
            "asdfasdfa",
            "aaabbbbcc",
            "dddeeefff",
            "asdfasdfa"
        ],
        "currentTask": {
            "id": "asdfasdfa",
            "skipped": False,
            "details": {
                "milestoneId": "zzz",
                "title": "Populate ART template",
                "displayHtml": "<p><strong>Lorem Ipsum</strong> is simply dummy <br /> text of the printing and typesetting industry.</p>",
                "skippable": True,
                "helpUrls": [
                    {"label": "Naomi help docs", "url":"http://example"},
                    {"label": "Spectrum documentation", "url":"http://example"}
                ]
            }
        }
    })


@main_blueprint.route('/workflows/<dataset_id>/tasks/<task_id>')
@login_required
def workflow_task_details(dataset_id, task_id):
    return jsonify({
        "id": f"{task_id}",
        "skipped": False,
        "details": {
            "milestoneId": "zzz",
            "title": "Populate ART template",
            "displayHtml": "<p><strong>Lorem Ipsum</strong> is simply dummy <br /> text of the printing and typesetting industry.</p>",
            "skippable": True,
            "actionUrl": "https://dev.adr.fjelltopp.org/datasets",
            "helpUrls": [
                {"label": "Naomi help docs", "url": "http://example"},
                {"label": "Spectrum documentation", "url": "http://example"}
            ]
        }
    })


@main_blueprint.route('/workflows/<dataset_id>/tasks/<task_id>/complete', methods=['POST'])
@login_required
def workflow_task_complete(dataset_id, task_id):
    return jsonify({"message": "success"})
    # return latest workflow state


@main_blueprint.route('/workflows/<dataset_id>/tasks/<task_id>/skip', methods=['POST'])
@login_required
def workflow_task_skip(dataset_id, task_id):
    return jsonify({"message": "success"})
    # return latest workflow state


def _get_ckan_client_from_session():
    user_details = session['ckan_user']
    ckan_cli = ckan_client.init_ckan(apikey=user_details['apikey'])
    return ckan_cli
