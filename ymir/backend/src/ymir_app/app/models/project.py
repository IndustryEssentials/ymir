from datetime import datetime
import json
from typing import List

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    SmallInteger,
    Text,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.constants.state import ResultState, TaskState, TaskType
from app.db.base_class import Base
from app.models.dataset import Dataset  # noqa
from app.models.dataset_group import DatasetGroup  # noqa
from app.models.iteration import Iteration  # noqa
from app.models.model import Model  # noqa
from app.models.model_group import ModelGroup  # noqa
from app.models.task import Task  # noqa


class Project(Base):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.STRING_LEN_LIMIT), index=True, nullable=False)
    description = Column(String(settings.STRING_LEN_LIMIT))

    iteration_target = Column(Integer)
    map_target = Column(Float)
    training_dataset_count_target = Column(Integer)

    mining_strategy = Column(SmallInteger, index=True)
    chunk_size = Column(Integer)

    training_type = Column(SmallInteger, index=True, default=0, nullable=False)
    training_keywords = Column(Text(settings.TEXT_LEN_LIMIT), nullable=False)
    training_dataset_group_id = Column(Integer, index=True)
    mining_dataset_id = Column(Integer, index=True)
    validation_dataset_id = Column(Integer, index=True)
    testing_dataset_ids = Column(String(settings.LONG_STRING_LEN_LIMIT))
    initial_model_id = Column(Integer, index=True)
    initial_model_stage_id = Column(Integer, index=True)
    initial_training_dataset_id = Column(Integer, index=True)
    candidate_training_dataset_id = Column(Integer)

    enable_iteration = Column(Boolean, default=True, nullable=False)
    # for project hasn't finished initialization, current_iteration_id is None
    current_iteration_id = Column(Integer)
    user_id = Column(Integer, index=True, nullable=False)

    training_dataset_group = relationship(
        "DatasetGroup",
        primaryjoin="foreign(DatasetGroup.id)==Project.training_dataset_group_id",
        uselist=False,
        viewonly=True,
    )
    datasets = relationship(
        "Dataset",
        primaryjoin="foreign(Dataset.project_id)==Project.id",
        uselist=True,
        viewonly=True,
    )
    validation_dataset = relationship(
        "Dataset",
        primaryjoin="foreign(Dataset.id)==Project.validation_dataset_id",
        uselist=False,
        viewonly=True,
    )
    mining_dataset = relationship(
        "Dataset",
        primaryjoin="foreign(Dataset.id)==Project.mining_dataset_id",
        uselist=False,
        viewonly=True,
    )
    model_groups = relationship(
        "ModelGroup",
        primaryjoin="foreign(ModelGroup.project_id)==Project.id",
        uselist=True,
        viewonly=True,
    )
    models = relationship(
        "Model",
        primaryjoin="foreign(Model.project_id)==Project.id",
        uselist=True,
        viewonly=True,
    )
    tasks = relationship(
        "Task",
        primaryjoin="foreign(Task.project_id)==Project.id",
        uselist=True,
        viewonly=True,
    )
    current_iteration = relationship(
        "Iteration",
        primaryjoin="foreign(Iteration.id)==Project.current_iteration_id",
        uselist=False,
        viewonly=True,
    )
    iterations = relationship(
        "Iteration",
        primaryjoin="foreign(Iteration.project_id)==Project.id",
        uselist=True,
        viewonly=True,
    )

    is_example = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def dataset_count(self) -> int:
        # Only ready and visible datasets count.
        # stick to `dataset_count` for compatibility
        return sum(d.result_state == ResultState.ready and d.is_visible for d in self.datasets)

    @property
    def model_count(self) -> int:
        # Only ready and visible models count.
        # stick to `model_count` for compatibility
        return sum(m.result_state == ResultState.ready and m.is_visible for m in self.models)

    @property
    def processing_dataset_count(self) -> int:
        return sum(d.result_state == ResultState.processing and d.is_visible for d in self.datasets)

    @property
    def error_dataset_count(self) -> int:
        return sum(d.result_state == ResultState.error and d.is_visible for d in self.datasets)

    @property
    def processing_model_count(self) -> int:
        return sum(m.result_state == ResultState.processing and m.is_visible for m in self.models)

    @property
    def error_model_count(self) -> int:
        return sum(m.result_state == ResultState.error and m.is_visible for m in self.models)

    @property
    def total_asset_count(self) -> int:
        return sum([dataset.asset_count for dataset in self.datasets if dataset.asset_count])

    @property
    def training_tasks(self) -> List[Task]:
        return [task for task in self.tasks if task.type == TaskType.training]

    @property
    def running_task_count(self) -> int:
        return sum([task.state == TaskState.running for task in self.training_tasks])

    @property
    def total_task_count(self) -> int:
        return len(self.training_tasks)

    @property
    def referenced_dataset_ids(self) -> List[int]:
        """
        for each project, there are some resources that are required, including:
        - project's testing dataset, mining dataset and initial training dataset
        - datasets and models of current iteration
        - all the training dataset of all the iterations
        """
        testing_dataset_ids = [int(i) for i in self.testing_dataset_ids.split(",")] if self.testing_dataset_ids else []
        project_dataset_ids = [
            self.validation_dataset_id,
            self.mining_dataset_id,
            self.initial_training_dataset_id,
            self.candidate_training_dataset_id,
            *testing_dataset_ids,
        ]
        current_iteration_dataset_ids = self.current_iteration.referenced_dataset_ids if self.current_iteration else []
        all_iterations_training_dataset_ids = [i.training_input_dataset_id for i in self.iterations]
        dataset_ids = filter(
            None,
            project_dataset_ids + current_iteration_dataset_ids + all_iterations_training_dataset_ids,  # type: ignore
        )
        return list(set(dataset_ids))

    @property
    def referenced_model_ids(self) -> List[int]:
        current_iteration_model_ids = self.current_iteration.referenced_model_ids if self.current_iteration else []
        all_iterations_training_model_ids = [i.training_output_model_id for i in self.iterations]
        model_ids = filter(
            None,
            current_iteration_model_ids + [self.initial_model_id] + all_iterations_training_model_ids,  # type: ignore
        )
        return list(set(model_ids))

    @property
    def training_targets(self) -> List[str]:
        return json.loads(self.training_keywords) if self.training_keywords else []
