import json
import time
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app.config import settings
from app.constants.state import FinalStates, TaskState, TaskType
from app.crud.base import CRUDBase
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    def create_task(
        self,
        db: Session,
        *,
        obj_in: TaskCreate,
        task_hash: str,
        user_id: int,
        state: int = TaskState.pending.value,
        progress: int = 0,
    ) -> Task:
        config = obj_in.config
        if isinstance(config, dict):
            config = json.dumps(config)
        db_obj = Task(
            name=obj_in.name,
            type=obj_in.type.value,
            config=config,
            hash=task_hash,
            user_id=user_id,
            project_id=obj_in.project_id,
            state=state,
            progress=progress,
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
        return query.filter(
            self.model.state.in_([state.value for state in states])
        ).all()

    def update_state(
        self,
        db: Session,
        *,
        task: Task,
        new_state: TaskState,
        state_code: Optional[str] = None,
    ) -> Task:
        task.state = new_state.value
        if state_code is not None:
            task.error_code = state_code
        db.add(task)
        db.commit()
        db.refresh(task)

        # for task reached finale, update `duration` correspondingly
        if task.state in FinalStates:
            self.update_duration(db, task=task)

        return task

    def update_duration(self, db: Session, *, task: Task) -> Task:
        task.duration = int(time.time() - datetime.timestamp(task.create_datetime))
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def update_progress(self, db: Session, *, task: Task, progress: int) -> Task:
        task.progress = progress
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def update_last_message_datetime(
        self, db: Session, *, task: Task, dt: datetime
    ) -> Task:
        task.last_message_datetime = dt
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def get_multi_tasks(
        self,
        db: Session,
        *,
        user_id: Optional[int] = None,
        name: Optional[str] = None,
        type_: Optional[TaskType] = None,
        state: Optional[TaskState] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        offset: int = 0,
        limit: int = settings.DEFAULT_LIMIT,
        order_by: str,
        is_desc: bool = True,
    ) -> Tuple[List[Task], int]:
        query = db.query(self.model).filter(not_(self.model.is_deleted))
        if user_id:
            query = query.filter(self.model.user_id == user_id)
        if name:
            query = query.filter(self.model.name.like(f"%{name}%"))
        if type_:
            query = query.filter(self.model.type == type_.value)
        if state:
            if state == TaskState.terminate:
                query = query.filter(
                    self.model.state.in_(
                        [TaskState.terminate.value, TaskState.premature.value]
                    )
                )
            else:
                query = query.filter(self.model.state == state.value)
        if start_time and end_time:
            _start_time = datetime.utcfromtimestamp(start_time)
            _end_time = datetime.utcfromtimestamp(end_time)
            query = query.filter(
                and_(
                    self.model.create_datetime >= _start_time,
                    self.model.create_datetime <= _end_time,
                )
            )

        order_by_column = getattr(self.model, order_by)
        if is_desc:
            order_by_column = desc(order_by_column)
        query = query.order_by(order_by_column)

        return query.offset(offset).limit(limit).all(), query.count()


task = CRUDTask(Task)
