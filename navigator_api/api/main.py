import logging

from flask import Blueprint, jsonify, session
from flask_login import login_required, current_user

import navigator_api.clients.ckan_client as ckan_client
from navigator_api import model
from navigator_api.api import error
from navigator_api.clients import engine_client
from navigator_api.model import get_workflows

main_blueprint = Blueprint('main', __name__)
log = logging.getLogger(__name__)


@main_blueprint.route('/')
def index():
    return jsonify({"app": "navigator_api"})


@main_blueprint.route('/user')
@login_required
def user_details():
    _user_details = session['ckan_user']
    return jsonify(
        {
            "fullname": _user_details["fullname"],
            "email": _user_details["email"],
        }
    )


@main_blueprint.route('/datasets')
@login_required
def datasets():
    ckan_user = session['ckan_user']
    ckan_cli = _get_ckan_client_from_session()
    dataset_list = ckan_client.fetch_country_estimates_datasets(ckan_cli)
    orgs = set(ckan_client.fetch_user_organization_ids(ckan_cli, capacity='editor'))
    collab_datasets = set(
        ckan_client.fetch_user_collabolator_ids(ckan_cli, ckan_user_id=ckan_user['id'], capacity='editor')
    )
    result = []
    for dataset in dataset_list:
        if dataset['organization']['id'] in orgs or dataset['id'] in collab_datasets:
            result.append({
                "id": dataset['id'],
                "organization_name": dataset['organization']['title'],
                "name": dataset["title"]
            })
    return jsonify({
        "datasets": result
    })


@main_blueprint.route('/workflows')
@login_required
def workflow_list():
    workflows = get_workflows(user_id=current_user.id)
    return jsonify({
        "workflows": [
            {
                "id": workflow.dataset_id,
                "name": workflow.name
            } for workflow in workflows
        ]
    })


def get_or_create_workflow(dataset_id, user_id, name=None):
    workflow = model.get_workflow(dataset_id, user_id)
    if not workflow:
        try:
            decision_engine = engine_client.get_decision_engine(dataset_id, user_id)
        except Exception:
            return None
        workflow = model.Workflow(
            dataset_id=dataset_id,
            name=name,
            user_id=user_id,
            decision_engine_id=decision_engine['id']
        )
        model.db.session.add(workflow)
        model.db.session.commit()

    return workflow


@main_blueprint.route('/workflows/<dataset_id>/state')
@login_required
def workflow_state(dataset_id):
    ckan_cli = _get_ckan_client_from_session()
    dataset = ckan_client.fetch_dataset_details(ckan_cli, dataset_id)
    if not dataset:
        return error.not_found(f"Could not find dataset with id: {dataset_id}")
    workflow = get_or_create_workflow(dataset['id'], current_user.id, name=dataset['title'])
    if not workflow:
        return error.error_response(500, f"Couldn't get decision engine details for dataset {dataset_id}")
    engine_decision = engine_client.get_decision(ckan_cli, dataset_id, skip_actions=workflow.skipped_tasks)
    return jsonify({
        "id": f"{workflow.id}",
        "progress": engine_decision["progress"]["progress"],
        "milestones": engine_decision["progress"]["milestones"],
        "milestoneListFullyResolved": engine_decision["progress"]["milestoneListFullyResolved"],
        "taskBreadcrumbs": engine_decision["actions"],
        "currentTask": {
            "id": engine_decision["decision"]["id"],
            "skipped": is_task_skipped(dataset_id, engine_decision["decision"]["id"]),
            "details": _mock_task_details(engine_decision["decision"]["content"])
        }
    })


def is_task_skipped(dataset_id, task_id):
    workflow = model.get_workflow(dataset_id, current_user.id)
    return task_id in workflow.skipped_tasks


@main_blueprint.route('/workflows/<dataset_id>/tasks/<task_id>')
@login_required
def workflow_task_details(dataset_id, task_id):
    try:
        task_details = engine_client.get_action(task_id)
    except Exception:
        log.exception(f"Failed to get task details {task_id}", exc_info=True)
        return error.not_found(f"Failed to get task details {task_id}")
    return jsonify({
        "id": f"{task_id}",
        "skipped": is_task_skipped(dataset_id, task_id),
        "details": _mock_task_details(task_details)
    })


def _mock_task_details(task_details):
    mock = {
        "milestoneId": "6",
        "helpUrls": [
            {"label": "Naomi help docs", "url": "http://example"},
            {"label": "Spectrum documentation", "url": "http://example"}
        ]
    }
    for k, v in mock.items():
        if k not in task_details:
            task_details[k] = v
    return task_details


@main_blueprint.route('/workflows/<dataset_id>/tasks/<task_id>/complete', methods=['POST'])
@login_required
def workflow_task_complete(dataset_id, task_id):
    ckan_cli = _get_ckan_client_from_session()
    try:
        wf_state = ckan_client.fetch_workflow_state(ckan_cli, dataset_id)
        completed_tasks = set(wf_state["completedTasks"])
        completed_tasks.add(str(task_id))
    except ckan_client.NotFound:
        completed_tasks = {str(task_id)}
    new_state = {
        "completedTasks": list(completed_tasks)
    }
    try:
        ckan_client.push_workflow_state(ckan_cli, dataset_id, new_state)
    except ckan_client.NotFound:
        return error.not_found(f"Dataset {dataset_id} not found")
    return jsonify({"message": "success"})


@main_blueprint.route('/workflows/<dataset_id>/tasks/<task_id>/complete', methods=['DELETE'])
@login_required
def workflow_task_undo_complete(dataset_id, task_id):
    ckan_cli = _get_ckan_client_from_session()
    try:
        wf_state = ckan_client.fetch_workflow_state(ckan_cli, dataset_id)
        completed_tasks = set(wf_state["completedTasks"])
    except ckan_client.NotFound:
        return error.not_found(f"Workflow completed tasks not found for dataset {dataset_id}")
    try:
        completed_tasks.remove(str(task_id))
    except KeyError:
        return error.not_found(f"Task {task_id} not found in completed tasks")
    new_state = {
        "completedTasks": list(completed_tasks)
    }
    try:
        ckan_client.push_workflow_state(ckan_cli, dataset_id, new_state)
    except ckan_client.NotFound:
        return error.not_found(f"Dataset {dataset_id} not found")
    return jsonify({"message": "success"})


@main_blueprint.route('/workflows/<dataset_id>/tasks/<task_id>/skip', methods=['POST'])
@login_required
def workflow_task_skip(dataset_id, task_id):
    workflow = model.get_workflow(dataset_id, current_user.id)
    if not workflow:
        return error.not_found(f"Workflow for dataset {dataset_id} not found.")
    if task_id not in workflow.skipped_tasks:
        workflow.skipped_tasks = workflow.skipped_tasks + [task_id]
        model.db.session.add(workflow)
        model.db.session.commit()
    return jsonify({"message": "success"})


def _get_ckan_client_from_session():
    ckan_user = session['ckan_user']
    ckan_cli = ckan_client.init_ckan(apikey=ckan_user['apikey'])
    return ckan_cli
