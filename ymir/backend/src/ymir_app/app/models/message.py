from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    SmallInteger,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.db.base_class import Base
from app.models.model import Model  # noqa
from app.models.dataset import Dataset  # noqa
from app.models.prediction import Prediction  # noqa
from app.models.image import DockerImage  # noqa


class Message(Base):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False)
    project_id = Column(Integer, index=True, nullable=False)

    state = Column(SmallInteger, index=True)
    task_type = Column(SmallInteger, index=True)
    content = Column(String(settings.LONG_STRING_LEN_LIMIT))
    dataset_id = Column(Integer, index=True)
    model_id = Column(Integer, index=True)
    prediction_id = Column(Integer, index=True)
    docker_image_id = Column(Integer, index=True)
    is_read = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    dataset = relationship(
        "Dataset",
        primaryjoin="foreign(Dataset.id)==Message.dataset_id",
        uselist=False,
        viewonly=True,
    )
    model = relationship(
        "Model",
        primaryjoin="foreign(Model.id)==Message.model_id",
        uselist=False,
        viewonly=True,
    )
    prediction = relationship(
        "Prediction",
        primaryjoin="foreign(Prediction.id)==Message.prediction_id",
        uselist=False,
        viewonly=True,
    )
    docker_image = relationship(
        "DockerImage",
        primaryjoin="foreign(DockerImage.id)==Message.docker_image_id",
        uselist=False,
        viewonly=True,
    )
