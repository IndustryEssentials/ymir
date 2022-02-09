from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


class CRUDWorkspace(CRUDBase[Workspace, WorkspaceCreate, WorkspaceUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[Workspace]:
        return db.query(self.model).filter(Workspace.user_id == user_id).one_or_none()


workspace = CRUDWorkspace(Workspace)
