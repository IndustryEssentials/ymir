from sqlalchemy import Column, Integer, Text, UniqueConstraint, SmallInteger

from app.config import settings
from app.db.base_class import Base


class DockerImageConfig(Base):
    __tablename__ = "docker_image_config"
    image_id = Column(Integer, primary_key=True, index=True, nullable=False)
    object_type = Column(SmallInteger, index=True, default=2, nullable=False)
    type = Column(Integer, primary_key=True, index=True, nullable=False)
    config = Column(Text(settings.TEXT_LEN_LIMIT), nullable=False)

    __table_args__ = (UniqueConstraint("image_id", "object_type", "type", name="unique_image_type"),)
