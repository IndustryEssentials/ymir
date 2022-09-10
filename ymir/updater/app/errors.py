from typing import Dict, List

from error_codes import UpgradeErrorCode


class UpgradeError(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__()
        self.code = code
        self.message = message


class InvalidUserLabelFile(UpgradeError):
    def __init__(self) -> None:
        super().__init__(code=UpgradeErrorCode.INVALID_USER_LABEL_FILE,
                         message='Invalid labels.yaml')


class MultipleUserSpaceVersions(UpgradeError):
    def __init__(self) -> None:
        super().__init__(code=UpgradeErrorCode.MULTIPLE_USER_SPACE_VERSIONS,
                         message='Found multiple user space versions')


class BackupDirNotEmpty(UpgradeError):
    def __init__(self) -> None:
        super().__init__(code=UpgradeErrorCode.BACKUP_DIR_NOT_EMPTY,
                         message='Backup directory not empty')
