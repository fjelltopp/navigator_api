from unittest.mock import patch

import pytest

import logic
import model
from tests import factories
from tests.helpers import ckan_client_test_double


@pytest.mark.parametrize(
    (
        "task_breadcrumbs",
        "task_id",
        "last_engine_decision_id",
        "previous_task_breadcrumbs",
        "skipped_tasks_to_remove",
        "expected_message"
    ),
    [
        ([f"task_{n}" for n in range(1, 6)], "task_5", "task_4",
         [f"task_{n}" for n in range(1, 5)], [], ""),
        ([f"task_{n}" for n in range(1, 6)], "task_5", "task_5",
         [f"task_{n}" for n in range(1, 6)], [],
         "It appears the task has either not been completed or is only partially completed"),
        ([f"task_{n}" for n in range(1, 3)], "task_2", "task_6",
         [f"task_{n}" for n in range(1, 5)], [],
         "You have been sent backwards to complete an earlier task"),
        ([f"task_{n}" for n in range(1, 8)], "task_7", "task_5",
         [f"task_{n}" for n in range(1, 6)], [],
         "you have been moved on multiple steps"),
        ([f"task_{n}" for n in range(1, 6)], "task_5", "task_5",
         [f"task_{n}" for n in range(1, 6)], ["task_5"], "you cannot skip this task")
    ],
    ids=[
        "no message for next, consequitve task",
        "info message for the same task twice",
        "info message if task from the past",
        "info message if task with a few steps in the future",
        "info message if task cannot be skipped"
    ]
    )
def test_workflow_state_message(workflow, task_breadcrumbs, task_id, last_engine_decision_id, previous_task_breadcrumbs,
                                skipped_tasks_to_remove, expected_message):
    workflow.last_engine_decision_id = last_engine_decision_id
    workflow.task_statuses_map = {task_id: {'id': task_id} for task_id in previous_task_breadcrumbs}
    message = logic.workflow_state_message(workflow, task_breadcrumbs, task_id, skipped_tasks_to_remove) or {}
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


def test_is_task_completed_returns_false_for_unknown_task(logged_in):
    workflow = factories.WorklowFactory.create(user_id=ckan_client_test_double.valid_user_id)
    workflow.task_statuses_map = {"task1": {}, "task2": {}}
    assert logic.is_task_completed(workflow.dataset_id, "unknown_task_id") is False



def test_workflow_task_list():
    tasks = [
        {
            "id": "EST-OVV-01-10-A",
            "manualConfirmationRequired": True,
            "milestoneID": None,
            "reached": True,
            "skipped": False,
            "title": "Welcome to the Navigator"
        }
    ]
    milestones = [
        {
            "completed": False,
            "id": "EST-OVV-03-01-M",
            "progress": 0,
            "title": "Preparing Input Data for HIV Estimates"
        },
        {
            "completed": False,
            "id": "EST-OVV-04-01-M",
            "progress": 0,
            "title": "Upload Estimates Inputs Package Data Files to ADR"
        },
        {
            "completed": False,
            "id": "EST-OVV-05-01-M",
            "progress": 0,
            "title": "Review quality of programme data inputs using the *Review Inputs* function in Naomi"
        }
    ]
    with patch('logic.is_task_completed', return_value=True):
        result = logic.get_task_list_with_milestones("fake_dataset_id", tasks, milestones)
    assert len(result) == 1
    actual_milestone = result[0]
    assert all(key in actual_milestone for key in ['id', 'title', 'progress', 'tasks'])
    assert len(actual_milestone['tasks']) == 1
    actual_task = actual_milestone['tasks'][0]
    assert actual_task['id'] == "EST-OVV-01-10-A"
    assert all(
        key in actual_task for key in ['id', 'milestoneID', 'reached', 'skipped', 'title', 'manual', 'completed'])
