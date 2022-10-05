import logging

from flask import jsonify, Blueprint
from flask_login import current_user

import logic
import model
from api import error
from api.validator import require_auth
from api.workflow.routes import workflow_state
from clients import engine_client, ckan_client

task_bp = Blueprint('task', __name__)

log = logging.getLogger(__name__)


@task_bp.route('/workflows/<dataset_id>/tasks/<task_id>')
@require_auth(None)
def workflow_task_details(dataset_id, task_id):
    workflow = model.get_workflow(dataset_id, current_user.id)
    if not workflow:
        return error.not_found(f"Couldn't get workflow for dataset {dataset_id}")
    try:
        action = engine_client.get_action(task_id)
    except engine_client.EngineError:
        log.exception(f"Failed to get task details {task_id}", exc_info=True)
        return error.not_found(f"Failed to get task details {task_id}")

    task_status = workflow.task_statuses_map.get(task_id, {})
    task = logic.compose_task_details(dataset_id, task_id, action['content'], task_status)
    return jsonify(task)


@task_bp.route('/workflows/<dataset_id>/tasks/<task_id>/complete', methods=['GET'])
@require_auth(None)
def workflow_task_complete_get(dataset_id, task_id):
    is_completed = logic.is_task_completed(dataset_id, task_id)
    return jsonify({
        "id": task_id,
        "completed": is_completed
    })


@task_bp.route('/workflows/<dataset_id>/tasks/<task_id>/complete', methods=['POST'])
@require_auth(None)
def workflow_task_complete(dataset_id, task_id):
    ckan_cli = logic.get_ckan_client_from_session()
    workflow_state = logic.get_workflow_state(ckan_cli, dataset_id)
    new_state = logic.complete_task(workflow_state, task_id)
    try:
        ckan_client.push_workflow_state(ckan_cli, dataset_id, new_state)
    except ckan_client.NotFound:
        return error.not_found(f"Dataset {dataset_id} not found")
    workflow_task_skip_delete(dataset_id, task_id)
    return jsonify({"message": "success"})


@task_bp.route('/workflows/<dataset_id>/tasks/<task_id>/complete', methods=['DELETE'])
@require_auth(None)
def workflow_task_undo_complete(dataset_id, task_id):
    ckan_cli = logic.get_ckan_client_from_session()
    wf_state = logic.get_workflow_state(ckan_cli, dataset_id)
    try:
        new_state = logic.uncomplete_task(wf_state, task_id)
    except logic.LogicError as e:
        return error.not_found(str(e))
    try:
        ckan_client.push_workflow_state(ckan_cli, dataset_id, new_state)
    except ckan_client.NotFound:
        return error.not_found(f"Dataset {dataset_id} not found")
    return jsonify({"message": "success"})


@task_bp.route('/workflows/<dataset_id>/tasks/<task_id>/skip', methods=['POST'])
@require_auth(None)
def workflow_task_skip(dataset_id, task_id):
    workflow = model.get_workflow(dataset_id, current_user.id)
    if not workflow:
        return error.not_found(f"Workflow for dataset {dataset_id} not found.")
    if task_id not in workflow.skipped_tasks:
        workflow.skipped_tasks = workflow.skipped_tasks + [task_id]
        model.db.session.add(workflow)
        model.db.session.commit()
    return jsonify({"message": "success"})


@task_bp.route('/workflows/<dataset_id>/tasks/<task_id>/skip', methods=['DELETE'])
@require_auth(None)
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


@task_bp.route('/workflows/<dataset_id>/tasks', methods=['GET'])
@require_auth(None)
def workflow_task_list(dataset_id):
    ckan_cli = logic.get_ckan_client_from_session()
    workflow = model.get_workflow(dataset_id, current_user.id)
    if not workflow:
        workflow_state(dataset_id)
        workflow = model.get_workflow(dataset_id, current_user.id)
    try:
        task_list = engine_client.get_workflow_tasks(ckan_cli, dataset_id, skip_actions=workflow.skipped_tasks)
    except engine_client.EngineError as err:
        return error.error_response(500, f"Engine error: {err}")

    task_list_with_milestones = logic.get_task_list_with_milestones(dataset_id, task_list['actionList'],
                                                                    task_list['milestones'])

    return jsonify({
        "progress": task_list['progress'],
        "fullyResolved": task_list['fullyResolved'],
        "taskList": task_list_with_milestones
    })
