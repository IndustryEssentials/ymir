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
from app.utils.ymir_controller import gen_task_hash


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    def create_task(
        self,
        db: Session,
        *,
        obj_in: TaskCreate,
        task_hash: str,
        user_id: int,
        state: int = int(TaskState.pending),
        percent: float = 0,
    ) -> Task:
        db_obj = Task(
            name=obj_in.name,
            type=obj_in.type,
            config=obj_in.docker_image_config if obj_in.docker_image_config else None,
            parameters=obj_in.parameters.json() if obj_in.parameters else None,
            project_id=obj_in.project_id,
            hash=task_hash,
            user_id=user_id,
            state=state,
            percent=percent,  # type: ignore
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_placeholder(
        self,
        db: Session,
        type_: TaskType,
        user_id: int,
        project_id: int,
        state_: TaskState = TaskState.done,
        hash_: Optional[str] = None,
        parameters: Optional[str] = None,
    ) -> Task:
        """
        create a task as placeholder, required by:
        - dataset import
        - dataset fusion
        - model import
        """
        task_hash = hash_ or gen_task_hash(user_id, project_id)
        # for a placeholder task, task state and percent are closely related
        percent = 1 if state_ is TaskState.done else 0
        db_obj = Task(
            name=task_hash,
            type=int(type_),
            project_id=project_id,
            hash=task_hash,
            user_id=user_id,
            state=int(state_),
            percent=percent,  # type: ignore
            parameters=parameters,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_tasks_by_states(
        self, db: Session, states: List[TaskState], including_deleted: bool = False, project_id: int = None
    ) -> List[Task]:
        query = db.query(self.model)
        if not including_deleted:
            query = query.filter(not_(self.model.is_deleted))
        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)

        return query.filter(self.model.state.in_([state.value for state in states])).all()

    def update_state(
        self,
        db: Session,
        *,
        task: Task,
        new_state: TaskState,
        state_code: Optional[str] = None,
    ) -> Task:
        task.state = int(new_state)
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

    def update_parameters_and_config(self, db: Session, *, task: Task, parameters: str, config: str) -> Task:
        task.parameters = parameters
        task.config = config
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def update_percent(self, db: Session, *, task: Task, percent: float) -> Task:
        task.percent = percent  # type: ignore
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def update_state_and_percent(
        self,
        db: Session,
        *,
        task: Task,
        new_state: TaskState,
        state_code: Optional[str] = None,
        percent: Optional[float],
    ) -> Task:
        task.state = int(new_state)
        if percent is not None:
            task.percent = percent  # type: ignore
        if state_code is not None:
            task.error_code = state_code
        db.add(task)
        db.commit()
        db.refresh(task)

        # for task reached finale, update `duration` correspondingly
        if task.state in FinalStates:
            self.update_duration(db, task=task)
        return task

    def update_last_message_datetime(self, db: Session, *, task: Task, dt: datetime) -> Task:
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
            query = query.filter(self.model.type == int(type_))
        if state:
            query = query.filter(self.model.state == int(state))
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

    def terminate(self, db: Session, task: Task) -> Task:
        task.is_terminated = True
        db.add(task)
        db.commit()
        db.refresh(task)
        return task


task = CRUDTask(Task)
