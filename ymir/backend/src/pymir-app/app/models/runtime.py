import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, SmallInteger, String

from app.config import settings
from app.db.base_class import Base


class RuntimeType(enum.IntEnum):
    unknown = 0
    training = 1
    mining = 2
    inference = 100  # internal use only, inference is not a task


class Runtime(Base):
    __tablename__ = "runtime"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.NAME_LEN_LIMIT), index=True)
    hash = Column(String(settings.HASH_LEN_LIMIT), index=True)
    type = Column(Enum(RuntimeType), index=True)
    config = Column(String(settings.PARA_LEN_LIMIT))
    is_deleted = Column(Boolean, default=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
