from datetime import datetime
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
from app.db.base_class import Base
from app.models.dataset import Dataset  # noqa
from app.models.dataset_group import DatasetGroup  # noqa
from app.models.iteration import Iteration  # noqa
from app.models.model import Model  # noqa
from app.models.model_group import ModelGroup  # noqa


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
    testing_dataset_id = Column(Integer, index=True)
    initial_model_id = Column(Integer, index=True)
    initial_training_dataset_id = Column(Integer, index=True)

    # for project haven't finish initialization, current_iteration_id is None
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
    testing_dataset = relationship(
        "Dataset",
        primaryjoin="foreign(Dataset.id)==Project.testing_dataset_id",
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
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    @property
    def dataset_count(self) -> int:
        return len(self.datasets)

    @property
    def model_count(self) -> int:
        return len(self.models)

    @property
    def referenced_dataset_ids(self) -> List[int]:
        """
        for each project, there are some resources that are required, including:
        - project's testing dataset, mining dataset and initial training dataset
        - datasets and models of current iteration
        - all the training dataset of all the iterations
        """
        project_dataset_ids = [self.testing_dataset_id, self.mining_dataset_id, self.initial_training_dataset_id]
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
