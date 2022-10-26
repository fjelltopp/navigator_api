from flask import Blueprint, jsonify

import logic
import model
from api import error
from api.auth import auth0_service
from api.workflow.routes import workflow_state
from clients import engine_client, ckan_client

milestone_bp = Blueprint('milestone', __name__,)


@milestone_bp.route('/workflows/<dataset_id>/milestones/<milestone_id>', methods=['GET'])
@auth0_service.require_auth(None)
def workflow_milestone_details(dataset_id, milestone_id):
    user_id = auth0_service.current_user_email()
    ckan_username = ckan_client.get_username_from_email(user_id)
    ckan_cli = ckan_client.init_ckan(username_for_substitution=ckan_username)
    workflow = model.get_workflow(dataset_id, user_id)
    if not workflow:
        workflow_state(dataset_id)
        workflow = model.get_workflow(dataset_id, user_id)
    try:
        task_list = engine_client.get_workflow_tasks(ckan_cli, dataset_id, skip_actions=workflow.skipped_tasks)
    except engine_client.EngineError as err:
        return error.error_response(500, f"Engine error: {err}")

    for _milestone in task_list['milestones']:
        if _milestone['id'] == milestone_id:
            milestone = _milestone
            break
    else:
        return error.not_found(f"Milestone details for {milestone_id} not found")
    milestone['tasks'] = logic.get_milestone_task_list(dataset_id, milestone_id, task_list['actionList'])
    return jsonify(milestone)
