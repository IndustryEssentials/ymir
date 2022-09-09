from enum import IntEnum
from typing import Dict, List


class UpdateErrorCode(IntEnum):
    UEC_INVALID_USER_LABEL_FILE = 170001
    UEC_MULTIPLE_USER_SPACE_VERSIONS = 170002
    UEC_BACKUP_DIR_NOT_EMPTY = 170003


class UpdateError(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__()
        self.code = code
        self.message = message


class InvalidUserLabelFile(UpdateError):
    def __init__(self, user_label_file: str) -> None:
        super().__init__(code=UpdateErrorCode.UEC_INVALID_USER_LABEL_FILE,
                         message=f"invalid labels.yaml:: {user_label_file}")


class MultipleUserSpaceVersions(UpdateError):
    def __init__(self, ver_to_users: Dict[str, List[str]]) -> None:
        super().__init__(code=UpdateErrorCode.UEC_MULTIPLE_USER_SPACE_VERSIONS,
                         message=f"{ver_to_users}")


class BackupDirNotEmpty(UpdateError):
    def __init__(self, backup_dir: str) -> None:
        super().__init__(code=UpdateErrorCode.UEC_BACKUP_DIR_NOT_EMPTY,
                         message=f"backup dir not empty: {backup_dir}")
