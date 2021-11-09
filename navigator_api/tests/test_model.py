def test_new_workflow_has_empty_skipped_tasks(workflow):
    assert workflow.skipped_tasks == []


def test_workflow_persists_saved_tasks(workflow):
    tasks = ['a', 'b', 'c']
    workflow.skipped_tasks = tasks
    assert workflow.skipped_tasks == tasks


def test_workflow_skipping_task(workflow):
    tasks = ['a', 'b', 'c']
    workflow.skipped_tasks = tasks
    workflow.skipped_tasks += 'd'
    assert workflow.skipped_tasks[-1] == 'd'
