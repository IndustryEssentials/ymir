from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Message
from app.schemas.message import MessageCreate, MessageUpdate
from app.schemas import CommonPaginationParams


class CRUDMessage(CRUDBase[Message, MessageCreate, MessageUpdate]):
    def create_message_from_task(
        self,
        db: Session,
        *,
        task_info: Dict,
    ) -> Message:
        db_obj = Message(
            user_id=task_info["user_id"],
            project_id=task_info["project_id"],
            state=task_info["state"],
            task_type=task_info["type"],
            dataset_id=task_info["result_dataset"]["id"] if task_info.get("result_dataset") else None,
            model_id=task_info["result_model"]["id"] if task_info.get("result_model") else None,
            prediction_id=task_info["result_prediction"]["id"] if task_info.get("result_prediction") else None,
            docker_image_id=task_info["result_docker_image"]["id"] if task_info.get("result_docker_image") else None,
            is_read=False,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_messages(
        self,
        db: Session,
        *,
        user_id: int,
        project_id: Optional[int],
        pagination: CommonPaginationParams,
    ) -> Tuple[List[Message], int]:
        start_time, end_time = pagination.start_time, pagination.end_time
        offset, limit = pagination.offset, pagination.limit
        order_by = pagination.order_by.name
        is_desc = pagination.is_desc

        query = db.query(self.model)
        query = query.filter(self.model.user_id == user_id, not_(self.model.is_read))

        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)

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

        if limit:
            return query.offset(offset).limit(limit).all(), query.count()
        return query.all(), query.count()


message = CRUDMessage(Message)
