from app.constants.state import TaskType, TaskState


def message_filter(task_state: TaskState, task_type: TaskType) -> bool:
    """
    check if message meet the following criteria:
    - task_state is done or error
    - task_type in (training, mining, dataset_infer, label)
    """
    return task_state in [TaskState.done, TaskState.error] and task_type in [
        TaskType.training,
        TaskType.mining,
        TaskType.dataset_infer,
        TaskType.label,
        TaskType.pull_image,
    ]
