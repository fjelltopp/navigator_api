from flask import Blueprint, jsonify, session
from flask_login import login_required

import navigator_api.ckan as ckan

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
    ckan_cli = _get_ckan_client_from_session()
    datasets = ckan.fetch_country_estimates_datasets(ckan_cli)
    result = [{
        "id": dataset['id'],
        "organizationName": dataset['organization']['name'],
        "name": dataset["title"]
    } for dataset in datasets]
    return jsonify(result)


@main_blueprint.route('/workflows')
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


@main_blueprint.route('/workflows/<dataset_id>/state')
def workflow_state(dataset_id):
    ckan_cli = _get_ckan_client_from_session()
    dataset = ckan.fetch_dataset_details(ckan_cli, dataset_id)
    return jsonify({
        "id": f"{dataset_id}",
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
def workflow_task_complete(dataset_id, task_id):
    return jsonify({"message": "success"})
    # return latest workflow state


@main_blueprint.route('/workflows/<dataset_id>/tasks/<task_id>/skip', methods=['POST'])
def workflow_task_skip(dataset_id, task_id):
    return jsonify({"message": "success"})
    # return latest workflow state


def _get_ckan_client_from_session():
    user_details = session['ckan_user']
    ckan_cli = ckan.init_ckan(apikey=user_details['apikey'])
    return ckan_cli
