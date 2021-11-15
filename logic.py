import model


def workflow_state_message(workflow, task_breadcrumbs, new_decision_action_id):
    task_history_set = set(task_breadcrumbs[:-2])
    previous_task_id = str(workflow.last_engine_decision_id)
    if previous_task_id == new_decision_action_id:
        return {
            "level": "info",
            "text": "Are you sure you have done this task. Looks like you haven't."
        }
    elif previous_task_id in task_history_set:
        return {
            "level": "info",
            "text": "You need to deal with a previous task."
        }
    return None


def remove_tasks_from_skipped_list(workflow, task_list):
    skipped_tasks = set(workflow.skipped_tasks)
    new_skipped_tasks = skipped_tasks - set(task_list)
    workflow.skipped_tasks = new_skipped_tasks
    model.db.session.add(workflow)
    model.db.session.commit()
    return None
