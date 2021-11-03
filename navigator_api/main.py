from flask import Blueprint, jsonify, session
from flask_login import login_required
from .utils import mockup

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
                "id": mockup.id(),
                "title": mockup.milestone(),
                "completed": True,
                "progress": 100
            },
            {
                "id": mockup.id(),
                "title": mockup.milestone(),
                "completed": False,
                "progress": 50
            },
            {
                "id": mockup.id(),
                "title": mockup.milestone(),
                "completed": False,
                "progress": 0
            }
        ],
        "tasks": [
            mockup.id(),
            mockup.id(),
            mockup.id(),
            mockup.id(),
            mockup.id(),
            mockup.id(),
        ],
        "current_task": {
            "id": mockup.id(),
            "milestone_id": mockup.id(),
            "skippable": mockup.boolean(),
            "content": {
                "display_html": mockup.html(),
                "actionable_links": mockup.actionable_links()
            },
        }
    })


@main_blueprint.route('/workflows/<dataset_id>/tasks/<task_id>/complete', methods=['POST'])
def workflow_task_complete(dataset_id, task_id):
    return jsonify({"message": "success"})


@main_blueprint.route('/workflows/<dataset_id>/tasks/<task_id>/skip', methods=['POST'])
def workflow_task_skip(dataset_id, task_id):
    return jsonify({"message": "success"})
