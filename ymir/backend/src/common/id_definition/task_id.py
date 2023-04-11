import secrets
import struct
import time
from typing import List, Tuple

from dataclasses import dataclass
from enum import Enum, IntEnum, unique


class IDProto(IntEnum):
    ID_LEN_ID_TYPE = 1
    ID_LEN_SUBTASK_ID = 1
    ID_LEN_SUBTASK_COUNT = 1
    ID_LEN_RESERVE = 1
    ID_LEN_USER_ID = 4
    ID_LEN_REPO_ID = 6
    ID_LEN_HEX_TASK_ID = 16
    ID_LENGTH = (ID_LEN_ID_TYPE + ID_LEN_SUBTASK_ID + ID_LEN_SUBTASK_COUNT + ID_LEN_RESERVE + ID_LEN_USER_ID
                 + ID_LEN_REPO_ID + ID_LEN_HEX_TASK_ID)


@unique
class IDType(Enum):
    ID_TYPE_UNKNOWN = "z"
    ID_TYPE_ASSET = "a"
    ID_TYPE_COMMIT = "c"
    ID_TYPE_TASK = "t"
    ID_TYPE_SEQ_TASK = "s"
    ID_TYPE_REPO = "r"
    ID_TYPE_USER = "u"


@dataclass
class TaskId:
    id_type: str
    sub_task_id: str
    seq_task_count: str
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
        return (f"{self.id_type}{self.sub_task_id}{self.seq_task_count}{self.id_reserve}"
                f"{self.user_id}{self.repo_id}{self.hex_task_id}")

    @classmethod
    def from_task_id(cls, task_id: str) -> "TaskId":
        fmt = "1s1s1s1s4s6s16s"
        try:
            components = struct.unpack(fmt, task_id.encode())
        except struct.error:
            raise ValueError(f"Ill-formatted task id: {task_id}")
        return cls(*(c.decode() for c in components))


def gen_user_hash(user_id: int) -> str:
    return f"{user_id:0>4}"


def gen_repo_hash(repo_id: int) -> str:
    return f"{repo_id:0>6}"


def gen_seq_ids(count: int, user_id: int, repo_id: int, hex_task_id: str = None) -> Tuple[str, List[str]]:
    """
    Generate sequential id and it's task ids
    Format:
        sequential id: s0b0ccccddddddzzzzzzzzzzzzzzzz
        sequential task id: sab0ccccddddddzzzzzzzzzzzzzzzz
        a: (only for sequential task): index of this task, one digit int, start from 1
        b: total task count, one digit int
        c: user id, 4 digits
        d: repo id, 6 digits
    Returns:
        first: seq id
        second: all it's task ids
    """
    user_hash = gen_user_hash(user_id)
    repo_hash = gen_repo_hash(repo_id)
    if count <= 1 or count > 9:
        raise ValueError(f"[gen_seq_ids]: invalid count: {count}")
    hex_task_id = hex_task_id or f"{secrets.token_hex(3)}{int(time.time())}"
    sids: List[str] = []
    for idx in range(count + 1):
        sids.append(str(TaskId(id_type=IDType.ID_TYPE_SEQ_TASK.value,
                    sub_task_id=f"{idx:0>1}",
                    seq_task_count=f"{count:0>1}",
                    id_reserve="0",
                    user_id=user_hash,
                    repo_id=repo_hash,
                    hex_task_id=hex_task_id)))
    return (sids[0], sids[1:])


def rebuild_seq_ids(seq_task_id: str) -> Tuple[str, List[str]]:
    """
    Generate sequential id and it's task ids from a single seq task id
    Returns:
        first: seq id
        second: all it's task ids
    Raises:
        ValueError: if seq_task_id not belongs to a sequential task
    """
    seq_id_typed = TaskId.from_task_id(seq_task_id)
    if seq_id_typed.id_type != IDType.ID_TYPE_SEQ_TASK.value:
        raise ValueError(f"seq_task_id not belongs to a sequential task: {seq_task_id}")
    return gen_seq_ids(user_id=int(seq_id_typed.user_id),
                       repo_id=int(seq_id_typed.repo_id),
                       count=int(seq_id_typed.seq_task_count),
                       hex_task_id=seq_id_typed.hex_task_id)


def gen_task_id(user_id: int, repo_id: int) -> str:
    hex_task_id = f"{secrets.token_hex(3)}{int(time.time())}"
    return str(
        TaskId(id_type=IDType.ID_TYPE_TASK.value,
               sub_task_id="0",
               seq_task_count="0",
               id_reserve="0",
               user_id=gen_user_hash(user_id),
               repo_id=gen_repo_hash(repo_id),
               hex_task_id=hex_task_id))
