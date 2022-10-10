from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.task import Task  # noqa
from app.config import settings


class IterationStep(Base):
    __tablename__ = "iteration_step"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.STRING_LEN_LIMIT), index=True, nullable=False)
    task_type = Column(Integer, index=True, nullable=False)
    iteration_id = Column(Integer, index=True, nullable=False)

    task_id = Column(Integer, index=True)
    input_dataset_id = Column(Integer, index=True)
    output_dataset_id = Column(Integer, index=True)
    output_model_id = Column(Integer, index=True)

    is_finished = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    task = relationship(
        "Task",
        primaryjoin="foreign(Task.id)==IterationStep.task_id",
        uselist=False,
        viewonly=True,
    )

    @property
    def percent(self) -> Optional[float]:
        return self.task.percent if self.task else None  # type: ignore

    @property
    def state(self) -> Optional[int]:
        """
        for each step in iteration,
        we only care about related dataset or model's state,
        task's state considered internal
        """
        if not self.task:
            return None
        result = self.task.result_model or self.task.result_dataset  # type: ignore
        return result.result_state if result else None
