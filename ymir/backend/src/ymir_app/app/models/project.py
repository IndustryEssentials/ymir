from datetime import datetime

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

    # for project haven't finish initialization, current_iteration_id is None
    current_iteration_id = Column(Integer)
    user_id = Column(Integer, index=True, nullable=False)

    dataset_groups = relationship(
        "DatasetGroup",
        primaryjoin="foreign(DatasetGroup.project_id)==Project.id",
        uselist=True,
        viewonly=True,
    )
    datasets = relationship(
        "Dataset",
        primaryjoin="foreign(Dataset.project_id)==Project.id",
        uselist=True,
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
