from flask import session
from flask_login import current_user

import model
from clients import ckan_client


def workflow_state_message(workflow, task_breadcrumbs, new_decision_action_id):
    task_history_set = set(task_breadcrumbs[:-2])
    previous_task_id = str(workflow.last_engine_decision_id)
    if previous_task_id == new_decision_action_id:
        return {
            "level": "info",
            "text": "Are you sure you have done this task? Looks like you haven't."
        }
    elif previous_task_id in task_history_set:
        return {
            "level": "info",
            "text": "You need to deal with a previous task."
        }
    return None


def is_task_completed(dataset_id, task_id):
    workflow = model.get_workflow(dataset_id, current_user.id)
    task_statuses_map = workflow.task_statuses_map
    task_status = task_statuses_map[task_id]
    manual = task_status["manualConfirmationRequired"]
    task_breadcrumbs = list(task_statuses_map.keys())
    if manual:
        ckan_cli = get_ckan_client_from_session()
        try:
            wf_state = ckan_client.fetch_workflow_state(ckan_cli, dataset_id)
        except ckan_client.NotFound:
            return False
        completed_tasks = set(wf_state["completedTasks"])
        return str(task_id) in completed_tasks
    else:
        skipped_tasks = workflow.skipped_tasks
        if task_id == task_breadcrumbs[-1] or task_id in skipped_tasks:
            return False
        else:
            return True


def remove_tasks_from_skipped_list(workflow, task_list):
    skipped_tasks = set(workflow.skipped_tasks)
    new_skipped_tasks = skipped_tasks - set(task_list)
    workflow.skipped_tasks = new_skipped_tasks
    model.db.session.add(workflow)
    model.db.session.commit()
    return None


def get_ckan_client_from_session():
    ckan_user = session['ckan_user']
    ckan_cli = ckan_client.init_ckan(apikey=ckan_user['apikey'])
    return ckan_cli


def compose_task_details(dataset_id, task_id, task_details, task_status):
    current_task = {
        "id": task_id,
        "skipped": task_status["skipped"],
        "completed": is_task_completed(dataset_id, task_id),
        "manual": task_status["manualConfirmationRequired"],
        "milestoneID": task_status["milestoneID"],
        "details": task_details
    }
    return current_task
