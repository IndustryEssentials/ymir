from app.crud.base import CRUDBase
from app.models import Role
from app.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    ...


role = CRUDRole(Role)
