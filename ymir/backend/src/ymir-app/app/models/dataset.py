from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, SmallInteger, Text
from sqlalchemy.orm import relationship

from app.config import settings
from app.db.base_class import Base
from app.models.task import Task  # noqa


class Dataset(Base):
    __tablename__ = "dataset"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hash = Column(
        String(settings.STRING_LEN_LIMIT), index=True, unique=True, nullable=False
    )
    name = Column(String(settings.STRING_LEN_LIMIT), index=True, nullable=False)
    version_num = Column(Integer, index=True, nullable=False)
    result_state = Column(SmallInteger, index=True, nullable=False)

    dataset_group_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    project_id = Column(Integer, index=True, nullable=False)
    task_id = Column(Integer, index=True, nullable=False)

    keywords = Column(Text(settings.TEXT_LEN_LIMIT))
    ignored_keywords = Column(Text(settings.TEXT_LEN_LIMIT))
    asset_count = Column(Integer)
    keyword_count = Column(Integer)

    related_task = relationship(
        "Task",
        primaryjoin="foreign(Task.id)==Dataset.task_id",
        uselist=False,
        viewonly=True,
    )

    is_deleted = Column(Boolean, default=False, nullable=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
