def test_new_workflow_has_empty_skipped_tasks(workflow):
    assert workflow.skipped_tasks == []


def test_workflow_persists_saved_tasks(workflow):
    tasks = [f"task_{i}" for i in range(1,4)]
    workflow.skipped_tasks = tasks
    assert workflow.skipped_tasks == tasks


def test_workflow_skipping_task(workflow):
    tasks = [f"task_{i}" for i in range(1,4)]
    workflow.skipped_tasks = tasks
    workflow.skipped_tasks = workflow.skipped_tasks + ['task_last']
    assert workflow.skipped_tasks[-1] == 'task_last'
