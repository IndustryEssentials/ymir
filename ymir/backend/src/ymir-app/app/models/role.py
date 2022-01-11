from sqlalchemy import Column, Integer, String, Text

from app.db.base_class import Base


class Role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), index=True)
    description = Column(Text)
