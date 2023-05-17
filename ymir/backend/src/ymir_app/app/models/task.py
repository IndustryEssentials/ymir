from datetime import datetime
import json
from typing import Dict, Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import DATETIME

from app.config import settings
from app.db.base_class import Base
from app.utils.timeutil import convert_datetime_to_timestamp

if TYPE_CHECKING:
    from app.models.model import Model
    from app.models.dataset import Dataset
    from app.models.prediction import Prediction
    from app.models.image import DockerImage


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.STRING_LEN_LIMIT), index=True, nullable=False)
    hash = Column(String(settings.STRING_LEN_LIMIT), index=True, nullable=False)
    type = Column(Integer, index=True, nullable=False)
    state = Column(Integer, index=True, nullable=False)

    parameters = Column(Text(settings.TEXT_LEN_LIMIT))
    config = Column(Text(settings.TEXT_LEN_LIMIT))
    percent = Column(Float)
    duration = Column(Integer)
    error_code = Column(String(settings.DEFAULT_LIMIT))

    user_id = Column(Integer, index=True, nullable=False)
    project_id = Column(Integer, index=True, nullable=False)

    dataset_id = Column(Integer, index=True, nullable=True)
    model_stage_id = Column(Integer, index=True, nullable=True)

    is_terminated = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    last_message_datetime = Column(DATETIME(fsp=6))
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    @property
    def task_parameters(self) -> Dict:
        return json.loads(self.parameters) if self.parameters else {}

    @property
    def last_message_timestamp(self) -> Optional[float]:
        return convert_datetime_to_timestamp(self.last_message_datetime) if self.last_message_datetime else None

    result_model: "Model"
    result_dataset: "Dataset"
    result_prediction: "Prediction"
    result_docker_image: "DockerImage"
