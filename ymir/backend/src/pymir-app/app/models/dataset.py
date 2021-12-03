from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Index, Integer, String, Text

from app.config import settings
from app.db.base_class import Base
from app.models.task import TaskType


class Dataset(Base):
    __tablename__ = "dataset"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.NAME_LEN_LIMIT), index=True)
    hash = Column(String(settings.HASH_LEN_LIMIT), index=True, unique=True)
    type = Column(Enum(TaskType), index=True)
    predicates = Column(Text(settings.PRED_LEN_LIMIT))
    asset_count = Column(Integer)
    keyword_count = Column(Integer)
    user_id = Column(Integer, index=True)
    task_id = Column(Integer, index=True)

    is_deleted = Column(Boolean, default=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
