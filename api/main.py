import logging

from flask import Blueprint, jsonify, session
from flask_login import login_required, current_user

import clients.ckan_client as ckan_client
import logic
import model
from api import error
from clients import engine_client

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
                "organizationName": dataset['organization']['title'],
                "name": dataset["title"]
            })
    return jsonify({
        "datasets": result
    })


@main_blueprint.route('/workflows')
@login_required
def workflow_list():
    workflows = model.get_workflows(user_id=current_user.id)
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
    skipped_task_to_remove = engine_decision.get("removeSkipActions")
    if skipped_task_to_remove:
        logic.remove_tasks_from_skipped_list(workflow, skipped_task_to_remove)
    task_breadcrumbs = [str(action_id) for action_id in engine_decision["actions"]]
    task = engine_decision["decision"]
    decision_task_id = str(task["id"])
    task_details = task["content"]
    task_progress = engine_decision["progress"]

    message = logic.workflow_state_message(workflow, task_breadcrumbs, decision_task_id)
    _update_last_decision_task_id(decision_task_id, workflow)
    return jsonify({
        "id": f"{workflow.id}",
        "progress": task_progress["progress"],
        "message": message,
        "milestones": task_progress["milestones"],
        "milestoneListFullyResolved": task_progress["milestoneListFullyResolved"],
        "taskBreadcrumbs": task_breadcrumbs,
        "currentTask": {
            "id": decision_task_id,
            "skipped": is_task_skipped(dataset_id, task["id"]),
            "manual": task["manualConfirmationRequired"],
            "milestoneID": task_progress["currentMilestoneID"],
            "details": task_details
        }
    })


@main_blueprint.route('/workflows/<dataset_id>/state', methods=['DELETE'])
@login_required
def workflow_delete(dataset_id):
    workflow = model.get_workflow(dataset_id, current_user.id)
    if not workflow:
        return error.error_response(404, f"Workflow for dataset {dataset_id} not found.")
    model.db.session.delete(workflow)
    model.db.session.commit()
    return jsonify({"message": "success"})


def _update_last_decision_task_id(decision_task_id, workflow):
    workflow.last_engine_decision_id = decision_task_id
    model.db.session.add(workflow)
    model.db.session.commit()


def is_task_skipped(dataset_id, task_id):
    workflow = model.get_workflow(dataset_id, current_user.id)
    return task_id in workflow.skipped_tasks


@main_blueprint.route('/workflows/<dataset_id>/tasks/<task_id>')
@login_required
def workflow_task_details(dataset_id, task_id):
    ckan_cli = _get_ckan_client_from_session()
    workflow = model.get_workflow(dataset_id, current_user.id)
    if not workflow:
        return error.not_found(f"Couldn't get workflow for dataset {dataset_id}")
    try:
        task = engine_client.get_action(ckan_cli, dataset_id, task_id, skip_actions=workflow.skipped_tasks)
    except Exception:
        log.exception(f"Failed to get task details {task_id}", exc_info=True)
        return error.not_found(f"Failed to get task details {task_id}")
    task["skipped"] = is_task_skipped(dataset_id, task_id)
    task["details"] = task["content"]
    del task["content"]
    return jsonify(task)


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
    workflow_task_skip_delete(dataset_id, task_id)
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


@main_blueprint.route('/workflows/<dataset_id>/tasks/<task_id>/skip', methods=['DELETE'])
@login_required
def workflow_task_skip_delete(dataset_id, task_id):
    workflow = model.get_workflow(dataset_id, current_user.id)
    if not workflow:
        return error.not_found(f"Workflow for dataset {dataset_id} not found.")
    if task_id not in workflow.skipped_tasks:
        return error.not_found(f"Task {task_id} not found in skipped tasks for workflow {dataset_id}")
    else:
        new_skipped_tasks = set(workflow.skipped_tasks)
        new_skipped_tasks.remove(task_id)
        workflow.skipped_tasks = new_skipped_tasks
        model.db.session.add(workflow)
        model.db.session.commit()
    return jsonify({"message": "success"})


def _get_ckan_client_from_session():
    ckan_user = session['ckan_user']
    ckan_cli = ckan_client.init_ckan(apikey=ckan_user['apikey'])
    return ckan_cli
