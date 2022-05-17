import json
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app.config import settings
from app.crud.base import CRUDBase
from app.models import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.api.errors.errors import ProjectNotFound


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    def create_project(
        self,
        db: Session,
        *,
        obj_in: ProjectCreate,
        user_id: int,
    ) -> Project:

        training_keywords = json.dumps(obj_in.training_keywords)

        db_obj = Project(
            user_id=user_id,
            name=obj_in.name,
            iteration_target=obj_in.iteration_target,
            map_target=obj_in.map_target,  # type: ignore
            training_dataset_count_target=obj_in.training_dataset_count_target,
            mining_strategy=obj_in.mining_strategy,
            chunk_size=obj_in.chunk_size,
            training_type=obj_in.training_type,
            training_keywords=training_keywords,
            description=obj_in.description,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

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

    def get_all_projects(self, db: Session, *, offset: int = 0, limit: int = settings.DEFAULT_LIMIT) -> List[Project]:
        query = db.query(self.model)
        query = query.filter(not_(self.model.is_deleted))
        return query.offset(offset).limit(limit).all()

    def update_current_iteration(
        self,
        db: Session,
        *,
        project_id: int,
        iteration_id: int,
    ) -> Project:
        project = self.get(db, id=project_id)
        if not project:
            raise ProjectNotFound()
        project.current_iteration_id = iteration_id
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def update_resources(self, db: Session, *, project_id: int, project_update: ProjectUpdate) -> Project:
        project = self.get(db, id=project_id)
        if not project:
            raise ProjectNotFound()
        return self.update(db, db_obj=project, obj_in=project_update)


project = CRUDProject(Project)
