from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    SmallInteger,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.db.base_class import Base
from app.models.task import Task  # noqa


class Model(Base):
    __tablename__ = "model"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hash = Column(String(settings.STRING_LEN_LIMIT), index=True)
    name = Column(String(settings.STRING_LEN_LIMIT), index=True, nullable=False)
    description = Column(String(settings.STRING_LEN_LIMIT))
    version_num = Column(Integer, index=True, nullable=False)
    result_state = Column(SmallInteger, index=True, nullable=False)

    model_group_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    project_id = Column(Integer, index=True, nullable=False)
    task_id = Column(Integer, index=True, nullable=False)

    # imported/copied model has no mAP
    map = Column(Float, nullable=True)

    related_task = relationship(
        "Task",
        primaryjoin="foreign(Task.id)==Model.task_id",
        backref="result_model",
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
    __table_args__ = (UniqueConstraint("project_id", "hash", name="uniq_project_hash"),)
