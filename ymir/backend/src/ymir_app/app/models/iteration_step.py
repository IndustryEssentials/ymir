from datetime import datetime
import json
from typing import Dict, Optional, Union

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.task import Task  # noqa
from app.models.dataset import Dataset  # noqa
from app.models.model import Model  # noqa
from app.config import settings


class IterationStep(Base):
    __tablename__ = "iteration_step"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.STRING_LEN_LIMIT), index=True, nullable=False)
    iteration_id = Column(Integer, index=True, nullable=False)

    task_type = Column(Integer, index=True, nullable=False)
    task_id = Column(Integer, index=True)
    serialized_presetting = Column(Text(settings.TEXT_LEN_LIMIT))

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
    def result_dataset(self) -> Optional[Dataset]:
        if not self.task:
            return None
        return self.task.result_dataset  # type: ignore

    @property
    def result_model(self) -> Optional[Dataset]:
        if not self.task:
            return None
        return self.task.result_model  # type: ignore

    @property
    def result(self) -> Optional[Union[Dataset, Model]]:
        return self.result_dataset or self.result_model

    @property
    def state(self) -> Optional[int]:
        """
        for each step in iteration,
        we only care about related dataset or model's state,
        task's state considered internal
        """
        return self.result.result_state if self.result else None

    @property
    def presetting(self) -> Dict:
        return json.loads(self.serialized_presetting) if self.serialized_presetting else {}

    @property
    def step_from_previous_iteration(self) -> "IterationStep":
        steps = self.iteration.previous_steps  # type: ignore
        return next(step for step in steps if step.name == self.name)
