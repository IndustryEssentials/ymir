from datetime import datetime
import json

from typing import Dict

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, UniqueConstraint

from app.config import settings
from app.db.base_class import Base


class ModelStage(Base):
    __tablename__ = "model_stage"
    __table_args__ = (UniqueConstraint("model_id", "name"),)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.STRING_LEN_LIMIT), index=True)
    timestamp = Column(Integer, nullable=False)
    map = Column(Float, nullable=True)
    serialized_metrics = Column(Text(settings.LONG_STRING_LEN_LIMIT))
    model_id = Column(Integer, index=True, nullable=False)

    is_deleted = Column(Boolean, default=False, nullable=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    @property
    def metrics(self) -> Dict:
        return json.loads(self.serialized_metrics) if self.serialized_metrics else {}
