from id_definition.error_codes import UpdateErrorCode


class UpdateError(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__()
        self.code = code
        self.message = message


class SandboxStateUnknown(UpdateError):
    def __init__(self) -> None:
        super().__init__(code=UpdateErrorCode.SANDBOX_STATE_UNKNOWN,
                         message='Sandbox state unknown')


class InvalidUserLabelFile(UpdateError):
    def __init__(self) -> None:
        super().__init__(code=UpdateErrorCode.INVALID_USER_LABEL_FILE,
                         message='Invalid labels.yaml')


class MultipleUserSpaceVersions(UpdateError):
    def __init__(self) -> None:
        super().__init__(code=UpdateErrorCode.MULTIPLE_USER_SPACE_VERSIONS,
                         message='Found multiple user space versions')


class BackupDirNotEmpty(UpdateError):
    def __init__(self) -> None:
        super().__init__(code=UpdateErrorCode.BACKUP_DIR_NOT_EMPTY,
                         message='Backup directory not empty')
