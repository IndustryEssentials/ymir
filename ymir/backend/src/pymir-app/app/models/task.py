import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Integer,
    SmallInteger,
    String,
    Text,
)

from app.config import settings
from app.db.base_class import Base


class TaskType(enum.IntEnum):
    unknown = 0
    training = 1
    mining = 2
    label = 3
    filter = 4
    import_data = 5
    export_data = 6
    copy_data = 7
    merge = 8


class TaskState(enum.IntEnum):
    unknown = 0
    pending = 1
    running = 2
    done = 3
    error = 4


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.NAME_LEN_LIMIT), index=True)
    hash = Column(String(settings.HASH_LEN_LIMIT), index=True)
    type = Column(Enum(TaskType), index=True)
    state = Column(Enum(TaskState), index=True)
    progress = Column(SmallInteger)
    parameters = Column(Text(settings.PARA_LEN_LIMIT))
    config = Column(Text(settings.PARA_LEN_LIMIT))
    user_id = Column(Integer, index=True)
    is_deleted = Column(Boolean, default=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
