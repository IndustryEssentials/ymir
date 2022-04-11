from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, SmallInteger, String

from app.config import settings
from app.db.base_class import Base
from app.models.task import Task  # noqa


class Iteration(Base):
    __tablename__ = "iteration"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    description = Column(String(settings.STRING_LEN_LIMIT))
    iteration_round = Column(Integer, index=True, nullable=False)
    current_stage = Column(SmallInteger, index=True, default=0, nullable=False)
    previous_iteration = Column(Integer, index=True, default=0, nullable=False)

    mining_input_dataset_id = Column(Integer)
    mining_output_dataset_id = Column(Integer)
    label_output_dataset_id = Column(Integer)
    training_input_dataset_id = Column(Integer)
    training_output_model_id = Column(Integer)
    testing_dataset_id = Column(Integer)

    user_id = Column(Integer, index=True, nullable=False)
    project_id = Column(Integer, index=True, nullable=False)

    is_deleted = Column(Boolean, default=False, nullable=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
