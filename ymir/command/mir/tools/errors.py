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
    def __init__(self, error_code: int, error_message: str, needs_new_commit: bool = True, mir_tasks: Any = None):
        super().__init__(error_code=error_code, error_message=error_message)
        self.needs_new_commit = needs_new_commit
        self.mir_tasks = mir_tasks

    def __str__(self) -> str:
        return f"code: {self.error_code} content: {self.error_message}, needs new commit: {self.needs_new_commit}"


class MirRuntimeErrorInvalidArgs(MirRuntimeError):
    def __init__(self, error_message: str = 'Invalid args'):
        super().__init__(error_code=MirCode.RC_CMD_INVALID_ARGS,
                         error_message=error_message,
                         needs_new_commit=False,
                         mir_tasks=None)


class MirRuntimeErrorEmptyTrainSet(MirRuntimeError):
    def __init__(self, error_message: str = 'Empty training set', mir_tasks: Any = None):
        super().__init__(error_code=MirCode.RC_CMD_EMPTY_TRAIN_SET,
                         error_message=error_message,
                         needs_new_commit=True,
                         mir_tasks=mir_tasks)


class MirRuntimeErrorEmptyValSet(MirRuntimeError):
    def __init__(self, error_message: str = 'Empty validation set', mir_tasks: Any = None):
        super().__init__(error_code=MirCode.RC_CMD_EMPTY_TRAIN_SET,
                         error_message=error_message,
                         needs_new_commit=True,
                         mir_tasks=mir_tasks)


class MirRuntimeErrorContainerNonZeroReturned(MirRuntimeError):
    def __init__(self, error_message: str, needs_new_commit: bool = True, mir_tasks: Any = None):
        super().__init__(error_code=MirCode.RC_RUNTIME_CONTAINER_ERROR,
                         error_message=error_message,
                         needs_new_commit=needs_new_commit,
                         mir_tasks=mir_tasks)


class MirRuntimeErrorUnknownTypes(MirRuntimeError):
    def __init__(self, error_message: str = 'Unknown types', mir_tasks: Any = None):
        super().__init__(error_code=MirCode.RC_RUNTIME_UNKNOWN_TYPES,
                         error_message=error_message,
                         needs_new_commit=True,
                         mir_tasks=mir_tasks)


class MirRuntimeErrorInvalidBranchOrTag(MirRuntimeError):
    def __init__(self,
                 error_message: str = 'Invalid branch or tag',
                 needs_new_commit: bool = True,
                 mir_tasks: Any = None):
        super().__init__(error_code=MirCode.RC_CMD_INVALID_BRANCH_OR_TAG,
                         error_message=error_message,
                         needs_new_commit=needs_new_commit,
                         mir_tasks=mir_tasks)


class MirRuntimeErrorDirtyRepo(MirRuntimeError):
    def __init__(self, error_message: str = 'Dirty repo'):
        super().__init__(error_code=MirCode.RC_CMD_DIRTY_REPO,
                         error_message=error_message,
                         needs_new_commit=False,
                         mir_tasks=None)


class MirRuntimeErrorMergeFailed(MirRuntimeError):
    def __init__(self, error_message: str = 'Merge failed', needs_new_commit: bool = True, mir_tasks: Any = None):
        super().__init__(error_code=MirCode.RC_CMD_MERGE_ERROR,
                         error_message=error_message,
                         needs_new_commit=needs_new_commit,
                         mir_tasks=mir_tasks)
