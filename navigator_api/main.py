from flask import Blueprint, jsonify, session
from flask_login import login_required

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return {"app": "navigator_api"}


@bp.route('/profile')
@login_required
def profile():
    return 'Profile'


@bp.route('/user')
@login_required
def user_details():
    user_details = session['ckan_user']
    return jsonify(
        {
            "fullname": user_details["fullname"],
            "email": user_details["email"],
        }
    )


@bp.route('/datasets')
@login_required
def datasets():
    return jsonify(
        {
            "datasets": [
                {
                    "id": "1",
                    "name": "Uganda Inputs UNAIDS Estimates 2021"
                },
                {
                    "id": "2",
                    "name": "Malawi Inputs UNAIDS Estimates 2021"
                },
                {
                    "id": "3",
                    "name": "Antarctica Inputs UNAIDS Estimates 2021"
                }
            ]
        }
    )


@bp.route('/workflows/<dataset_id>/state/')
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


@bp.route('/workflows/<dataset_id>/tasks/<task_id>/complete', methods=['POST'])
def workflow_task_complete(dataset_id, task_id):
    return jsonify({"message": "success"})


@bp.route('/workflows/<dataset_id>/tasks/<task_id>')
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


@bp.route('/workflows/<dataset_id>/tasks/<task_id>/skip', methods=['POST'])
def workflow_task_skip(dataset_id, task_id):
    return jsonify({"message": "success"})

