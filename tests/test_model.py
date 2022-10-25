from model import get_workflows
from tests import factories


def test_new_workflow_has_empty_skipped_tasks(workflow):
    assert workflow.skipped_tasks == []


def test_workflow_persists_saved_tasks(workflow):
    tasks = [f"task_{i}" for i in range(1, 4)]
    workflow.skipped_tasks = tasks
    assert workflow.skipped_tasks == tasks


def test_workflow_skipping_task(workflow):
    tasks = [f"task_{i}" for i in range(1, 4)]
    workflow.skipped_tasks = tasks
    workflow.skipped_tasks = workflow.skipped_tasks + ['task_last']
    assert workflow.skipped_tasks[-1] == 'task_last'


def test_get_workflows_return_all_for_user():
    user_id = "fake_user_id"
    factories.WorklowFactory.create_batch(10, user_id=user_id)
    actual = get_workflows(user_id=user_id)
    assert len(actual) == 10
