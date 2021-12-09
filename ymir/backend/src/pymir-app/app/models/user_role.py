from sqlalchemy import Column, Integer, UniqueConstraint

from app.db.base_class import Base


class UserRole(Base):
    __tablename__ = "user_role"
    user_id = Column(Integer, primary_key=True, index=True, nullable=False)
    role_id = Column(Integer, primary_key=True, index=True, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "role_id", name="unique_user_role"),)
