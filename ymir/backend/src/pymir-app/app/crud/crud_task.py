import json
from datetime import datetime
from typing import List, Optional, Tuple, Union

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app.config import settings
from app.crud.base import CRUDBase
from app.models.task import Task, TaskState, TaskType
from app.schemas.task import TaskCreate, TaskUpdate


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    def create_task(
        self, db: Session, *, obj_in: TaskCreate, task_hash: str, user_id: int,
    ) -> Task:
        config = obj_in.config
        if isinstance(config, dict):
            config = json.dumps(config)
        db_obj = Task(
            name=obj_in.name,
            type=obj_in.type.name,
            config=config,
            hash=task_hash,
            user_id=user_id,
            state=TaskState.pending.name,
            progress=0,
            parameters=obj_in.parameters.json() if obj_in.parameters else None,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_tasks_by_states(
        self, db: Session, states: List[TaskState], including_deleted: bool = False
    ) -> List[Task]:
        query = db.query(self.model)
        if not including_deleted:
            query = query.filter(not_(self.model.is_deleted))
        return query.filter(self.model.state.in_(states)).all()

    def update_task_state(
        self, db: Session, *, task_id: int, new_state: TaskState
    ) -> Optional[Task]:
        db_obj = self.get(db, id=task_id)
        if not db_obj:
            return None
        db_obj.state = new_state.name
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_tasks(
        self,
        db: Session,
        user_id: Optional[int] = None,
        name: Optional[str] = None,
        type_: Optional[TaskType] = None,
        state: Optional[TaskState] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        offset: int = 0,
        limit: int = settings.DEFAULT_LIMIT,
    ) -> Tuple[List[Task], int]:
        query = db.query(self.model).filter(not_(self.model.is_deleted))
        if user_id:
            query = query.filter(self.model.user_id == user_id)
        if name:
            query = query.filter(self.model.name.like(f"%{name}%"))
        if type_:
            query = query.filter(self.model.type == type_)
        if state:
            query = query.filter(self.model.state == state)
        if start_time and end_time:
            _start_time = datetime.utcfromtimestamp(start_time)
            _end_time = datetime.utcfromtimestamp(end_time)
            query = query.filter(
                and_(
                    self.model.create_datetime >= _start_time,
                    self.model.create_datetime <= _end_time,
                )
            )

        query = query.order_by(desc(self.model.id))
        return query.offset(offset).limit(limit).all(), query.count()


task = CRUDTask(Task)
