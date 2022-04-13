from typing import List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import DockerImageRelationship
from app.schemas.image_relationship import (
    ImageRelationshipCreate,
    ImageRelationshipUpdate,
)


class CRUDImageRelationship(CRUDBase[DockerImageRelationship, ImageRelationshipCreate, ImageRelationshipUpdate]):
    def get_relationships_of_src_image(self, db: Session, *, src_image_id: int) -> List[DockerImageRelationship]:
        return db.query(self.model).filter(self.model.src_image_id == src_image_id).all()

    def get_relationships_of_dest_image(self, db: Session, *, dest_image_id: int) -> List[DockerImageRelationship]:
        return db.query(self.model).filter(self.model.dest_image_id == dest_image_id).all()

    def delete_relationships_of_src_image(self, db: Session, *, src_image_id: int) -> None:
        """
        remove all relationships from src_image_id
        """
        db.query(self.model).filter(self.model.src_image_id == src_image_id).delete()

    def make_relationships_as(
        self, db: Session, *, src_image_id: int, dest_image_ids: List[int]
    ) -> List[DockerImageRelationship]:
        """
        idempotently make relationships as src_image_id mapping to all dest_image_ids
        """
        self.delete_relationships_of_src_image(db, src_image_id=src_image_id)
        db_objs = [
            self.model(src_image_id=src_image_id, dest_image_id=dest_image_id) for dest_image_id in dest_image_ids
        ]
        db.bulk_save_objects(db_objs)
        db.commit()
        return db_objs

    def having_relationships(self, db: Session, *, image_id: int) -> bool:
        return bool(
            self.get_relationships_of_src_image(db, src_image_id=image_id)
            or self.get_relationships_of_dest_image(db, dest_image_id=image_id)
        )


image_relationship = CRUDImageRelationship(DockerImageRelationship)
