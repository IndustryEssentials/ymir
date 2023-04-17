import itertools


from app.libs import messages as m
from app.constants.state import TaskState, TaskType


class TestMessageFilter:
    def test_keep_message(self) -> None:
        for task_state, task_type in itertools.product(
            [TaskState.done, TaskState.error],
            [TaskType.training, TaskType.mining, TaskType.dataset_infer, TaskType.label],
        ):
            assert m.message_filter(task_state, task_type)

    def test_delete_message(self) -> None:
        for task_state, task_type in itertools.product(
            [TaskState.pending, TaskState.running, TaskState.terminate],
            [
                TaskType.import_data,
                TaskType.copy_data,
                TaskType.filter,
                TaskType.merge,
                TaskType.import_model,
                TaskType.pull_image,
            ],
        ):
            assert not m.message_filter(task_state, task_type)
