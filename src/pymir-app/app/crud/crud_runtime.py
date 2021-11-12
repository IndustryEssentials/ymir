from datetime import datetime
from typing import List, Optional, Tuple, Union

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app.config import settings
from app.crud.base import CRUDBase
from app.models.runtime import Runtime
from app.schemas.runtime import RuntimeCreate, RuntimeType, RuntimeUpdate


class CRUDRuntime(CRUDBase[Runtime, RuntimeCreate, RuntimeUpdate]):
    def get_multi_runtimes(
        self,
        db: Session,
        *,
        name: Optional[str] = None,
        hash_: Optional[str] = None,
        type_: Optional[RuntimeType] = None,
    ) -> List[Runtime]:
        query = db.query(self.model).filter(not_(self.model.is_deleted))
        if name:
            query = query.filter(self.model.name.like(f"%{name}%"))
        if hash_:
            query = query.filter(self.model.hash == hash_)
        if type_:
            query = query.filter(self.model.type == type_)
        return query.all()

    def get_inference_runtime(self, db: Session) -> Optional[Runtime]:
        query = db.query(self.model).filter(not_(self.model.is_deleted))
        query = query.filter(self.model.type == RuntimeType.inference)
        return query.first()


runtime = CRUDRuntime(Runtime)
