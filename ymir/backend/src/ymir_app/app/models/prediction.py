from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, SmallInteger, Text
from sqlalchemy.orm import relationship

from app.config import settings
from app.db.base_class import Base
from app.models.task import Task  # noqa


class Prediction(Base):
    __tablename__ = "prediction"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.STRING_LEN_LIMIT), index=True, nullable=False)
    hash = Column(String(settings.STRING_LEN_LIMIT), index=True, unique=True, nullable=False)
    source = Column(SmallInteger, index=True, nullable=False)
    description = Column(String(settings.STRING_LEN_LIMIT))
    result_state = Column(SmallInteger, index=True, nullable=False)

    user_id = Column(Integer, index=True, nullable=False)
    project_id = Column(Integer, index=True, nullable=False)
    task_id = Column(Integer, index=True, nullable=False)
    dataset_id = Column(Integer, index=True, nullable=False)
    model_id = Column(Integer, index=True, nullable=False)
    model_stage_id = Column(Integer, index=True, nullable=False)

    asset_count = Column(Integer)
    keyword_count = Column(Integer)
    keywords = Column(Text(settings.TEXT_LEN_LIMIT))

    related_task = relationship(
        "Task",
        primaryjoin="foreign(Task.id)==Prediction.task_id",
        backref="result_prediction",
        uselist=False,
        viewonly=True,
    )

    is_visible = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
