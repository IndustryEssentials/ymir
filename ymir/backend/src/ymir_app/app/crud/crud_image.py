from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy import desc, not_
from sqlalchemy.orm import Session

from app.constants.state import DockerImageState, DockerImageType
from app.crud.base import CRUDBase
from app.models.image import DockerImage
from app.models.image_config import DockerImageConfig
from app.schemas.image import DockerImageCreate, DockerImageUpdate


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
            query = query.filter(DockerImage.configs.any(DockerImageConfig.type == int(filters["type"])))

        query = query.order_by(desc(self.model.create_datetime))
        if limit:
            return query.offset(offset).limit(limit).all(), query.count()
        else:
            return query.all(), query.count()

    def get_inference_docker_image(self, db: Session, url: str) -> Optional[DockerImage]:
        query = db.query(self.model).filter(not_(self.model.is_deleted))
        query = query.filter(DockerImage.configs.any(DockerImageConfig.type == int(DockerImageType.infer)))
        return query.filter(self.model.url == url).first()  # type: ignore

    def get_by_url(self, db: Session, url: str) -> Optional[DockerImage]:
        query = db.query(self.model).filter(not_(self.model.is_deleted))
        return query.filter(self.model.url == url).first()  # type: ignore

    def docker_name_exists(self, db: Session, url: str) -> bool:
        query = db.query(self.model).filter(not_(self.model.is_deleted))
        return query.filter(self.model.url == url).first() is not None

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

    def update_state(self, db: Session, *, docker_image: DockerImage, state: DockerImageState) -> DockerImage:
        update_data = {"state": int(state)}
        return self.update(db, db_obj=docker_image, obj_in=update_data)

    def update_sharing_status(self, db: Session, *, docker_image: DockerImage, is_shared: bool = True) -> DockerImage:
        update_data = {"is_shared": is_shared}
        return self.update(db, db_obj=docker_image, obj_in=update_data)

    def update_from_dict(self, db: Session, *, docker_image_id: int, updates: Dict) -> Optional[DockerImage]:
        docker_image = self.get(db, id=docker_image_id)
        if docker_image:
            return self.update(db, db_obj=docker_image, obj_in=updates)
        return docker_image


docker_image = CRUDDockerImage(DockerImage)
