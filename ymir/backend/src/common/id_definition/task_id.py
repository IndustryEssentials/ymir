import struct

from dataclasses import dataclass
from enum import Enum, IntEnum, unique
from typing import Any


class IDProto(IntEnum):
    ID_LEN_ID_TYPE = 1
    ID_LEN_SUBTASK_ID = 1
    ID_LEN_RESERVE = 2
    ID_LEN_USER_ID = 4
    ID_LEN_REPO_ID = 6
    ID_LEN_HEX_TASK_ID = 16
    ID_LENGTH = (ID_LEN_ID_TYPE + ID_LEN_SUBTASK_ID + ID_LEN_RESERVE + ID_LEN_USER_ID + ID_LEN_REPO_ID
                 + ID_LEN_HEX_TASK_ID)


@unique
class IDType(Enum):
    ID_TYPE_UNKNOWN = "z"
    ID_TYPE_ASSET = "a"
    ID_TYPE_COMMIT = "c"
    ID_TYPE_TASK = "t"
    ID_TYPE_REPO = "r"
    ID_TYPE_USER = "u"


@dataclass
class TaskId:
    id_type: str
    sub_task_id: str
    id_reserve: str
    user_id: str
    repo_id: str
    hex_task_id: str

    def __post_init__(self) -> None:
        if len(self.id_type) != IDProto.ID_LEN_ID_TYPE:
            raise ValueError(f"Invalid id_type: {self.id_type}")
        if len(self.sub_task_id) != IDProto.ID_LEN_SUBTASK_ID:
            raise ValueError(f"Invalid sub_task_id: {self.sub_task_id}")
        if len(self.id_reserve) != IDProto.ID_LEN_RESERVE:
            raise ValueError(f"Invalid id_reserve: {self.id_reserve}")
        if len(self.user_id) != IDProto.ID_LEN_USER_ID:
            raise ValueError(f"Invalid user_id: {self.user_id}")
        if len(self.repo_id) != IDProto.ID_LEN_REPO_ID:
            raise ValueError(f"Invalid repo_id: {self.repo_id}")
        if len(self.hex_task_id) != IDProto.ID_LEN_HEX_TASK_ID:
            raise ValueError(f"Invalid hex_task_id: {self.hex_task_id}")

    def __str__(self) -> str:
        return f"{self.id_type}{self.sub_task_id}{self.id_reserve}{self.user_id}{self.repo_id}{self.hex_task_id}"

    @classmethod
    def from_task_id(cls, task_id: str) -> Any:
        fmt = "1s1s2s4s6s16s"
        components = struct.unpack(fmt, task_id.encode())
        return cls(*(c.decode() for c in components))
