from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, SmallInteger, String
from sqlalchemy.orm import relationship

from app.config import settings
from app.db.base_class import Base
from app.models.task import Task  # noqa
from app.models.dataset import Dataset  # noqa
from app.models.iteration_step import IterationStep


class Iteration(Base):
    __tablename__ = "iteration"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    description = Column(String(settings.STRING_LEN_LIMIT))
    iteration_round = Column(Integer, index=True, nullable=False)
    current_stage = Column(SmallInteger, index=True, default=0, nullable=False)
    previous_iteration = Column(Integer, index=True, default=0, nullable=False)

    mining_dataset_id = Column(Integer)
    mining_input_dataset_id = Column(Integer)
    mining_output_dataset_id = Column(Integer)
    label_output_dataset_id = Column(Integer)
    training_input_dataset_id = Column(Integer)
    training_output_model_id = Column(Integer)
    training_output_model_stage_id = Column(Integer)
    validation_dataset_id = Column(Integer)

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

    mining_dataset = relationship(
        "Dataset",
        primaryjoin="foreign(Dataset.id)==Iteration.mining_dataset_id",
        uselist=False,
        viewonly=True,
    )

    iteration_steps = relationship(
        "IterationStep",
        primaryjoin="foreign(IterationStep.iteration_id)==Iteration.id",
        backref="iteration",
        uselist=True,
        viewonly=True,
    )

    @property
    def current_step(self) -> Optional[IterationStep]:
        """
        list all the remaining steps in current iteration and return the first one when possible
        if no remaining steps exist, current iteration should have finished
        """
        remaining_steps = sorted(filter(lambda i: not i.is_finished, self.iteration_steps), key=lambda i: i.id)
        return remaining_steps[0] if remaining_steps else None

    @property
    def referenced_dataset_ids(self) -> List[int]:
        return [step.result_dataset.id for step in self.iteration_steps if step.result_dataset]

    @property
    def referenced_model_ids(self) -> List[int]:
        return [step.result_model.id for step in self.iteration_steps if step.result_model]
