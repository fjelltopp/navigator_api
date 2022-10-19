from authlib.integrations.flask_oauth2 import current_token
from flask import Blueprint, jsonify
from flask_login import login_required, current_user

import logic
import model
from api import error
from api.auth0_integration import require_auth
from api.workflow.routes import workflow_state
from clients import engine_client, ckan_client
from clients.ckan_client import get_username_from_token_or_404, get_user_id_from_token_or_404

milestone_bp = Blueprint('milestone', __name__,)


@milestone_bp.route('/workflows/<dataset_id>/milestones/<milestone_id>', methods=['GET'])
@require_auth(None)
def workflow_milestone_details(dataset_id, milestone_id):
    ckan_cli = ckan_client.init_ckan(username_for_substitution=get_username_from_token_or_404(current_token))
    user_id = get_user_id_from_token_or_404(current_token)
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
    milestone['tasks'] = logic.get_milestone_task_list(dataset_id, milestone_id, task_list['actionList'], user_id)
    return jsonify(milestone)
