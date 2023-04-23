from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.config import settings
from app.db.base_class import Base
from app.models.dataset import Dataset  # noqa


class DatasetGroup(Base):
    __tablename__ = "dataset_group"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.STRING_LEN_LIMIT), index=True, nullable=False)
    description = Column(String(settings.STRING_LEN_LIMIT))

    project_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)

    datasets = relationship(
        "Dataset",
        primaryjoin="foreign(Dataset.dataset_group_id)==DatasetGroup.id",
        backref="group",
        uselist=True,
        viewonly=True,
    )
    visible_datasets = relationship(
        "Dataset",
        primaryjoin="and_(foreign(Dataset.dataset_group_id)==DatasetGroup.id, foreign(Dataset.is_visible))",
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

    @property
    def is_visible(self) -> bool:
        return bool(self.visible_datasets)
