from sqlalchemy import Column, Integer, String

from app.db.base_class import Base
from app.config import settings


class Role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.STRING_LEN_LIMIT), index=True)
    description = Column(String(settings.STRING_LEN_LIMIT))
