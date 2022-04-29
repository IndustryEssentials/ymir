from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.config import settings
from app.db.base_class import Base
from app.models.image_config import DockerImageConfig  # noqa
from app.models.image_relationship import DockerImageRelationship


class DockerImage(Base):
    __tablename__ = "docker_image"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.STRING_LEN_LIMIT), index=True, nullable=False)
    url = Column(String(settings.STRING_LEN_LIMIT), index=True, nullable=False)
    hash = Column(String(settings.STRING_LEN_LIMIT), index=True)
    description = Column(String(settings.LONG_STRING_LEN_LIMIT))
    state = Column(Integer, index=True, nullable=False)
    related = relationship(
        "DockerImage",
        secondary=DockerImageRelationship.__table__,
        primaryjoin=id == DockerImageRelationship.__table__.c.src_image_id,
        secondaryjoin=id == DockerImageRelationship.__table__.c.dest_image_id,
        uselist=True,
    )
    configs = relationship(
        "DockerImageConfig",
        primaryjoin="foreign(DockerImageConfig.image_id)==DockerImage.id",
        uselist=True,
    )
    is_shared = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
