import json
from datetime import datetime
from enum import IntEnum
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app import schemas
from app.constants.state import ResultState, TaskType
from app.crud.base import CRUDBase
from app.models import Dataset
from app.schemas.dataset import DatasetCreate, DatasetUpdate


class CRUDDataset(CRUDBase[Dataset, DatasetCreate, DatasetUpdate]):
    def get_multi_datasets(
        self,
        db: Session,
        *,
        user_id: int,
        project_id: Optional[int] = None,
        group_id: Optional[int] = None,
        source: Optional[TaskType] = None,
        state: Optional[IntEnum] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = None,
        order_by: str = "id",
        is_desc: bool = True,
    ) -> Tuple[List[Dataset], int]:
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

        if state:
            query = query.filter(self.model.result_state == int(state))
        if source:
            query = query.filter(self.model.source == int(source))
        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)
        if group_id is not None:
            query = query.filter(self.model.dataset_group_id == group_id)

        order_by_column = getattr(self.model, order_by)
        if is_desc:
            order_by_column = desc(order_by_column)
        query = query.order_by(order_by_column)

        if limit:
            return query.offset(offset).limit(limit).all(), query.count()
        return query.all(), query.count()

    def update_state(
        self,
        db: Session,
        *,
        dataset_id: int,
        new_state: ResultState,
    ) -> Optional[Dataset]:
        dataset = self.get(db, id=dataset_id)
        if not dataset:
            return dataset
        dataset.result_state = int(new_state)
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset

    def get_latest_version(self, db: Session, dataset_group_id: int) -> Optional[int]:
        query = db.query(self.model)
        latest_dataset_in_group = (
            query.filter(self.model.dataset_group_id == dataset_group_id).order_by(desc(self.model.id)).first()
        )
        if latest_dataset_in_group:
            return latest_dataset_in_group.version_num
        return None

    def next_available_version(self, db: Session, group_id: int) -> int:
        latest_version = self.get_latest_version(db, group_id)
        return latest_version + 1 if latest_version is not None else 1

    def create_with_version(self, db: Session, obj_in: DatasetCreate, dest_group_name: Optional[str] = None) -> Dataset:
        # fixme
        #  add mutex lock to protect latest_version
        version_num = self.next_available_version(db, obj_in.dataset_group_id)

        db_obj = Dataset(
            version_num=version_num,
            hash=obj_in.hash,
            source=int(obj_in.source),
            result_state=int(obj_in.result_state),
            dataset_group_id=obj_in.dataset_group_id,
            project_id=obj_in.project_id,
            user_id=obj_in.user_id,
            task_id=obj_in.task_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_as_task_result(
        self, db: Session, task: schemas.TaskInternal, dest_group_id: int, dest_group_name: str
    ) -> Dataset:
        dataset_in = DatasetCreate(
            hash=task.hash,
            source=task.type,
            dataset_group_id=dest_group_id,
            project_id=task.project_id,
            user_id=task.user_id,
            task_id=task.id,
        )
        return self.create_with_version(db, obj_in=dataset_in, dest_group_name=dest_group_name)

    def finish(
        self,
        db: Session,
        dataset_id: int,
        result_state: ResultState = ResultState.ready,
        result: Optional[Dict] = None,
    ) -> Optional[Dataset]:
        dataset = self.get(db, id=dataset_id)
        if not dataset:
            return dataset
        dataset.result_state = int(result_state)

        if result:
            dataset.keywords = json.dumps(result["keywords"])
            dataset.ignored_keywords = json.dumps(result["ignored_keywords"])
            dataset.negative_info = json.dumps(result["negative_info"])
            dataset.asset_count = result["asset_count"]
            dataset.keyword_count = result["keyword_count"]

        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset

    def remove_group_resources(self, db: Session, *, group_id: int) -> List[Dataset]:
        objs = db.query(self.model).filter(self.model.dataset_group_id == group_id).all()
        for obj in objs:
            obj.is_deleted = True
        db.bulk_save_objects(objs)
        db.commit()
        return objs


dataset = CRUDDataset(Dataset)
