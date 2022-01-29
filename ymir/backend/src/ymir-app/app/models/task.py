from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Integer,
    SmallInteger,
    String,
    Text,
)

from app.config import settings
from app.db.base_class import Base


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.NAME_LEN_LIMIT), index=True, nullable=False)
    hash = Column(String(settings.HASH_LEN_LIMIT), index=True, nullable=False)
    type = Column(Integer, index=True)
    state = Column(Integer, index=True)
    error_code = Column(String(settings.DEFAULT_LIMIT))
    progress = Column(SmallInteger)
    parameters = Column(Text(settings.PARA_LEN_LIMIT))
    config = Column(Text(settings.PARA_LEN_LIMIT))
    user_id = Column(Integer, index=True)
    is_deleted = Column(Boolean, default=False)
    duration = Column(BigInteger)
    last_message_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
