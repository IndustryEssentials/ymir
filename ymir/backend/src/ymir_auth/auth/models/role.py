from sqlalchemy import Column, Integer, String

from auth.config import settings
from auth.db.base_class import Base


class Role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(settings.STRING_LEN_LIMIT), index=True)
    description = Column(String(settings.STRING_LEN_LIMIT))
