from flask import Blueprint, jsonify, session
from flask_login import login_required

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    return {"app": "navigator_api"}


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
    return jsonify(
        {
            "id": "dataset-1",
            "organisation_name": "Uganda",
            "name": "Uganda Inputs UNAIDS Estimates 2021"
        },
        {
            "id": "dataset-2",
            "organisation_name": "Malawi",
            "name": "Malawi Inputs UNAIDS Estimates 2021"
        },
        {
            "id": "dataset-3",
            "organisation_name": "Antarctica",
            "name": "Antarctica Inputs UNAIDS Estimates 2021"
        },
        {
            "id": "dataset-4",
            "organisation_name": "Sudan",
            "name": "Sudan Inputs UNAIDS Estimates 2021"
        }
    )


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
    return jsonify({
        "id": "xxx-yyy-zzz",
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
        "tasks": [
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
            "content": {
                "title": "Populate ART template",
                "display_html": "<p><strong>Lorem Ipsum</strong> is simply dummy <br /> text of the printing and typesetting industry.</p>",
                "skippable": True,
                "url": "https://dev.adr.fjelltopp.org/datasets"
            }
        }
    })


@main_blueprint.route('/workflows/<dataset_id>/tasks/<task_id>')
def workflow_task_details(dataset_id, task_id):
    return jsonify({
        "id": f"{task_id}",
        "skipped": True,
        "content": {
            "title": "Populate geo template",
            "display_html": "<p>Lorem Ipsum has been the industry's standard dummy text ever since the <strong>1500s</strong></p>",
            "skippable": True,
            "url": "http://fjelltopp.org"
        }
    })


@main_blueprint.route('/workflows/<dataset_id>/tasks/<task_id>/complete', methods=['POST'])
def workflow_task_complete(dataset_id, task_id):
    return jsonify({"message": "success"})


@main_blueprint.route('/workflows/<dataset_id>/tasks/<task_id>/skip', methods=['POST'])
def workflow_task_skip(dataset_id, task_id):
    return jsonify({"message": "success"})
