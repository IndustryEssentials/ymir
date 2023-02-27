import json
from datetime import datetime
from enum import IntEnum
from typing import Dict, List, Optional, Tuple, Union

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app import schemas, models
from app.constants.state import ResultState, TaskType
from app.crud.base import CRUDBase
from app.models import Dataset
from app.models.dataset_group import DatasetGroup
from app.models.project import Project
from app.schemas.dataset import DatasetCreate, DatasetUpdate
from app.schemas import CommonPaginationParams


class CRUDDataset(CRUDBase[Dataset, DatasetCreate, DatasetUpdate]):
    def get_multi_datasets(
        self,
        db: Session,
        *,
        user_id: int,
        project_id: Optional[int] = None,
        group_id: Optional[int] = None,
        group_name: Optional[str] = None,
        source: Optional[TaskType] = None,
        exclude_source: Optional[TaskType] = None,
        state: Optional[IntEnum] = None,
        object_type: Optional[IntEnum] = None,
        visible: bool = True,
        allow_empty: bool = True,
        pagination: CommonPaginationParams,
    ) -> Tuple[List[Dataset], int]:
        # each dataset is associate with one task
        # we need related task info as well
        start_time, end_time = pagination.start_time, pagination.end_time
        offset, limit = pagination.offset, pagination.limit
        order_by = pagination.order_by.name
        is_desc = pagination.is_desc

        query = db.query(self.model)
        query = query.filter(
            self.model.user_id == user_id,
            self.model.is_visible == int(visible),
            not_(self.model.is_deleted),
        )

        if start_time and end_time:
            _start_time = datetime.utcfromtimestamp(start_time)
            _end_time = datetime.utcfromtimestamp(end_time)
            query = query.filter(
                and_(
                    self.model.create_datetime >= _start_time,
                    self.model.create_datetime <= _end_time,
                )
            )

        if state is not None:
            query = query.filter(self.model.result_state == int(state))
        if source is not None:
            query = query.filter(self.model.source == int(source))
        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)
        if group_id is not None:
            query = query.filter(self.model.dataset_group_id == group_id)
        if not allow_empty:
            query = query.filter(self.model.asset_count > 0)

        if object_type is not None:
            query = query.join(Project, Project.id == self.model.project_id).filter(
                Project.object_type == int(object_type)
            )
        if group_name:
            # basic fuzzy search
            query = query.join(DatasetGroup, DatasetGroup.id == self.model.dataset_group_id).filter(
                DatasetGroup.name.like(f"%{group_name}%")
            )

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

    def create_with_version(self, db: Session, obj_in: DatasetCreate) -> Dataset:
        # fixme
        #  add mutex lock to protect latest_version
        version_num = self.next_available_version(db, obj_in.dataset_group_id)

        db_obj = Dataset(
            version_num=version_num,
            hash=obj_in.hash,
            description=obj_in.description,
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
        self,
        db: Session,
        task: Union[schemas.TaskInternal, models.Task],
        dest_group_id: int,
        description: Optional[str] = None,
    ) -> Dataset:
        dataset_in = DatasetCreate(
            hash=task.hash,
            description=description,
            source=task.type,
            dataset_group_id=dest_group_id,
            project_id=task.project_id,
            user_id=task.user_id,
            task_id=task.id,
        )
        return self.create_with_version(db, obj_in=dataset_in)

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
            dataset.asset_count = result["total_assets_count"]

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

    def batch_toggle_visibility(self, db: Session, *, ids: List[int], action: str) -> List[Dataset]:
        objs = self.get_multi_by_ids(db, ids=ids)
        for obj in objs:
            if action == "hide":
                obj.is_visible = False
            elif action == "unhide":
                obj.is_visible = True
        db.bulk_save_objects(objs)
        db.commit()
        return objs

    def migrate_keywords(self, db: Session, *, id: int) -> Optional[Dataset]:
        dataset = self.get(db, id=id)
        if not dataset:
            return dataset
        if not dataset.keywords:
            return dataset
        keywords = json.loads(dataset.keywords)
        if "gt" in keywords:
            return dataset
        dataset.keywords = json.dumps({"gt": keywords, "pred": {}})
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset


dataset = CRUDDataset(Dataset)
