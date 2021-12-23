import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Integer,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.db.base_class import Base
from app.models.image_relationship import DockerImageRelationship


class DockerImage(Base):
    __tablename__ = "docker_image"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.NAME_LEN_LIMIT), index=True)
    url = Column(String(settings.PARA_LEN_LIMIT), index=True)
    hash = Column(String(settings.HASH_LEN_LIMIT), index=True)
    config = Column(Text(settings.CONFIG_LEN_LIMIT))
    description = Column(Text(settings.CONFIG_LEN_LIMIT))
    type = Column(Integer, index=True)
    state = Column(Integer, index=True)
    related = relationship(
        "DockerImage",
        secondary=DockerImageRelationship.__table__,
        primaryjoin=id == DockerImageRelationship.__table__.c.src_image_id,
        secondaryjoin=id == DockerImageRelationship.__table__.c.dest_image_id,
        uselist=True,
    )
    is_shared = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    create_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_datetime = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
