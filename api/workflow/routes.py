from flask import Blueprint, jsonify

import logic
import model
from api import error
from api.auth import auth0_service
from clients import engine_client, ckan_client

workflow_bp = Blueprint('workflow', __name__)


@workflow_bp.route('/workflows')
@auth0_service.require_auth(None)
def workflow_list():
    user_id = auth0_service.current_user_email()
    _user_details = ckan_client.get_user_details_for_email_or_404(user_id)
    workflows = model.get_workflows(user_id=user_id)
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
        except engine_client.EngineError:
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


@workflow_bp.route('/workflows/<dataset_id>/state')
@auth0_service.require_auth(None)
def workflow_state(dataset_id):
    ckan_username = ckan_client.get_username_from_email_or_404(auth0_service.current_user_email())
    ckan_cli = ckan_client.init_ckan(username_for_substitution=ckan_username)
    user_id = auth0_service.current_user_email()
    try:
        dataset = ckan_client.fetch_dataset_details(ckan_cli, dataset_id)
    except ckan_client.NotFound:
        return error.not_found(f"Could not find dataset with id: {dataset_id}")
    workflow = get_or_create_workflow(dataset['id'], user_id, name=dataset['title'])
    if not workflow:
        return error.error_response(500, f"Couldn't get decision engine details for dataset {dataset_id}")
    try:
        engine_decision = engine_client.get_decision(ckan_cli, dataset_id, skip_actions=workflow.skipped_tasks)
    except engine_client.EngineError as err:
        return error.error_response(500, f"Engine error: {err}")

    task_statuses_map = {action['id']: action for action in engine_decision["actions"]}
    task = engine_decision["decision"]

    task_breadcrumbs = list(task_statuses_map.keys())
    decision_task_id = str(task["id"])
    task_details = task["content"]
    task_progress = engine_decision["progress"]
    skipped_tasks_to_remove = engine_decision.get("removeSkipActions")

    message = logic.workflow_state_message(workflow, task_breadcrumbs, decision_task_id, skipped_tasks_to_remove)

    _update_last_decision_task_id(decision_task_id, workflow)
    workflow.task_statuses_map = task_statuses_map
    model.db.session.add(workflow)
    model.db.session.commit()
    if skipped_tasks_to_remove:
        logic.remove_tasks_from_skipped_list(workflow, skipped_tasks_to_remove)

    current_task = logic.compose_task_details(dataset_id, decision_task_id, task_details,
                                              task_statuses_map[decision_task_id], user_id)
    return jsonify({
        "id": f"{workflow.id}",
        "progress": task_progress["progress"],
        "message": message,
        "milestones": task_progress["milestones"],
        "milestoneListFullyResolved": task_progress["milestoneListFullyResolved"],
        "taskBreadcrumbs": task_breadcrumbs,
        "currentTask": current_task
    })


@workflow_bp.route('/workflows/<dataset_id>/state', methods=['DELETE'])
@auth0_service.require_auth(None)
def workflow_delete(dataset_id):
    user_id = auth0_service.current_user_email()
    workflow = model.get_workflow(dataset_id, user_id)
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
    user_id = auth0_service.current_user_email()
    workflow = model.get_workflow(dataset_id, user_id)
    return task_id in workflow.skipped_tasks
