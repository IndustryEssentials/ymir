from sqlalchemy import Column, Integer, String

from app.config import settings
from app.db.base_class import Base


class Role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.STRING_LEN_LIMIT), index=True)
    description = Column(String(settings.STRING_LEN_LIMIT))
