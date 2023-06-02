from typing import Any, Dict, List, Optional, Tuple, Union

from fastapi.logger import logger
from sqlalchemy import desc, not_, and_
from sqlalchemy.orm import Session

from app.constants.state import ResultState, DockerImageType
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
            query = query.filter(DockerImage.result_state == int(filters["state"]))
        if filters.get("url"):
            query = query.filter(DockerImage.url == filters["url"])
        if filters.get("object_type") and filters.get("type"):
            query = query.filter(
                DockerImage.configs.any(
                    and_(
                        DockerImageConfig.object_type == int(filters["object_type"]),
                        DockerImageConfig.type == int(filters["type"]),
                    )
                )
            )
        if filters.get("is_official"):
            query = query.filter(self.model.is_official)

        query = query.order_by(desc(self.model.create_datetime))
        if limit:
            return query.offset(offset).limit(limit).all(), query.count()
        else:
            return query.all(), query.count()

    def get_inference_docker_image(self, db: Session, id: int) -> Optional[DockerImage]:
        query = db.query(self.model).filter(not_(self.model.is_deleted))
        query = query.filter(DockerImage.configs.any(DockerImageConfig.type == int(DockerImageType.infer)))
        return query.filter(self.model.id == id).first()  # type: ignore

    def get_official_docker_images(self, db: Session) -> List[DockerImage]:
        query = db.query(self.model).filter(not_(self.model.is_deleted))
        return query.filter(self.model.is_official).all()

    def get_by_url(self, db: Session, url: str) -> Optional[DockerImage]:
        query = db.query(self.model).filter(not_(self.model.is_deleted))
        return query.filter(self.model.url == url).first()  # type: ignore

    def get_by_name(self, db: Session, name: str) -> Optional[DockerImage]:
        query = db.query(self.model).filter(not_(self.model.is_deleted))
        return query.filter(self.model.name == name).first()  # type: ignore

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

    def update_state(self, db: Session, *, docker_image: DockerImage, state: ResultState) -> DockerImage:
        update_data = {"result_state": int(state)}
        return self.update(db, db_obj=docker_image, obj_in=update_data)

    def toggle_offical_image(self, db: Session, *, docker_image_id: int, is_official: bool) -> Optional[DockerImage]:
        docker_image = self.get(db, docker_image_id)
        if not docker_image:
            return docker_image
        return self.update(db, db_obj=docker_image, obj_in={"is_official": is_official})

    def update_from_dict(self, db: Session, *, docker_image_id: int, updates: Dict) -> Optional[DockerImage]:
        docker_image = self.get(db, id=docker_image_id)
        if not docker_image:
            return docker_image
        if updates.get("is_official"):
            # ensure there is at most one offical image
            logger.info(f"updating {docker_image_id} as official docker_image, unsetting others")
            for existing_image in self.get_official_docker_images(db):
                logger.info(f"unsetting official docker_image {existing_image.id}")
                self.toggle_offical_image(db, docker_image_id=existing_image.id, is_official=False)
            # Note that we have to re-get docker_image SQLAlchemy ORM object
            # because updating other docker images has ended original session
            docker_image = self.get(db, id=docker_image_id)
            if not docker_image:  # make mypy happy
                return docker_image
        return self.update(db, db_obj=docker_image, obj_in=updates)


docker_image = CRUDDockerImage(DockerImage)
