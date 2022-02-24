from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.config import settings
from app.db.base_class import Base
from app.models.model import Model  # noqa


class ModelGroup(Base):
    __tablename__ = "model_group"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.STRING_LEN_LIMIT), index=True, nullable=False)

    user_id = Column(Integer, index=True, nullable=False)
    project_id = Column(Integer, index=True, nullable=False)
    training_dataset_id = Column(Integer, index=True, nullable=False)

    models = relationship(
        "Model",
        primaryjoin="foreign(Model.model_group_id)==ModelGroup.id",
        uselist=True,
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
