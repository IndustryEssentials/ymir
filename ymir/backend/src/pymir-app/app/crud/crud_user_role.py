from typing import Optional, Protocol, Tuple

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Role, UserRole
from app.schemas.user_role import UserRoleCreate, UserRoleUpdate


class UserRoleRes(Protocol):
    role_name: str
    role_id: int
    user_id: int


class CRUDUserRole(CRUDBase[UserRole, UserRoleCreate, UserRoleUpdate]):
    def get_role_name_by_user_id(
        self, db: Session, *, user_id: int
    ) -> Optional[UserRoleRes]:
        query = db.query(
            Role.name.label("role_name"), self.model.role_id, self.model.user_id
        )
        query = query.join(Role, self.model.role_id == Role.id)
        return query.filter(UserRole.user_id == user_id).first()


user_role = CRUDUserRole(UserRole)
