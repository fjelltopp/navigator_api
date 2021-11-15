import pytest

import logic
import model


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
