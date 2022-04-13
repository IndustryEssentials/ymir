from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import DATETIME

from app.config import settings
from app.db.base_class import Base


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.STRING_LEN_LIMIT), index=True, nullable=False)
    hash = Column(String(settings.STRING_LEN_LIMIT), index=True, nullable=False)
    type = Column(Integer, index=True, nullable=False)
    state = Column(Integer, index=True, nullable=False)

    parameters = Column(Text(settings.TEXT_LEN_LIMIT))
    config = Column(Text(settings.TEXT_LEN_LIMIT))
    percent = Column(Float)
    duration = Column(Integer)
    error_code = Column(String(settings.DEFAULT_LIMIT))

    user_id = Column(Integer, index=True, nullable=False)
    project_id = Column(Integer, index=True, nullable=False)

    is_terminated = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    last_message_datetime = Column(DATETIME(fsp=6), default=datetime.utcnow, nullable=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
