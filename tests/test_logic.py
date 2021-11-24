from unittest.mock import patch

import pytest

import logic
import model
from tests import factories
from tests.helpers import ckan_client_test_double


@pytest.mark.parametrize("task_breadcrumbs,task_id,last_engine_decision_id,expected_message",
                         [
                             ([f"task_{n}" for n in range(1, 6)], "task_5", "task_4", ""),
                             ([f"task_{n}" for n in range(1, 6)], "task_5", "task_5",
                              "Are you sure you have done this task? Looks like you haven't."),
                             ([f"task_{n}" for n in range(1, 6)], "task_5", "task_2",
                              "You need to deal with a previous task."),
                         ],
                         ids=[
                             "no message for next, consequitve task",
                             "info message for the same task twice",
                             "info message if task from the past"
                         ]
                         )
def test_workflow_state_message(workflow, task_breadcrumbs, task_id, last_engine_decision_id, expected_message):
    workflow.last_engine_decision_id = last_engine_decision_id
    message = logic.workflow_state_message(workflow, task_breadcrumbs, task_id) or {}
    actual = message.get("text", "")

    assert expected_message in actual


@pytest.mark.parametrize("skipped_tasks,skipped_tasks_to_remove,expected",
                         [
                             ([f"task_{n}" for n in range(1, 6)], [f"task_{n}" for n in range(4, 6)],
                              [f"task_{n}" for n in range(1, 4)]),
                             ([f"task_{n}" for n in range(1, 4)], ["task_2"], ["task_1", "task_3"]),
                             ([f"task_{n}" for n in range(1, 6)], ["task_1"], [f"task_{n}" for n in range(2, 6)]),
                             ([f"task_{n}" for n in range(1, 6)], [f"task_{n}" for n in range(1, 6)], []),
                             ([f"task_{n}" for n in range(1, 6)], [], [f"task_{n}" for n in range(1, 6)]),
                             ([f"task_{n}" for n in range(1, 6)], ["not_skipped"], [f"task_{n}" for n in range(1, 6)]),
                         ],
                         ids=[
                             "unskipp last two actions",
                             "unskipp action from the middle",
                             "unskipp first action",
                             "unskipp all actions",
                             "unskipp no actions",
                             "unskipp actions not skipped"
                         ]
                         )
def test_remove_tasks_from_skipped_list(workflow, skipped_tasks, skipped_tasks_to_remove, expected):
    workflow.skipped_tasks = skipped_tasks

    logic.remove_tasks_from_skipped_list(workflow, skipped_tasks_to_remove)

    expected_set = set(expected)
    actual = set(model.Workflow.query.get(workflow.id).skipped_tasks)
    assert actual == expected_set


@pytest.mark.parametrize("task_id,skipped_tasks,expected",
                         [
                             ("task3", [], False),
                             ("task2", [], True),
                             ("task1", ["task1"], False),
                         ],
                         ids=[
                            "automated current task is always not done",
                            "automated unskipped task from breadcrumbs in done",
                            "automated skipped task is not done",
                         ]
                         )
def test_is_task_completed_for_automated_tasks(logged_in, task_id, skipped_tasks, expected):
    automated_task_statuses = {
        "task1": {'manualConfirmationRequired': False},
        "task2": {'manualConfirmationRequired': False},
        "task3": {'manualConfirmationRequired': False}
    }
    workflow = factories.WorklowFactory.create(user_id=ckan_client_test_double.valid_user_id)
    workflow.skipped_tasks = skipped_tasks
    workflow.task_statuses_map = automated_task_statuses
    assert logic.is_task_completed(workflow.dataset_id, task_id) == expected


@pytest.mark.parametrize("task_id,expected",
                         [
                             ("task1", False),
                             ("task2", True),
                             ("task3", True)
                         ],
                         ids=[
                            "task not marked as completed",
                            "task marked as completed",
                            "current task marked as completed"
                         ]
                         )
def test_is_task_completed_for_manual_tasks(logged_in, task_id, expected):
    automated_task_statuses = {
        "task1": {'manualConfirmationRequired': True},
        "task2": {'manualConfirmationRequired': True},
        "task3": {'manualConfirmationRequired': True}
    }
    workflow = factories.WorklowFactory.create(user_id=ckan_client_test_double.valid_user_id)
    workflow.task_statuses_map = automated_task_statuses
    with patch('logic.ckan_client', wraps=ckan_client_test_double):
        assert logic.is_task_completed(workflow.dataset_id, task_id) == expected
