from typing import Any


class MirRuntimeError(Exception):
    """

    error raised by ymir-command

    if raised from a function surrounded by decorator `@command_run_in_out`,
    new commit will made if `needs_new_commit` true

    """
    def __init__(self, error_code: int, error_message: str, needs_new_commit: bool = True, mir_tasks: Any = None):
        super().__init__(self)
        self.error_code = error_code
        self.error_message = error_message
        self.needs_new_commit = needs_new_commit
        self.mir_tasks = mir_tasks

    def __str__(self) -> str:
        return f"code: {self.error_code} content: {self.error_message}, needs new commit: {self.needs_new_commit}"
