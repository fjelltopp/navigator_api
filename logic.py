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
