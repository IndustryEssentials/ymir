from auth.crud.base import CRUDBase
from auth.models import Role
from auth.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    ...


role = CRUDRole(Role)
