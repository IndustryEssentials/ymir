from typing import Any

from mir.tools.code import MirCode


class MirError(Exception):
    """
    error raised by ymir-command
    """
    def __init__(self, error_code: int, error_message: str) -> None:
        super().__init__()
        self.error_code = error_code
        self.error_message = error_message

    def __str__(self) -> str:
        return f"code: {self.error_code}, content: {self.error_message}"


class MirRuntimeError(MirError):
    """

    error raised by ymir-command

    if raised from a function surrounded by decorator `@command_run_in_out`,
    new commit will made if `needs_new_commit` true

    """
    def __init__(self, error_code: int, error_message: str, needs_new_commit: bool = True, task: Any = None):
        super().__init__(error_code=error_code, error_message=error_message)
        self.needs_new_commit = needs_new_commit
        self.task = task

    def __copy__(self) -> 'MirRuntimeError':
        return MirRuntimeError(error_code=self.error_code,
                               error_message=self.error_message,
                               needs_new_commit=self.needs_new_commit,
                               task=self.task)

    def __str__(self) -> str:
        return f"code: {self.error_code}, message: {self.error_message}"


class MirContainerError(MirRuntimeError):
    def __init__(self, error_message: str, task: Any):
        super().__init__(error_code=MirCode.RC_CMD_CONTAINER_ERROR,
                         error_message=error_message,
                         needs_new_commit=True,
                         task=task)
