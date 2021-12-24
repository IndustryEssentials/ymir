from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import Session

from app.config import settings
from app.crud.base import CRUDBase
from app.models.image import DockerImage
from app.schemas.image import (
    DockerImageCreate,
    DockerImageState,
    DockerImageType,
    DockerImageUpdate,
)


class CRUDDockerImage(CRUDBase[DockerImage, DockerImageCreate, DockerImageUpdate]):
    def get_multi_with_filter(
        self,
        db: Session,
        *,
        offset: Optional[int] = 0,
        limit: Optional[int] = None,
        **filters: Any,
    ) -> Tuple[List[DockerImage], int]:
        query = db.query(self.model)
        query = query.filter(not_(self.model.is_deleted))
        if filters.get("name"):
            query = query.filter(DockerImage.name.like(f"%{filters['name']}%"))
        if filters.get("state"):
            query = query.filter(DockerImage.state == int(filters["state"]))
        if filters.get("type"):
            query = query.filter(DockerImage.type == int(filters["type"]))

        query = query.order_by(desc(self.model.create_datetime))
        if limit:
            return query.offset(offset).limit(limit).all(), query.count()
        else:
            return query.all(), query.count()

    def get_inference_docker_image(self, db: Session) -> Optional[DockerImage]:
        query = db.query(self.model).filter(not_(self.model.is_deleted))
        query = query.filter(self.model.type == int(DockerImageType.infer))
        return query.first()

    def update(
        self,
        db: Session,
        *,
        db_obj: DockerImage,
        obj_in: Union[DockerImageUpdate, Dict[str, Any]],
    ) -> DockerImage:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def update_state(
        self, db: Session, *, docker_image: DockerImage, state: DockerImageState
    ) -> DockerImage:
        update_data = {"state": int(state)}
        return self.update(db, db_obj=docker_image, obj_in=update_data)

    def update_sharing_status(
        self, db: Session, *, docker_image: DockerImage, is_shared: bool = True
    ) -> DockerImage:
        update_data = {"is_shared": is_shared}
        return self.update(db, db_obj=docker_image, obj_in=update_data)


docker_image = CRUDDockerImage(DockerImage)
