from flask import session
from flask_login import current_user

import model
from clients import ckan_client


def workflow_state_message(workflow, task_breadcrumbs, decision_action_id, skipped_tasks_to_remove):
    previous_task_id = str(workflow.last_engine_decision_id)
    previous_task_breadcrumbs = list(workflow.task_statuses_map.keys())
    if decision_action_id in skipped_tasks_to_remove:
        return {
            "level": "info",
            "text": "Unfortunately you cannot skip this task.  You must complete this task to continue further."
        }
    elif previous_task_id == decision_action_id:
        return {
            "level": "info",
            "text": "The status of this task is checked automatically by Navigator. It appears the task has either not "
                    "been completed or is only partially completed. Please review the task instructions again and "
                    "complete the task before clicking “What’s Next?”."
        }
    elif len(task_breadcrumbs) < len(previous_task_breadcrumbs):
        return {
            "level": "info",
            "text": "You have been sent backwards to complete an earlier task, either because it can no longer be "
                    "skipped, or Navigator has spotted it is now incomplete."
        }
    elif len(task_breadcrumbs) - len(previous_task_breadcrumbs) > 1:
        return {
            "level": "info",
            "text": "Navigator can see that you have already completed some of your next tasks, so you have been moved "
                    "on multiple steps to your next incomplete task."
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


def get_task_list_with_milestones(dataset_id, tasks, milestones):
    milestone_map = {milestone['id']: milestone for milestone in milestones}
    task_list_with_milestones = []
    last_milestone_id = None
    for task in tasks:
        task['manual'] = task['manualConfirmationRequired']
        del task['manualConfirmationRequired']
        task['completed'] = is_task_completed(dataset_id=dataset_id, task_id=task['id'])

        milestone_id = task['milestoneID']
        if len(task_list_with_milestones) > 0 and milestone_id == last_milestone_id:
            milestone_with_tasks = task_list_with_milestones[-1]
            milestone_with_tasks['tasks'].append(task)
        else:
            milestone = milestone_map.get(milestone_id, {})
            task_list_with_milestones.append({
                'id': milestone.get('id'),
                'title': milestone.get('title'),
                'progress': milestone.get('progress'),
                'tasks': [task]
            })
            last_milestone_id = milestone_id
    return task_list_with_milestones
