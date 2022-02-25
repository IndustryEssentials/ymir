from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    def get_multi_projects(
        self,
        db: Session,
        *,
        user_id: int,
        name: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = None,
        order_by: str = "id",
        is_desc: bool = True,
    ) -> Tuple[List[Project], int]:
        # each dataset is associate with one task
        # we need related task info as well
        query = db.query(self.model)
        query = query.filter(self.model.user_id == user_id, not_(self.model.is_deleted))

        if start_time and end_time:
            _start_time = datetime.utcfromtimestamp(start_time)
            _end_time = datetime.utcfromtimestamp(end_time)
            query = query.filter(
                and_(
                    self.model.create_datetime >= _start_time,
                    self.model.create_datetime <= _end_time,
                )
            )

        if name:
            query = query.filter(self.model.name.like(f"%{name}%"))

        order_by_column = getattr(self.model, order_by)
        if is_desc:
            order_by_column = desc(order_by_column)
        query = query.order_by(order_by_column)

        if limit:
            return query.offset(offset).limit(limit).all(), query.count()
        return query.all(), query.count()


project = CRUDProject(Project)
